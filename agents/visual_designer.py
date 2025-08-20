from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from models.schemas import AgentState, Page, Character, IllustrationRequest
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import io
import base64


class VisualDesignerAgent:
    """Visual Designer - creates illustrations for each page"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
    def create_system_prompt(self) -> str:
        return """You are an expert children's book illustrator specializing in creating engaging, age-appropriate illustrations.
        
        Your role is to:
        1. Create detailed illustration descriptions that can be rendered
        2. Design characters with consistent appearances
        3. Create engaging scenes that complement the text
        4. Use appropriate colors and styles for the target age group
        5. Ensure illustrations enhance the story without overwhelming the text
        
        Illustration Guidelines:
        - Create scenes that are 50% of the page (text takes the other 50%)
        - Use bright, engaging colors for young children
        - Include clear character expressions and body language
        - Create depth and visual interest
        - Ensure characters are easily recognizable
        - Match the mood and tone of the text
        
        Respond with JSON containing:
        - scene_description: detailed description of the illustration
        - color_palette: list of colors to use
        - character_positions: where each character should be placed
        - background_elements: what should be in the background
        - mood_indicators: visual elements that convey the page's mood
        """
    
    def design_illustration(self, state: AgentState, page_number: int) -> AgentState:
        """Design an illustration for a specific page"""
        try:
            book_state = state.book_state
            page = next((p for p in book_state.pages if p.page_number == page_number), None)
            
            if not page:
                state.errors.append(f"Page {page_number} not found for illustration design")
                return state
            
            # Create illustration request
            illustration_request = IllustrationRequest(
                page_number=page_number,
                description=page.illustration_description,
                characters=page.characters_present,
                setting=page.setting_description,
                mood=page.mood,
                style_guide=book_state.visual_style_guide,
                previous_illustrations=[p.illustration_description for p in book_state.pages[:page_number-1]]
            )
            
            prompt = f"""
            Design an illustration for page {page_number} of this children's book:
            
            Book Title: {book_state.parameters.title}
            Age Group: {book_state.parameters.age_group}
            Genre: {book_state.parameters.genre}
            
            Page Text: {page.text}
            Illustration Description: {page.illustration_description}
            Characters Present: {page.characters_present}
            Setting: {page.setting_description}
            Mood: {page.mood}
            
            Character Details: {[char.dict() for char in book_state.characters if char.name in page.characters_present]}
            Style Guide: {book_state.visual_style_guide}
            Previous Illustrations: {illustration_request.previous_illustrations}
            
            Create a detailed illustration design that:
            1. Takes up 50% of the page (text will be on the other 50%)
            2. Matches the age group's visual preferences
            3. Maintains character consistency
            4. Enhances the story's mood and theme
            5. Is engaging and appropriate for children
            """
            
            messages = [
                SystemMessage(content=self.create_system_prompt()),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                design_data = json.loads(response.content)
                
                # Store the illustration design
                if "illustration_designs" not in state.task_results:
                    state.task_results["illustration_designs"] = {}
                
                state.task_results["illustration_designs"][page_number] = design_data
                state.current_task = f"illustration_{page_number}_designed"
                
            except json.JSONDecodeError:
                state.errors.append(f"Failed to parse illustration design for page {page_number}")
                
        except Exception as e:
            state.errors.append(f"Illustration design for page {page_number} failed: {str(e)}")
            
        return state
    
    def design_all_illustrations(self, state: AgentState) -> AgentState:
        """Design illustrations for all pages"""
        try:
            for page in state.book_state.pages:
                state = self.design_illustration(state, page.page_number)
                
                if state.errors:
                    break
                    
            state.current_task = "all_illustrations_designed"
            
        except Exception as e:
            state.errors.append(f"Designing all illustrations failed: {str(e)}")
            
        return state
    
    def generate_placeholder_illustration(self, state: AgentState, page_number: int) -> AgentState:
        """Generate a placeholder illustration using matplotlib"""
        try:
            # Get the illustration design
            design = state.task_results.get("illustration_designs", {}).get(page_number, {})
            
            # Create a simple placeholder illustration
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Set background color based on mood
            mood_colors = {
                "happy": "#FFE5B4",  # Light orange
                "sad": "#E6F3FF",    # Light blue
                "excited": "#FFE5E5", # Light red
                "peaceful": "#E8F5E8", # Light green
                "mysterious": "#F0E6FF", # Light purple
                "adventurous": "#FFF2CC" # Light yellow
            }
            
            background_color = mood_colors.get(design.get("mood", "happy").lower(), "#FFFFFF")
            ax.set_facecolor(background_color)
            
            # Add some simple shapes to represent the scene
            # This is a placeholder - in a real implementation, you'd use a proper illustration library
            
            # Add a sun for happy scenes
            if "happy" in design.get("mood", "").lower():
                sun = patches.Circle((7, 5), 0.5, color='yellow', alpha=0.8)
                ax.add_patch(sun)
            
            # Add some clouds
            for i in range(3):
                cloud = patches.Circle((2 + i*2, 4.5), 0.3, color='white', alpha=0.7)
                ax.add_patch(cloud)
            
            # Add ground
            ground = patches.Rectangle((0, 0), 8, 1, color='green', alpha=0.6)
            ax.add_patch(ground)
            
            # Set plot limits and remove axes
            ax.set_xlim(0, 8)
            ax.set_ylim(0, 6)
            ax.axis('off')
            
            # Add title
            ax.text(4, 5.5, f"Page {page_number}", ha='center', va='center', 
                   fontsize=16, fontweight='bold')
            
            # Add mood indicator
            ax.text(4, 5, design.get("mood", "Happy"), ha='center', va='center', 
                   fontsize=12, style='italic')
            
            # Convert to base64 for storage
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            # Store the illustration
            if "illustrations" not in state.task_results:
                state.task_results["illustrations"] = {}
            
            state.task_results["illustrations"][page_number] = {
                "image_base64": image_base64,
                "design": design
            }
            
            state.current_task = f"illustration_{page_number}_generated"
            
        except Exception as e:
            state.errors.append(f"Placeholder illustration generation for page {page_number} failed: {str(e)}")
            
        return state
    
    def generate_all_illustrations(self, state: AgentState) -> AgentState:
        """Generate placeholder illustrations for all pages"""
        try:
            for page in state.book_state.pages:
                state = self.generate_placeholder_illustration(state, page.page_number)
                
                if state.errors:
                    break
                    
            state.current_task = "all_illustrations_generated"
            
        except Exception as e:
            state.errors.append(f"Generating all illustrations failed: {str(e)}")
            
        return state
    
    def create_character_reference_sheet(self, state: AgentState) -> AgentState:
        """Create a character reference sheet for consistent illustrations"""
        try:
            characters = state.book_state.characters
            
            # Create a reference sheet with all characters
            fig, axes = plt.subplots(1, len(characters), figsize=(4*len(characters), 6))
            if len(characters) == 1:
                axes = [axes]
            
            for i, character in enumerate(characters):
                ax = axes[i]
                
                # Create a simple character representation
                # Head
                head = patches.Circle((2, 4), 0.8, color='peachpuff', alpha=0.8)
                ax.add_patch(head)
                
                # Body
                body = patches.Rectangle((1.5, 2), 1, 2, color='lightblue', alpha=0.8)
                ax.add_patch(body)
                
                # Eyes
                eye1 = patches.Circle((1.7, 4.2), 0.1, color='black')
                eye2 = patches.Circle((2.3, 4.2), 0.1, color='black')
                ax.add_patch(eye1)
                ax.add_patch(eye2)
                
                # Smile
                smile = patches.Arc((2, 3.8), 0.4, 0.3, angle=0, theta1=0, theta2=180, color='black')
                ax.add_patch(smile)
                
                # Character name
                ax.text(2, 1.5, character.name, ha='center', va='center', 
                       fontsize=10, fontweight='bold')
                
                # Character role
                ax.text(2, 1.2, character.role, ha='center', va='center', 
                       fontsize=8, style='italic')
                
                ax.set_xlim(0, 4)
                ax.set_ylim(0, 5)
                ax.axis('off')
            
            # Add title
            fig.suptitle("Character Reference Sheet", fontsize=16, fontweight='bold')
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            # Store the reference sheet
            state.task_results["character_reference_sheet"] = {
                "image_base64": image_base64,
                "characters": [char.dict() for char in characters]
            }
            
            state.current_task = "character_reference_sheet_created"
            
        except Exception as e:
            state.errors.append(f"Character reference sheet creation failed: {str(e)}")
            
        return state