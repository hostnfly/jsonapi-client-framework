from typing import Any, Generic, TypeVar, cast


from .query import JsonAPIIncludeValue, JsonAPIQuery
from .request import JsonAPIClient
from .schema import JsonAPIResourceSchema
from .serializer import JsonAPISerializer, JsonType

T = TypeVar("T", bound=JsonAPIResourceSchema)


class JsonAPIResource(Generic[T]):
    def __init__(self, client: JsonAPIClient) -> None:
        self.client = client

    def get(self, include: JsonAPIIncludeValue | None = None) -> T:
        query = JsonAPIQuery(include=include)
        return cast("T", self.client.get(query.to_request_params())[0])

    def update(self, include: JsonAPIIncludeValue | None = None, **kwargs: list[Any] | dict[str, Any] | JsonType) -> T:
        query = JsonAPIQuery(include=include)
        payload = JsonAPISerializer.tojsonapi(**kwargs)
        return cast("T", self.client.put(payload, query.to_request_params())[0])

    def delete(self) -> None:
        self.client.delete()

