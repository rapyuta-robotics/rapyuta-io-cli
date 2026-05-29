import pytest
from riocli.chart.util import branch_repository_url


def test_branch_repository_url_normal():
    assert branch_repository_url("feature-x") == (
        "https://chartsbranch.blob.core.windows.net/charts-per-branch/feature-x/incubator/index.yaml"
    )


def test_branch_repository_url_urlencoding():
    result = branch_repository_url("bug/fix some")
    assert result == (
        "https://chartsbranch.blob.core.windows.net/charts-per-branch/bug/fix some/incubator/index.yaml"
    )


def test_branch_repository_url_strips_and_safe():
    assert branch_repository_url("  new-feature  ") == (
        "https://chartsbranch.blob.core.windows.net/charts-per-branch/  new-feature  /incubator/index.yaml"
    )


def test_branch_repository_url_empty():
    with pytest.raises(ValueError):
        branch_repository_url("")


def test_branch_repository_url_symbols():
    raw = branch_repository_url("bran©h@!")
    assert "bran©h@!" in raw
