# Quick Start Guide 🚀

Get up and running with the Multi-Agent Storybook Generator in minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone or download the project
cd multi-agent-storybook-generator

# Run the setup script
python setup.py
```

The setup script will:
- ✅ Check Python version
- ✅ Install all dependencies
- ✅ Create configuration files
- ✅ Test the installation

### Option 2: Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Configuration

1. **Get an OpenAI API Key**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Create an account and get an API key
   - Add credits to your account

2. **Configure the API Key**
   ```bash
   # Edit .env file
   OPENAI_API_KEY=your_actual_api_key_here
   ```

## Usage

### Web Interface (Recommended)

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Command Line

```bash
# Generate a simple book
python main.py

# Run tests
python test_system.py --single
python test_system.py --all
```

## Example Book Generation

### Step 1: Choose Parameters
- **Title**: "The Brave Little Mouse"
- **Genre**: Adventure
- **Age Group**: 4-6 years
- **Theme**: Courage
- **Pages**: 8

### Step 2: Generate
Click "Generate Storybook" and watch the AI agents work!

### Step 3: Review Results
- 📖 Read the complete story
- 🎨 View illustrations
- 👥 Meet the characters
- 📊 Check consistency reports

## What You'll Get

✅ **Complete Storybook** with text and illustrations
✅ **Character Reference Sheet** for consistent designs
✅ **Consistency Reports** ensuring quality
✅ **Age-Appropriate Content** tailored to your target audience
✅ **Downloadable Data** in JSON format

## Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Make sure you've added your API key to the `.env` file
- Check that the key is valid and has credits

**"Module not found" errors**
- Run `pip install -r requirements.txt` again
- Make sure you're using Python 3.8+

**"Generation failed"**
- Check your internet connection
- Verify your OpenAI API key has sufficient credits
- Try with a simpler book (fewer pages)

### Getting Help

1. Check the full README.md for detailed documentation
2. Run the test suite: `python test_system.py --all`
3. Check the logs in the `logs/` directory

## Tips for Best Results

🎯 **Start Simple**: Begin with 6-8 pages for testing
🎨 **Be Specific**: Include detailed character names and settings
📚 **Age-Appropriate**: Choose the right age group for your content
🔄 **Iterate**: Generate multiple versions to find the best one
💾 **Save Results**: Download your book data for future reference

## Next Steps

- Explore different genres and themes
- Try different age groups
- Customize character descriptions
- Use the web interface for easy experimentation

Happy storybook creating! 📚✨