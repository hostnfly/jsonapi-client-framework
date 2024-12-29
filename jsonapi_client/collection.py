from abc import ABC
from typing import Generic, TypeVar
from urllib.parse import urljoin

from requests.auth import AuthBase  # type: ignore[import-untyped]

from .resource import JsonAPIResource
from .resources_list import JsonAPIResourcesList
from .schema import JsonAPIResourceSchema

T = TypeVar("T", bound=JsonAPIResourceSchema)

def full_path(path_prefix: str, endpoint: str, resource_id: str | None = None) -> str:
    return f"{path_prefix or ""}{endpoint}{'' if resource_id is None else f'/{resource_id}'}"

class JsonAPISingleton(ABC, Generic[T]):
    path_prefix: str
    endpoint: str
    schema: type[JsonAPIResourceSchema]

    def __init__(self, base_url: str, auth: AuthBase) -> None:
        self.base_url = base_url
        self.auth = auth

    def resource(self) -> JsonAPIResource[T]:
        return JsonAPIResource[T](
            url=urljoin(self.base_url, full_path(self.path_prefix, self.endpoint)),
            auth=self.auth,
            schema=self.schema,
        )


class JsonAPICollection(ABC, Generic[T]):
    path_prefix: str
    endpoint: str
    schema: type[JsonAPIResourceSchema]

    def __init__(self, base_url: str, auth: AuthBase) -> None:
        self.base_url = base_url
        self.auth = auth

    def resource(self, resource_id: str) -> JsonAPIResource[T]:
        return JsonAPIResource[T](
            url=urljoin(self.base_url, full_path(self.path_prefix, self.endpoint, resource_id)),
            auth=self.auth,
            schema=self.schema,
        )

    def resources(self) -> JsonAPIResourcesList[T]:
        return JsonAPIResourcesList[T](
            url=urljoin(self.base_url, full_path(self.path_prefix, self.endpoint)),
            auth=self.auth,
            schema=self.schema,
        )
