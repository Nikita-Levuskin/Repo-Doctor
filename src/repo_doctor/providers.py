"""GitHub and GitLab pull/merge request adapters."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import quote

import httpx

from repo_doctor.models import PullRequestRequest


class ProviderError(RuntimeError):
    """Predictable provider failure without token disclosure."""


class ChangeRequestProvider(ABC):
    """Common provider interface."""

    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=10.0)

    @abstractmethod
    def create(self, request: PullRequestRequest) -> dict[str, Any]:
        """Create a pull or merge request."""

    @staticmethod
    def _token(name: str) -> str:
        token = os.getenv(name)
        if not token:
            raise ProviderError(f"Required environment variable is not set: {name}")
        return token

    @staticmethod
    def _response(response: httpx.Response) -> dict[str, Any]:
        if response.is_success:
            data = response.json()
            if not isinstance(data, dict):
                raise ProviderError("Provider returned an unexpected response")
            return data
        hints = {
            401: "authentication failed",
            403: "access forbidden or rate limited",
            404: "repository or endpoint not found",
            409: "request conflicts with provider state",
            429: "rate limit exceeded",
        }
        reason = hints.get(response.status_code, "provider request failed")
        raise ProviderError(f"HTTP {response.status_code}: {reason}")


class GitHubProvider(ChangeRequestProvider):
    """GitHub REST API adapter."""

    def create(self, request: PullRequestRequest) -> dict[str, Any]:
        token = self._token("GITHUB_TOKEN")
        try:
            response = self.client.post(
                f"https://api.github.com/repos/{request.owner}/{request.repository}/pulls",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                },
                json={
                    "title": request.title,
                    "body": request.body,
                    "head": request.source_branch,
                    "base": request.target_branch,
                },
            )
        except httpx.TimeoutException as exc:
            raise ProviderError("GitHub request timed out") from exc
        except httpx.NetworkError as exc:
            raise ProviderError("GitHub network error") from exc
        return self._response(response)


class GitLabProvider(ChangeRequestProvider):
    """GitLab REST API adapter."""

    def create(self, request: PullRequestRequest) -> dict[str, Any]:
        token = self._token("GITLAB_TOKEN")
        project = quote(f"{request.owner}/{request.repository}", safe="")
        try:
            response = self.client.post(
                f"https://gitlab.com/api/v4/projects/{project}/merge_requests",
                headers={"PRIVATE-TOKEN": token},
                json={
                    "title": request.title,
                    "description": request.body,
                    "source_branch": request.source_branch,
                    "target_branch": request.target_branch,
                },
            )
        except httpx.TimeoutException as exc:
            raise ProviderError("GitLab request timed out") from exc
        except httpx.NetworkError as exc:
            raise ProviderError("GitLab network error") from exc
        return self._response(response)
