from abc import ABC
from typing import Generic, TypeVar
from urllib.parse import urljoin

from requests.auth import AuthBase  # type: ignore[import-untyped]

from .resource import JsonAPIResource
from .resources_list import JsonAPIResourcesList
from .schema import JsonAPIResourceSchema

T = TypeVar("T", bound=JsonAPIResourceSchema)


class JsonAPICollection(ABC, Generic[T]):
    path_prefix: str
    endpoint: str
    schema: type[JsonAPIResourceSchema]

    def __init__(self, base_url: str, auth: AuthBase) -> None:
        self.base_url = base_url
        self.auth = auth

    def resource(self, resource_id: str | None = None) -> JsonAPIResource[T]:
        return JsonAPIResource[T](
            url=urljoin(self.base_url, self.__full_path(resource_id)),
            auth=self.auth,
            schema=self.schema,
        )

    def resources(self) -> JsonAPIResourcesList[T]:
        return JsonAPIResourcesList[T](
            url=urljoin(self.base_url, self.__full_path()),
            auth=self.auth,
            schema=self.schema,
        )

    def __full_path(self, resource_id: str | None = None) -> str:
        return f"{self.path_prefix or ""}{self.endpoint}{f'/{resource_id}' if resource_id else ''}"
