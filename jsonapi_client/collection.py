from abc import ABC
from typing import Generic, TypeVar
from urllib.parse import quote

from requests.auth import AuthBase  # type: ignore[import-untyped]

from .request import JsonAPIClient
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
        url = f"{self.base_url}{self.endpoint}"
        client = JsonAPIClient[T](url=url, schema=self.schema, auth=self.auth)
        return JsonAPIResource[T](client)


class JsonAPICollection(ABC, Generic[T]):
    endpoint: str
    schema: type[JsonAPIResourceSchema]

    def __init__(self, base_url: str, auth: AuthBase | None = None, default_page_size: int | None = None) -> None:
        self.base_url = base_url
        self.auth = auth
        self.default_page_size = default_page_size

    def resource(self, resource_id: str) -> JsonAPIResource[T]:
        url = f"{self.base_url}{self.endpoint}/{quote(resource_id)}"
        client = JsonAPIClient[T](url=url, schema=self.schema, auth=self.auth)
        return JsonAPIResource[T](client)

    def resources(self) -> JsonAPIResourcesList[T]:
        url = f"{self.base_url}{self.endpoint}"
        client = JsonAPIClient[T](url=url, schema=self.schema, auth=self.auth)
        return JsonAPIResourcesList[T](client, default_page_size=self.default_page_size)

