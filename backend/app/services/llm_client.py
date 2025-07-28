import requests
import json
from typing import Optional, Dict, Any
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """Client for DeepSeek R1 API integration"""

    def __init__(self, api_key: str = None, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable or pass api_key parameter.")
        self.base_url = base_url
        self.model = "deepseek/deepseek-chat"

    def generate_text(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
        """
        Generate text using DeepSeek R1 API

        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0 - 1.0)

        Returns:
            Generated text response
        """
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,

            "stream": False
        }

        try:
            response_data = self._make_request(payload)

            if "choices" in response_data and len(response_data["choices"]) > 0:
                choice = response_data["choices"][0]

                if "message" in choice:
                    message = choice["message"]

                    if "content" in message and message["content"]:
                        generated_text = message["content"]
                        return generated_text.strip()
                    elif "reasoning" in message and message["reasoning"]:
                        generated_text = message["reasoning"]
                        return generated_text.strip()
                    else:
                        raise Exception(f"No content or reasoning in message: {message}")
                else:
                    raise Exception(f"No message in choice: {choice}")
            else:
                raise Exception(f"No choices in response: {response_data}")

        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise Exception(f"Failed to generate text: {str(e)}")

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request to OpenRouter API
        
        Args:
            payload: Request payload
            
        Returns:
            API response as dictionary
        """
        headers = self._prepare_headers()
        url = f"{self.base_url}/chat/completions"
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code != 200:
                self._handle_api_error(response)
            
            response_data = response.json()
            return response_data
            
        except requests.exceptions.Timeout:
            raise Exception("OpenRouter API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error connecting to OpenRouter API: {str(e)}")

    def _prepare_headers(self) -> Dict[str, str]:
        """
        Prepare headers for DeepSeek API request

        Returns:
            Headers dictionary
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "Mafia Online Game"
        }

    def _handle_api_error(self, response: requests.Response) -> None:
        """
        Handle API errors and raise appropriate exceptions

        Args:
            response: HTTP response object
        """
        if response.status_code == 401:
            raise Exception("Invalid API key - check your DeepSeek API credentials")
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded - too many requests")
        elif response.status_code == 500:
            raise Exception("DeepSeek API server error - try again later")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Unknown API error")
                raise Exception(f"DeepSeek API error: {error_message}")
            except:
                raise Exception(f"DeepSeek API error: HTTP {response.status_code}")