from sqlalchemy import select, asc, desc, or_
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.Core.Database import getAsyncDb
from app.Models.City import City
from app.Models.Country import Country
from app.Http.Requests.CityRequest import CityListRequest, CityFormRequest
from app.Http.Responses.CityResponse import CityItemResponse
from app.Http.Responses.JsonResponse import JsonResponse
from app.Http.Responses.CommonResponse import SimpleListItemResponse
from bootstrap.exception.exceptions import raiseUnprocessableContent, raiseNotFound
from bootstrap.exception.validations import exists
from app.Http.Requests.DtRequest import DtRequest
from libs.Paginate import paginate
from typing import Optional
from string import capwords


class CityController:
    def __init__(self) -> None:
        pass

    async def index(
        self, request: DtRequest = Depends(), db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        query = select(City).join(Country, Country.id == City.country_id)
        if request.search is not None:
            query = query.where(
                or_(
                    City.name.like(f"%{request.search}%"),
                    City.state_code.like(f"%{request.search}%"),
                    City.country_code.like(f"%{request.search}%"),
                    City.latitude.like(f"%{request.search}%"),
                    City.longitude.like(f"%{request.search}%"),
                    Country.name.like(f"%{request.search}%"),
                )
            )
        columns = {
            "name": City.name,
            "state_code": City.state_code,
            "country_code": City.country_code,
            "latitude": City.latitude,
            "longitude": City.longitude,
            "created_at": City.created_at,
            "countries.name": Country.name,
        }
        order_by = City.created_at
        if request.order_by is not None:
            order_by = columns.get(request.order_by)
        direction = asc if request.order_dir == "asc" else desc
        query = query.order_by(direction(order_by))

        data = await paginate(db, query, request)
        data.list = [
            CityItemResponse(
                id=item["City"].id,
                name=item["City"].name,
                state_code=item["City"].state_code,
                country_id=item["City"].country_id,
                country_code=item["City"].country_code,
                country_name=item["Country"].name,
                latitude=item["City"].latitude,
                longitude=item["City"].longitude,
                created_at=item["City"].created_at,
            )
            for item in data.list
        ]
        return JsonResponse(data={"countries": data})

    async def list(
        self,
        request: CityListRequest = Depends(),
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        list_type = request.list_type
        stmt = await db.execute(select(City).order_by(asc(City.name)))
        list = stmt.scalars().all()
        list = [
            SimpleListItemResponse(**self.__listItemFormat(list_type, item))
            for item in list
        ]
        return JsonResponse(data={"list": list})

    async def show(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        city = await self.__findForWrite(db, id)
        return JsonResponse(data=CityItemResponse(**city.toDict()).model_dump())

    async def store(
        self, request: CityFormRequest, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        await self.__validateFormRequest(db, request)
        city = City(**request.model_dump())
        db.add(city)
        await db.commit()
        return JsonResponse(message="City created successfully.")

    async def update(
        self,
        request: CityFormRequest,
        id: int,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        city: City = await self.__findForWrite(db, id)
        await self.__validateFormRequest(db, request, id)
        city.name = request.name
        city.state_code = request.state_code
        city.country_code = request.country_code
        city.country_id = request.country_id
        city.latitude = request.latitude
        city.longitude = request.longitude
        await db.commit()
        return JsonResponse(message="City updated successfully.")

    async def delete(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        city: City = await self.__findForWrite(db, id)
        await db.delete(city)
        await db.commit()
        return JsonResponse(message="City deleted successfully.")

    async def __findForWrite(self, db: AsyncSession, id: int) -> City:
        query = await db.execute(select(City).where(City.id == id))
        city: Optional[City] = query.scalar_one_or_none()
        if city is None:
            raiseNotFound("City not found.")
        return city

    def __listItemFormat(self, list_type: Optional[str], city: City) -> dict:
        label = city.name
        value = str(city.id)
        if list_type == "with_country":
            label = f"{city.name} ({city.country_code})"
        elif list_type == "full":
            label = f"{city.name} ({city.country_code}, {city.state_code})"
        return {
            "label": label,
            "value": value,
        }

    async def __validateFormRequest(
        self, db: AsyncSession, request: CityFormRequest, id: Optional[int] = None
    ):
        errors = {}
        filter = {"country_id": id, "state_code": request.state_code}
        if id is not None:
            filter["id"] = {"!=": id}
        if not await exists(db, Country, "id", request.country_id):
            errors["country_id"] = ["Country does not exist."]
        elif await exists(db, City, "name", request.name, filter):
            errors["name"] = ["This name already exists."]
        if len(errors) > 0:
            raiseUnprocessableContent(errors)
