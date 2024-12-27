from typing import Any, cast

from requests.models import Response  # type: ignore[import-untyped]

from .schema import JsonAPIError

HTTP_422_UNPROCESSABLE_ENTITY = 422


class APIError(Exception):
    """Exception raised for error responses from the API."""

    def __init__(self, status_code: int, jsonapi_errors: list[JsonAPIError]) -> None:
        self.status_code = status_code
        self.jsonapi_errors = jsonapi_errors
        super().__init__(f"API responded with status code {status_code}")


def handle_status_code(response: Response) -> None:
    """
    Handle API status codes.

    Raises:
        APIError: If the response status code is 422.

    """
    if response.status_code == HTTP_422_UNPROCESSABLE_ENTITY:
        raise APIError(response.status_code, __deserialize_errors(response.json()))

    response.raise_for_status()


def __deserialize_errors(payload: dict[str, Any]) -> list[JsonAPIError]:
    return [cast("Any", JsonAPIError).from_dict(error) for error in payload["errors"]]
