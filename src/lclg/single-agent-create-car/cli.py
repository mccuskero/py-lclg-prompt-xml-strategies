"""Command Line Interface for the Single-Agent Car Creation System."""

import click
import json
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))
from agents.car_agent import CarAgent
from utils.logging_config import LoggingConfig, setup_logging


class SingleAgentCarCLI:
    """Command line interface for single-agent car creation system."""

    def __init__(self):
        self.agent: Optional[CarAgent] = None

    def _initialize_agent(
        self,
        model: str,
        base_url: str,
        temperature: float,
        use_json_subtypes_in_prompts_creation: bool = False,
        enable_logging: bool = True
    ) -> bool:
        """Initialize the car agent."""
        try:
            self.agent = CarAgent(
                model_name=model,
                base_url=base_url,
                temperature=temperature,
                use_json_subtypes_in_prompts_creation=use_json_subtypes_in_prompts_creation,
                enable_logging=enable_logging
            )
            return True
        except Exception as e:
            click.echo(f"❌ Failed to initialize car agent: {str(e)}", err=True)
            return False

    def _format_output(self, data: Dict[str, Any], format_type: str) -> str:
        """Format output data according to specified format."""
        if format_type == "json":
            return json.dumps(data, indent=2)
        elif format_type == "compact":
            return json.dumps(data)
        elif format_type == "summary":
            return self._create_summary(data)
        else:
            return json.dumps(data, indent=2)

    def _create_summary(self, data: Dict[str, Any]) -> str:
        """Create a human-readable summary of the car creation result."""
        if "error" in data:
            return f"❌ Error: {data['error']}"

        car_config = data.get("car_configuration", {})
        metadata = data.get("metadata", {})

        if not car_config:
            return "❌ No car configuration data available."

        vehicle_info = car_config.get("vehicle_info", {})
        engine = car_config.get("engine", {})
        body = car_config.get("body", {})
        electrical = car_config.get("electrical", {})
        tires = car_config.get("tires_and_wheels", {})

        summary = f"""🚗 Single-Agent Car Creation Summary
{'='*60}
Vehicle Info:
  Type: {vehicle_info.get('type', 'N/A')}
  Performance Level: {vehicle_info.get('performance_level', 'N/A')}
  Fuel Preference: {vehicle_info.get('fuel_preference', 'N/A')}
  Budget: {vehicle_info.get('budget', 'N/A')}

Components:
  🔧 Engine: {engine.get('fuelType', 'N/A')} ({engine.get('horsepower', 'N/A')} HP, {engine.get('displacement', 'N/A')})
  🚙 Body: {body.get('exterior', {}).get('style', 'N/A')} - {body.get('exterior', {}).get('color', 'N/A')}
  ⚡ Electrical: {electrical.get('main_system', {}).get('voltage_system', 'N/A')} system
  🛞 Tires: {tires.get('tires', {}).get('size', 'N/A')} ({tires.get('tires', {}).get('type', 'N/A')})

Performance Summary:
  Power Rating: {metadata.get('performance_summary', {}).get('power_rating', 'N/A')}
  Performance Category: {metadata.get('performance_summary', {}).get('performance_category', 'N/A')}
  Component Compatibility: {metadata.get('estimated_compatibility', 'N/A')}

Creation Info:
  Created By: {metadata.get('created_by', 'N/A')}
  Method: {metadata.get('creation_method', 'N/A')}
  Component Count: {metadata.get('component_count', 'N/A')}
"""

        validation = data.get("validation", {})
        if validation:
            summary += f"\nValidation:\n  Status: {validation.get('status', 'N/A')}\n"

        return summary

    def _save_output(self, data: Dict[str, Any], output_file: str, format_type: str) -> bool:
        """Save output data to file."""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            formatted_data = self._format_output(data, format_type)

            with open(output_path, 'w') as f:
                f.write(formatted_data)

            click.echo(f"✅ Output saved to: {output_path}")
            return True

        except Exception as e:
            click.echo(f"❌ Failed to save output: {str(e)}", err=True)
            return False


# Initialize CLI instance
cli_instance = SingleAgentCarCLI()


@click.group()
@click.option("--model", default="llama3.2", help="Ollama model name")
@click.option("--base-url", default="http://localhost:11434", help="Ollama server URL")
@click.option("--temperature", default=0.1, type=float, help="LLM temperature")
@click.option("--use-json-subtypes-in-prompts-creation/--use-markdown-prompts", default=False, help="Use JSON schema subtypes in prompt creation instead of markdown")
@click.option("--log-level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]), help="Set logging level")
@click.option("--log-to-file/--no-log-to-file", default=False, help="Enable file logging")
@click.option("--log-file", help="Custom log file path")
@click.option("--log-format", default="standard", type=click.Choice(["standard", "detailed"]), help="Log format style")
@click.option("--disable-colors/--enable-colors", default=False, help="Disable colored console output")
@click.option("--json-logs/--text-logs", default=False, help="Use JSON format for file logs")
@click.pass_context
def main(ctx, model, base_url, temperature, use_json_subtypes_in_prompts_creation,
         log_level, log_to_file, log_file, log_format, disable_colors, json_logs):
    """Single-Agent Car Creation System CLI

    Create complete car configurations using a single AI agent with all car creation tools.
    """
    ctx.ensure_object(dict)
    ctx.obj['model'] = model
    ctx.obj['base_url'] = base_url
    ctx.obj['temperature'] = temperature
    ctx.obj['use_json_subtypes_in_prompts_creation'] = use_json_subtypes_in_prompts_creation

    # Setup logging based on CLI options
    try:
        setup_logging(
            level=log_level,
            log_to_console=True,
            log_to_file=log_to_file,
            log_file_path=log_file,
            log_format=log_format,
            enable_colors=not disable_colors,
            json_format=json_logs
        )

        import logging
        logger = logging.getLogger("cli")
        logger.info(
            f"Starting Single-Agent Car Creation CLI",
            extra={
                "cli_model": model,
                "cli_base_url": base_url,
                "cli_log_level": log_level,
                "cli_log_to_file": log_to_file
            }
        )
    except Exception as e:
        click.echo(f"❌ Failed to setup logging: {str(e)}", err=True)

    # Store logging settings in context
    ctx.obj['logging_enabled'] = True
    ctx.obj['log_level'] = log_level


@main.command()
@click.option("--vehicle-type", default="sedan", help="Type of vehicle (sedan, suv, truck, coupe, etc.)")
@click.option("--performance-level", default="standard", help="Performance level (economy, standard, performance, sport)")
@click.option("--fuel-preference", default="gasoline", help="Fuel preference (gasoline, diesel, electric, hybrid)")
@click.option("--budget", default="medium", help="Budget level (low, medium, high, luxury)")
@click.option("--special-features", multiple=True, help="Special features (can be used multiple times)")
@click.option("--output", "-o", help="Output file path")
@click.option("--format", "output_format", default="summary", type=click.Choice(["json", "compact", "summary"]), help="Output format")
@click.pass_context
def create_car(ctx, vehicle_type, performance_level, fuel_preference, budget, special_features, output, output_format):
    """Create a complete car configuration using the single agent."""
    import logging
    logger = logging.getLogger("cli.create_car")

    logger.info(
        f"Car creation command started",
        extra={
            "request_vehicle_type": vehicle_type,
            "request_performance_level": performance_level,
            "request_fuel_preference": fuel_preference,
            "request_budget": budget,
            "request_special_features": list(special_features),
            "request_output_format": output_format
        }
    )

    # Initialize agent
    if not cli_instance._initialize_agent(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        ctx.obj['use_json_subtypes_in_prompts_creation'],
        ctx.obj.get('logging_enabled', True)
    ):
        logger.error("Failed to initialize car agent")
        sys.exit(1)

    click.echo(f"🚗 Creating {vehicle_type} with single car agent")
    click.echo(f"🎯 Performance: {performance_level}, Fuel: {fuel_preference}, Budget: {budget}")
    if special_features:
        click.echo(f"✨ Special Features: {', '.join(special_features)}")
    click.echo(f"🤖 Model: {ctx.obj['model']}")
    click.echo("=" * 60)

    try:
        # Build requirements
        requirements = {
            "vehicle_type": vehicle_type,
            "performance_level": performance_level,
            "fuel_preference": fuel_preference,
            "budget": budget,
            "special_features": list(special_features)
        }

        logger.debug("Starting car creation with agent", extra={"requirements": requirements})

        # Create car using the agent
        result = cli_instance.agent.create_complete_car(requirements)

        # Display result
        formatted_output = cli_instance._format_output(result, output_format)
        click.echo(formatted_output)

        # Save to file if specified
        if output:
            logger.info(f"Saving output to file: {output}", extra={"output_file": output})
            cli_instance._save_output(result, output, "json")

        # Log completion
        success = "error" not in result
        logger.info(
            f"Car creation command completed",
            extra={
                "success": success,
                "has_output_file": output is not None,
                "output_format": output_format
            }
        )

        # Exit with appropriate code
        if not success:
            logger.warning("Car creation completed with errors")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Car creation command failed: {str(e)}", extra={"error_type": type(e).__name__})
        click.echo(f"❌ Car creation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--requirements-file", required=True, help="JSON file with car requirements")
@click.option("--output-dir", "-o", default="./batch_output", help="Output directory")
@click.pass_context
def batch_create(ctx, requirements_file, output_dir):
    """Create multiple cars from a requirements file."""

    # Load car requirements
    try:
        with open(requirements_file, 'r') as f:
            car_requirements = json.load(f)

        if not isinstance(car_requirements, list):
            click.echo("❌ Requirements file must contain a JSON array of car requirements", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Failed to load requirements file: {str(e)}", err=True)
        sys.exit(1)

    # Initialize agent
    if not cli_instance._initialize_agent(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        ctx.obj['use_json_subtypes_in_prompts_creation']
    ):
        sys.exit(1)

    click.echo(f"🚗 Batch creating {len(car_requirements)} cars")
    click.echo(f"📁 Output directory: {output_dir}")
    click.echo("=" * 60)

    try:
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Process each requirement
        successful = 0
        failed = 0
        results = []

        for i, requirements in enumerate(car_requirements):
            click.echo(f"🔄 Processing car {i+1}/{len(car_requirements)}...")

            try:
                result = cli_instance.agent.create_complete_car(requirements)
                results.append(result)

                if "error" not in result:
                    successful += 1
                    status = "✅"
                else:
                    failed += 1
                    status = "❌"

                # Generate filename
                vehicle_type = requirements.get("vehicle_type", "car")
                performance = requirements.get("performance_level", "standard")
                filename = f"{vehicle_type}_{performance}_{i}.json"

                # Save result
                result_file = output_path / filename
                with open(result_file, 'w') as f:
                    json.dump(result, f, indent=2)

                click.echo(f"{status} {requirements.get('vehicle_type', 'car')} ({requirements.get('performance_level', 'standard')}) -> {filename}")

            except Exception as e:
                failed += 1
                error_result = {"error": f"Processing failed: {str(e)}", "requirements": requirements}
                results.append(error_result)

                filename = f"error_{i}.json"
                result_file = output_path / filename
                with open(result_file, 'w') as f:
                    json.dump(error_result, f, indent=2)

                click.echo(f"❌ Error processing car {i+1} -> {filename}")

        # Save batch summary
        summary = {
            "batch_summary": {
                "total": len(car_requirements),
                "successful": successful,
                "failed": failed,
                "timestamp": datetime.now().isoformat()
            },
            "results": results
        }

        with open(output_path / "batch_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        click.echo("=" * 60)
        click.echo(f"📊 Batch Summary: {successful}/{len(car_requirements)} successful")
        click.echo(f"📁 Results saved to: {output_path}")

        if failed > 0:
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Batch creation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.pass_context
def validate_agent(ctx):
    """Validate agent components and connectivity."""

    # Initialize agent
    if not cli_instance._initialize_agent(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        ctx.obj['use_json_subtypes_in_prompts_creation']
    ):
        sys.exit(1)

    click.echo("🔍 Validating single-agent system...")
    click.echo("=" * 60)

    try:
        # Get agent info
        agent_info = cli_instance.agent.get_agent_info()

        click.echo("✅ Agent Status: READY")
        click.echo(f"🤖 Agent Name: {agent_info['name']}")
        click.echo(f"📝 Agent Type: {agent_info['type']}")
        click.echo(f"🛠️  Available Tools: {len(agent_info['tools'])}")
        click.echo(f"🧠 LLM Type: {agent_info['llm_type']}")
        click.echo(f"🎯 Model: {agent_info['model']}")

        # List tools by category
        tool_categories = cli_instance.agent.get_tool_categories()
        click.echo("\n🛠️  Tool Categories:")
        for category, tools in tool_categories.items():
            click.echo(f"  {category.title()}: {', '.join(tools)}")

        # Test basic LLM connectivity
        click.echo("\n🔌 Testing LLM connectivity...")
        test_message = cli_instance.agent.create_component_json({
            "vehicle_type": "test",
            "performance_level": "standard",
            "fuel_preference": "gasoline",
            "budget": "medium"
        })

        if "error" not in test_message:
            click.echo("✅ LLM connectivity: SUCCESS")
        else:
            click.echo(f"❌ LLM connectivity: FAILED - {test_message.get('error', 'Unknown error')}")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Agent validation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--tool-category", type=click.Choice(["engine", "body", "electrical", "tires", "all"]), default="all", help="Tool category to test")
@click.option("--output", "-o", help="Output file path")
@click.pass_context
def test_tools(ctx, tool_category, output):
    """Test agent tools with sample data."""

    # Initialize agent
    if not cli_instance._initialize_agent(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        ctx.obj['use_json_subtypes_in_prompts_creation']
    ):
        sys.exit(1)

    click.echo(f"🧪 Testing {tool_category} tools...")
    click.echo("=" * 60)

    try:
        # Define test requirements for different categories
        test_requirements = {
            "engine": {"vehicle_type": "sedan", "performance_level": "standard", "fuel_preference": "gasoline"},
            "body": {"vehicle_type": "coupe", "performance_level": "performance", "budget": "high"},
            "electrical": {"vehicle_type": "electric", "performance_level": "standard", "fuel_preference": "electric"},
            "tires": {"vehicle_type": "suv", "performance_level": "sport", "budget": "medium"}
        }

        if tool_category == "all":
            # Test complete car creation
            requirements = {
                "vehicle_type": "sedan",
                "performance_level": "standard",
                "fuel_preference": "gasoline",
                "budget": "medium",
                "special_features": ["test_mode"]
            }
            test_result = cli_instance.agent.create_complete_car(requirements)
        else:
            # Test specific category
            requirements = test_requirements.get(tool_category, test_requirements["engine"])
            test_result = cli_instance.agent.create_component_json(requirements)

        # Display test results
        if "error" not in test_result:
            click.echo(f"✅ {tool_category} tools test: PASSED")
        else:
            click.echo(f"❌ {tool_category} tools test: FAILED")
            click.echo(f"Error: {test_result.get('error', 'Unknown error')}")

        # Show formatted result
        formatted_output = cli_instance._format_output(test_result, "json")
        click.echo("\n📄 Test Result:")
        click.echo(formatted_output)

        # Save to file if specified
        if output:
            cli_instance._save_output(test_result, output, "json")

        # Exit with appropriate code
        if "error" in test_result:
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Tool test failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.pass_context
def agent_info(ctx):
    """Show detailed agent information and capabilities."""

    # Initialize agent
    if not cli_instance._initialize_agent(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        ctx.obj['use_json_subtypes_in_prompts_creation']
    ):
        sys.exit(1)

    try:
        agent_info = cli_instance.agent.get_agent_info()
        tool_categories = cli_instance.agent.get_tool_categories()

        status_info = {
            "agent_info": agent_info,
            "tool_categories": tool_categories,
            "system_config": {
                "model": ctx.obj['model'],
                "base_url": ctx.obj['base_url'],
                "temperature": ctx.obj['temperature'],
                "json_prompts": ctx.obj['use_json_subtypes_in_prompts_creation']
            }
        }

        click.echo("📊 Single-Agent System Information")
        click.echo("=" * 60)

        formatted_output = cli_instance._format_output(status_info, "json")
        click.echo(formatted_output)

    except Exception as e:
        click.echo(f"❌ Failed to get agent info: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()