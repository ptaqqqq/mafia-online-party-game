from typing import List, Dict, Any
import time
import random
import asyncio
import logging
from .llm_client import DeepSeekClient

logger = logging.getLogger(__name__)

class CharacterProfile:
    """Data class for character profile information"""

    def __init__(self, player_id: str, name: str, profession: str, description: str, emoji: str):
        self.player_id = player_id
        self.name = name
        self.profession = profession
        self.description = description
        self.emoji = emoji

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "profession": self.profession,
            "description": self.description,
            "emoji": self.emoji
        }

class CharacterGenerator:
    """Generates character profiles for mafia game players"""

    def __init__(self, llm_client: DeepSeekClient):
        self.llm_client = llm_client
        self.available_professions = [
            "Baker", "Librarian", "Mechanic", "Teacher",
            "Doctor", "Shop Owner", "Postman", "Firefighter",
            "Hairdresser", "Bartender", "Accountant", "Gardener",
            "Police Officer", "Nurse", "Chef", "Taxi Driver"
        ]

    def generate_profiles_for_players(self, player_data: List[Dict[str, str]]) -> List[CharacterProfile]:
        """
        Generate character profiles for all players

        Args:
            player_data: List of dicts with 'player_id' and 'name' keys

        Returns:
            List of CharacterProfile objects
        """
        if not player_data:
            return []
        
        player_count = len(player_data)
        professions = self._select_professions(player_count)
        
        profiles = []
        for i, player in enumerate(player_data):
            player_id = player["player_id"]
            name = player["name"]
            profession = professions[i]

            logger.info(f"Generating profile {i+1}/{player_count}: {name} as {profession}")

            profile = self.generate_single_profile(player_id, name, profession)
            profiles.append(profile)

            if i < player_count - 1:
                time.sleep(0.5)
        logger.info(f"Generated {len(profiles)} character profiles")
        return profiles

    def generate_single_profile(self, player_id: str, name: str, profession: str) -> CharacterProfile:
        """
        Generate a single character profile

        Args:
            player_id: Unique player identifier
            name: Player's display name
            profession: Assigned profession

        Returns:
            CharacterProfile object
        """
        try:
            prompt = self._create_character_prompt(name, profession)
            
            logger.info(f"Generating profile for {name} - {profession}")
            response = self.llm_client.generate_text(
                prompt, 
                max_tokens=100,
                temperature=0.8
            )
            profile = self._parse_llm_response(response, player_id, name, profession)
            logger.info(f"Successfully generated profile for {name}")
            return profile
        
        except Exception as e:
            logger.warning(f"LLM failed for {name}, using fallback: {str(e)}")
            return self._create_fallback_profile(player_id, name, profession)

    def _select_professions(self, player_count: int) -> List[str]:
        """
        Select unique professions for players

        Args:
            player_count: Number of players

        Returns:
            List of profession names
        """
        if player_count <= len(self.available_professions):
            return random.sample(self.available_professions, player_count)
        else:
            return random.choices(self.available_professions, k=player_count)

    def _create_character_prompt(self, name: str, profession: str) -> str:
        """
        Create prompt for character generation
        
        Args:
            name: Player name
            profession: Character profession
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Create a character profile for a mafia game set in a small town.

    Character Details:
    - Name: {name}
    - Profession: {profession}

    Generate a short character description (maximum 2 sentences) that includes:
    1. What they do in their profession
    2. One interesting personality trait or habit
    3. How they might be connected to the town

    Style: Realistic, intriguing but not suspicious. Make them feel like a real person.
    Language: English
    Format: Return only the description, no extra text.

    Example: "Sarah runs the local library and knows everyone's reading habits by heart. She's known for her excellent memory and often helps townspeople find lost items."
    """
        return prompt

    def _parse_llm_response(self, response: str, player_id: str, name: str, profession: str) -> CharacterProfile:
        """
        Parse LLM response into CharacterProfile

        Args:
            response: Raw LLM response
            player_id: Player identifier
            name: Player name
            profession: Character profession

        Returns:
            CharacterProfile object
        """
        description = response.strip()
        if description.startswith('"') and description.endswith('"'):
            description = description[1:-1]
        if len(description) > 200:
            description = description[:200] + "..."
        emoji = self._get_profession_emoji(profession)
        return CharacterProfile(
            player_id=player_id,
            name=name,
            profession=profession,
            description=description,
            emoji=emoji
        )

    def _create_fallback_profile(self, player_id: str, name: str, profession: str) -> CharacterProfile:
        """
        Create fallback profile if LLM fails
        
        Args:
            player_id: Player identifier
            name: Player name
            profession: Character profession
            
        Returns:
            Basic CharacterProfile object
        """
        fallback_descriptions = {
            "Baker": f"{name} runs the local bakery and is known for fresh bread every morning.",
            "Librarian": f"{name} manages the town library and knows everyone's reading preferences.",
            "Mechanic": f"{name} fixes cars and machinery at the local garage.",
            "Teacher": f"{name} teaches at the local school and cares deeply about the students.",
            "Doctor": f"{name} provides medical care to the townspeople at the clinic.",
            "Shop Owner": f"{name} runs a general store that serves the whole community."
        }
        
        description = fallback_descriptions.get(
            profession, 
            f"{name} works as a {profession.lower()} in the town."
        )
        
        emoji = self._get_profession_emoji(profession)
        
        return CharacterProfile(
            player_id=player_id,
            name=name,
            profession=profession,
            description=description,
            emoji=emoji
        )

    def _get_profession_emoji(self, profession: str) -> str:
        """
        Get emoji for profession
        
        Args:
            profession: Profession name
            
        Returns:
            Emoji string
        """
        emoji_map = {
            "Baker": "🍞",
            "Librarian": "📚", 
            "Mechanic": "🔧",
            "Teacher": "📝",
            "Doctor": "⚕️",
            "Shop Owner": "🏪",
            "Postman": "📮",
            "Firefighter": "🚒",
            "Hairdresser": "💇",
            "Bartender": "🍺",
            "Accountant": "📊",
            "Gardener": "🌱",
            "Police Officer": "👮",
            "Nurse": "👩‍⚕️",
            "Chef": "👨‍🍳",
            "Taxi Driver": "🚕"
        }
        return emoji_map.get(profession, "👤")