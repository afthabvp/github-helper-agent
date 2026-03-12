import os
import httpx

GITHUB_API = "https://api.github.com"


def _headers() -> dict:
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "A2A-GitHub-Helper"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def get_repo_info(owner: str, repo: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=_headers())
        resp.raise_for_status()
        data = resp.json()

    return (
        f"Repository: {data['full_name']}\n"
        f"Description: {data.get('description', 'N/A')}\n"
        f"Language: {data.get('language', 'N/A')}\n"
        f"Stars: {data['stargazers_count']}\n"
        f"Forks: {data['forks_count']}\n"
        f"Open Issues: {data['open_issues_count']}\n"
        f"Default Branch: {data['default_branch']}\n"
        f"Created: {data['created_at']}\n"
        f"Last Updated: {data['updated_at']}\n"
        f"URL: {data['html_url']}"
    )


async def list_issues(owner: str, repo: str, count: int = 10) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/issues",
            headers=_headers(),
            params={"state": "open", "per_page": count, "sort": "created", "direction": "desc"},
        )
        resp.raise_for_status()
        issues = resp.json()

    if not issues:
        return f"No open issues found in {owner}/{repo}"

    lines = [f"Open issues in {owner}/{repo} (showing {len(issues)}):"]
    for issue in issues:
        labels = ", ".join(l["name"] for l in issue.get("labels", []))
        label_str = f" [{labels}]" if labels else ""
        lines.append(f"  #{issue['number']} - {issue['title']}{label_str} (by {issue['user']['login']}, {issue['created_at'][:10]})")
    return "\n".join(lines)


async def search_code(owner: str, repo: str, query: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/search/code",
            headers=_headers(),
            params={"q": f"{query} repo:{owner}/{repo}"},
        )
        resp.raise_for_status()
        data = resp.json()

    items = data.get("items", [])
    if not items:
        return f"No code matches found for '{query}' in {owner}/{repo}"

    lines = [f"Code search results for '{query}' in {owner}/{repo} ({data['total_count']} total matches, showing {len(items)}):"]
    for item in items[:15]:
        lines.append(f"  {item['path']} (score: {item.get('score', 'N/A'):.1f})")
    return "\n".join(lines)
