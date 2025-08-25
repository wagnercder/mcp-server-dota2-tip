# Dota 2 Helper MCP Server

A Model Context Protocol server that provides Dota 2 game data and statistics using the OpenDota API.

### Installation

1. Ensure you have Python 3.11+ installed
2. Install the required dependencies:

```bash
pip install .
```

Run the server with:

```bash
python main.py
```

### Available Tools
1. get_hero_stats(hero_id: int) - Detailed statistics for a specific hero

2. get_match_details(match_id: int) - Full match information

3. get_hero_matchups(hero_id: int) - Matchup analysis (good/bad against)

4. get_all_items() - List of all Dota 2 items

5. get_hero_item_popularity(hero_id: int) - Item popularity by game stage

6. get_heroes_available() - Complete hero catalog

### API Data Source
This server uses the OpenDota API to provide real-time Dota 2 statistics and match data.

⚠️ Important Note
This project is a proof of concept and is intended for demonstration purposes only. It may not be suitable for production use and the API responses are dependent on the OpenDota service availability and rate limits.

