from typing import Optional
from typing_extensions import TypedDict

class AllergenState(TypedDict):
    #Input
    url:str
    user_allergens: list[str]             # allergens user is allergic to

    # Filled by scrape_node
    ingredients: Optional[str]           # raw ingredient text

    # Filled by detect_node
    is_safe: Optional[bool]              # safe or not
    allergens_found: Optional[list[str]] # what was found
    reason: Optional[str]                # explanation

    # Filled by search + validate nodes
    alternative_urls: Optional[list[str]]      # candidate URLs
    safe_alternatives: Optional[list[dict]]    # validated safe products
