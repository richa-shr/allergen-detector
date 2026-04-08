import os
import json
from dotenv import load_dotenv

load_dotenv()

def detect_allergens(ingredients: str, user_allergens: list[str]) -> dict:
    """
    Exact string match — checks if any user allergen appears
    in the ingredient list. No LLM involved.
    """
    
    ingredients_lower = ingredients.lower()
    found = []

    for allergen in user_allergens:
        if allergen.lower() in ingredients_lower:
            found.append(allergen)

    return {
        "is_safe": len(found) == 0,
        "allergens_found": found,
        "reason": f"Found {', '.join(found)} in ingredients." if found else "No allergens found."
    }