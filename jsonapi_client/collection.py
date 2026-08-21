from abc import ABC
from typing import Any, Generic, TypeVar, cast
from urllib.parse import quote

from requests.auth import AuthBase

from .client import JsonAPIClient
from .parser import parse
from .query import JsonAPIFilterValue, JsonAPIIncludeValue, JsonAPIQuery, JsonAPISortValue
from .resource import JsonAPIResource, deserialize_resource
from .resources_list import JsonAPIResourcesList
from .schema import JsonAPIResourceSchema
from .serializer import JsonType, serialize

T = TypeVar("T", bound=JsonAPIResourceSchema)


class JsonAPISingleton(ABC, Generic[T]):
    endpoint: str
    schema: type[JsonAPIResourceSchema]

    def __init__(self, base_url: str, auth: AuthBase | None = None, include: JsonAPIIncludeValue | None = None) -> None:
        self.base_url = base_url
        self.auth = auth
        self.include = include

    def resource(self) -> JsonAPIResource[T]:
        url = f"{self.base_url}{self.endpoint}"
        client = JsonAPIClient[T](url=url, auth=self.auth)
        return JsonAPIResource[T](self.schema, client=client, include=self.include)


class JsonAPICollection(ABC, Generic[T]):
    endpoint: str
    schema: type[JsonAPIResourceSchema]

    def __init__(
        self,
        base_url: str,
        auth: AuthBase | None = None,
        default_page_size: int | None = None,
        include: JsonAPIIncludeValue | None = None,
    ) -> None:
        self.base_url = base_url
        self.auth = auth
        self.default_page_size = default_page_size
        self.include = include

    def resource(self, resource_id: str) -> JsonAPIResource[T]:
        url = f"{self.base_url}{self.endpoint}/{quote(resource_id)}"
        client = JsonAPIClient[T](url=url, auth=self.auth)
        return JsonAPIResource[T](self.schema, client=client, include=self.include)

    def create(self, **kwargs: list[Any] | dict[str, Any] | JsonType) -> T:
        url = f"{self.base_url}{self.endpoint}"
        client = JsonAPIClient[T](url=url, auth=self.auth)
        query = JsonAPIQuery(include=self.include)
        params = query.to_request_params()
        body = serialize(**kwargs)
        payload = client.post(body, params)
        parsed = cast("dict[str, Any]", parse(**payload))
        return cast("T", deserialize_resource(self.schema, parsed))

    def list(
        self,
        filters: dict[str, JsonAPIFilterValue] | None = None,
        sort: JsonAPISortValue | None = None,
        extra_params: dict[str, str] | None = None,
    ) -> JsonAPIResourcesList[T]:
        url = f"{self.base_url}{self.endpoint}"
        client = JsonAPIClient[T](url=url, auth=self.auth)
        return JsonAPIResourcesList[T](
            schema=self.schema,
            client=client,
            default_page_size=self.default_page_size,
            filters=filters,
            sort=sort,
            include=self.include,
            extra_params=extra_params,
        )

