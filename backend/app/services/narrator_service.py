from typing import List, Dict, Any, Optional
import time
import logging
from .llm_client import DeepSeekClient
from .character_generator import CharacterProfile

logger = logging.getLogger(__name__)

class GameContext:
    """Stores game context for narrative generation"""

    def __init__(self):
        self.setting = ""
        self.atmosphere = "peaceful"
        self.day_count = 0
        self.events = []
        self.character_profiles: Dict[str, CharacterProfile] = {}

    def add_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Add event to game history"""
        event = {
            "type": event_type,
            "details": details,
            "timestamp": time.time()
            }
        self.events.append(event)

        if len(self.events) > 20:
            self.events = self.events[-20:]

    def update_atmosphere(self, new_atmosphere: str) -> None:
        """Update game atmosphere"""
        self.atmosphere = new_atmosphere

        self.add_event("atmosphere_change", {
            "new_atmosphere": new_atmosphere,
            "day_count": self.day_count
            })

class NarratorService:
    """Main service for generating game narratives using LLM"""

    def __init__(self, llm_client: DeepSeekClient):
        self.llm_client = llm_client
        self.game_context = GameContext()

    def set_character_profiles(self, profiles: List[CharacterProfile]) -> None:
        """
        Set character profiles for narrative context

        Args:
            profiles: List of character profiles
        """
        for profile in profiles:
            logger.info(f"Setting profile: {type(profile)} - name: {type(profile.name)} '{profile.name}'")
            self.game_context.character_profiles[profile.name] = profile
        
        logger.info(f"Set {len(profiles)} character profiles for narrative context")

    def generate_story_opening(self, player_names: List[str]) -> str:
        """
        Generate opening story for the game
        
        Args:
            player_names: List of player display names
            
        Returns:
            Opening narrative text
        """
        try:
            character_info = []
            for name in player_names:
                profile = self._get_character_context(name)
                if profile:
                    character_info.append(f"- {profile.emoji} {name} ({profile.profession}): {profile.description}")
                else:
                    character_info.append(f"- {name} (resident)")
            
            characters_text = "\n".join(character_info)
            
            prompt = f"""Write a dramatic opening for a mafia game set in a small town.

    Town Residents:
    {characters_text}

    Requirements:
    - 4-5 sentences maximum
    - Create rich atmosphere of mystery and tension
    - Reference specific residents and their roles in the community
    - Mention the approaching night and growing unease
    - Don't reveal anyone's game role (mafia/innocent)
    - Make it feel like a cinematic thriller opening
    - Use vivid, atmospheric language

    Style: Dark, atmospheric, cinematic, literary. Think Stephen King meets Agatha Christie."""

            response = self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=250,  # Increased for richer narratives
                temperature=0.8
            )
            
            self._update_game_context("game_start", {
                "player_count": len(player_names),
                "players": player_names
            })
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate opening story: {str(e)}")
            return f"Night falls over the quiet town. {len(player_names)} residents lock their doors, knowing that danger lurks in the shadows. The mafia will strike tonight, but who can be trusted?"

    def generate_death_narrative(self, victim_name: str, killer_role: str, context: Dict[str, Any]) -> str:
        """
        Generate narrative for player death
        
        Args:
            victim_name: Name of killed player
            killer_role: Role of killer (mafia/vote)
            context: Additional context information
            
        Returns:
            Death narrative text
        """
        try:
            victim_profile = self._get_character_context(victim_name)
            
            if victim_profile:
                victim_info = f"{victim_name} ({victim_profile.profession}): {victim_profile.description}"
            else:
                victim_info = f"{victim_name} (town resident)"
            
            if killer_role == "mafia":
                death_type = "killed by the mafia during the night"
                style_instruction = "mysterious and dark, focus on the discovery of the body"
            else:
                death_type = "executed by town vote"
                style_instruction = "dramatic and emotional, focus on the community's decision"
            
            prompt = f"""Write a dramatic narrative about a character's death in a mafia game.

    Victim: {victim_info}
    Death type: {death_type}
    Game atmosphere: {self.game_context.atmosphere}

    Requirements:
    - 3-4 sentences maximum
    - {style_instruction}
    - Reference their profession, personality, and place in the community
    - Show how their death affects the town
    - Use vivid, atmospheric details
    - Create emotional impact and suspense
    - Don't reveal any game roles

    Style: Cinematic, dramatic, immersive, literary. Think noir thriller meets small-town mystery."""

            response = self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=200,  # Increased for richer narratives
                temperature=0.7
            )
            
            self._update_game_context("player_death", {
                "victim": victim_name,
                "killer_role": killer_role,
                "day_count": self.game_context.day_count
            })
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate death narrative: {str(e)}")
            # Rich fallback death narratives - instant and atmospheric
            if killer_role == "mafia":
                return f"As dawn broke over the town square, {victim_name} was discovered motionless, their secrets forever silenced by the shadows that prowl these streets. The town mourns another soul claimed by the darkness."
            else:
                return f"With heavy hearts and trembling hands, the townspeople have spoken. {victim_name} walks toward an uncertain fate, their footsteps echoing through streets that may never see them again."

    def generate_voting_narrative(self, voted_player: str, vote_results: Dict[str, Any]) -> str:
        """
        Generate narrative for voting results
        
        Args:
            voted_player: Name of voted out player
            vote_results: Voting statistics
            
        Returns:
            Voting narrative text
        """
        try:
            player_profile = self._get_character_context(voted_player)
            
            if player_profile:
                player_info = f"{voted_player} ({player_profile.profession}): {player_profile.description}"
            else:
                player_info = f"{voted_player} (town resident)"
            
            total_votes = vote_results.get("total_votes", 0)
            vote_margin = vote_results.get("margin", "close")
            
            prompt = f"""Write a dramatic narrative about a town voting to exile someone in a mafia game.

    Voted player: {player_info}
    Vote margin: {vote_margin}
    Total votes: {total_votes}
    Game atmosphere: {self.game_context.atmosphere}

    Requirements:
    - 3-4 sentences maximum
    - Show the tension and emotion of the decision
    - Reference their profession and role in the community
    - Include the community's conflicted reaction
    - Show how their exile affects the town
    - Create dramatic tension about whether it's the right choice
    - Use atmospheric details

    Style: Tense, emotional, community-focused, literary. Think town hall drama meets psychological thriller."""

            response = self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=200,  # Increased for richer narratives
                temperature=0.7
            )
            
            self._update_game_context("voting_execution", {
                "voted_player": voted_player,
                "vote_results": vote_results,
                "day_count": self.game_context.day_count
            })
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate voting narrative: {str(e)}")
            return f"After intense deliberation, the town has decided. {voted_player} must leave. Was this the right choice?"

    def generate_save_narrative(self, saved_player: str, context: Dict[str, Any]) -> str:
        """
        Generate narrative for when someone is saved by medic

        Args:
            saved_player: Name of saved player
            context: Additional context information

        Returns:
            Save narrative text
        """
        try:
            saved_profile = self._get_character_context(saved_player)

            if saved_profile:
                saved_info = f"{saved_player} ({saved_profile.profession}): {saved_profile.description}"
            else:
                saved_info = f"{saved_player} (town resident)"

            prompt = f"""Write a dramatic narrative about someone being saved by a medic in a mafia game.

    Saved player: {saved_info}
    Game atmosphere: {self.game_context.atmosphere}
    Day count: {self.game_context.day_count}

    Requirements:
    - 2-3 sentences maximum
    - Show that danger was averted without revealing the medic
    - Reference their profession and place in the community
    - Create mystery about what happened
    - Suggest they were protected by "unseen forces" or "guardian angel"
    - Don't reveal any game roles

    Style: Mysterious, hopeful, atmospheric. Think divine intervention meets small-town mystery."""

            response = self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=150,
                temperature=0.7
            )

            self._update_game_context("player_saved", {
                "saved_player": saved_player,
                "day_count": self.game_context.day_count
            })

            return response.strip()

        except Exception as e:
            logger.error(f"Failed to generate save narrative: {str(e)}")
            return f"The night passed quietly. {saved_player} was protected by unseen forces."

    def generate_phase_transition(self, from_phase: str, to_phase: str) -> str:
        """
        Generate narrative for phase transitions
        
        Args:
            from_phase: Current phase
            to_phase: Next phase
            
        Returns:
            Transition narrative text
        """
        try:
            # Mapowanie faz na opisy
            phase_descriptions = {
                "night": "darkness falls and the town sleeps uneasily",
                "day": "dawn breaks and the townspeople gather",
                "voting": "the time for discussion ends, decisions must be made",
                "lobby": "a new game begins"
            }
            
            transition_type = f"{from_phase}_to_{to_phase}"
            
            prompt = f"""Write a brief atmospheric transition for a mafia game.

    Transition: {from_phase} → {to_phase}
    Current atmosphere: {self.game_context.atmosphere}
    Day count: {self.game_context.day_count}

    Context:
    - From: {phase_descriptions.get(from_phase, from_phase)}
    - To: {phase_descriptions.get(to_phase, to_phase)}

    Requirements:
    - 1-2 sentences maximum
    - Create appropriate mood for the phase
    - Build tension and atmosphere
    - Match the current game atmosphere

    Style: Atmospheric, cinematic, brief"""

            response = self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=80,
                temperature=0.6
            )
            
            # Aktualizuj kontekst
            if to_phase == "day":
                self.game_context.day_count += 1
                
            self._update_game_context("phase_transition", {
                "from_phase": from_phase,
                "to_phase": to_phase,
                "day_count": self.game_context.day_count
            })
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate phase transition: {str(e)}")
            # Rich fallback transitions - instant and atmospheric
            fallbacks = {
                "night_to_day": "As the first pale light of dawn creeps over the town, the shadows retreat reluctantly, leaving behind whispers of secrets that linger in the crisp morning air.",
                "day_to_voting": "The sun reaches its zenith as heated discussions fill the town square. The time for words has passed - now comes the moment of terrible decision.",
                "voting_to_night": "As twilight descends like a heavy curtain, the town holds its breath. Another night of uncertainty awaits, and not everyone may see the dawn.",
                "lobby_to_night": "The game begins as darkness falls over the quiet town. Behind closed doors and drawn curtains, secrets stir and alliances form in the shadows."
            }
            return fallbacks.get(transition_type, f"The {to_phase} phase begins...")

    def generate_game_ending(self, winner: str, final_players: List[str]) -> str:
        """
        Generate ending narrative
        
        Args:
            winner: Winning side (mafia/innocents/draw)
            final_players: List of surviving players
            
        Returns:
            Ending narrative text
        """
        try:
            survivor_info = []
            for player_name in final_players:
                profile = self._get_character_context(player_name)
                if profile:
                    survivor_info.append(f"{profile.emoji} {player_name} ({profile.profession})")
                else:
                    survivor_info.append(player_name)
            
            survivors_text = ", ".join(survivor_info) if survivor_info else "no one"
            
            if winner == "mafia":
                victory_type = "The mafia has taken control of the town"
                mood = "dark and ominous"
            elif winner == "innocents":
                victory_type = "The innocent townspeople have prevailed"
                mood = "hopeful but scarred"
            else:
                victory_type = "The conflict ends in a stalemate"
                mood = "ambiguous and haunting"
            
            prompt = f"""Write an epic ending for a mafia game.

    Victory: {victory_type}
    Survivors: {survivors_text}
    Total days survived: {self.game_context.day_count}
    Final atmosphere: {self.game_context.atmosphere}

    Requirements:
    - 3-4 sentences maximum
    - {mood} tone
    - Reference the survivors and their journey
    - Create a sense of conclusion
    - Include a moral or reflection about trust/betrayal

    Style: Epic, conclusive, emotionally resonant"""

            response = self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=150,
                temperature=0.7
            )
            
            self._update_game_context("game_end", {
                "winner": winner,
                "survivors": final_players,
                "total_days": self.game_context.day_count
            })
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate game ending: {str(e)}")
            if winner == "mafia":
                return f"The mafia has won. {survivors_text} remain to tell the tale of this dark chapter."
            elif winner == "innocents":
                return f"Justice prevails! The innocent townspeople have survived. {survivors_text} can finally rest easy."
            else:
                return f"The conflict ends with no clear victor. {survivors_text} must live with the consequences."

    def _create_narrative_prompt(self, prompt_type: str, context: Dict[str, Any]) -> str:
        """
        Create prompt for narrative generation

        Args:
            prompt_type: Type of narrative (opening, death, voting, etc.)
            context: Context information for prompt

        Returns:
            Formatted prompt string
        """
        # TODO: Create appropriate prompt based on type
        pass

    def _get_character_context(self, player_name: str) -> Optional[CharacterProfile]:
        """
        Get character profile for player

        Args:
            player_name: Player display name

        Returns:
            CharacterProfile if found, None otherwise
        """
        return self.game_context.character_profiles.get(player_name)

    def _update_game_context(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Update game context with new event

        Args:
            event_type: Type of event
            details: Event details
        """
        self.game_context.add_event(event_type, details)

        if event_type == "player_death":
            self.game_context.update_atmosphere("dark")
        elif event_type == "voting_execution":
            self.game_context.update_atmosphere("tense")
        elif event_type == "game_start":
            self.game_context.update_atmosphere("mysterious")
        elif event_type == "day_phase":
            if self.game_context.day_count > 2:
                self.game_context.update_atmosphere("desperate")
            else:
                self.game_context.update_atmosphere("tense")