from typing import Any, Generic, TypeVar, cast


from .query import JsonAPIFilterValue, JsonAPIIncludeValue, JsonAPIQuery, JsonAPISortValue
from .request import JsonAPIClient
from .schema import JsonAPIResourceSchema

T = TypeVar("T", bound=JsonAPIResourceSchema)


class JsonAPIResourcesListPaginated(Generic[T]):
    def __init__(self, client: JsonAPIClient, page: dict[str, int] | None = None) -> None:
        self.client = client
        self.page = page

    def get(
        self,
        filters: dict[str, JsonAPIFilterValue] | None = None,
        sort: JsonAPISortValue | None = None,
        include: JsonAPIIncludeValue | None = None,
        extra_params: dict[str, str] | None = None,
    ) -> tuple[list[T], dict[str, Any]]:
        query = JsonAPIQuery(filters=filters, sort=sort, page=self.page, include=include)
        extra_params = extra_params or {}
        results, meta = self.client.get({**query.to_request_params(), **extra_params})
        return cast("list[T]", results), meta


class JsonAPIResourcesList(Generic[T]):
    def __init__(self, client: JsonAPIClient, default_page_size: int | None = None) -> None:
        self.client = client
        self.default_page_size = default_page_size

    def get(
        self,
        filters: dict[str, JsonAPIFilterValue] | None = None,
        sort: JsonAPISortValue | None = None,
        include: JsonAPIIncludeValue | None = None,
        extra_params: dict[str, str] | None = None,
    ) -> list[T]:
        results = []
        next_page = 1
        while next_page:
            resources, meta = self.paginated(page=next_page).get(
                filters=filters,
                sort=sort,
                include=include,
                extra_params=extra_params,
            )
            results += resources
            next_page = meta["pagination"].get("next")
        return results

    def paginated(self, page: int | None = None, size: int | None = None) -> JsonAPIResourcesListPaginated[T]:
        jsonapi_page = {} if page is None else {"number": page}
        size = size or self.default_page_size
        if size is not None:
            jsonapi_page["size"] = size
        return JsonAPIResourcesListPaginated(self.client, page=jsonapi_page)
