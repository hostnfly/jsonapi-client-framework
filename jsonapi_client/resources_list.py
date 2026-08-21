from typing import Any, Generic, TypeVar, cast

from .client import JsonAPIClient
from .parser import parse
from .query import JsonAPIFilterValue, JsonAPIIncludeValue, JsonAPIQuery, JsonAPISortValue
from .resource import deserialize_resource
from .schema import JsonAPIResourceSchema

T = TypeVar("T", bound=JsonAPIResourceSchema)


class JsonAPIResourcesList(Generic[T]):
    def __init__(
        self,
        schema: type[JsonAPIResourceSchema],
        client: JsonAPIClient,
        default_page_size: int | None = None,
        filters: dict[str, JsonAPIFilterValue] | None = None,
        sort: JsonAPISortValue | None = None,
        include: JsonAPIIncludeValue | None = None,
        extra_params: dict[str, str] | None = None,
    ) -> None:
        self.schema = schema
        self.client = client
        self.default_page_size = default_page_size
        self.filters = filters
        self.sort = sort
        self.include = include
        self.extra_params = extra_params or {}

    def all(self) -> list[T]:
        results = []
        next_page = 1
        while next_page:
            resources, meta = self.paginated(page=next_page)
            results += resources
            next_page = meta.get("pagination", {}).get("next")
        return results

    def paginated(self, page: int | None = None, size: int | None = None) -> tuple[list[T], dict[str, Any]]:
        jsonapi_page = {} if page is None else {"number": page}
        size = size or self.default_page_size
        if size is not None:
            jsonapi_page["size"] = size
        query = JsonAPIQuery(filters=self.filters, sort=self.sort, page=jsonapi_page, include=self.include)
        params = {**query.to_request_params(), **self.extra_params}
        payload = self.client.get(params)
        parsed = cast("list", parse(**payload))
        return cast("list[T]", [deserialize_resource(self.schema, p) for p in parsed]), payload["meta"]
