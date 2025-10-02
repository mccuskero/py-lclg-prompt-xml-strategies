"""Unit tests for CLI interface."""

import pytest
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the CLI module
import cli
from cli import SingleAgentCarCLI, main


class TestSingleAgentCarCLI:
    """Test cases for SingleAgentCarCLI class."""

    @pytest.fixture
    def cli_instance(self):
        """Create a CLI instance for testing."""
        return SingleAgentCarCLI()

    def test_cli_initialization(self, cli_instance):
        """Test CLI initialization."""
        assert cli_instance.agent is None

    @patch('cli.CarAgent')
    def test_initialize_agent_success(self, mock_car_agent, cli_instance):
        """Test successful agent initialization."""
        mock_agent = Mock()
        mock_car_agent.return_value = mock_agent

        result = cli_instance._initialize_agent(
            model="test_model",
            base_url="http://test:11434",
            temperature=0.2,
            use_json_subtypes_in_prompts_creation=True,
            enable_logging=False
        )

        assert result is True
        assert cli_instance.agent == mock_agent
        mock_car_agent.assert_called_once_with(
            model_name="test_model",
            base_url="http://test:11434",
            temperature=0.2,
            use_json_subtypes_in_prompts_creation=True,
            enable_logging=False
        )

    @patch('cli.CarAgent')
    def test_initialize_agent_failure(self, mock_car_agent, cli_instance):
        """Test agent initialization failure."""
        mock_car_agent.side_effect = Exception("Initialization failed")

        result = cli_instance._initialize_agent(
            model="test_model",
            base_url="http://test:11434",
            temperature=0.2
        )

        assert result is False
        assert cli_instance.agent is None

    def test_format_output_json(self, cli_instance):
        """Test JSON output formatting."""
        data = {"key": "value", "number": 42}
        result = cli_instance._format_output(data, "json")

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == data

    def test_format_output_compact(self, cli_instance):
        """Test compact output formatting."""
        data = {"key": "value"}
        result = cli_instance._format_output(data, "compact")

        assert isinstance(result, str)
        assert "\n" not in result  # Compact should have no newlines
        parsed = json.loads(result)
        assert parsed == data

    def test_format_output_summary(self, cli_instance):
        """Test summary output formatting."""
        data = {
            "car_configuration": {
                "vehicle_info": {
                    "type": "sedan",
                    "performance_level": "standard"
                },
                "engine": {"horsepower": "280"},
                "body": {"exterior": {"style": "sedan"}},
                "electrical": {"main_system": {"voltage_system": "12V"}},
                "tires_and_wheels": {"tires": {"size": "225/60R16"}}
            },
            "metadata": {
                "created_by": "car_agent",
                "performance_summary": {"power_rating": "280 HP"}
            }
        }

        result = cli_instance._format_output(data, "summary")

        assert isinstance(result, str)
        assert "Single-Agent Car Creation Summary" in result
        assert "sedan" in result
        assert "280 HP" in result

    def test_format_output_summary_with_error(self, cli_instance):
        """Test summary formatting with error data."""
        data = {"error": "Something went wrong"}
        result = cli_instance._format_output(data, "summary")

        assert "❌ Error: Something went wrong" in result

    def test_create_summary_missing_data(self, cli_instance):
        """Test summary creation with missing data."""
        data = {}
        result = cli_instance._create_summary(data)

        assert "No car configuration data available" in result

    def test_save_output_success(self, cli_instance, tmp_path):
        """Test successful output saving."""
        data = {"test": "data"}
        output_file = tmp_path / "test_output.json"

        result = cli_instance._save_output(data, str(output_file), "json")

        assert result is True
        assert output_file.exists()

        with open(output_file) as f:
            saved_data = json.load(f)
        assert saved_data == data

    def test_save_output_failure(self, cli_instance):
        """Test output saving failure."""
        data = {"test": "data"}
        invalid_path = "/invalid/path/output.json"

        result = cli_instance._save_output(data, invalid_path, "json")

        assert result is False


class TestCLICommands:
    """Test cases for CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @patch('cli.setup_logging')
    def test_main_command_with_logging_options(self, mock_setup_logging, runner):
        """Test main command with logging options."""
        result = runner.invoke(main, [
            '--log-level', 'DEBUG',
            '--log-to-file',
            '--log-format', 'detailed',
            '--json-logs',
            'agent-info'
        ])

        mock_setup_logging.assert_called_once()
        call_args = mock_setup_logging.call_args[1]
        assert call_args['level'] == 'DEBUG'
        assert call_args['log_to_file'] is True
        assert call_args['log_format'] == 'detailed'
        assert call_args['json_format'] is True

    @patch('cli.cli_instance._initialize_agent')
    def test_create_car_command_success(self, mock_init_agent, runner):
        """Test successful create-car command."""
        # Mock successful agent initialization
        mock_init_agent.return_value = True

        # Mock agent with successful car creation
        mock_agent = Mock()
        mock_agent.create_complete_car.return_value = {
            "car_configuration": {
                "vehicle_info": {"type": "sedan"},
                "engine": {"horsepower": "280"}
            },
            "metadata": {"created_by": "car_agent"}
        }

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, [
                'create-car',
                '--vehicle-type', 'sedan',
                '--performance-level', 'standard',
                '--fuel-preference', 'gasoline',
                '--budget', 'medium',
                '--format', 'summary'
            ])

        assert result.exit_code == 0
        assert "Creating sedan with single car agent" in result.output
        mock_agent.create_complete_car.assert_called_once()

    @patch('cli.cli_instance._initialize_agent')
    def test_create_car_command_with_special_features(self, mock_init_agent, runner):
        """Test create-car command with special features."""
        mock_init_agent.return_value = True
        mock_agent = Mock()
        mock_agent.create_complete_car.return_value = {"car_configuration": {}}

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, [
                'create-car',
                '--vehicle-type', 'suv',
                '--special-features', 'sunroof',
                '--special-features', 'leather_seats'
            ])

        # Check that special features were passed to the agent
        call_args = mock_agent.create_complete_car.call_args[0][0]
        assert call_args['special_features'] == ['sunroof', 'leather_seats']

    @patch('cli.cli_instance._initialize_agent')
    def test_create_car_command_with_output_file(self, mock_init_agent, runner, tmp_path):
        """Test create-car command with output file."""
        mock_init_agent.return_value = True
        mock_agent = Mock()
        mock_agent.create_complete_car.return_value = {"test": "data"}

        output_file = tmp_path / "output.json"

        with patch.object(cli.cli_instance, 'agent', mock_agent), \
             patch.object(cli.cli_instance, '_save_output') as mock_save:
            mock_save.return_value = True

            result = runner.invoke(main, [
                'create-car',
                '--vehicle-type', 'sedan',
                '--output', str(output_file)
            ])

        mock_save.assert_called_once()

    @patch('cli.cli_instance._initialize_agent')
    def test_create_car_command_initialization_failure(self, mock_init_agent, runner):
        """Test create-car command with agent initialization failure."""
        mock_init_agent.return_value = False

        result = runner.invoke(main, ['create-car'])

        assert result.exit_code == 1

    @patch('cli.cli_instance._initialize_agent')
    def test_create_car_command_with_error_result(self, mock_init_agent, runner):
        """Test create-car command when agent returns error."""
        mock_init_agent.return_value = True
        mock_agent = Mock()
        mock_agent.create_complete_car.return_value = {"error": "Car creation failed"}

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, ['create-car'])

        assert result.exit_code == 1

    @patch('cli.cli_instance._initialize_agent')
    def test_create_car_command_exception(self, mock_init_agent, runner):
        """Test create-car command with exception during creation."""
        mock_init_agent.return_value = True
        mock_agent = Mock()
        mock_agent.create_complete_car.side_effect = Exception("Unexpected error")

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, ['create-car'])

        assert result.exit_code == 1
        assert "Car creation failed" in result.output

    @patch('cli.cli_instance._initialize_agent')
    def test_validate_agent_command(self, mock_init_agent, runner):
        """Test validate-agent command."""
        mock_init_agent.return_value = True
        mock_agent = Mock()
        mock_agent.get_agent_info.return_value = {
            "name": "car_agent",
            "type": "car",
            "tools": ["tool1", "tool2"],
            "llm_type": "OllamaLLM",
            "model": "llama3.2"
        }
        mock_agent.get_tool_categories.return_value = {
            "engine": ["configure_engine"],
            "body": ["design_body"]
        }
        mock_agent.create_component_json.return_value = {"test": "success"}

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, ['validate-agent'])

        assert result.exit_code == 0
        assert "Agent Status: READY" in result.output
        assert "car_agent" in result.output

    @patch('cli.cli_instance._initialize_agent')
    def test_validate_agent_with_llm_failure(self, mock_init_agent, runner):
        """Test validate-agent command with LLM connectivity failure."""
        mock_init_agent.return_value = True
        mock_agent = Mock()
        mock_agent.get_agent_info.return_value = {"name": "car_agent"}
        mock_agent.get_tool_categories.return_value = {"engine": ["tool1"]}
        mock_agent.create_component_json.return_value = {"error": "LLM connection failed"}

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, ['validate-agent'])

        assert result.exit_code == 1
        assert "LLM connectivity: FAILED" in result.output

    @patch('cli.cli_instance._initialize_agent')
    def test_test_tools_command(self, mock_init_agent, runner):
        """Test test-tools command."""
        mock_init_agent.return_value = True
        mock_agent = Mock()
        mock_agent.create_component_json.return_value = {"test": "result"}

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, [
                'test-tools',
                '--tool-category', 'engine'
            ])

        assert result.exit_code == 0
        assert "engine tools test: PASSED" in result.output

    @patch('cli.cli_instance._initialize_agent')
    def test_test_tools_all_categories(self, mock_init_agent, runner):
        """Test test-tools command with all categories."""
        mock_init_agent.return_value = True
        mock_agent = Mock()
        mock_agent.create_complete_car.return_value = {"test": "result"}

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, [
                'test-tools',
                '--tool-category', 'all'
            ])

        assert result.exit_code == 0
        mock_agent.create_complete_car.assert_called_once()

    @patch('cli.cli_instance._initialize_agent')
    def test_agent_info_command(self, mock_init_agent, runner):
        """Test agent-info command."""
        mock_init_agent.return_value = True
        mock_agent = Mock()
        mock_agent.get_agent_info.return_value = {
            "name": "car_agent",
            "type": "car",
            "tools": ["tool1", "tool2"]
        }
        mock_agent.get_tool_categories.return_value = {
            "engine": ["tool1"],
            "body": ["tool2"]
        }

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, ['agent-info'])

        assert result.exit_code == 0
        assert "Single-Agent System Information" in result.output

    @patch('cli.cli_instance._initialize_agent')
    def test_batch_create_command(self, mock_init_agent, runner, tmp_path):
        """Test batch-create command."""
        # Create requirements file
        requirements = [
            {
                "vehicle_type": "sedan",
                "performance_level": "standard",
                "fuel_preference": "gasoline",
                "budget": "medium"
            },
            {
                "vehicle_type": "suv",
                "performance_level": "performance",
                "fuel_preference": "hybrid",
                "budget": "high"
            }
        ]

        requirements_file = tmp_path / "requirements.json"
        with open(requirements_file, 'w') as f:
            json.dump(requirements, f)

        output_dir = tmp_path / "batch_output"

        mock_init_agent.return_value = True
        mock_agent = Mock()
        mock_agent.create_complete_car.return_value = {"car_configuration": {}}

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, [
                'batch-create',
                '--requirements-file', str(requirements_file),
                '--output-dir', str(output_dir)
            ])

        assert result.exit_code == 0
        assert output_dir.exists()
        assert "Batch Summary: 2/2 successful" in result.output

    def test_batch_create_invalid_file(self, runner):
        """Test batch-create command with invalid requirements file."""
        result = runner.invoke(main, [
            'batch-create',
            '--requirements-file', 'nonexistent.json'
        ])

        assert result.exit_code == 1
        assert "Failed to load requirements file" in result.output

    @patch('cli.cli_instance._initialize_agent')
    def test_batch_create_with_errors(self, mock_init_agent, runner, tmp_path):
        """Test batch-create command with some failures."""
        requirements = [
            {"vehicle_type": "sedan"},
            {"vehicle_type": "suv"}
        ]

        requirements_file = tmp_path / "requirements.json"
        with open(requirements_file, 'w') as f:
            json.dump(requirements, f)

        mock_init_agent.return_value = True
        mock_agent = Mock()

        # First call succeeds, second fails
        mock_agent.create_complete_car.side_effect = [
            {"car_configuration": {}},
            Exception("Creation failed")
        ]

        with patch.object(cli.cli_instance, 'agent', mock_agent):
            result = runner.invoke(main, [
                'batch-create',
                '--requirements-file', str(requirements_file),
                '--output-dir', str(tmp_path / "output")
            ])

        assert result.exit_code == 1  # Should exit with error due to failures


class TestCLIParameterHandling:
    """Test cases for CLI parameter handling."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_default_parameters(self, runner):
        """Test CLI with default parameters."""
        with patch('cli.setup_logging') as mock_setup:
            result = runner.invoke(main, ['agent-info'])

            # Check that setup_logging was called with defaults
            call_kwargs = mock_setup.call_args[1] if mock_setup.call_args else {}
            assert call_kwargs.get('level') == 'INFO'
            assert call_kwargs.get('log_to_file') is False

    def test_custom_logging_parameters(self, runner):
        """Test CLI with custom logging parameters."""
        with patch('cli.setup_logging') as mock_setup:
            result = runner.invoke(main, [
                '--log-level', 'DEBUG',
                '--log-to-file',
                '--log-file', '/tmp/test.log',
                '--log-format', 'detailed',
                '--disable-colors',
                '--json-logs',
                'agent-info'
            ])

            call_kwargs = mock_setup.call_args[1]
            assert call_kwargs['level'] == 'DEBUG'
            assert call_kwargs['log_to_file'] is True
            assert call_kwargs['log_file_path'] == '/tmp/test.log'
            assert call_kwargs['log_format'] == 'detailed'
            assert call_kwargs['enable_colors'] is False
            assert call_kwargs['json_format'] is True

    def test_model_parameters(self, runner):
        """Test CLI with custom model parameters."""
        with patch('cli.cli_instance._initialize_agent') as mock_init:
            mock_init.return_value = False  # Quick exit

            runner.invoke(main, [
                '--model', 'custom_model',
                '--base-url', 'http://custom:11434',
                '--temperature', '0.5',
                '--use-json-subtypes-in-prompts-creation',
                'create-car'
            ])

            call_args = mock_init.call_args[0]
            assert call_args[0] == 'custom_model'  # model
            assert call_args[1] == 'http://custom:11434'  # base_url
            assert call_args[2] == 0.5  # temperature

            call_kwargs = mock_init.call_args[1]
            assert call_kwargs['use_json_subtypes_in_prompts_creation'] is True


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @patch('cli.CarAgent')
    def test_full_create_car_workflow(self, mock_car_agent_class, runner, tmp_path):
        """Test complete create-car workflow."""
        # Mock agent
        mock_agent = Mock()
        mock_agent.create_complete_car.return_value = {
            "car_configuration": {
                "vehicle_info": {"type": "sedan"},
                "engine": {"horsepower": "280", "fuelType": "gasoline"},
                "body": {"exterior": {"style": "sedan", "color": "blue"}},
                "electrical": {"main_system": {"voltage_system": "12V"}},
                "tires_and_wheels": {"tires": {"size": "225/60R16"}}
            },
            "metadata": {
                "created_by": "car_agent",
                "performance_summary": {"power_rating": "280 HP"}
            }
        }
        mock_car_agent_class.return_value = mock_agent

        output_file = tmp_path / "car_output.json"

        result = runner.invoke(main, [
            '--log-level', 'DEBUG',
            'create-car',
            '--vehicle-type', 'sedan',
            '--performance-level', 'standard',
            '--fuel-preference', 'gasoline',
            '--budget', 'medium',
            '--special-features', 'sunroof',
            '--output', str(output_file),
            '--format', 'summary'
        ])

        assert result.exit_code == 0
        assert "Creating sedan with single car agent" in result.output
        assert "280 HP" in result.output
        assert output_file.exists()

    def test_logging_setup_integration(self, runner):
        """Test that logging setup works correctly."""
        with patch('cli.setup_logging') as mock_setup, \
             patch('cli.cli_instance._initialize_agent') as mock_init:

            mock_init.return_value = False  # Quick exit

            result = runner.invoke(main, [
                '--log-level', 'DEBUG',
                '--log-to-file',
                'create-car'
            ])

            # Verify logging was set up
            mock_setup.assert_called_once()
            setup_kwargs = mock_setup.call_args[1]
            assert setup_kwargs['level'] == 'DEBUG'
            assert setup_kwargs['log_to_file'] is True