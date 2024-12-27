from typing import Any, Generic, TypeVar, cast

import jsonpickle  # type: ignore[import-untyped]
from requests import request  # type: ignore[import-untyped]
from requests.auth import AuthBase  # type: ignore[import-untyped]

from .parser import JsonAPIParser
from .query import JsonAPIIncludeValue, JsonAPIQuery
from .request import DEFAULT_TIMEOUT
from .response import handle_status_code
from .schema import JsonAPIResourceSchema
from .serializer import JsonAPISerializer, JsonType

T = TypeVar("T", bound=JsonAPIResourceSchema)


class JsonAPIResource(Generic[T]):
    def __init__(
        self,
        url: str,
        auth: AuthBase,
        schema: type[JsonAPIResourceSchema],
    ) -> None:
        self.url = url
        self.auth = auth
        self.schema = schema

    def get(self, include: JsonAPIIncludeValue | None = None) -> T:
        query = JsonAPIQuery(include=include)
        response = request(
            "GET", self.url,
            auth=self.auth,
            params=query.to_request_params(),
            timeout=DEFAULT_TIMEOUT,
        )
        handle_status_code(response)
        return self.__deserialize_resource(response.json())

    def update(self, include: JsonAPIIncludeValue | None = None, **kwargs: list[Any] | dict[str, Any] | JsonType) -> T:
        query = JsonAPIQuery(include=include)
        payload = JsonAPISerializer.tojsonapi(**kwargs)
        response = request(
            "PUT", self.url,
            params=query.to_request_params(),
            data=jsonpickle.encode(payload, unpicklable=False),
            headers={"Content-Type": "application/json"},
            auth=self.auth,
            timeout=DEFAULT_TIMEOUT,
        )
        handle_status_code(response)
        return self.__deserialize_resource(response.json())

    def delete(self) -> None:
        response = request("DELETE", self.url, auth=self.auth, timeout=DEFAULT_TIMEOUT)
        handle_status_code(response)

    def __deserialize_resource(self, payload: dict[str, Any]) -> T:
        parsed = JsonAPIParser().parse(**payload)
        return cast("T", cast("Any", self.schema).from_dict(parsed))
