import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.llm_client import DeepSeekClient
from app.services.character_generator import CharacterGenerator

def test_character_generator():
    """Test character generation system"""
    
    print("🧪 Testing Character Generator...")
    
    try:
        # 1. Stwórz klienta i generator
        llm_client = DeepSeekClient()
        generator = CharacterGenerator(llm_client)
        print("✅ Character Generator created")
        
        # 2. Test danych graczy
        test_players = [
            {"player_id": "uuid-1", "name": "Alice"},
            {"player_id": "uuid-2", "name": "Bob"},
            {"player_id": "uuid-3", "name": "Charlie"}
        ]
        
        print(f"\n🎭 Generating profiles for {len(test_players)} players...")
        
        # 3. Generuj profile
        profiles = generator.generate_profiles_for_players(test_players)
        
        print(f"✅ Generated {len(profiles)} profiles:")
        
        # 4. Wyświetl profile
        for i, profile in enumerate(profiles, 1):
            print(f"\n  {i}. {profile.emoji} {profile.name}")
            print(f"     Profession: {profile.profession}")
            print(f"     Description: {profile.description}")
            print(f"     Player ID: {profile.player_id}")
        
        # 5. Test pojedynczego profilu
        print(f"\n🔍 Testing single profile generation...")
        single_profile = generator.generate_single_profile("test-uuid", "TestPlayer", "Baker")
        print(f"✅ Single profile: {single_profile.name} - {single_profile.description}")
        
        # 6. Test metod pomocniczych
        print(f"\n🔧 Testing helper methods...")
        professions = generator._select_professions(3)
        print(f"✅ Selected professions: {professions}")
        
        emoji = generator._get_profession_emoji("Baker")
        print(f"✅ Baker emoji: {emoji}")
        
        print(f"\n🎉 Character Generator tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_character_generator()