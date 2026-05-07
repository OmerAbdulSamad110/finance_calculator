from sqlalchemy import select, asc, desc, or_
from fastapi import Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.Core.Database import getAsyncDb
from app.Models.Company import Company
from app.Models.Country import Country
from app.Models.City import City
from app.Http.Requests.CompanyRequest import CompanyFormRequest
from app.Http.Responses.CompanyResponse import CompanyDetailResponse
from app.Http.Responses.JsonResponse import JsonResponse
from app.Http.Responses.CommonResponse import SimpleListItemResponse
from bootstrap.exception.exceptions import raiseUnprocessableContent, raiseNotFound
from bootstrap.exception.validations import (
    exists,
    fieldsExists,
    isImage,
    validateMimes,
    fileMaxSize,
    isUrl,
    isNumber,
)
from app.Http.Requests.DtRequest import DtRequest, CursorPaginateRequest
from libs.Paginate import paginate, cursorPaginate
from libs.Storage import Storage
from utils.helper import snakeCase


class CompanyController:
    def __init__(self) -> None:
        pass

    async def index(
        self, request: DtRequest = Depends(), db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        query = (
            select(Company)
            .join(Country, Country.id == Company.country_id)
            .join(City, City.id == Company.city_id)
        )
        if request.search is not None:
            query = query.where(
                or_(
                    Company.name.like(f"%{request.search}%"),
                    Company.address.like(f"%{request.search}%"),
                    Company.email.like(f"%{request.search}%"),
                    Company.phone.like(f"%{request.search}%"),
                    Company.website_url.like(f"%{request.search}%"),
                    Company.iata_no.like(f"%{request.search}%"),
                    Company.zip_code.like(f"%{request.search}%"),
                    Company.nature_of_business.like(f"%{request.search}%"),
                    Country.name.like(f"%{request.search}%"),
                    City.name.like(f"%{request.search}%"),
                )
            )
        columns = {
            "name": Company.name,
            "address": Company.address,
            "email": Company.email,
            "phone": Company.phone,
            "website_url": Company.website_url,
            "iata_no": Company.iata_no,
            "zip_code": Company.zip_code,
            "nature_of_business": Company.nature_of_business,
            "is_active": Company.is_active,
            "created_at": Company.created_at,
            "countries.name": Country.name,
            "cities.name": City.name,
        }
        order_by = Company.created_at
        if request.order_by is not None:
            order_by = columns.get(request.order_by)
        direction = asc if request.order_dir == "asc" else desc
        query = query.order_by(direction(order_by))

        data = await paginate(db, query, request)
        data.list = [
            CompanyDetailResponse(
                id=item["Company"].id,
                name=item["Company"].name,
                logo=item["Company"].logo,
                certificate=item["Company"].certificate,
                address=item["Company"].address,
                email=item["Company"].email,
                phone=item["Company"].phone,
                website_url=item["Company"].website_url,
                iata_no=item["Company"].iata_no,
                zip_code=item["Company"].zip_code,
                nature_of_business=item["Company"].nature_of_business,
                is_active=item["Company"].is_active,
                country_id=item["Company"].country_id,
                country_name=item["Country"].name,
                city_id=item["Company"].city_id,
                city_name=item["City"].city.name,
                created_at=item["Company"].created_at,
            )
            for item in data.list
        ]
        return JsonResponse(data={"companies": data})

    async def list(
        self,
        request: CursorPaginateRequest = Depends(),
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        query = await db.execute(select(Company).order_by(asc(Company.name)))
        data = await cursorPaginate(db, query, request)
        data.list = [
            SimpleListItemResponse(
                label=item["Company"].name, value=str(item["Company"].id)
            )
            for item in data.list
        ]
        return JsonResponse(data={"list": list})

    async def show(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        company = await self.__findForWrite(db, id)
        return JsonResponse(data=CompanyDetailResponse(**company.toDict()).model_dump())

    async def store(
        self, request: CompanyFormRequest, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        await self.__validateFormRequest(db, request)
        company = Company(**request.model_dump(exclude=["logo", "certificate"]))
        db.add(company)
        await db.commit()
        if request.logo is not None or request.certificate is not None:
            await self.__storeFiles(db, company, request.logo, request.certificate)
        return JsonResponse(message="Company created successfully.")

    async def update(
        self,
        request: CompanyFormRequest,
        id: int,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        company: Company = await self.__findForWrite(db, id)
        await self.__validateFormRequest(db, request, id)
        company.name = request.name
        company.address = request.address
        company.email = request.email
        company.phone = request.phone
        company.website_url = request.website_url
        company.iata_no = request.iata_no
        company.zip_code = request.zip_code
        company.nature_of_business = request.nature_of_business
        company.is_active = request.is_active
        company.country_id = request.country_id
        company.city_id = request.city_id

        await self.__storeFiles(db, company, request.logo, request.certificate)
        return JsonResponse(message="Company updated successfully.")

    async def delete(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        company: Company = await self.__findForWrite(db, id)
        await db.delete(company)
        await db.commit()
        return JsonResponse(message="Company deleted successfully.")

    async def __findForWrite(self, db: AsyncSession, id: int) -> Company:
        query = await db.execute(select(Company).where(Company.id == id))
        company: Optional[Company] = query.scalar_one_or_none()
        if company is None:
            raiseNotFound("Company not found.")
        return company

    async def __storeFiles(
        self,
        db: AsyncSession,
        company: Company,
        logo: Optional[UploadFile] = None,
        certificate: Optional[UploadFile] = None,
    ):
        company_path = f"companies/company_{company.id}_{snakeCase(company.name)}"
        logo_path = None
        certificate_path = None
        if logo is not None:
            logo_path = await Storage.upload(logo, company_path, "logo")
            company.logo = logo_path
        if certificate is not None:
            certificate_path = await Storage.upload(
                certificate, company_path, "certificate"
            )
            company.certificate = certificate_path
        await db.commit()

    async def __validateFormRequest(
        self, db: AsyncSession, request: CompanyFormRequest, id: Optional[int] = None
    ):
        errors = {}
        existing_fields = await fieldsExists(
            db,
            Company,
            {
                "email": request.email,
                "iata_no": request.iata_no,
                "zip_code": request.zip_code,
            },
            id,
        )
        if request.website_url is not None and not isUrl(request.website_url):
            errors["website_url"] = ["Invalid website url format."]
        if "email" in existing_fields:
            errors["email"] = ["This email already exists."]
        if request.logo is not None:
            logo_errors = []
            if await fileMaxSize(request.logo, 2 * 1024 * 1024):
                logo_errors.append("The logo size must be less than 2MB.")
            if not await isImage(request.logo):
                logo_errors.append("The logo must be an image.")
            if not validateMimes(request.logo, ["png", "jpeg", "jpg"]):
                logo_errors.append("The logo must be of type png, jpeg or jpg.")
            if len(logo_errors) > 0:
                errors["logo"] = logo_errors
        if request.certificate is not None:
            certificate_errors = []
            if await fileMaxSize(request.certificate, 5 * 1024 * 1024):
                certificate_errors.append("The certificate size must be less than 5MB.")
            if not validateMimes(request.certificate, ["pdf"]):
                certificate_errors.append("The certificate must be of type pdf.")
            if len(certificate_errors) > 0:
                errors["certificate"] = certificate_errors
        if request.iata_no is not None:
            if not isNumber(request.iata_no, True):
                errors["iata_no"] = ["The IATA number should be a valid number."]
            elif "iata_no" in existing_fields:
                errors["iata_no"] = ["The IATA number already exists."]
        if not await exists(db, Country, "id", request.country_id):
            errors["country_id"] = ["Country does not exist."]
        if not await exists(db, City, "id", request.city_id):
            errors["city_id"] = ["City does not exist."]
        if request.zip_code is not None:
            if not isNumber(request.zip_code, True):
                errors["zip_code"] = ["The zip code should be a valid number."]
            elif "zip_code" in existing_fields:
                errors["zip_code"] = ["The zip code already exists."]
        if len(errors) > 0:
            raiseUnprocessableContent(errors)
