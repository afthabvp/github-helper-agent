AGENT_CARD = {
    "name": "GitHub Helper Agent",
    "description": "An agent that answers questions about GitHub repositories, including repo info, issues, and code search",
    "version": "1.0.0",
    "protocol": "a2a",
    "skills": [
        {
            "id": "repo_info",
            "name": "Repository Info",
            "description": "Get metadata about a GitHub repository (stars, forks, language, description)",
        },
        {
            "id": "list_issues",
            "name": "List Issues",
            "description": "List recent open issues in a GitHub repository",
        },
        {
            "id": "search_code",
            "name": "Search Code",
            "description": "Search for code in a GitHub repository by keyword",
        },
    ],
}
