"""Unit tests for OllamaLLM."""

import pytest
from unittest.mock import Mock, patch
import requests

from llm.ollama_llm import OllamaLLM


class TestOllamaLLM:
    """Test OllamaLLM class functionality."""

    @pytest.fixture
    def ollama_llm(self):
        """Create an OllamaLLM instance for testing."""
        return OllamaLLM(model="llama3.2")

    def test_ollama_llm_initialization(self, ollama_llm):
        """Test OllamaLLM initialization."""
        assert ollama_llm.model == "llama3.2"
        assert ollama_llm.base_url == "http://localhost:11434"
        assert ollama_llm.temperature == 0.1

    def test_ollama_llm_initialization_with_custom_params(self):
        """Test OllamaLLM initialization with custom parameters."""
        llm = OllamaLLM(
            model="custom_model",
            base_url="http://custom:11434",
            temperature=0.5
        )
        assert llm.model == "custom_model"
        assert llm.base_url == "http://custom:11434"
        assert llm.temperature == 0.5

    def test_ollama_llm_properties(self, ollama_llm):
        """Test OllamaLLM properties."""
        # Test LLM type property
        assert ollama_llm._llm_type == "ollama"

        # Test identifying properties
        assert hasattr(ollama_llm, '_identifying_params')
        params = ollama_llm._identifying_params
        assert isinstance(params, dict)
        assert "model" in params
        assert "base_url" in params
        assert "temperature" in params

    @patch('requests.post')
    def test_call_method_success(self, mock_post, ollama_llm):
        """Test successful _call method."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "This is a test response"
        }
        mock_post.return_value = mock_response

        # Test the call
        result = ollama_llm._call("Test prompt")

        # Verify result
        assert result == "This is a test response"

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "http://localhost:11434/api/generate" in call_args[0][0]

        # Check request payload
        request_data = call_args[1]['json']
        assert request_data['model'] == "llama3.2"
        assert request_data['prompt'] == "Test prompt"
        assert request_data['stream'] is False

    @patch('requests.post')
    def test_call_method_with_stop_words(self, mock_post, ollama_llm):
        """Test _call method with stop words."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "This is a test response"
        }
        mock_post.return_value = mock_response

        # Test the call with stop words
        stop_words = ["stop", "end"]
        result = ollama_llm._call("Test prompt", stop=stop_words)

        # Verify result
        assert result == "This is a test response"

        # Verify stop words were included in request
        call_args = mock_post.call_args
        request_data = call_args[1]['json']
        assert 'stop' in request_data

    @patch('requests.post')
    def test_call_method_request_error(self, mock_post, ollama_llm):
        """Test _call method with request error."""
        # Mock request exception
        mock_post.side_effect = requests.RequestException("Connection error")

        # Test the call should raise an exception
        with pytest.raises(Exception) as exc_info:
            ollama_llm._call("Test prompt")

        assert "Connection error" in str(exc_info.value)

    @patch('requests.post')
    def test_call_method_http_error(self, mock_post, ollama_llm):
        """Test _call method with HTTP error."""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        # Test the call should raise an exception
        with pytest.raises(Exception) as exc_info:
            ollama_llm._call("Test prompt")

        assert "500" in str(exc_info.value)

    @patch('requests.get')
    def test_validate_connection_success(self, mock_get, ollama_llm):
        """Test successful connection validation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response

        # Test validation
        result = ollama_llm.validate_connection()

        # Should return True for successful connection
        assert result is True

        # Verify the request was made to the tags endpoint
        mock_get.assert_called_once_with("http://localhost:11434/api/tags")

    @patch('requests.get')
    def test_validate_connection_failure(self, mock_get, ollama_llm):
        """Test connection validation failure."""
        # Mock request exception
        mock_get.side_effect = requests.RequestException("Connection refused")

        # Test validation
        result = ollama_llm.validate_connection()

        # Should return False for failed connection
        assert result is False

    @patch('requests.get')
    def test_get_available_models_success(self, mock_get, ollama_llm):
        """Test successful model list retrieval."""
        # Mock successful response with models
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:latest"},
                {"name": "codellama:7b"},
                {"name": "mistral:latest"}
            ]
        }
        mock_get.return_value = mock_response

        # Test getting available models
        models = ollama_llm.get_available_models()

        # Verify result
        expected_models = ["llama3.2:latest", "codellama:7b", "mistral:latest"]
        assert models == expected_models

    @patch('requests.get')
    def test_get_available_models_failure(self, mock_get, ollama_llm):
        """Test model list retrieval failure."""
        # Mock request exception
        mock_get.side_effect = requests.RequestException("Connection error")

        # Test getting available models
        models = ollama_llm.get_available_models()

        # Should return empty list on error
        assert models == []

    @patch('requests.get')
    def test_get_available_models_empty_response(self, mock_get, ollama_llm):
        """Test model list retrieval with empty response."""
        # Mock successful response with no models
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response

        # Test getting available models
        models = ollama_llm.get_available_models()

        # Should return empty list
        assert models == []

    def test_llm_type_property(self, ollama_llm):
        """Test _llm_type property."""
        assert ollama_llm._llm_type == "ollama"

    def test_identifying_params_content(self, ollama_llm):
        """Test content of identifying params."""
        params = ollama_llm._identifying_params

        # Should contain key parameters
        assert "model" in params
        assert "base_url" in params
        assert "temperature" in params

        # Check values
        assert params["model"] == "llama3.2"
        assert params["base_url"] == "http://localhost:11434"
        assert params["temperature"] == 0.1

    @patch('requests.post')
    def test_call_method_with_custom_temperature(self, mock_post):
        """Test _call method uses custom temperature."""
        # Create LLM with custom temperature
        llm = OllamaLLM(model="llama3.2", temperature=0.8)

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "test"}
        mock_post.return_value = mock_response

        # Test the call
        llm._call("Test prompt")

        # Verify temperature was set correctly
        call_args = mock_post.call_args
        request_data = call_args[1]['json']

        # Check if temperature-related options are in request
        assert 'options' in request_data or 'temperature' in request_data

    def test_string_representation(self, ollama_llm):
        """Test string representation of OllamaLLM."""
        str_repr = str(ollama_llm)

        # Should contain model and base URL info
        assert "llama3.2" in str_repr or "OllamaLLM" in str_repr