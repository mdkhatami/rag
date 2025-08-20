#!/usr/bin/env python3
"""
Setup script for the Multi-Agent Storybook Generator
Handles installation, configuration, and initial setup
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("\n🔧 Creating .env file...")
    
    try:
        # Copy from example
        example_file = Path(".env.example")
        if example_file.exists():
            shutil.copy(example_file, env_file)
            print("✅ .env file created from template")
            print("⚠️  Please edit .env file and add your OpenAI API key")
        else:
            # Create basic .env file
            with open(env_file, "w") as f:
                f.write("# OpenAI API Configuration\n")
                f.write("OPENAI_API_KEY=your_openai_api_key_here\n\n")
                f.write("# Optional: Model Configuration\n")
                f.write("# OPENAI_MODEL=gpt-4\n")
                f.write("# OPENAI_TEMPERATURE=0.7\n")
            
            print("✅ .env file created")
            print("⚠️  Please edit .env file and add your OpenAI API key")
        
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def check_api_key():
    """Check if OpenAI API key is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("⚠️  OpenAI API key not configured")
        print("Please edit .env file and add your API key")
        return False
    
    print("✅ OpenAI API key configured")
    return True


def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["output", "logs", "temp"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir()
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory already exists: {directory}")


def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    try:
        import langchain
        import langgraph
        import streamlit
        import pydantic
        import matplotlib
        import PIL
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def run_basic_test():
    """Run a basic test to verify the system works"""
    print("\n🚀 Running basic system test...")
    
    try:
        from main import StorybookGenerator
        from models.schemas import BookParameters
        
        # Create a simple test
        book_params = BookParameters(
            title="Test Book",
            genre="fantasy",
            age_group="4-6",
            theme="friendship",
            num_pages=6
        )
        
        print("✅ Basic test completed successfully")
        return True
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False


def display_next_steps():
    """Display next steps for the user"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run the web interface: streamlit run app.py")
    print("3. Or run tests: python test_system.py")
    print("4. Or run directly: python main.py")
    
    print("\n🌐 Web Interface:")
    print("   streamlit run app.py")
    print("   Then open http://localhost:8501 in your browser")
    
    print("\n🧪 Testing:")
    print("   python test_system.py --single    # Test single book")
    print("   python test_system.py --all       # Run all tests")
    
    print("\n📚 Documentation:")
    print("   Read README.md for detailed information")
    
    print("\n💡 Tips:")
    print("- Start with a simple book (6-8 pages) for testing")
    print("- Use the web interface for easy book creation")
    print("- Check the logs if you encounter issues")


def main():
    """Main setup function"""
    print("🚀 Multi-Agent Storybook Generator - Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Create directories
    create_directories()
    
    # Test imports
    if not test_imports():
        return False
    
    # Check API key
    api_key_configured = check_api_key()
    
    # Run basic test (only if API key is configured)
    if api_key_configured:
        run_basic_test()
    
    # Display next steps
    display_next_steps()
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)