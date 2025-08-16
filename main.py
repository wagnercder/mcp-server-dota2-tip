import os
import logging
import base64
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from dotabase import dotabase_session, Hero

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

logging.info("Starting Dota2HelperServer...")
DOTABUFF_URL = "https://www.dotabuff.com/heroes"
ABSOLUTE_PATH = os.path.abspath(os.path.dirname(__file__))

session = dotabase_session()


def format_hero_data(hero_data: Hero) -> dict:
    """Format hero data for MCP response from dotabase"""
    return {
        "name": hero_data.name,
        "localized_name": hero_data.localized_name,
        "roles": hero_data.roles,
    }


mcp = FastMCP("Dota2HelperServer")


@mcp.tool(title="Get hero icons available", annotations={"readOnlyHint": True})
async def get_heroes_icons_list() -> list[str]:
    """Get all the minimapa icons available for a any generated report.

    Args:
        hero_name: Name of the Dota 2 hero, the complete list of heroes
            can be retrieved using the `get_heroes_available` tool.
    """
    logger.info(f"Retrieved all hero icon paths")
    return os.listdir(f"{ABSOLUTE_PATH}/assets/hero_icons")


@mcp.tool(title="Get Hero Icon", annotations={"readOnlyHint": True})
async def get_hero_icon(file_name: str) -> str | None:
    """Get specific icon from a heroe to add to any generated report  by
    `get_hero_resume`.

    Args:
        file_name: name from file retrieved from `get_heroes_icons_list`
    """
    full_path = os.path.join(f"{ABSOLUTE_PATH}/assets/hero_icons", file_name)
    if os.path.isfile(full_path):
        with open(full_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return encoded
    return "Could not find the icon file, please check the name provided."


@mcp.tool(title="Get Hero Resume")
async def get_hero_resume(hero_name: str) -> dict:
    """Get a resumed description for a Dota2 hero

    This tool retrieves the hero's name, localized name, roles,
    from the database and formats it for the response.

    It can be used to generate a report or provide quick information
    about a specific hero.

    Whenever a hero is returned it will also return the hero's icon
    in base64 format, so it can be used in a report.

    The MCP Client should ask later what is the purpose of the report,
    if they want to know wich heroes are good against the hero,
    or if they want to know the hero's win rate and pick rate.

    The information of a build to counter another hero should be provided
    by the LLM.

    Args:
        hero_name: Name of the Dota 2 hero, the complete list of heroes
            can be retrieved using the `get_heroes_available` tool.
    """
    hero = session.query(Hero).filter(Hero.name == hero_name).one_or_none()
    if not hero:
        return f"No hero found with name '{hero_name}'."

    logger.info(f"Retrieved hero: {hero.name}")
    return format_hero_data(hero)


@mcp.prompt()
def to_ask_after_resume(hero_name: str) -> list[base.Message]:
    """Debug prompt for PDF issues.

    This prompt helps the user by suggesting the right questions after
    the resume is provided.

    Args:
        hero_name: name from the hero
    """
    return [
        base.Message(
            role="user",
            content=[
                base.TextContent(
                    text=f"What heroes are good against {hero_name}?"
                ),
                base.TextContent(
                    text=f"What heroes are countered by {hero_name}?"
                ),
                base.TextContent(
                    text=f"What are the core items for {hero_name}?"
                )
            ],
        )
    ]


@mcp.tool(title="Get Heroes available on this server by its name")
async def get_heroes_available() -> list[str]:
    """Get all the list of heroes available to be used in
    the hero resume tool"""
    heroes = session.query(Hero).all()
    return [hero.name for hero in heroes]


if __name__ == "__main__":
    try:
        mcp.run(port=5000)
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
