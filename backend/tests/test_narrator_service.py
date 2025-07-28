import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.llm_client import DeepSeekClient
from app.services.character_generator import CharacterGenerator, CharacterProfile
from app.services.narrator_service import NarratorService

def test_narrator_service():
    """Test narrator service system"""
    
    print("🧪 Testing Narrator Service...")
    
    try:
        # 1. Stwórz serwisy
        llm_client = DeepSeekClient()
        narrator = NarratorService(llm_client)
        print("✅ Narrator Service created")
        
        # 2. Stwórz przykładowe profile postaci
        test_profiles = [
            CharacterProfile("uuid-1", "Alice", "Baker", "Alice runs the local bakery and knows everyone's morning routine.", "🍞"),
            CharacterProfile("uuid-2", "Bob", "Mechanic", "Bob fixes cars and machinery, often working late into the night.", "🔧"),
            CharacterProfile("uuid-3", "Charlie", "Teacher", "Charlie teaches at the local school and cares deeply about the students.", "📝")
        ]
        
        # 3. Ustaw profile w narratorze
        narrator.set_character_profiles(test_profiles)
        print("✅ Character profiles set")
        
        # 4. Test opening story
        print(f"\n📖 Testing story opening...")
        player_names = ["Alice", "Bob", "Charlie"]
        opening = narrator.generate_story_opening(player_names)
        print(f"✅ Opening story:")
        print(f"   {opening}")
        
        # 5. Test death narrative
        print(f"\n⚰️ Testing death narrative...")
        death_story = narrator.generate_death_narrative("Alice", "mafia", {})
        print(f"✅ Death narrative:")
        print(f"   {death_story}")
        
        # 6. Test voting narrative
        print(f"\n🗳️ Testing voting narrative...")
        vote_results = {"total_votes": 3, "margin": "close"}
        voting_story = narrator.generate_voting_narrative("Bob", vote_results)
        print(f"✅ Voting narrative:")
        print(f"   {voting_story}")
        
        # 7. Test phase transition
        print(f"\n🌅 Testing phase transition...")
        transition = narrator.generate_phase_transition("night", "day")
        print(f"✅ Phase transition:")
        print(f"   {transition}")
        
        # 8. Test game ending
        print(f"\n🏆 Testing game ending...")
        ending = narrator.generate_game_ending("innocents", ["Charlie"])
        print(f"✅ Game ending:")
        print(f"   {ending}")
        
        # 9. Test context methods
        print(f"\n🔍 Testing context methods...")
        profile = narrator._get_character_context("Alice")
        print(f"✅ Found Alice's profile: {profile.profession if profile else 'None'}")
        
        print(f"\n🎉 Narrator Service tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_narrator_service()