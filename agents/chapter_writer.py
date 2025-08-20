from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from models.schemas import AgentState, Page, Character, StoryArc, AgeGroup
import json


class ChapterWriterAgent:
    """Chapter Writer - writes engaging, age-appropriate text for each page"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
    def create_system_prompt(self) -> str:
        return """You are an expert children's book writer specializing in creating engaging, age-appropriate content.
        
        Your role is to:
        1. Write compelling text that matches the target age group's reading level
        2. Create vivid descriptions that inspire illustrations
        3. Maintain character voices and personalities
        4. Build suspense and emotional engagement
        5. Ensure smooth story flow between pages
        
        Writing Guidelines:
        - Use age-appropriate vocabulary and sentence structure
        - Include sensory details and emotional cues
        - Create clear action and dialogue
        - Balance text length with illustration space
        - End pages with hooks that encourage turning to the next page
        
        Respond with JSON containing:
        - text: the page text
        - illustration_description: detailed description for the illustrator
        - characters_present: list of character names on this page
        - setting_description: description of the scene setting
        - mood: emotional tone of the page
        """
    
    def write_page(self, state: AgentState, page_number: int) -> AgentState:
        """Write content for a specific page"""
        try:
            book_state = state.book_state
            params = book_state.parameters
            story_arc = book_state.story_arc
            characters = book_state.characters
            
            # Determine page content based on story arc
            page_content = self._determine_page_content(page_number, params.num_pages, story_arc)
            
            # Get age-appropriate writing guidelines
            writing_guidelines = self._get_writing_guidelines(params.age_group)
            
            prompt = f"""
            Write page {page_number} of {params.num_pages} for this children's book:
            
            Title: {params.title}
            Age Group: {params.age_group}
            Genre: {params.genre}
            Theme: {params.theme}
            
            Story Arc:
            - Beginning: {story_arc.beginning}
            - Middle: {story_arc.middle}
            - End: {story_arc.end}
            - Conflict: {story_arc.conflict}
            - Resolution: {story_arc.resolution}
            
            Characters: {[char.dict() for char in characters]}
            
            Page Content Focus: {page_content}
            Writing Guidelines: {writing_guidelines}
            
            Previous Pages: {[page.dict() for page in book_state.pages]}
            
            Create engaging text and illustration description for this page.
            """
            
            messages = [
                SystemMessage(content=self.create_system_prompt()),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                page_data = json.loads(response.content)
                
                # Create Page object
                page = Page(
                    page_number=page_number,
                    text=page_data["text"],
                    illustration_description=page_data["illustration_description"],
                    characters_present=page_data["characters_present"],
                    setting_description=page_data["setting_description"],
                    mood=page_data["mood"]
                )
                
                # Add page to book state
                book_state.pages.append(page)
                book_state.current_page = page_number
                
                # Update state
                state.current_task = f"page_{page_number}_written"
                state.task_results[f"page_{page_number}"] = page.dict()
                
            except json.JSONDecodeError:
                state.errors.append(f"Failed to parse page {page_number} response")
                
        except Exception as e:
            state.errors.append(f"Page {page_number} writing failed: {str(e)}")
            
        return state
    
    def write_all_pages(self, state: AgentState) -> AgentState:
        """Write all pages for the book"""
        try:
            num_pages = state.book_state.parameters.num_pages
            
            for page_num in range(1, num_pages + 1):
                state = self.write_page(state, page_num)
                
                if state.errors:
                    break  # Stop if there are errors
                    
            state.current_task = "all_pages_written"
            
        except Exception as e:
            state.errors.append(f"Writing all pages failed: {str(e)}")
            
        return state
    
    def _determine_page_content(self, page_number: int, total_pages: int, story_arc: StoryArc) -> str:
        """Determine what content should be on each page based on story arc"""
        if total_pages <= 6:
            # Short book structure
            if page_number == 1:
                return "Introduction and setup"
            elif page_number == total_pages:
                return "Resolution and ending"
            else:
                return "Story development"
        else:
            # Longer book structure
            beginning_pages = max(1, total_pages // 4)
            middle_pages = total_pages // 2
            end_pages = total_pages - beginning_pages - middle_pages
            
            if page_number <= beginning_pages:
                return "Beginning: Introduction, character setup, and initial situation"
            elif page_number <= beginning_pages + middle_pages:
                return "Middle: Conflict development, challenges, and character growth"
            else:
                return "End: Climax, resolution, and conclusion"
    
    def _get_writing_guidelines(self, age_group: AgeGroup) -> str:
        """Get age-appropriate writing guidelines"""
        guidelines = {
            AgeGroup.TODDLER: """
            - 2-3 simple sentences per page
            - Repetitive patterns and rhyming
            - Basic vocabulary and concepts
            - Clear, bold actions
            - Bright, simple descriptions
            """,
            AgeGroup.PRESCHOOL: """
            - 3-4 sentences per page
            - Simple cause-and-effect
            - Familiar situations and emotions
            - Rhyming and rhythm encouraged
            - Vivid but simple descriptions
            """,
            AgeGroup.EARLY_READER: """
            - 4-6 sentences per page
            - More complex plots and character development
            - Introduce new vocabulary naturally
            - Dialogue and action balance
            - Detailed descriptions for illustrations
            """,
            AgeGroup.MIDDLE_READER: """
            - 6-8 sentences per page
            - Complex character arcs and relationships
            - Sophisticated vocabulary and themes
            - Rich dialogue and internal thoughts
            - Detailed world-building descriptions
            """
        }
        return guidelines.get(age_group, "Age-appropriate content")
    
    def revise_page(self, state: AgentState, page_number: int, feedback: str) -> AgentState:
        """Revise a specific page based on feedback"""
        try:
            # Find the page to revise
            page_index = next((i for i, page in enumerate(state.book_state.pages) 
                             if page.page_number == page_number), None)
            
            if page_index is None:
                state.errors.append(f"Page {page_number} not found for revision")
                return state
            
            current_page = state.book_state.pages[page_index]
            
            prompt = f"""
            Revise page {page_number} based on this feedback:
            
            Current Page: {current_page.dict()}
            Feedback: {feedback}
            
            Book Parameters: {state.book_state.parameters.dict()}
            Characters: {[char.dict() for char in state.book_state.characters]}
            
            Please revise the page to address the feedback while maintaining consistency with the rest of the book.
            """
            
            messages = [
                SystemMessage(content="You are an expert children's book editor and writer."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                revised_data = json.loads(response.content)
                
                # Update the page
                state.book_state.pages[page_index] = Page(
                    page_number=page_number,
                    text=revised_data["text"],
                    illustration_description=revised_data["illustration_description"],
                    characters_present=revised_data["characters_present"],
                    setting_description=revised_data["setting_description"],
                    mood=revised_data["mood"]
                )
                
                state.current_task = f"page_{page_number}_revised"
                state.task_results[f"page_{page_number}_revision"] = revised_data
                
            except json.JSONDecodeError:
                state.errors.append(f"Failed to parse page {page_number} revision response")
                
        except Exception as e:
            state.errors.append(f"Page {page_number} revision failed: {str(e)}")
            
        return state