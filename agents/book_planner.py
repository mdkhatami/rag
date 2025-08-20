from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from models.schemas import AgentState, BookParameters, Character, StoryArc, AgeGroup, Genre, Theme
import json


class BookPlannerAgent:
    """Overall Book & Character Planner - defines story arc, setting, and characters"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
    def create_system_prompt(self) -> str:
        return """You are an expert children's book planner specializing in creating engaging, age-appropriate stories. 
        
        Your role is to:
        1. Create compelling story arcs with clear beginning, middle, and end
        2. Design memorable characters with distinct personalities and appearances
        3. Establish engaging settings that enhance the story
        4. Ensure age-appropriate content and themes
        
        Guidelines:
        - Stories should have clear conflict and resolution
        - Characters should be relatable and memorable
        - Settings should be vivid and appropriate for the age group
        - Include positive themes and moral lessons when appropriate
        - Consider the target age group's reading level and interests
        
        Respond with JSON containing:
        - story_arc: beginning, middle, end, conflict, resolution, moral_lesson
        - characters: list of character objects with name, description, personality, appearance, role, visual_style
        - setting_details: detailed setting description
        """
    
    def plan_book(self, state: AgentState) -> AgentState:
        """Plan the overall book structure and characters"""
        try:
            params = state.book_state.parameters
            
            # Create age-appropriate guidelines
            age_guidelines = self._get_age_guidelines(params.age_group)
            
            prompt = f"""
            Create a children's book plan for:
            Title: {params.title}
            Genre: {params.genre}
            Age Group: {params.age_group}
            Theme: {params.theme}
            Number of Pages: {params.num_pages}
            Main Character: {params.main_character_name or 'To be created'}
            Setting: {params.setting or 'To be created'}
            Additional Notes: {params.additional_notes or 'None'}
            
            Age Guidelines: {age_guidelines}
            
            Create a complete book plan with story arc, characters, and setting details.
            """
            
            messages = [
                SystemMessage(content=self.create_system_prompt()),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse the response
            try:
                plan_data = json.loads(response.content)
                
                # Create StoryArc
                story_arc = StoryArc(
                    beginning=plan_data["story_arc"]["beginning"],
                    middle=plan_data["story_arc"]["middle"],
                    end=plan_data["story_arc"]["end"],
                    conflict=plan_data["story_arc"]["conflict"],
                    resolution=plan_data["story_arc"]["resolution"],
                    moral_lesson=plan_data["story_arc"].get("moral_lesson")
                )
                
                # Create Characters
                characters = []
                for char_data in plan_data["characters"]:
                    character = Character(
                        name=char_data["name"],
                        description=char_data["description"],
                        personality=char_data["personality"],
                        appearance=char_data["appearance"],
                        role=char_data["role"],
                        visual_style=char_data["visual_style"]
                    )
                    characters.append(character)
                
                # Update state
                state.book_state.story_arc = story_arc
                state.book_state.characters = characters
                state.book_state.consistency_notes["setting"] = plan_data.get("setting_details", "")
                state.current_task = "book_planned"
                state.task_results["book_plan"] = {
                    "story_arc": story_arc.dict(),
                    "characters": [char.dict() for char in characters],
                    "setting": plan_data.get("setting_details", "")
                }
                
            except json.JSONDecodeError:
                state.errors.append("Failed to parse book plan response")
                
        except Exception as e:
            state.errors.append(f"Book planning failed: {str(e)}")
            
        return state
    
    def _get_age_guidelines(self, age_group: AgeGroup) -> str:
        """Get age-appropriate guidelines"""
        guidelines = {
            AgeGroup.TODDLER: "Very simple stories, repetitive patterns, bright colors, basic emotions, 2-3 sentences per page",
            AgeGroup.PRESCHOOL: "Simple plots, clear cause-and-effect, familiar situations, 3-4 sentences per page, rhyming encouraged",
            AgeGroup.EARLY_READER: "More complex plots, character development, 4-6 sentences per page, introduce new vocabulary",
            AgeGroup.MIDDLE_READER: "Detailed plots, character arcs, 6-8 sentences per page, can handle more complex themes"
        }
        return guidelines.get(age_group, "Age-appropriate content")