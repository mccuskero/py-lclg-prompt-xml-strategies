"""Command-line interface for the Single Agent Car Creation System."""

import argparse
import logging
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from single_agent_system import SingleAgentSystem


def setup_logging(log_level: str = "INFO"):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('car_creation.log')
        ]
    )


def run_interactive_mode(args):
    """Run the interactive session mode."""
    setup_logging(args.log_level)

    print(f"\nInitializing system with model: {args.model}")
    print(f"Connecting to OLLAMA at: {args.base_url}")
    print(f"Memory backend: {args.memory_backend}")
    if args.memory_backend == "postgres":
        print(f"PostgreSQL session: {args.memory_session_id}")
    print()

    system = SingleAgentSystem(
        model_name=args.model,
        base_url=args.base_url,
        temperature=args.temperature,
        enable_logging=not args.no_logging,
        log_llm_comms=args.log_llm_comms,
        memory_backend=args.memory_backend,
        memory_connection_string=args.memory_connection_string,
        memory_session_id=args.memory_session_id,
        max_memory_messages=args.max_memory_messages
    )

    system.interactive_session()


def run_single_request(args):
    """Run a single car creation request."""
    setup_logging(args.log_level)

    # Parse requirements from args or file
    if args.requirements_file:
        with open(args.requirements_file, 'r') as f:
            requirements = json.load(f)
    else:
        requirements = {
            "vehicle_type": args.vehicle_type,
            "performance_level": args.performance_level,
            "fuel_preference": args.fuel_preference,
            "budget": args.budget
        }

    print(f"\nInitializing system with model: {args.model}")
    print(f"Connecting to OLLAMA at: {args.base_url}")
    print(f"Memory backend: {args.memory_backend}")
    if args.memory_backend == "postgres":
        print(f"PostgreSQL session: {args.memory_session_id}")
    print(f"\nRequirements: {json.dumps(requirements, indent=2)}\n")

    system = SingleAgentSystem(
        model_name=args.model,
        base_url=args.base_url,
        temperature=args.temperature,
        enable_logging=not args.no_logging,
        log_llm_comms=args.log_llm_comms,
        memory_backend=args.memory_backend,
        memory_connection_string=args.memory_connection_string,
        memory_session_id=args.memory_session_id,
        max_memory_messages=args.max_memory_messages
    )

    result = system.run_single_request(requirements)

    # Display result
    print("\n" + "=" * 60)
    print("  Result")
    print("=" * 60)

    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)
    else:
        print("\n✅ Car configuration created successfully!")
        print(json.dumps(result, indent=2))

    # Save to output file if specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Result saved to: {args.output}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Single Agent Car Creation System with Interactive Looping",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run interactive session with in-memory storage (default)
  python cli.py interactive

  # Run interactive session with custom model
  python cli.py interactive --model llama3.2 --base-url http://localhost:11434

  # Run interactive session with PostgreSQL memory backend
  python cli.py interactive --memory-backend postgres \\
    --memory-connection-string "postgresql://user:pass@localhost:5432/car_agent" \\
    --memory-session-id "user123"

  # Run with custom memory window size
  python cli.py interactive --max-memory-messages 20

  # Create a single car with default settings
  python cli.py single --vehicle-type sedan --performance-level standard

  # Create a car from requirements file with PostgreSQL memory
  python cli.py single --requirements-file requirements.json --output result.json \\
    --memory-backend postgres \\
    --memory-connection-string "postgresql://user:pass@localhost:5432/car_agent"

  # Create a performance SUV
  python cli.py single --vehicle-type suv --performance-level performance --fuel-preference hybrid
        """
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set the logging level (default: INFO)"
    )

    parser.add_argument(
        "--no-logging",
        action="store_true",
        help="Disable logging"
    )

    parser.add_argument(
        "--log-llm-comms",
        action="store_true",
        help="Log full LLM communications (requests and responses) at DEBUG level"
    )

    parser.add_argument(
        "--memory-backend",
        default="memory",
        choices=["memory", "postgres"],
        help="Memory backend type: 'memory' for in-memory (default) or 'postgres' for PostgreSQL"
    )

    parser.add_argument(
        "--memory-connection-string",
        help="PostgreSQL connection string (e.g., postgresql://user:pass@localhost:5432/dbname). Required if --memory-backend=postgres"
    )

    parser.add_argument(
        "--memory-session-id",
        default="default",
        help="Session ID for memory isolation (useful for PostgreSQL multi-session support). Default: 'default'"
    )

    parser.add_argument(
        "--max-memory-messages",
        type=int,
        default=10,
        help="Maximum number of messages to keep in memory (sliding window). Default: 10"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Interactive mode subcommand
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="Run interactive session with context memory"
    )
    interactive_parser.add_argument(
        "--model",
        default="llama3.2",
        help="OLLAMA model name (default: llama3.2)"
    )
    interactive_parser.add_argument(
        "--base-url",
        default="http://localhost:11434",
        help="OLLAMA base URL (default: http://localhost:11434)"
    )
    interactive_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="LLM temperature (default: 0.1)"
    )

    # Single request subcommand
    single_parser = subparsers.add_parser(
        "single",
        help="Run a single car creation request"
    )
    single_parser.add_argument(
        "--model",
        default="llama3.2",
        help="OLLAMA model name (default: llama3.2)"
    )
    single_parser.add_argument(
        "--base-url",
        default="http://localhost:11434",
        help="OLLAMA base URL (default: http://localhost:11434)"
    )
    single_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="LLM temperature (default: 0.1)"
    )
    single_parser.add_argument(
        "--requirements-file",
        help="JSON file containing car requirements"
    )
    single_parser.add_argument(
        "--vehicle-type",
        default="sedan",
        choices=["sedan", "suv", "truck", "coupe", "hatchback", "convertible", "wagon"],
        help="Vehicle type (default: sedan)"
    )
    single_parser.add_argument(
        "--performance-level",
        default="standard",
        choices=["economy", "standard", "performance"],
        help="Performance level (default: standard)"
    )
    single_parser.add_argument(
        "--fuel-preference",
        default="gasoline",
        choices=["gasoline", "diesel", "electric", "hybrid"],
        help="Fuel preference (default: gasoline)"
    )
    single_parser.add_argument(
        "--budget",
        default="medium",
        choices=["low", "medium", "high"],
        help="Budget level (default: medium)"
    )
    single_parser.add_argument(
        "--output",
        help="Output file for the result JSON"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "interactive":
        run_interactive_mode(args)
    elif args.command == "single":
        run_single_request(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
