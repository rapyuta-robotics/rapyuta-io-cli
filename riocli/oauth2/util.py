from typing import Any

import json


def sanitize_parameters(params: dict[str, Any]) -> dict[str, Any]:
    scope = params.pop("scope")
    if scope is not None:
        params["scope"] = " ".join(scope)

    grant_types = params.pop("grant_types")
    if grant_types is not None:
        updated = []
        for i in grant_types:
            updated.extend(i.split(","))

        params["grant_types"] = updated

    response_types = params.pop("response_types")
    if response_types is not None:
        updated = []
        for i in response_types:
            updated.extend(i.split(","))

        params["response_types"] = updated

    name = params.pop("name")
    if name is not None:
        params["client_name"] = name

    metadata = params.pop("metadata")
    if metadata is not None:
        params["metadata"] = json.loads(metadata)

    return params
