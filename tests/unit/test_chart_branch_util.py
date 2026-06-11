from riocli.chart.util import branch_repository_url


def test_branch_repository_url_normal():
    assert branch_repository_url("feature-x") == (
        "https://chartsbranch.blob.core.windows.net/charts-per-branch/feature-x/incubator/index.yaml"
    )


def test_branch_repository_url_urlencoding():
    result = branch_repository_url("bug/fix some")
    assert result == (
        "https://chartsbranch.blob.core.windows.net/charts-per-branch/bug/fix%20some/incubator/index.yaml"
    )


def test_branch_repository_url_query_char():
    # ? must be encoded so it cannot silently become a query-string delimiter
    result = branch_repository_url("feat?oops")
    assert result == (
        "https://chartsbranch.blob.core.windows.net/charts-per-branch/feat%3Foops/incubator/index.yaml"
    )


def test_branch_repository_url_symbols():
    result = branch_repository_url("bran©h@!")
    assert "bran%C2%A9h%40%21" in result
