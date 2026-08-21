from typing import Any, cast

Json = dict[str, Any] | list[dict[str, Any]]

def parse(
    data: Json,
    included: list[dict[str, Any]] | None = None,
    parsed_by_type_and_id: dict[str, dict[str, Json]] | None = None,
    **kwargs: Any,
) -> Json:
    included = included or []
    parsed_by_type_and_id = parsed_by_type_and_id or {}
    if isinstance(data, list):
        return cast(
            "list[dict[str, Any]]",
            [parse(data=item, included=included, parsed_by_type_and_id=parsed_by_type_and_id) for item in data],
        )

    parsed = {"id": data["id"]}
    parsed_by_type = parsed_by_type_and_id.setdefault(data["type"], {})
    parsed_by_type[data["id"]] = parsed
    parsed.update(data["attributes"])
    if data.get("relationships", None):
        parsed.update(
            {
                key: parse_relationship(key, value["data"], included, parsed_by_type_and_id)
                for key, value in data["relationships"].items()
            },
        )
    return parsed

def parse_relationship(
    key: str,
    data: Json | None,
    included: list[dict[str, Any]],
    parsed_by_type_and_id: dict[str, dict[str, Json]],
) -> Json | None:
    if data is None:
        return None

    if isinstance(data, list):
        return cast(
            "list[dict[str, Any]]",
            [parse_relationship(key, d, included, parsed_by_type_and_id) for d in data],
        )

    cached = parsed_by_type_and_id.get(data["type"], {}).get(data["id"], None)
    if cached:
        return cached

    included_data = find_included_data(data, included)
    if included_data:
        return parse(data=included_data, included=included, parsed_by_type_and_id=parsed_by_type_and_id)

    return data

def find_included_data(
    identifier: dict[str, Any],
    included: list[dict[str, Any]],
) -> Json | None:
    for element in included:
        if element["id"] == identifier["id"] and element["type"] == identifier["type"]:
            return element

    return None


