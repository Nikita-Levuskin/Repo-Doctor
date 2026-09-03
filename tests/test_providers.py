from __future__ import annotations

import httpx
import pytest

from repo_doctor.models import PullRequestRequest
from repo_doctor.providers import GitHubProvider, GitLabProvider, ProviderError


@pytest.fixture
def pr_request() -> PullRequestRequest:
    return PullRequestRequest(owner="student", repository="demo", source_branch="repo-doctor-fixes")


def test_missing_tokens(monkeypatch: pytest.MonkeyPatch, pr_request: PullRequestRequest) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITLAB_TOKEN", raising=False)
    with pytest.raises(ProviderError, match="GITHUB_TOKEN"):
        GitHubProvider().create(pr_request)
    with pytest.raises(ProviderError, match="GITLAB_TOKEN"):
        GitLabProvider().create(pr_request)


@pytest.mark.parametrize("provider_name", ["github", "gitlab"])
def test_provider_success(
    monkeypatch: pytest.MonkeyPatch, pr_request: PullRequestRequest, provider_name: str
) -> None:
    def handler(incoming: httpx.Request) -> httpx.Response:
        assert incoming.method == "POST"
        return httpx.Response(201, json={"id": 42, "html_url": "https://example.test/42"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    if provider_name == "github":
        monkeypatch.setenv("GITHUB_TOKEN", "test-token")
        result = GitHubProvider(client).create(pr_request)
    else:
        monkeypatch.setenv("GITLAB_TOKEN", "test-token")
        result = GitLabProvider(client).create(pr_request)
    assert result["id"] == 42


@pytest.mark.parametrize("status", [401, 403, 404, 409, 429, 500, 503])
def test_http_errors(
    monkeypatch: pytest.MonkeyPatch, pr_request: PullRequestRequest, status: int
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(status)))
    with pytest.raises(ProviderError, match=f"HTTP {status}"):
        GitHubProvider(client).create(pr_request)


@pytest.mark.parametrize(
    ("exception", "message"),
    [
        (httpx.ReadTimeout("timeout"), "timed out"),
        (httpx.ConnectError("offline"), "network error"),
    ],
)
def test_network_failures(
    monkeypatch: pytest.MonkeyPatch,
    pr_request: PullRequestRequest,
    exception: Exception,
    message: str,
) -> None:
    monkeypatch.setenv("GITLAB_TOKEN", "test-token")

    def handler(_: httpx.Request) -> httpx.Response:
        raise exception

    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(ProviderError, match=message):
        GitLabProvider(client).create(pr_request)


def test_unexpected_success_payload(
    monkeypatch: pytest.MonkeyPatch, pr_request: PullRequestRequest
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(201, json=[])))
    with pytest.raises(ProviderError, match="unexpected"):
        GitHubProvider(client).create(pr_request)
