# Dota2HelperServer

Dota2HelperServer is a FastMCP-powered backend service designed to provide structured data and assets for Dota 2 heroes. It integrates with the Dotabase database to deliver hero metadata, icons, and contextual prompts for building reports or enhancing gameplay insights.

Well this is merely a prove of concept project.

---

## Features

- **Hero Resume Tool**
  Retrieve a hero's name, localized name, and roles from the Dotabase.

- **Hero Icon Retrieval**
  Access base64-encoded hero icons for use in reports or UI elements.

- **Hero Icon Listing**
  List all available hero icons stored locally.

- **Hero Availability**
  Get a list of all heroes available in the Dotabase.

- **Prompt Suggestions**
  Generate follow-up questions after retrieving a hero resume to guide further analysis (e.g., counters, item builds).

---

## Usage

Make sure you have MCP installed and then to start the server:

```bash
mcp run dota2_helper_server.py
