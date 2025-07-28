import os
import sys
from pathlib import Path

# Add backend to path so we can import app modules
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.llm_client import DeepSeekClient

def test_deepseek_client():
    """Simple test for DeepSeek client"""
    
    print("🧪 Testing DeepSeek Client...")
    
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        client = DeepSeekClient(api_key=api_key)
        print("✅ Client created successfully")
        
        # Test simple generation
        prompt = "Write a short description of a baker in a small town. Maximum 2 sentences."
        print(f"🔄 Testing with prompt: {prompt}")
        
        response = client.generate_text(prompt, max_tokens=100, temperature=0.7)
        print(f"✅ Response received: {response}")
        print(f"📏 Response length: {len(response)} characters")

        # Test with different parameters
        print("\n🔄 Testing with lower temperature...")
        response2 = client.generate_text(
            "Describe a librarian in one sentence.",
            max_tokens=50,
            temperature=0.3
        )
        print(f"✅ Second response: {response2}")
        
        print("\n🎉 All tests passed!")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {str(e)}")
        print("💡 Make sure to set DEEPSEEK_API_KEY in your .env file")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_deepseek_client()