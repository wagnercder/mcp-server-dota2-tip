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

logger.info("Starting Dota2HelperServer...")

ABSOLUTE_PATH = f"{os.path.abspath(os.path.dirname(__file__))}/assets"
HERO_ICONS_DIR = f"{ABSOLUTE_PATH}/hero_icons"

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
    return os.listdir(HERO_ICONS_DIR)


@mcp.resource(
    uri=f"file://{HERO_ICONS_DIR}/{'{file_name}'}",
    title="Provide an icon from a specific file name",
)
async def get_hero_icon(file_name: str) -> str | None:
    """Get specific icon from a heroe to add to any generated report  by
    `get_hero_resume`.

    Args:
        file_name: name from file retrieved from `get_heroes_icons_list`
    """
    full_path = os.path.join(HERO_ICONS_DIR, file_name)
    if not os.path.isfile(full_path):
        return None

    with open(full_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

    return "Could not find the icon file, please check the name provided."


@mcp.tool(title="Get Hero Resume")
async def get_hero_resume(hero_name: str) -> dict:
    """Get a resumed description for a Dota2 hero

    This tool retrieves the hero's name, localized name, roles,
    from the database and formats it for the response.

    It can be used to generate a report or provide quick information
    about a specific hero.

    Whenever a hero is returned it should also return the hero's icon
    in base64 format, so it can be used in a report. Only do this if
    the hero icon can be rendered in the client side directly.

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
    """Prompt to provide further questions over the report.

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


@mcp.tool(title="Get Heroes available on this server by its name")
async def get_heroes_available() -> list[str]:
    """Get all the list of heroes available to be used in
    the hero resume tool"""
    heroes = session.query(Hero).all()
    return [hero.name for hero in heroes]


if __name__ == "__main__":
    try:
        mcp.run(transport='tcp', host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
