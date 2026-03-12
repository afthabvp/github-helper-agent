import os
import json
from openai import AsyncOpenAI
from app import github_service

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_repo_info",
            "description": "Get metadata about a GitHub repository (stars, forks, language, description)",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner (e.g. 'facebook')"},
                    "repo": {"type": "string", "description": "Repository name (e.g. 'react')"},
                },
                "required": ["owner", "repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_issues",
            "description": "List recent open issues in a GitHub repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "count": {"type": "integer", "description": "Number of issues to fetch (default 10)", "default": 10},
                },
                "required": ["owner", "repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Search for code in a GitHub repository by keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "query": {"type": "string", "description": "Search query string"},
                },
                "required": ["owner", "repo", "query"],
            },
        },
    },
]

SYSTEM_PROMPT = """You are a GitHub Helper Agent. You help users get information about GitHub repositories.
You have access to three tools: get_repo_info, list_issues, and search_code.
Parse the user's request, call the appropriate tool, and provide a clear, well-formatted response.
If the user doesn't specify a repository, ask them to provide one in the format owner/repo."""

TOOL_FUNCTIONS = {
    "get_repo_info": github_service.get_repo_info,
    "list_issues": github_service.list_issues,
    "search_code": github_service.search_code,
}


async def process_message(text: str) -> str:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]

    # First call: let the model decide which tool to use
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    # If no tool call, return the direct response
    if not assistant_message.tool_calls:
        return assistant_message.content or "I couldn't understand the request. Please ask about a GitHub repository."

    # Execute tool calls
    messages.append(assistant_message)

    for tool_call in assistant_message.tool_calls:
        fn_name = tool_call.function.name
        fn_args = json.loads(tool_call.function.arguments)

        fn = TOOL_FUNCTIONS.get(fn_name)
        if not fn:
            tool_result = f"Unknown tool: {fn_name}"
        else:
            try:
                tool_result = await fn(**fn_args)
            except Exception as e:
                tool_result = f"Error calling {fn_name}: {e}"

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result,
        })

    # Second call: generate the final response with tool results
    final_response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    return final_response.choices[0].message.content or "No response generated."
