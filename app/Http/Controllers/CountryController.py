from sqlalchemy import select, asc, desc
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.Core.Database import getAsyncDb
from app.Models.Country import Country
from app.Http.Requests.CountryRequest import CountryListRequest, CountryFormRequest
from app.Http.Responses.CountryResponse import CountryItemResponse
from app.Http.Responses.JsonResponse import JsonResponse
from app.Http.Responses.CommonResponse import SimpleListItemResponse
from bootstrap.exception.exceptions import raiseUnprocessableContent, raiseNotFound
from bootstrap.exception.validations import fieldsExists
from app.Http.Requests.DtRequest import DtRequest
from libs.Paginate import paginate
from typing import Optional
from string import capwords


class CountryController:
    def __init__(self) -> None:
        pass

    async def index(
        self, request: DtRequest = Depends(), db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        query = select(Country)
        if request.search is not None:
            query = query.where(
                Country.name.like(f"%{request.search}%"),
                Country.iso2_code.like(f"%{request.search}%"),
                Country.iso3_code.like(f"%{request.search}%"),
                Country.phone_code.like(f"%{request.search}%"),
                Country.currency_name.like(f"%{request.search}%"),
                Country.currency_code.like(f"%{request.search}%"),
                Country.currency_symbol.like(f"%{request.search}%"),
                Country.nationality.like(f"%{request.search}%"),
                Country.capital.like(f"%{request.search}%"),
                Country.region.like(f"%{request.search}%"),
                Country.sub_region.like(f"%{request.search}%"),
                Country.latitude.like(f"%{request.search}%"),
                Country.longitude.like(f"%{request.search}%"),
            )
        columns = {
            "name": Country.name,
            "iso2_code": Country.iso2_code,
            "iso3_code": Country.iso3_code,
            "phone_code": Country.phone_code,
            "currency_name": Country.currency_name,
            "currency_code": Country.currency_code,
            "currency_symbol": Country.currency_symbol,
            "nationality": Country.nationality,
            "capital": Country.capital,
            "region": Country.region,
            "sub_region": Country.sub_region,
            "latitude": Country.latitude,
            "longitude": Country.longitude,
        }
        order_by = Country.created_at
        if request.order_by is not None:
            order_by = columns.get(request.order_by)
        direction = asc if request.order_dir == "asc" else desc
        query = query.order_by(direction(order_by))

        data = await paginate(db, query, request)
        data.list = [
            CountryItemResponse(
                name=item["Country"].name,
                iso2_code=item["Country"].iso2_code,
                iso3_code=item["Country"].iso3_code,
                phone_code=item["Country"].phone_code,
                currency_name=item["Country"].currency_name,
                currency_code=item["Country"].currency_code,
                currency_symbol=item["Country"].currency_symbol,
                nationality=item["Country"].nationality,
                capital=item["Country"].capital,
                region=item["Country"].region,
                sub_region=item["Country"].sub_region,
                timezones=item["Country"].timezones,
                latitude=item["Country"].latitude,
                longitude=item["Country"].longitude,
            )
            for item in data.list
        ]
        return JsonResponse(data={"countries": data})

    async def list(
        self,
        request: CountryListRequest = Depends(),
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        list_type = request.list_type
        stmt = await db.execute(select(Country).order_by(asc(Country.name)))
        list = stmt.scalars().all()
        list = [
            SimpleListItemResponse(**self.__listItemFormat(list_type, item))
            for item in list
        ]
        return JsonResponse(data={"list": list})

    async def show(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        country = await self.__findForWrite(db, id)
        return JsonResponse(data=CountryItemResponse(**country.toDict()).model_dump())

    async def store(
        self, request: CountryFormRequest, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        await self.__validateFormRequest(db, request)
        country = Country(**request.model_dump())
        db.add(country)
        await db.commit()
        return JsonResponse(message="Country created successfully.")

    async def update(
        self,
        request: CountryFormRequest,
        id: int,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        country: Country = await self.__findForWrite(db, id)
        await self.__validateFormRequest(db, request, id)
        country.name = request.name
        country.iso2_code = request.iso2_code
        country.iso3_code = request.iso3_code
        country.phone_code = request.phone_code
        country.currency_name = request.currency_name
        country.currency_code = request.currency_code
        country.currency_symbol = request.currency_symbol
        country.nationality = request.nationality
        country.capital = request.capital
        country.region = request.region
        country.sub_region = request.sub_region
        country.latitude = request.latitude
        country.longitude = request.longitude
        await db.commit()
        return JsonResponse(message="Country updated successfully.")

    async def delete(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        country: Country = await self.__findForWrite(db, id)
        await db.delete(country)
        await db.commit()
        return JsonResponse(message="Country deleted successfully.")

    async def __findForWrite(self, db: AsyncSession, id: int) -> Country:
        query = await db.execute(select(Country).where(Country.id == id))
        country: Optional[Country] = query.scalar_one_or_none()
        if country is None:
            raiseNotFound("Country not found.")
        return country

    def __listItemFormat(self, list_type: Optional[str], country: Country) -> dict:
        label = country.name
        value = str(country.id)
        if list_type == "iso2":
            label = country.iso2_code
            value = str(country.id)
        elif list_type == "currency":
            label = country.currency_name
            value = country.currency_code
        elif list_type == "nationality":
            label = f"{country.nationality} ({capwords(country.iso2_code)})"
            value = str(country.iso2_code)
        return {
            "label": label,
            "value": value,
        }

    async def __validateFormRequest(
        self, db: AsyncSession, request: CountryFormRequest, id: Optional[int] = None
    ):
        errors = {}
        existing_fields = await fieldsExists(
            db,
            Country,
            {
                "name": request.name,
                "iso2_code": request.iso2_code,
                "iso3_code": request.iso3_code,
            },
            id,
        )
        if "name" in existing_fields:
            errors["name"] = ["This name already exists."]
        if "iso2_code" in existing_fields:
            errors["iso2_code"] = ["This ISO2 code already exists."]
        if "iso3_code" in existing_fields:
            errors["iso3_code"] = ["This ISO3 code already exists."]
        phone_code_errors = []
        if request.phone_code[0] != "+":
            phone_code_errors.append("The phone code should start with +.")
        elif not request.phone_code[1:].isnumeric():
            phone_code_errors.append("The phone code should be a valid number.")
        if len(phone_code_errors) > 0:
            errors["phone_code"] = phone_code_errors
        if request.region not in [
            "Asia",
            "Europe",
            "North America",
            "South America",
            "Africa",
            "Oceania",
        ]:
            errors["region"] = ["Invalid region given."]
        if len(errors) > 0:
            raiseUnprocessableContent(errors)
