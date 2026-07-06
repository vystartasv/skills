---
name: native-mcp
description: "MCP client: connect servers, register tools (stdio/HTTP)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [MCP, Tools, Integrations]
    related_skills: [mcporter]
---

# Native MCP Client

This skill covers connecting to and using MCP (Model Context Protocol) servers directly from Hermes.

## When to Use

- You need to connect an external data source or tool via MCP
- A user asks to use a specific MCP server
- You need to debug MCP server connections
- You want to register MCP tools for the current session

## Adding an MCP Server

MCP servers are configured in `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  my-server:
    command: python3
    args: ["/path/to/server.py"]
    # or for HTTP:
    # url: "http://localhost:8000/mcp"
```

Then reload in-session with `/reload-mcp` or restart the gateway.

### Available MCP commands

```bash
hermes mcp add NAME --command "..."          # Add stdio server
hermes mcp add NAME --url "http://..."       # Add HTTP server
hermes mcp remove NAME                       # Remove
hermes mcp list                              # List configured
hermes mcp test NAME                         # Test connection
```

## Verifying Tools are Registered

After connecting, check available tools:

```bash
hermes tools list
```

Look for tools prefixed with `mcp_<server-name>_`.

## Pitfalls

- **MCP servers must be running or executable** — a broken path or missing interpreter causes silent failures
- **Tool names are prefixed** — `mcp_server_toolname` format, not the bare tool name from the MCP spec
- **Restart required** — `hermes mcp add` updates config but the current session needs `/reload-mcp` to pick up the new server
- **HTTP servers** — must implement the MCP Streamable HTTP transport, not a plain REST API
- **Environment variables** — MCP servers inherit the Hermes process environment. For secrets, add them to `~/.hermes/.env` not the server code.
