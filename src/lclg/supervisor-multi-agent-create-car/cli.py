"""Command Line Interface for the Car Creation Multi-Agent System."""

import click
import json
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))
from agents.multi_agent_system import MultiAgentSystem


class CarCreationCLI:
    """Command line interface for car creation multi-agent system."""

    def __init__(self):
        self.system: Optional[MultiAgentSystem] = None

    def _initialize_system(
        self,
        model: str,
        base_url: str,
        temperature: float,
        execution_mode: str,
        enable_logging: bool,
        log_level: str = "INFO",
        use_json_subtypes_in_prompts_creation: bool = False
    ) -> bool:
        """Initialize the multi-agent system."""
        try:
            self.system = MultiAgentSystem(
                model=model,
                base_url=base_url,
                temperature=temperature,
                execution_mode=execution_mode,
                enable_logging=enable_logging,
                log_level=log_level,
                use_json_subtypes_in_prompts_creation=use_json_subtypes_in_prompts_creation
            )
            return True
        except Exception as e:
            click.echo(f"❌ Failed to initialize system: {str(e)}", err=True)
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

        if "car_json" not in data or data["car_json"] is None:
            return f"❌ No car data available. Status: {data.get('workflow_status', 'unknown')}"

        car = data["car_json"]
        system_info = data.get("system_info", {})

        summary = f"""🚗 Car Creation Summary
{'='*50}
Vehicle Info:
  VIN: {car.get('@vin', 'N/A')}
  Year: {car.get('@year', 'N/A')}
  Make: {car.get('@make', 'N/A')}
  Model: {car.get('@model', 'N/A')}

Components:
  🔧 Engine: {car.get('Engine', {}).get('displacement', 'N/A')} {car.get('Engine', {}).get('fuelType', 'N/A')} ({car.get('Engine', {}).get('horsepower', 'N/A')} HP)
  🚙 Body: {car.get('Body', {}).get('style', 'N/A')} - {car.get('Body', {}).get('color', 'N/A')} {car.get('Body', {}).get('material', 'N/A')}
  🛞 Tires: {car.get('Tire', {}).get('brand', 'N/A')} {car.get('Tire', {}).get('size', 'N/A')} ({car.get('Tire', {}).get('@season', 'N/A')})
  ⚡ Electrical: {car.get('Electrical', {}).get('@systemType', 'N/A')} ({car.get('Electrical', {}).get('batteryVoltage', 'N/A')})

Workflow:
  Status: {data.get('workflow_status', 'unknown')}
  Completed Agents: {', '.join(data.get('completed_agents', []))}
  Execution Time: {system_info.get('execution_time_seconds', 'N/A')}s
  Model Used: {system_info.get('model_used', 'N/A')}

Validation:
  Schema Compliance: {'✅' if data.get('validation_results', {}).get('schema_compliance', False) else '❌'}
  Errors: {len(data.get('errors', []))}
"""

        if data.get('errors'):
            summary += f"\n❌ Errors:\n"
            for error in data['errors']:
                summary += f"  - {error}\n"

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
cli_instance = CarCreationCLI()


@click.group()
@click.option("--model", default="llama3.2", help="Ollama model name")
@click.option("--base-url", default="http://localhost:11434", help="Ollama server URL")
@click.option("--temperature", default=0.1, type=float, help="LLM temperature")
@click.option("--execution-mode", default="hybrid", type=click.Choice(["hybrid", "sequential", "parallel"]), help="Workflow execution mode")
@click.option("--enable-logging/--disable-logging", default=True, help="Enable system logging")
@click.option("--log-level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), help="Set logging level")
@click.option("--use-json-subtypes-in-prompts-creation/--use-markdown-prompts", default=False, help="Use JSON schema subtypes in prompt creation instead of markdown")
@click.pass_context
def main(ctx, model, base_url, temperature, execution_mode, enable_logging, log_level, use_json_subtypes_in_prompts_creation):
    """Car Creation Multi-Agent System CLI

    Create complete car JSON descriptions using specialized AI agents.
    """
    ctx.ensure_object(dict)
    ctx.obj['model'] = model
    ctx.obj['base_url'] = base_url
    ctx.obj['temperature'] = temperature
    ctx.obj['execution_mode'] = execution_mode
    ctx.obj['enable_logging'] = enable_logging
    ctx.obj['log_level'] = log_level
    ctx.obj['use_json_subtypes_in_prompts_creation'] = use_json_subtypes_in_prompts_creation


@main.command()
@click.option("--vin", required=True, help="Vehicle Identification Number")
@click.option("--year", required=True, help="Car year")
@click.option("--make", required=True, help="Car make")
@click.option("--model-name", required=True, help="Car model")
@click.option("--output", "-o", help="Output file path")
@click.option("--format", "output_format", default="summary", type=click.Choice(["json", "compact", "summary"]), help="Output format")
@click.option("--execution-mode", type=click.Choice(["hybrid", "sequential", "parallel"]), help="Override execution mode")
@click.pass_context
def create_car(ctx, vin, year, make, model_name, output, output_format, execution_mode):
    """Create a complete car JSON description."""

    # Initialize system
    if not cli_instance._initialize_system(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        execution_mode or ctx.obj['execution_mode'], ctx.obj['enable_logging'],
        ctx.obj['log_level'], ctx.obj['use_json_subtypes_in_prompts_creation']
    ):
        sys.exit(1)

    click.echo(f"🚗 Creating car: {year} {make} {model_name}")
    click.echo(f"📋 VIN: {vin}")
    click.echo(f"⚙️  Mode: {execution_mode or ctx.obj['execution_mode']}")
    click.echo(f"🤖 Model: {ctx.obj['model']}")
    click.echo("=" * 50)

    async def create_car_async():
        return await cli_instance.system.create_car(
            vin=vin,
            year=year,
            make=make,
            model=model_name,
            execution_mode=execution_mode
        )

    try:
        # Run async function
        result = asyncio.run(create_car_async())

        # Display result
        formatted_output = cli_instance._format_output(result, output_format)
        click.echo(formatted_output)

        # Save to file if specified
        if output:
            cli_instance._save_output(result, output, "json")

        # Exit with appropriate code
        if "error" in result or result.get("workflow_status") == "error":
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Car creation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--cars-file", required=True, help="JSON file with car specifications")
@click.option("--output-dir", "-o", default="./batch_output", help="Output directory")
@click.option("--max-concurrent", default=3, type=int, help="Maximum concurrent executions")
@click.option("--execution-mode", type=click.Choice(["hybrid", "sequential", "parallel"]), help="Override execution mode")
@click.pass_context
def batch_create(ctx, cars_file, output_dir, max_concurrent, execution_mode):
    """Create multiple cars from a JSON specification file."""

    # Load car specifications
    try:
        with open(cars_file, 'r') as f:
            car_specs = json.load(f)

        if not isinstance(car_specs, list):
            click.echo("❌ Cars file must contain a JSON array of car specifications", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Failed to load cars file: {str(e)}", err=True)
        sys.exit(1)

    # Initialize system
    if not cli_instance._initialize_system(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        execution_mode or ctx.obj['execution_mode'], ctx.obj['enable_logging'],
        ctx.obj['log_level'], ctx.obj['use_json_subtypes_in_prompts_creation']
    ):
        sys.exit(1)

    click.echo(f"🚗 Batch creating {len(car_specs)} cars")
    click.echo(f"📁 Output directory: {output_dir}")
    click.echo(f"🔄 Max concurrent: {max_concurrent}")
    click.echo("=" * 50)

    async def batch_create_async():
        return await cli_instance.system.batch_create_cars(
            car_specifications=car_specs,
            execution_mode=execution_mode,
            max_concurrent=max_concurrent
        )

    try:
        # Run batch creation
        results = asyncio.run(batch_create_async())

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save individual results
        successful = 0
        failed = 0

        for i, result in enumerate(results):
            spec = car_specs[i] if i < len(car_specs) else {"index": i}

            if "error" not in result:
                successful += 1
                status = "✅"
            else:
                failed += 1
                status = "❌"

            # Generate filename
            vin = spec.get("vin", f"car_{i}")
            filename = f"{vin}.json"

            # Save result
            result_file = output_path / filename
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)

            click.echo(f"{status} {spec.get('year', '')} {spec.get('make', '')} {spec.get('model', '')} -> {filename}")

        # Save batch summary
        summary = {
            "batch_summary": {
                "total": len(car_specs),
                "successful": successful,
                "failed": failed,
                "timestamp": datetime.now().isoformat()
            },
            "results": results
        }

        with open(output_path / "batch_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        click.echo("=" * 50)
        click.echo(f"📊 Batch Summary: {successful}/{len(car_specs)} successful")
        click.echo(f"📁 Results saved to: {output_path}")

        if failed > 0:
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Batch creation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.pass_context
def validate_system(ctx):
    """Validate system components and connectivity."""

    # Initialize system
    if not cli_instance._initialize_system(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        ctx.obj['execution_mode'], ctx.obj['enable_logging'],
        ctx.obj['use_json_subtypes_in_prompts_creation']
    ):
        sys.exit(1)

    click.echo("🔍 Validating system components...")
    click.echo("=" * 50)

    async def validate_async():
        return await cli_instance.system.validate_system()

    try:
        validation_results = asyncio.run(validate_async())

        # Display validation results
        overall_status = validation_results["overall_status"]

        if overall_status == "ready":
            click.echo("✅ System Status: READY")
        elif overall_status == "agents_ready_ollama_issue":
            click.echo("⚠️  System Status: AGENTS READY (Ollama connectivity issue)")
        else:
            click.echo("❌ System Status: NOT READY")

        # Ollama status
        ollama_info = validation_results["components"]["ollama"]
        if ollama_info["status"] == "connected":
            click.echo(f"✅ Ollama: Connected ({ollama_info['base_url']})")
            click.echo(f"🤖 Model: {ollama_info['model']} ({'available' if ollama_info.get('model_available') else 'not available'})")
            if ollama_info.get('available_models'):
                click.echo(f"📋 Available models: {', '.join(ollama_info['available_models'])}")
        else:
            click.echo(f"❌ Ollama: {ollama_info['status']} ({ollama_info.get('error', 'Unknown error')})")

        # Agent status
        agents_info = validation_results["components"]["agents"]
        click.echo("\n🤖 Agent Status:")
        for agent_name, agent_info in agents_info.items():
            status_icon = "✅" if agent_info["status"] == "ready" else "❌"
            click.echo(f"  {status_icon} {agent_name}: {agent_info['status']}")

        # Exit with appropriate code
        if overall_status not in ["ready", "agents_ready_ollama_issue"]:
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ System validation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--agent", type=click.Choice(["engine", "body", "tire", "electrical", "supervisor"]), required=True, help="Agent to test")
@click.option("--output", "-o", help="Output file path")
@click.pass_context
def test_agent(ctx, agent, output):
    """Test an individual agent with sample data."""

    # Initialize system
    if not cli_instance._initialize_system(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        ctx.obj['execution_mode'], ctx.obj['enable_logging'],
        ctx.obj['use_json_subtypes_in_prompts_creation']
    ):
        sys.exit(1)

    click.echo(f"🧪 Testing {agent} agent...")
    click.echo("=" * 50)

    async def test_async():
        return await cli_instance.system.test_individual_agent(agent)

    try:
        test_result = asyncio.run(test_async())

        # Display test results
        if test_result["test_status"] == "success":
            click.echo(f"✅ {agent} agent test: PASSED")
        else:
            click.echo(f"❌ {agent} agent test: FAILED")
            click.echo(f"Error: {test_result.get('error', 'Unknown error')}")

        # Show formatted result
        formatted_output = cli_instance._format_output(test_result, "json")
        click.echo("\n📄 Test Result:")
        click.echo(formatted_output)

        # Save to file if specified
        if output:
            cli_instance._save_output(test_result, output, "json")

        # Exit with appropriate code
        if test_result["test_status"] != "success":
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Agent test failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.pass_context
def list_models(ctx):
    """List available Ollama models."""

    # Initialize system
    if not cli_instance._initialize_system(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        ctx.obj['execution_mode'], ctx.obj['enable_logging'],
        ctx.obj['use_json_subtypes_in_prompts_creation']
    ):
        sys.exit(1)

    try:
        models = cli_instance.system.get_available_models()

        if models:
            click.echo("🤖 Available Ollama Models:")
            click.echo("=" * 50)
            for model in models:
                icon = "👉" if model == ctx.obj['model'] else "  "
                click.echo(f"{icon} {model}")
        else:
            click.echo("❌ No models available or unable to connect to Ollama")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Failed to list models: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.pass_context
def system_status(ctx):
    """Show detailed system status and configuration."""

    # Initialize system
    if not cli_instance._initialize_system(
        ctx.obj['model'], ctx.obj['base_url'], ctx.obj['temperature'],
        ctx.obj['execution_mode'], ctx.obj['enable_logging'],
        ctx.obj['use_json_subtypes_in_prompts_creation']
    ):
        sys.exit(1)

    try:
        status = cli_instance.system.get_system_status()

        click.echo("📊 System Status & Configuration")
        click.echo("=" * 50)

        formatted_output = cli_instance._format_output(status, "json")
        click.echo(formatted_output)

    except Exception as e:
        click.echo(f"❌ Failed to get system status: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()