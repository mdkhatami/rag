import base64
import io
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def create_simple_illustration(description: str, mood: str, size: tuple = (800, 600)) -> str:
    """Create a simple placeholder illustration and return as base64 string"""
    try:
        # Create a new image
        img = Image.new('RGB', size, color=get_mood_color(mood))
        draw = ImageDraw.Draw(img)
        
        # Add some simple shapes based on mood
        if "happy" in mood.lower():
            # Draw a sun
            draw.ellipse([650, 50, 750, 150], fill='yellow', outline='orange', width=3)
            
            # Draw some clouds
            for i in range(3):
                x = 100 + i * 200
                draw.ellipse([x, 100, x + 100, 150], fill='white', outline='lightgray', width=2)
        
        elif "sad" in mood.lower():
            # Draw rain clouds
            for i in range(2):
                x = 150 + i * 300
                draw.ellipse([x, 80, x + 120, 140], fill='gray', outline='darkgray', width=3)
                # Draw rain drops
                for j in range(5):
                    drop_x = x + 20 + j * 20
                    drop_y = 150 + j * 10
                    draw.line([drop_x, drop_y, drop_x, drop_y + 20], fill='blue', width=2)
        
        elif "excited" in mood.lower():
            # Draw stars
            for i in range(8):
                x = 100 + i * 80
                y = 100 + (i % 3) * 50
                draw_star(draw, x, y, 20, 'yellow')
        
        # Add ground
        draw.rectangle([0, 500, size[0], size[1]], fill='green', outline='darkgreen', width=2)
        
        # Add title
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((size[0]//2 - 100, 50), f"Mood: {mood.title()}", fill='black', font=font)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()
        
    except Exception as e:
        print(f"Error creating illustration: {e}")
        return ""


def draw_star(draw, x: int, y: int, size: int, color: str):
    """Draw a simple star shape"""
    points = []
    for i in range(10):
        angle = i * 36 * 3.14159 / 180
        if i % 2 == 0:
            radius = size
        else:
            radius = size // 2
        points.append((x + radius * (angle * 0.5), y + radius * (angle * 0.5)))
    
    # Draw the star
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=color, width=2)


def get_mood_color(mood: str) -> str:
    """Get background color based on mood"""
    mood_colors = {
        "happy": "#FFE5B4",      # Light orange
        "sad": "#E6F3FF",        # Light blue
        "excited": "#FFE5E5",    # Light red
        "peaceful": "#E8F5E8",   # Light green
        "mysterious": "#F0E6FF", # Light purple
        "adventurous": "#FFF2CC", # Light yellow
        "scared": "#FFE6E6",     # Very light red
        "curious": "#E6F7FF",    # Very light blue
        "brave": "#FFF8DC",      # Cornsilk
        "friendly": "#F0FFF0"    # Honeydew
    }
    
    mood_lower = mood.lower()
    for key, color in mood_colors.items():
        if key in mood_lower:
            return color
    
    return "#FFFFFF"  # Default white


def validate_book_parameters(params: Dict[str, Any]) -> List[str]:
    """Validate book parameters and return list of errors"""
    errors = []
    
    if not params.get('title', '').strip():
        errors.append("Book title is required")
    
    if not params.get('genre'):
        errors.append("Genre is required")
    
    if not params.get('age_group'):
        errors.append("Age group is required")
    
    if not params.get('theme'):
        errors.append("Theme is required")
    
    num_pages = params.get('num_pages', 0)
    if num_pages < 6 or num_pages > 20:
        errors.append("Number of pages must be between 6 and 20")
    
    return errors


def format_text_for_age_group(text: str, age_group: str) -> str:
    """Format text to be appropriate for the target age group"""
    if age_group == "2-4":
        # Very simple, repetitive patterns
        sentences = text.split('.')
        simple_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Keep sentences very short
                words = sentence.split()
                if len(words) > 8:
                    # Split long sentences
                    mid = len(words) // 2
                    simple_sentences.append(' '.join(words[:mid]) + '.')
                    simple_sentences.append(' '.join(words[mid:]) + '.')
                else:
                    simple_sentences.append(sentence + '.')
        return ' '.join(simple_sentences)
    
    elif age_group == "4-6":
        # Simple but varied sentences
        return text
    
    elif age_group == "6-8":
        # Can handle more complex sentences
        return text
    
    elif age_group == "8-10":
        # Can handle sophisticated language
        return text
    
    return text


def create_character_summary(characters: List[Dict[str, Any]]) -> str:
    """Create a summary of all characters"""
    if not characters:
        return "No characters defined."
    
    summary = f"Total Characters: {len(characters)}\n\n"
    
    for char in characters:
        summary += f"**{char['name']}** ({char['role']})\n"
        summary += f"- {char['description']}\n"
        summary += f"- Personality: {char['personality']}\n"
        summary += f"- Appearance: {char['appearance']}\n\n"
    
    return summary


def create_story_summary(pages: List[Dict[str, Any]]) -> str:
    """Create a summary of the story"""
    if not pages:
        return "No pages generated yet."
    
    summary = f"Story Summary ({len(pages)} pages):\n\n"
    
    for page in pages:
        summary += f"**Page {page['page_number']}:** {page['text'][:100]}...\n"
        summary += f"Characters: {', '.join(page['characters_present'])}\n"
        summary += f"Mood: {page['mood']}\n\n"
    
    return summary


def calculate_reading_level(text: str) -> str:
    """Calculate approximate reading level of text"""
    words = text.split()
    sentences = text.split('.')
    
    if not sentences or not words:
        return "Unknown"
    
    avg_sentence_length = len(words) / len(sentences)
    
    if avg_sentence_length <= 5:
        return "Early Reader (K-1)"
    elif avg_sentence_length <= 8:
        return "Early Elementary (1-2)"
    elif avg_sentence_length <= 12:
        return "Elementary (3-4)"
    elif avg_sentence_length <= 15:
        return "Upper Elementary (5-6)"
    else:
        return "Middle School (7+)"


def check_content_appropriateness(text: str, age_group: str) -> Dict[str, Any]:
    """Check if content is appropriate for the age group"""
    issues = []
    suggestions = []
    
    # Check for complex words
    complex_words = ["nevertheless", "consequently", "furthermore", "subsequently"]
    found_complex = [word for word in complex_words if word.lower() in text.lower()]
    
    if found_complex and age_group in ["2-4", "4-6"]:
        issues.append(f"Complex words found: {', '.join(found_complex)}")
        suggestions.append("Consider using simpler alternatives")
    
    # Check sentence length
    sentences = text.split('.')
    long_sentences = [s for s in sentences if len(s.split()) > 15]
    
    if long_sentences and age_group in ["2-4", "4-6"]:
        issues.append(f"Found {len(long_sentences)} long sentences")
        suggestions.append("Consider breaking into shorter sentences")
    
    # Check for potentially scary content
    scary_words = ["monster", "ghost", "dark", "scary", "frightened"]
    found_scary = [word for word in scary_words if word.lower() in text.lower()]
    
    if found_scary and age_group == "2-4":
        issues.append(f"Potentially scary words: {', '.join(found_scary)}")
        suggestions.append("Consider using gentler language for very young children")
    
    return {
        "appropriate": len(issues) == 0,
        "issues": issues,
        "suggestions": suggestions
    }