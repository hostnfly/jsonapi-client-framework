from typing import Any, Generic, TypeVar, cast

import jsonpickle  # type: ignore[import-untyped]
from requests import request
from requests.auth import AuthBase
from requests.models import Response

from .schema import JsonAPIError, JsonAPIResourceSchema

T = TypeVar("T", bound=JsonAPIResourceSchema)

DEFAULT_TIMEOUT = 10  # seconds
HTTP_422_UNPROCESSABLE_ENTITY = 422

def handle_status_code(response: Response) -> None:
    """
    Handle API status codes.

    Raises:
        APIError: If the response status code is 422.

    """
    if response.status_code == HTTP_422_UNPROCESSABLE_ENTITY:
        jsonapi_errors = [cast("Any", JsonAPIError).from_dict(e) for e in response.json()["errors"]]
        raise APIError(response.status_code, jsonapi_errors)

    response.raise_for_status()


class APIError(Exception):
    """Exception raised for error responses from the API."""

    def __init__(self, status_code: int, jsonapi_errors: list[JsonAPIError]) -> None:
        self.status_code = status_code
        self.jsonapi_errors = jsonapi_errors
        super().__init__(f"API responded with status code {status_code}")


class JsonAPIClient(Generic[T]):
    def __init__(self, url: str, auth: AuthBase | None = None) -> None:
        self.url = url
        self.auth = auth

    def get(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.http("GET", params)

    def post(self, payload: dict[str, Any], params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.http("POST", params, payload)

    def put(self, payload: dict[str, Any], params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.http("PUT", params, payload)

    def delete(self) -> dict[str, Any]:
        return self.http("DELETE")

    def http(self, method: str, params: dict[str, Any] | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else jsonpickle.encode(payload, unpicklable=False)
        response = request(method=method, params=params, data=body, **self.default_params)
        handle_status_code(response)
        return cast("dict[str, Any]", response.json())

    @property
    def default_params(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "auth": self.auth,
            "timeout": DEFAULT_TIMEOUT,
            "headers": {"Content-Type": "application/json"},
        }

