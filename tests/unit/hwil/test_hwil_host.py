"""hwil_host (config key) points the CLI at a non-production HWIL; the Entra token only goes to trusted hosts."""

import pytest

from riocli.hwilclient.client import Client, check_hwil_host


@pytest.mark.parametrize(
    "host",
    [
        "http://localhost:8000",
        "http://localhost",
        "http://127.0.0.1:8000/",
        "https://hwilv3.rapyuta.io",
        "https://hwil.dev.rapyuta.io:8443",
    ],
)
def test_trusted_hosts(host):
    assert check_hwil_host(host) == host


@pytest.mark.parametrize(
    "host",
    [
        "http://hwilv3.rapyuta.io",  # plain http off-box
        "https://evil.com",
        "https://rapyuta.io.evil.com",
        "https://evilrapyuta.io",
        "http://localhost.evil.com:8000",
        "http://127.0.0.1@evil.com",
        "http://localhost:8000/x",
        "https://hwilv3.rapyuta.io\n",
        "file:///etc/passwd",
    ],
)
def test_untrusted_hosts_never_get_the_token(host):
    calls = []
    with pytest.raises(ValueError):
        Client(token_provider=lambda: calls.append(1) or "tok", hwil_host=host)
    assert calls == []


def test_default_is_production_and_trailing_slash_is_stripped():
    assert Client(token_provider=lambda: "t")._host == Client.HWIL_URL.rstrip("/")
    assert (
        Client(token_provider=lambda: "t", hwil_host="http://127.0.0.1:8000/")._host
        == "http://127.0.0.1:8000"
    )
