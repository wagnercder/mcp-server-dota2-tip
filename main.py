import logging
import requests
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

OPENDOTA_URL = "https://opendota.com/api"


logger.info("Starting Dota2HelperServer...")
mcp = FastMCP("Dota2HelperServer")


@mcp.prompt()
def to_ask_after_resume(hero_name: str) -> list[base.Message]:
    """If not provided by the user the questions below might be usefull.

    Args:
        hero_name: name from hero
    """
    return [
        base.Message(
            role="user",
            content=[
                base.TextContent(text=f"What heroes are good against {hero_name}?"),
                base.TextContent(text=f"What heroes are countered by {hero_name}?"),
                base.TextContent(text=f"What are the core items for {hero_name}?"),
            ],
        )
    ]


@mcp.tool(title="Get detailed stats for a hero")
async def get_hero_stats(hero_id: int) -> dict:
    """Retrieve detailed statistics for a specific hero from OpenDota.

    Includes metrics like win rate, pick rate, and more.

    Returns:
        Dictionary with hero stats. Example:
        {
            "1_pick": 123456,
            "1_win": 65432,
            "2_pick": 234567,
            "2_win": 123456,
            "3_pick": 345678,
            "3_win": 234567,
            ...
        }
    """
    stats = requests.get(f"{OPENDOTA_URL}/heroes/{hero_id}/statistics").json()
    return stats


@mcp.tool(title="Get match details by match ID")
async def get_match_details(match_id: int) -> dict:
    """Get full info about a match, including players and scores.

    Returns:
        Dictionary with match details. Example:
        {
            "match_id": 1234567890,
            "duration": 2345,
            "radiant_win": True,
            "players": [
                {
                    "account_id": 123456,
                    "hero_id": 1,
                    "kills": 10,
                    "deaths": 2,
                    "assists": 15,
                    ...
                },
                ...
            ],
            "radiant_score": 45,
            "dire_score": 38,
            ...
        }
    """
    return requests.get(f"{OPENDOTA_URL}/matches/{match_id}").json()


@mcp.tool(title="Get heroes good and bad against a hero (by its id)")
async def get_hero_matchups(hero_id) -> dict:
    """Retrieve matchup statistics for a given hero by ID using the OpenDota.

    Calculates win rates against all other heroes and returns the top 5 heroes
    with the highest win rates (heroes that this hero is good against) and the
    bottom 5 heroes with the lowest win rates (heroes that are strong against
    this hero).

    Returns:
        a dict with both the bad and good heroes to play against:
        {
            "good_against_heroes": [23,45,1],
            "bad_against_heroes": [33,7,50]
        }
    """
    matchups: list = requests.get(f"{OPENDOTA_URL}/heroes/{hero_id}/matchups").json()

    for matchup in matchups:
        matchup["win_rate"] = (
            matchup["wins"] / matchup["games_played"]
            if matchup["games_played"] > 0
            else 0
        )

    sorted_heroes = sorted(matchups, key=lambda x: x["win_rate"], reverse=True)
    top_5 = sorted_heroes[:5]
    bottom_5 = sorted_heroes[-5:]

    return {
        "good_against_heroes": top_5,
        "bad_against_heroes": bottom_5,
    }


@mcp.tool(title="Get all the items available")
async def get_all_items() -> list[dict]:
    """Get all the items in the opendota api"""
    items: dict = requests.get(f"{OPENDOTA_URL}/heroes/constants/items").json()
    return [
        {
            "item_id": items[item_name]["id"],
            "name": item_name,
        }
        for item_name in items.keys()
    ]


@mcp.tool(title="Get Hero item popularity based on the stage of the game")
async def get_hero_item_popularity(hero_id) -> dict:
    """
    Retrieve the most popular items for a given hero from the OpenDota API,
    grouped by stage of the game (start, early, mid, late).

    Returns:
        A dictionary where keys are game stages and values are lists of item IDs.
    """
    items_pop: dict = requests.get(
        f"{OPENDOTA_URL}/heroes/{hero_id}/itemPopularity"
    ).json()

    items_stage = {}

    for game_stage in items_pop.keys():
        items_stage[game_stage] = items_pop[game_stage].keys()

    return items_stage


@mcp.tool(title="Get Heroes available on this server by its name")
async def get_heroes_available() -> list[dict]:
    """
    Retrieve all Dota 2 heroes available from the OpenDota API.
    Returns a list of heroes with their ID, localized name, roles,
    and primary attribute. This data can be used by other tools,
    such as hero matchup or to check its core items.

    Returns:
        a list of dictionary with the structure below:
            {
                "hero_id": hero["id"],
                "name": hero["localized_name"],
                "roles": hero["roles"],
                "primary_attr": hero["primary_attr"],
            }
    """
    heroes = requests.get(f"{OPENDOTA_URL}/heroes").json()

    return [
        {
            "hero_id": hero["id"],
            "name": hero["localized_name"],
            "roles": hero["roles"],
            "primary_attr": hero["primary_attr"],
        }
        for hero in heroes
    ]


if __name__ == "__main__":
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
