# Skill: MCP Builder

Guide for creating MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Triggers on: "build MCP server", "create MCP integration", "design MCP tools", "MCP server from scratch". Output artifact: working MCP server project directory with `server.py` (or `index.ts`), tool implementations, and `README.md`.

---

# MCP Builder

Build MCP (Model Context Protocol) servers to connect Claude to external APIs and services.

## When to Use

- Building a new MCP server from scratch
- Adding tools to an existing MCP server
- Integrating an external API with Claude via MCP
- Designing the tool interface for an MCP integration

## MCP Architecture Basics

An MCP server exposes **tools** that Claude can call. Each tool has:
- A **name** (snake_case)
- A **description** (critical — Claude uses this to decide when to call the tool)
- **Input schema** (JSON Schema)
- **Implementation** (the actual logic)

## Choosing a Framework

### Python — FastMCP (recommended for Python)
```python
from fastmcp import FastMCP

mcp = FastMCP("my-service")

@mcp.tool()
def get_user(user_id: str) -> dict:
    """Get a user by their ID. Returns user profile including name, email, and role."""
    return api_client.get(f"/users/{user_id}")
```

### TypeScript — MCP SDK
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "my-service", version: "1.0.0" });

server.tool(
  "get_user",
  "Get a user by their ID. Returns user profile including name, email, and role.",
  { user_id: z.string() },
  async ({ user_id }) => {
    const user = await apiClient.get(`/users/${user_id}`);
    return { content: [{ type: "text", text: JSON.stringify(user) }] };
  }
);
```

## Tool Design Principles

### Write Descriptions for Claude, Not Developers
The description is how Claude decides when and how to use a tool. Be explicit:

Bad: `"Get user"`
Good: `"Retrieve a user's profile by ID. Use this when you need name, email, role, or account status for a specific user."`

### Name Tools by Action
- `get_`, `list_`, `create_`, `update_`, `delete_`, `search_`
- snake_case always
- Consistent with the domain (e.g., `create_ticket`, not `add_issue`)

### Return Structured Data
Return JSON objects, not plain strings. Claude can reason over structured data better.

### Handle Errors Gracefully
```python
@mcp.tool()
def get_user(user_id: str) -> dict:
    """..."""
    try:
        return api_client.get(f"/users/{user_id}")
    except NotFoundError:
        return {"error": "User not found", "user_id": user_id}
    except Exception as e:
        return {"error": str(e)}
```

## Project Structure

```
my-mcp-server/
├── server.py (or index.ts)     # MCP server definition
├── client.py (or client.ts)    # API client/auth logic
├── tools/                      # Tool implementations (if many)
│   ├── users.py
│   └── projects.py
├── tests/
│   └── test_tools.py
├── README.md
└── requirements.txt (or package.json)
```

## Authentication Patterns

### API Key (via environment variable)
```python
import os
API_KEY = os.environ.get("MY_SERVICE_API_KEY")
```

### OAuth2
Use a separate auth flow and store tokens securely. Never hardcode credentials.

## Testing

Test each tool in isolation:
```python
def test_get_user():
    result = get_user("user_123")
    assert "name" in result
    assert result["id"] == "user_123"
```

## claude_desktop_config.json Entry

```json
{
  "mcpServers": {
    "my-service": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "MY_SERVICE_API_KEY": "your-key-here"
      }
    }
  }
}
```
