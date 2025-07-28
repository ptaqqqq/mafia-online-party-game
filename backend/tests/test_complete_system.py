import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.llm_client import DeepSeekClient
from app.services.character_generator import CharacterGenerator
from app.services.narrator_service import NarratorService

def test_complete_system():
    """Test the complete character and narrator system working together"""
    
    print("🧪 Testing Complete Character & Narrator System...")
    
    try:
        # 1. Inicjalizacja
        llm_client = DeepSeekClient()
        char_generator = CharacterGenerator(llm_client)
        narrator = NarratorService(llm_client)
        print("✅ All services initialized")
        
        # 2. Symulacja graczy dołączających do gry
        players = [
            {"player_id": "player-001", "name": "Alice"},
            {"player_id": "player-002", "name": "Bob"},
            {"player_id": "player-003", "name": "Charlie"},
            {"player_id": "player-004", "name": "Diana"}
        ]
        
        print(f"\n👥 Simulating game with {len(players)} players...")
        
        # 3. Generowanie profili (jak w prawdziwej grze)
        print(f"\n🎭 Generating character profiles...")
        profiles = char_generator.generate_profiles_for_players(players)
        
        print(f"✅ Generated profiles:")
        for profile in profiles:
            print(f"   {profile.emoji} {profile.name} ({profile.profession})")
            print(f"      {profile.description}")
        
        # 4. Ustawienie profili w narratorze
        narrator.set_character_profiles(profiles)
        
        # 5. Symulacja przebiegu gry
        print(f"\n📖 Simulating game flow...")
        
        # Opening
        player_names = [p["name"] for p in players]
        opening = narrator.generate_story_opening(player_names)
        print(f"\n🌅 GAME START:")
        print(f"   {opening}")
        
        # Night -> Day transition
        transition1 = narrator.generate_phase_transition("night", "day")
        print(f"\n🌅 DAWN:")
        print(f"   {transition1}")
        
        # Death discovery
        death = narrator.generate_death_narrative("Alice", "mafia", {})
        print(f"\n⚰️ MORNING NEWS:")
        print(f"   {death}")
        
        # Day -> Voting transition
        transition2 = narrator.generate_phase_transition("day", "voting")
        print(f"\n🗳️ VOTING TIME:")
        print(f"   {transition2}")
        
        # Voting result
        vote_result = narrator.generate_voting_narrative("Bob", {"total_votes": 3, "margin": "unanimous"})
        print(f"\n⚖️ VOTING RESULT:")
        print(f"   {vote_result}")
        
        # Game ending
        ending = narrator.generate_game_ending("innocents", ["Charlie", "Diana"])
        print(f"\n🏆 GAME END:")
        print(f"   {ending}")
        
        print(f"\n🎉 Complete system test successful!")
        print(f"📊 Generated {len(profiles)} profiles and 6 narrative pieces")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_system()