from types import UnionType
from typing import Any, Generic, TypeVar, cast, get_args

from .client import JsonAPIClient
from .parser import parse
from .query import JsonAPIIncludeValue, JsonAPIQuery
from .schema import JsonAPIResourceSchema
from .serializer import JsonType, serialize

T = TypeVar("T", bound=JsonAPIResourceSchema)

def deserialize_resource(schema: type[JsonAPIResourceSchema], parsed: dict[str, Any]) -> JsonAPIResourceSchema:
    if isinstance(cast("JsonAPIResourceSchema", schema), UnionType):
        for schema_type in get_args(schema):
            try:
                return cast("JsonAPIResourceSchema", cast("Any", schema_type).from_dict(parsed))
            except KeyError as e:
                last_error = e
        raise last_error

    return cast("JsonAPIResourceSchema", cast("Any", schema).from_dict(parsed))


class JsonAPIResource(Generic[T]):
    def __init__(self, schema: type[JsonAPIResourceSchema], *, client: JsonAPIClient, include: JsonAPIIncludeValue | None = None) -> None:
        self.client = client
        self.schema = schema
        self.include = include

    def get(self) -> T:
        query = JsonAPIQuery(include=self.include)
        params = query.to_request_params()
        payload = self.client.get(params)
        parsed = cast("dict[str, Any]", parse(**payload))
        return cast("T", deserialize_resource(self.schema, parsed))

    def update(self, **kwargs: list[Any] | dict[str, Any] | JsonType) -> T:
        query = JsonAPIQuery(include=self.include)
        payload = serialize(**kwargs)
        params = query.to_request_params()
        payload = self.client.put(payload, params)
        parsed = cast("dict[str, Any]", parse(**payload))
        return cast("T", deserialize_resource(self.schema, parsed))

    def delete(self) -> T:
        payload = self.client.delete()
        parsed = cast("dict[str, Any]", parse(**payload))
        return cast("T", deserialize_resource(self.schema, parsed))

