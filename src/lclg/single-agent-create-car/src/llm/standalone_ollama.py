"""Standalone OllamaClient for single-agent car creation system."""

import json
import requests
from typing import Any, Dict, List, Optional, Union


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


class StandaloneOllamaClient:
    """Standalone Ollama client for direct API communication."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize the Ollama client.

        Args:
            base_url: Base URL for the Ollama server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response using the Ollama generate endpoint.

        Args:
            prompt: The input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated response text

        Raises:
            LLMError: If the request fails
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": kwargs.get("model", "llama3.2"),
            "prompt": prompt,
            "stream": kwargs.get("stream", False),
        }

        # Add optional parameters
        optional_params = [
            "temperature", "top_p", "top_k", "repeat_penalty",
            "seed", "keep_alive", "format", "max_tokens"
        ]

        for param in optional_params:
            if param in kwargs and kwargs[param] is not None:
                payload[param] = kwargs[param]

        try:
            response = self.session.post(url, json=payload, timeout=120)
            response.raise_for_status()

            if kwargs.get("stream", False):
                # Handle streaming response
                lines = response.text.strip().split('\n')
                full_response = ""
                for line in lines:
                    if line.strip():
                        chunk = json.loads(line)
                        if chunk.get("response"):
                            full_response += chunk["response"]
                return full_response
            else:
                # Handle non-streaming response
                result = response.json()
                return result.get("response", "")

        except requests.exceptions.RequestException as e:
            raise LLMError(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse response: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error: {str(e)}")

    def chat_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat response using the Ollama chat endpoint.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional generation parameters

        Returns:
            Generated response text

        Raises:
            LLMError: If the request fails
        """
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": kwargs.get("model", "llama3.2"),
            "messages": messages,
            "stream": kwargs.get("stream", False),
        }

        # Add optional parameters
        optional_params = [
            "temperature", "top_p", "top_k", "repeat_penalty",
            "seed", "keep_alive", "format", "max_tokens"
        ]

        for param in optional_params:
            if param in kwargs and kwargs[param] is not None:
                payload[param] = kwargs[param]

        try:
            response = self.session.post(url, json=payload, timeout=120)
            response.raise_for_status()

            if kwargs.get("stream", False):
                # Handle streaming response
                lines = response.text.strip().split('\n')
                full_response = ""
                for line in lines:
                    if line.strip():
                        chunk = json.loads(line)
                        if chunk.get("message", {}).get("content"):
                            full_response += chunk["message"]["content"]
                return full_response
            else:
                # Handle non-streaming response
                result = response.json()
                return result.get("message", {}).get("content", "")

        except requests.exceptions.RequestException as e:
            raise LLMError(f"Chat request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse chat response: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected chat error: {str(e)}")

    def get_available_models(self) -> List[str]:
        """Get list of available models.

        Returns:
            List of model names

        Raises:
            LLMError: If the request fails
        """
        url = f"{self.base_url}/api/tags"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            result = response.json()
            models = result.get("models", [])
            return [model["name"] for model in models]

        except requests.exceptions.RequestException as e:
            raise LLMError(f"Failed to get available models: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse models response: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error getting models: {str(e)}")

    def validate_connection(self) -> bool:
        """Validate connection to Ollama server.

        Returns:
            True if connection is successful

        Raises:
            LLMError: If connection fails
        """
        try:
            self.get_available_models()
            return True
        except LLMError:
            return False
        except Exception as e:
            raise LLMError(f"Connection validation failed: {str(e)}")

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with model information

        Raises:
            LLMError: If the request fails
        """
        url = f"{self.base_url}/api/show"

        payload = {"name": model_name}

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise LLMError(f"Failed to get model info: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse model info response: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error getting model info: {str(e)}")