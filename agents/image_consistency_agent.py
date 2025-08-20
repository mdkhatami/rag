from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from models.schemas import AgentState, Character, Page, ConsistencyCheck
import json


class ImageConsistencyAgent:
    """Image Consistency Agent - keeps character designs, environments, and style uniform"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
    def create_system_prompt(self) -> str:
        return """You are an expert children's book visual consistency specialist. Your role is to ensure:
        
        1. Character Design Consistency: Characters look the same across all pages
        2. Environmental Consistency: Settings and backgrounds are coherent
        3. Style Consistency: Art style, color palette, and visual elements remain uniform
        4. Visual Storytelling: Illustrations enhance and support the narrative
        5. Age-Appropriate Visuals: Images are suitable for the target age group
        
        Analyze illustrations and provide specific feedback for maintaining visual consistency.
        Respond with JSON containing consistency checks and recommendations.
        """
    
    def check_visual_consistency(self, state: AgentState) -> AgentState:
        """Check visual consistency across all illustrations"""
        try:
            book_state = state.book_state
            illustrations = state.task_results.get("illustration_designs", {})
            
            if not illustrations:
                state.errors.append("No illustrations found for consistency check")
                return state
            
            # Prepare data for consistency analysis
            consistency_data = {
                "characters": [char.dict() for char in book_state.characters],
                "pages": [page.dict() for page in book_state.pages],
                "illustrations": illustrations,
                "style_guide": book_state.visual_style_guide,
                "parameters": book_state.parameters.dict()
            }
            
            prompt = f"""
            Perform a comprehensive visual consistency check for this children's book:
            
            Book Parameters: {consistency_data['parameters']}
            Characters: {consistency_data['characters']}
            Pages: {consistency_data['pages']}
            Illustrations: {consistency_data['illustrations']}
            Style Guide: {consistency_data['style_guide']}
            
            Check for:
            1. Character appearance consistency (clothing, features, proportions)
            2. Environmental consistency (settings, backgrounds, props)
            3. Style consistency (art style, color palette, visual elements)
            4. Visual storytelling coherence
            5. Age-appropriate visual content
            
            Provide specific recommendations for any inconsistencies found.
            """
            
            messages = [
                SystemMessage(content=self.create_system_prompt()),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                consistency_data = json.loads(response.content)
                
                # Create visual consistency check
                visual_consistency = {
                    "character_consistency": consistency_data.get("character_consistency", {}),
                    "environmental_consistency": consistency_data.get("environmental_consistency", []),
                    "style_consistency": consistency_data.get("style_consistency", []),
                    "visual_storytelling": consistency_data.get("visual_storytelling", []),
                    "age_appropriateness": consistency_data.get("age_appropriateness", [])
                }
                
                # Update state
                state.book_state.consistency_notes["visual_consistency"] = visual_consistency
                state.current_task = "visual_consistency_checked"
                state.task_results["visual_consistency_check"] = visual_consistency
                
                # Add warnings for any issues found
                for category, issues in visual_consistency.items():
                    if isinstance(issues, list) and issues:
                        state.warnings.extend([f"Visual {category}: {issue}" for issue in issues])
                    elif isinstance(issues, dict) and issues:
                        for char, char_issues in issues.items():
                            if char_issues:
                                state.warnings.extend([f"Visual {category} - {char}: {issue}" for issue in char_issues])
                
            except json.JSONDecodeError:
                state.errors.append("Failed to parse visual consistency check response")
                
        except Exception as e:
            state.errors.append(f"Visual consistency check failed: {str(e)}")
            
        return state
    
    def create_visual_style_guide(self, state: AgentState) -> AgentState:
        """Create a comprehensive visual style guide"""
        try:
            book_state = state.book_state
            
            prompt = f"""
            Create a comprehensive visual style guide for this children's book:
            
            Title: {book_state.parameters.title}
            Age Group: {book_state.parameters.age_group}
            Genre: {book_state.parameters.genre}
            Theme: {book_state.parameters.theme}
            Characters: {[char.dict() for char in book_state.characters]}
            
            Include:
            1. Color palette specifications (primary, secondary, accent colors)
            2. Character design rules (proportions, features, clothing styles)
            3. Environmental design guidelines (settings, backgrounds, props)
            4. Art style specifications (line weight, shading, texture)
            5. Visual storytelling rules (composition, perspective, mood indicators)
            6. Age-appropriate visual guidelines
            
            Respond with JSON containing the visual style guide.
            """
            
            messages = [
                SystemMessage(content="You are an expert children's book visual style guide creator."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                visual_style_guide = json.loads(response.content)
                state.book_state.visual_style_guide = visual_style_guide
                state.task_results["visual_style_guide"] = visual_style_guide
                
            except json.JSONDecodeError:
                state.errors.append("Failed to parse visual style guide response")
                
        except Exception as e:
            state.errors.append(f"Visual style guide creation failed: {str(e)}")
            
        return state
    
    def validate_character_consistency(self, state: AgentState, character_name: str) -> AgentState:
        """Validate consistency of a specific character across all pages"""
        try:
            character = next((c for c in state.book_state.characters if c.name == character_name), None)
            
            if not character:
                state.errors.append(f"Character {character_name} not found")
                return state
            
            # Get all pages where this character appears
            character_pages = [page for page in state.book_state.pages if character_name in page.characters_present]
            illustrations = state.task_results.get("illustration_designs", {})
            
            if not character_pages:
                state.warnings.append(f"Character {character_name} does not appear in any pages")
                return state
            
            # Check character consistency across pages
            consistency_issues = []
            
            for page in character_pages:
                page_illustration = illustrations.get(page.page_number, {})
                
                # Check if character description is consistent
                if page_illustration:
                    char_positions = page_illustration.get("character_positions", {})
                    if character_name in char_positions:
                        # Validate character position and appearance
                        position = char_positions[character_name]
                        if not self._validate_character_appearance(character, position, page.mood):
                            consistency_issues.append(f"Page {page.page_number}: Character appearance may not be consistent")
            
            if consistency_issues:
                state.warnings.extend(consistency_issues)
                state.task_results[f"character_consistency_{character_name}"] = {
                    "issues": consistency_issues,
                    "pages_appearing": [page.page_number for page in character_pages]
                }
            else:
                state.task_results[f"character_consistency_{character_name}"] = {
                    "status": "consistent",
                    "pages_appearing": [page.page_number for page in character_pages]
                }
                
        except Exception as e:
            state.errors.append(f"Character consistency validation failed: {str(e)}")
            
        return state
    
    def _validate_character_appearance(self, character: Character, position: Dict, mood: str) -> bool:
        """Validate if character appearance is consistent with their design"""
        # This is a simplified validation - in practice, you'd use more sophisticated image analysis
        
        # Check if character position makes sense for their personality
        personality = character.personality.lower()
        position_description = str(position).lower()
        
        # Some basic consistency checks
        if "shy" in personality and "center" in position_description:
            return False  # Shy characters shouldn't be in center positions
        if "bold" in personality and "corner" in position_description:
            return False  # Bold characters shouldn't be hidden in corners
            
        return True
    
    def create_environment_consistency_report(self, state: AgentState) -> AgentState:
        """Create a report on environmental consistency across the book"""
        try:
            pages = state.book_state.pages
            illustrations = state.task_results.get("illustration_designs", {})
            
            # Analyze environmental elements across pages
            environments = {}
            consistency_issues = []
            
            for page in pages:
                page_illustration = illustrations.get(page.page_number, {})
                if page_illustration:
                    background = page_illustration.get("background_elements", [])
                    setting = page.setting_description
                    
                    # Track environmental elements
                    for element in background:
                        if element not in environments:
                            environments[element] = []
                        environments[element].append(page.page_number)
                    
                    # Check for environmental consistency
                    if page.page_number > 1:
                        prev_page = pages[page.page_number - 2]  # 0-indexed
                        prev_illustration = illustrations.get(prev_page.page_number, {})
                        
                        if prev_illustration:
                            prev_background = prev_illustration.get("background_elements", [])
                            
                            # Check for jarring environmental changes
                            if not self._validate_environment_transition(prev_background, background, prev_page.mood, page.mood):
                                consistency_issues.append(f"Page {page.page_number}: Environmental transition may be jarring")
            
            # Create consistency report
            environment_report = {
                "environments": environments,
                "consistency_issues": consistency_issues,
                "recommendations": self._generate_environment_recommendations(environments, consistency_issues)
            }
            
            state.task_results["environment_consistency_report"] = environment_report
            
            if consistency_issues:
                state.warnings.extend(consistency_issues)
                
        except Exception as e:
            state.errors.append(f"Environment consistency report creation failed: {str(e)}")
            
        return state
    
    def _validate_environment_transition(self, prev_background: List, current_background: List, prev_mood: str, current_mood: str) -> bool:
        """Validate if environmental transition is smooth"""
        # Check for jarring transitions
        jarring_transitions = [
            (["indoor", "home"], ["outdoor", "forest"]),
            (["day", "sunny"], ["night", "dark"]),
            (["city", "buildings"], ["nature", "mountains"])
        ]
        
        for prev_set, current_set in jarring_transitions:
            if any(element in prev_background for element in prev_set) and any(element in current_background for element in current_set):
                return False
                
        return True
    
    def _generate_environment_recommendations(self, environments: Dict, issues: List) -> List[str]:
        """Generate recommendations for environmental consistency"""
        recommendations = []
        
        # Check for overused environments
        for element, pages in environments.items():
            if len(pages) > 3:
                recommendations.append(f"Consider varying the use of '{element}' (appears on {len(pages)} pages)")
        
        # Check for missing environmental variety
        if len(environments) < 3:
            recommendations.append("Consider adding more environmental variety to maintain visual interest")
        
        # Add specific recommendations for issues
        for issue in issues:
            recommendations.append(f"Review {issue}")
        
        return recommendations