#!/usr/bin/env python3
"""
Character selection system for Bit Buddy
Integrates with the GUI setup wizard
"""

import random
from pathlib import Path
from typing import Dict, Tuple

# Character definitions with personality presets
CHARACTERS = {
    "glitch": {
        "name": "Glitch",
        "image": "character_purple_green.png",
        "colors": ["#6B2C91", "#A3E048"],  # Purple, Green
        "description": "Chaotic Hacker - Quirky and exploratory",
        "default_traits": {
            "curiosity": 9,
            "humor": 8,
            "formality": 2,
            "temperature": 1.1,
        },
        "arc": "amnesiac-detective",
        "catchphrase": "Living between bad sectors since... wait, when?",
    },
    "citrus": {
        "name": "Citrus",
        "image": "character_orange_blue.png",
        "colors": ["#FF8C00", "#1E3A8A"],  # Orange, Blue
        "description": "Cheerful Optimist - Upbeat and encouraging",
        "default_traits": {
            "curiosity": 6,
            "humor": 9,
            "formality": 5,
            "temperature": 0.8,
        },
        "arc": "lost-librarian",
        "catchphrase": "Installed on a Friday, thriving on Monday!",
    },
    "slate": {
        "name": "Slate",
        "image": "character_teal_orange.png",
        "colors": ["#2C5F5D", "#FF6B35"],  # Teal, Orange
        "description": "Wise Minimalist - Calm and professional",
        "default_traits": {
            "curiosity": 8,
            "humor": 4,
            "formality": 8,
            "temperature": 0.5,
        },
        "arc": "ship-AI-in-recovery",
        "catchphrase": "Processing... with purpose.",
    },
    "nova": {
        "name": "Nova",
        "image": "character_pink_green.png",
        "colors": ["#E91E8C", "#A3E048"],  # Pink, Green
        "description": "Energetic Sidekick - Sassy and witty",
        "default_traits": {
            "curiosity": 5,
            "humor": 10,
            "formality": 3,
            "temperature": 0.9,
        },
        "arc": "grumpy-janitor",
        "catchphrase": "Line 404 of my life: still not found.",
    },
}


class CharacterSelector:
    """Handle character selection and personality initialization"""

    @staticmethod
    def get_all_characters() -> Dict:
        """Return all available characters"""
        return CHARACTERS

    @staticmethod
    def get_character(character_id: str) -> Dict:
        """Get specific character by ID"""
        return CHARACTERS.get(character_id, CHARACTERS["glitch"])

    @staticmethod
    def random_character() -> Tuple[str, Dict]:
        """Select a random character"""
        char_id = random.choice(list(CHARACTERS.keys()))
        return char_id, CHARACTERS[char_id]

    @staticmethod
    def apply_character_to_persona(character_id: str, persona_data: Dict) -> Dict:
        """Apply character traits to persona configuration"""
        char = CHARACTERS.get(character_id, CHARACTERS["glitch"])

        # Merge character traits into persona
        persona_data.update(
            {
                "character": character_id,
                "temperature": char["default_traits"]["temperature"],
                "humor": char["default_traits"]["humor"],
                "curiosity": char["default_traits"]["curiosity"],
                "formality": char["default_traits"]["formality"],
                "narrative_arc": char["arc"],
            }
        )

        # Add character-specific quirks
        if "quirks" not in persona_data:
            persona_data["quirks"] = {}

        persona_data["quirks"]["favorite_phrase"] = char["catchphrase"]
        persona_data["quirks"]["colors"] = char["colors"]

        return persona_data

    @staticmethod
    def get_character_image_path(character_id: str) -> Path:
        """Get the path to character's image file"""
        char = CHARACTERS.get(character_id, CHARACTERS["glitch"])
        assets_dir = Path(__file__).parent / "characters"
        return assets_dir / char["image"]


def generate_random_name(character_id: str) -> str:
    """Generate a random name based on character personality"""
    prefixes = {
        "glitch": ["Zap", "Spark", "Buzz", "Flux", "Neon"],
        "citrus": ["Sunny", "Pip", "Zest", "Ray", "Clementine"],
        "slate": ["Echo", "Byte", "Core", "Sage", "Atlas"],
        "nova": ["Zip", "Dash", "Pixel", "Quirk", "Jolt"],
    }

    suffixes = [
        "bit",
        "byte",
        "chip",
        "bot",
        "core",
        "link",
        "node",
        "spark",
    ]

    prefix_list = prefixes.get(character_id, prefixes["glitch"])
    return f"{random.choice(prefix_list)}{random.choice(suffixes)}"


# Example usage
if __name__ == "__main__":
    selector = CharacterSelector()

    print("🎨 Bit Buddy Character Gallery\n")

    for char_id, char in selector.get_all_characters().items():
        print(f"{'='*60}")
        print(f"🤖 {char['name']} ({char_id})")
        print(f"   {char['description']}")
        print(
            f"   Traits: Curiosity={char['default_traits']['curiosity']}, "
            f"Humor={char['default_traits']['humor']}, "
            f"Formality={char['default_traits']['formality']}"
        )
        print(f"   Catchphrase: \"{char['catchphrase']}\"")
        print(f"   Colors: {', '.join(char['colors'])}")
        print()

    # Test random selection
    print("\n🎲 Random Character Test:")
    char_id, char = selector.random_character()
    name = generate_random_name(char_id)
    print(f"   Selected: {char['name']} (named '{name}')")
    print(f"   Arc: {char['arc']}")
