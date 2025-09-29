"""UV-based setup script for the multi-agent system."""

import os
import subprocess
import sys

def check_uv_installed():
    """Check if uv is installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv is not installed")
        print("Please install uv first:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def install_dependencies():
    """Install dependencies with uv."""
    print("\n📦 Installing dependencies with uv...")
    try:
        subprocess.check_call(["uv", "sync"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def install_dev_dependencies():
    """Install development dependencies with uv."""
    print("\n🔧 Installing development dependencies...")
    try:
        subprocess.check_call(["uv", "sync", "--dev"])
        print("✅ Development dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dev dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    if not os.path.exists(".env"):
        print("\n🔧 Creating .env file...")
        try:
            with open(".env", "w") as f:
                f.write("# OpenAI API Key\n")
                f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            print("✅ .env file created")
            print("   Please edit .env and add your OpenAI API key")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("✅ .env file already exists")
        return True

def check_api_key():
    """Check if API key is set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("⚠️  OpenAI API key not set")
        print("   Please edit .env file and add your OpenAI API key")
        return False
    print("✅ OpenAI API key is set")
    return True

def run_tests():
    """Run system tests with uv."""
    print("\n🧪 Running system tests...")
    try:
        subprocess.check_call(["uv", "run", "python", "test_system.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Multi-Agent System UV Setup")
    print("=" * 40)
    
    # Check if uv is installed
    if not check_uv_installed():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Install dev dependencies
    if not install_dev_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Check API key
    api_key_set = check_api_key()
    
    print("\n" + "=" * 40)
    print("📋 Setup Summary:")
    print("   ✅ uv package manager")
    print("   ✅ Dependencies installed")
    print("   ✅ Development dependencies installed")
    print("   ✅ Environment file created")
    print(f"   {'✅' if api_key_set else '⚠️ '} API key {'configured' if api_key_set else 'needs configuration'}")
    
    if api_key_set:
        print("\n🎉 Setup complete! You can now run:")
        print("   uv run python src/main.py          # Interactive session")
        print("   uv run python src/main.py examples # Example queries")
        print("   uv run python test_system.py       # Run tests")
        print("   uv run python examples.py          # Run examples")
        print("\n🔧 Development commands:")
        print("   uv run pytest                      # Run tests")
        print("   uv run ruff check .                # Lint code")
        print("   uv run black .                     # Format code")
    else:
        print("\n⚠️  Setup incomplete. Please configure your API key and run again.")
    
    return True

if __name__ == "__main__":
    main()
