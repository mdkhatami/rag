from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from models.schemas import AgentState, ConsistencyCheck, Character, StoryArc, Page
import json


class ConsistencyPlannerAgent:
    """Consistency Planner - ensures coherence across chapters, characters, and themes"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
    def create_system_prompt(self) -> str:
        return """You are an expert children's book consistency planner. Your role is to ensure:
        
        1. Character consistency: personalities, appearances, and behaviors remain consistent
        2. Plot consistency: story flows logically without contradictions
        3. Style consistency: writing style and tone remain appropriate for the age group
        4. Theme consistency: the main theme is woven throughout the story
        5. Age appropriateness: content is suitable for the target age group
        
        Analyze the book elements and provide specific recommendations for maintaining consistency.
        Respond with JSON containing consistency checks and recommendations.
        """
    
    def check_consistency(self, state: AgentState) -> AgentState:
        """Check and maintain consistency across the book"""
        try:
            book_state = state.book_state
            
            # Prepare data for consistency check
            consistency_data = {
                "characters": [char.dict() for char in book_state.characters],
                "story_arc": book_state.story_arc.dict() if book_state.story_arc else None,
                "pages": [page.dict() for page in book_state.pages],
                "parameters": book_state.parameters.dict(),
                "visual_style_guide": book_state.visual_style_guide
            }
            
            prompt = f"""
            Perform a comprehensive consistency check for this children's book:
            
            Book Parameters: {consistency_data['parameters']}
            Characters: {consistency_data['characters']}
            Story Arc: {consistency_data['story_arc']}
            Pages: {consistency_data['pages']}
            Visual Style Guide: {consistency_data['visual_style_guide']}
            
            Check for:
            1. Character consistency (personality, appearance, behavior)
            2. Plot consistency (logical flow, no contradictions)
            3. Style consistency (writing tone, age-appropriateness)
            4. Theme consistency (main theme throughout)
            5. Visual consistency (character designs, settings)
            
            Provide specific recommendations for any inconsistencies found.
            """
            
            messages = [
                SystemMessage(content=self.create_system_prompt()),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                consistency_data = json.loads(response.content)
                
                # Create ConsistencyCheck object
                consistency_check = ConsistencyCheck(
                    character_consistency=consistency_data.get("character_consistency", {}),
                    plot_consistency=consistency_data.get("plot_consistency", []),
                    style_consistency=consistency_data.get("style_consistency", []),
                    age_appropriateness=consistency_data.get("age_appropriateness", []),
                    theme_alignment=consistency_data.get("theme_alignment", [])
                )
                
                # Update state with consistency information
                state.book_state.consistency_notes["consistency_check"] = consistency_check.dict()
                state.current_task = "consistency_checked"
                state.task_results["consistency_check"] = consistency_check.dict()
                
                # Add warnings for any issues found
                for category, issues in consistency_check.dict().items():
                    if isinstance(issues, list) and issues:
                        state.warnings.extend([f"{category}: {issue}" for issue in issues])
                    elif isinstance(issues, dict) and issues:
                        for char, char_issues in issues.items():
                            if char_issues:
                                state.warnings.extend([f"{category} - {char}: {issue}" for issue in char_issues])
                
            except json.JSONDecodeError:
                state.errors.append("Failed to parse consistency check response")
                
        except Exception as e:
            state.errors.append(f"Consistency check failed: {str(e)}")
            
        return state
    
    def create_style_guide(self, state: AgentState) -> AgentState:
        """Create a comprehensive style guide for the book"""
        try:
            book_state = state.book_state
            
            prompt = f"""
            Create a comprehensive style guide for this children's book:
            
            Title: {book_state.parameters.title}
            Age Group: {book_state.parameters.age_group}
            Genre: {book_state.parameters.genre}
            Theme: {book_state.parameters.theme}
            Characters: {[char.dict() for char in book_state.characters]}
            
            Include:
            1. Writing style guidelines (sentence length, vocabulary level, tone)
            2. Visual style guidelines (color palette, art style, character design rules)
            3. Character interaction patterns
            4. Setting consistency rules
            5. Age-appropriate content guidelines
            
            Respond with JSON containing the style guide.
            """
            
            messages = [
                SystemMessage(content="You are an expert children's book style guide creator."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                style_guide = json.loads(response.content)
                state.book_state.visual_style_guide = style_guide
                state.task_results["style_guide"] = style_guide
                
            except json.JSONDecodeError:
                state.errors.append("Failed to parse style guide response")
                
        except Exception as e:
            state.errors.append(f"Style guide creation failed: {str(e)}")
            
        return state
    
    def validate_page_consistency(self, state: AgentState, new_page: Page) -> AgentState:
        """Validate a new page against existing content for consistency"""
        try:
            existing_pages = state.book_state.pages
            characters = state.book_state.characters
            
            # Check character consistency
            for char_name in new_page.characters_present:
                char = next((c for c in characters if c.name == char_name), None)
                if char:
                    # Validate character behavior matches personality
                    if not self._validate_character_behavior(char, new_page.text):
                        state.warnings.append(f"Character {char_name} behavior may not match established personality")
            
            # Check plot consistency
            if existing_pages:
                last_page = existing_pages[-1]
                if not self._validate_plot_flow(last_page, new_page):
                    state.warnings.append("Plot flow may have inconsistencies")
            
            # Check style consistency
            if not self._validate_style_consistency(new_page, state.book_state.parameters.age_group):
                state.warnings.append("Page style may not be consistent with age group")
                
        except Exception as e:
            state.errors.append(f"Page consistency validation failed: {str(e)}")
            
        return state
    
    def _validate_character_behavior(self, character: Character, page_text: str) -> bool:
        """Validate if character behavior in text matches established personality"""
        # This is a simplified validation - in practice, you'd use more sophisticated NLP
        personality_keywords = character.personality.lower().split()
        text_lower = page_text.lower()
        
        # Check if personality traits are reflected in the text
        personality_matches = sum(1 for keyword in personality_keywords if keyword in text_lower)
        return personality_matches > 0
    
    def _validate_plot_flow(self, last_page: Page, new_page: Page) -> bool:
        """Validate logical flow between pages"""
        # Simplified validation - check for obvious contradictions
        last_mood = last_page.mood
        new_mood = new_page.mood
        
        # Some mood transitions might be jarring
        jarring_transitions = [
            ("happy", "terrified"),
            ("excited", "depressed"),
            ("peaceful", "angry")
        ]
        
        return (last_mood, new_mood) not in jarring_transitions
    
    def _validate_style_consistency(self, page: Page, age_group: str) -> bool:
        """Validate if page style is appropriate for age group"""
        sentence_count = len(page.text.split('.'))
        
        if age_group == "2-4" and sentence_count > 3:
            return False
        elif age_group == "4-6" and sentence_count > 4:
            return False
        elif age_group == "6-8" and sentence_count > 6:
            return False
        elif age_group == "8-10" and sentence_count > 8:
            return False
            
        return True