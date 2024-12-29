from abc import ABC
from typing import Generic, TypeVar
from urllib.parse import quote

from requests.auth import AuthBase  # type: ignore[import-untyped]

from .resource import JsonAPIResource
from .resources_list import JsonAPIResourcesList
from .schema import JsonAPIResourceSchema

T = TypeVar("T", bound=JsonAPIResourceSchema)


class JsonAPISingleton(ABC, Generic[T]):
    endpoint: str
    schema: type[JsonAPIResourceSchema]

    def __init__(self, base_url: str, auth: AuthBase | None = None) -> None:
        self.base_url = base_url
        self.auth = auth

    def resource(self) -> JsonAPIResource[T]:
        return JsonAPIResource[T](
            url=f"{self.base_url}{self.endpoint}",
            auth=self.auth,
            schema=self.schema,
        )


class JsonAPICollection(ABC, Generic[T]):
    endpoint: str
    schema: type[JsonAPIResourceSchema]

    def __init__(self, base_url: str, auth: AuthBase | None = None) -> None:
        self.base_url = base_url
        self.auth = auth

    def resource(self, resource_id: str) -> JsonAPIResource[T]:
        return JsonAPIResource[T](
            url=f"{self.base_url}{self._full_path(resource_id)}",
            auth=self.auth,
            schema=self.schema,
        )

    def resources(self) -> JsonAPIResourcesList[T]:
        return JsonAPIResourcesList[T](
            url=f"{self.base_url}{self.endpoint}",
            auth=self.auth,
            schema=self.schema,
        )

    def _full_path(self, resource_id: str) -> str:
        return f"{self.endpoint}/{quote(resource_id)}"
