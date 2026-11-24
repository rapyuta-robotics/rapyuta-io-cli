from unittest.mock import MagicMock

from riocli.static_route.model import StaticRoute


def _route():
    return StaticRoute(
        {
            "apiVersion": "apiextensions.rapyuta.io/v1",
            "kind": "StaticRoute",
            "metadata": {"name": "gateway-site"},
            "spec": {"sourceIPRange": ["10.0.0.0/24"]},
        }
    )


def test_update_and_delete_use_the_org_suffixed_name():
    config = MagicMock(organization_short_id="oksjpprod")
    client = MagicMock()
    route = _route()

    route.update_object(v2_client=client, config=config)
    route.delete_object(v2_client=client, config=config)

    assert client.update_staticroute.call_args.kwargs["name"] == "gateway-site-oksjpprod"
    assert client.delete_staticroute.call_args.kwargs["name"] == "gateway-site-oksjpprod"
