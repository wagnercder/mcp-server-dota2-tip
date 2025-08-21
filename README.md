# Dota2HelperServer

Dota2HelperServer is a FastMCP-powered backend service designed to provide structured data and assets for Dota 2 heroes. It integrates with the Dotabase database to deliver hero metadata, icons, and contextual prompts for building reports or enhancing gameplay insights.

```Well this is merely a prove of concept project creating a MCP server.

---

## Features

- Retrieve a hero's name, localized name, and roles from the Dotabase.
- Access base64-encoded hero icons for use in reports or UI elements.
- List all available hero icons stored locally.
- Get a list of all heroes available in the Dotabase.

---

## Usage

Make sure you have MCP installed and then to start the server:

```bash
make mcp-server

or in case you want to check what tools, resources and prompts are available.

```bash
make mcp-dev-server
