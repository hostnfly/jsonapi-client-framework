from typing import Any, Generic, TypeVar, cast

from requests import request  # type: ignore[import-untyped]
from requests.auth import AuthBase  # type: ignore[import-untyped]

from .parser import JsonAPIParser
from .query import JsonAPIFilterValue, JsonAPIIncludeValue, JsonAPIQuery, JsonAPISortValue
from .request import DEFAULT_TIMEOUT
from .response import handle_status_code
from .schema import JsonAPIResourceSchema

T = TypeVar("T", bound=JsonAPIResourceSchema)

DEFAULT_PAGE_SIZE = 30


class JsonAPIResourcesListPaginated(Generic[T]):
    def __init__(
        self,
        *,
        url: str,
        auth: AuthBase,
        schema: type[JsonAPIResourceSchema],
        page: dict[str, int] | None = None,
    ) -> None:
        self.url = url
        self.auth = auth
        self.schema = schema
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
        params = {**query.to_request_params(), **extra_params}
        response = request("GET", self.url, auth=self.auth, params=params, timeout=DEFAULT_TIMEOUT)
        handle_status_code(response)
        return self.__deserialize_resources(response.json()), response.json()["meta"]

    def __deserialize_resources(self, payload: dict[str, Any]) -> list[T]:
        parsed_list = JsonAPIParser().parse(**payload)
        return cast("list[T]", [cast("Any", self.schema).from_dict(parsed) for parsed in parsed_list])


class JsonAPIResourcesList(Generic[T]):
    def __init__(
        self,
        *,
        url: str,
        auth: AuthBase,
        schema: type[JsonAPIResourceSchema],
    ) -> None:
        self.url = url
        self.auth = auth
        self.schema = schema

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

    def paginated(self, page: int | None = None, size: int = DEFAULT_PAGE_SIZE) -> JsonAPIResourcesListPaginated[T]:
        jsonapi_page = None if page is None else {"number": page, "size": size}
        return JsonAPIResourcesListPaginated(
            url=self.url,
            auth=self.auth,
            schema=self.schema,
            page=jsonapi_page,
        )
