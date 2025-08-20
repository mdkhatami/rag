import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models.schemas import AgentState, BookParameters, BookState
from agents.book_planner import BookPlannerAgent
from agents.consistency_planner import ConsistencyPlannerAgent
from agents.chapter_writer import ChapterWriterAgent
from agents.visual_designer import VisualDesignerAgent
from agents.image_consistency_agent import ImageConsistencyAgent


# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)


class StorybookGenerator:
    """Main class for generating storybooks using the multi-agent system"""
    
    def __init__(self):
        self.llm = llm
        
        # Initialize agents
        self.book_planner = BookPlannerAgent(llm)
        self.consistency_planner = ConsistencyPlannerAgent(llm)
        self.chapter_writer = ChapterWriterAgent(llm)
        self.visual_designer = VisualDesignerAgent(llm)
        self.image_consistency_agent = ImageConsistencyAgent(llm)
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Define the workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent task
        workflow.add_node("plan_book", self._plan_book_node)
        workflow.add_node("create_style_guide", self._create_style_guide_node)
        workflow.add_node("write_pages", self._write_pages_node)
        workflow.add_node("check_consistency", self._check_consistency_node)
        workflow.add_node("design_illustrations", self._design_illustrations_node)
        workflow.add_node("check_visual_consistency", self._check_visual_consistency_node)
        workflow.add_node("generate_illustrations", self._generate_illustrations_node)
        workflow.add_node("create_character_reference", self._create_character_reference_node)
        workflow.add_node("final_consistency_check", self._final_consistency_check_node)
        
        # Define the workflow edges
        workflow.set_entry_point("plan_book")
        
        workflow.add_edge("plan_book", "create_style_guide")
        workflow.add_edge("create_style_guide", "write_pages")
        workflow.add_edge("write_pages", "check_consistency")
        workflow.add_edge("check_consistency", "design_illustrations")
        workflow.add_edge("design_illustrations", "check_visual_consistency")
        workflow.add_edge("check_visual_consistency", "generate_illustrations")
        workflow.add_edge("generate_illustrations", "create_character_reference")
        workflow.add_edge("create_character_reference", "final_consistency_check")
        workflow.add_edge("final_consistency_check", END)
        
        # Compile the workflow
        return workflow.compile(checkpointer=MemorySaver())
    
    def _plan_book_node(self, state: AgentState) -> AgentState:
        """Node for planning the overall book structure"""
        print("📚 Planning book structure and characters...")
        return self.book_planner.plan_book(state)
    
    def _create_style_guide_node(self, state: AgentState) -> AgentState:
        """Node for creating style guides"""
        print("🎨 Creating style guides...")
        state = self.consistency_planner.create_style_guide(state)
        state = self.image_consistency_agent.create_visual_style_guide(state)
        return state
    
    def _write_pages_node(self, state: AgentState) -> AgentState:
        """Node for writing all pages"""
        print("✍️ Writing story pages...")
        return self.chapter_writer.write_all_pages(state)
    
    def _check_consistency_node(self, state: AgentState) -> AgentState:
        """Node for checking content consistency"""
        print("🔍 Checking content consistency...")
        return self.consistency_planner.check_consistency(state)
    
    def _design_illustrations_node(self, state: AgentState) -> AgentState:
        """Node for designing illustrations"""
        print("🎨 Designing illustrations...")
        return self.visual_designer.design_all_illustrations(state)
    
    def _check_visual_consistency_node(self, state: AgentState) -> AgentState:
        """Node for checking visual consistency"""
        print("👁️ Checking visual consistency...")
        return self.image_consistency_agent.check_visual_consistency(state)
    
    def _generate_illustrations_node(self, state: AgentState) -> AgentState:
        """Node for generating placeholder illustrations"""
        print("🖼️ Generating illustrations...")
        return self.visual_designer.generate_all_illustrations(state)
    
    def _create_character_reference_node(self, state: AgentState) -> AgentState:
        """Node for creating character reference sheet"""
        print("👥 Creating character reference sheet...")
        return self.visual_designer.create_character_reference_sheet(state)
    
    def _final_consistency_check_node(self, state: AgentState) -> AgentState:
        """Node for final consistency check"""
        print("✅ Performing final consistency check...")
        state = self.consistency_planner.check_consistency(state)
        state = self.image_consistency_agent.create_environment_consistency_report(state)
        
        # Mark book as complete
        state.book_state.status = "completed"
        return state
    
    def generate_storybook(self, book_parameters: BookParameters) -> Dict[str, Any]:
        """Generate a complete storybook"""
        print(f"🚀 Starting storybook generation: {book_parameters.title}")
        
        # Initialize the state
        initial_state = AgentState(
            book_state=BookState(parameters=book_parameters),
            current_task="initialized",
            task_results={},
            errors=[],
            warnings=[]
        )
        
        try:
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            print("🎉 Storybook generation completed!")
            
            # Return the results
            return {
                "success": True,
                "book_state": result.book_state.dict(),
                "task_results": result.task_results,
                "errors": result.errors,
                "warnings": result.warnings
            }
            
        except Exception as e:
            print(f"❌ Storybook generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "book_state": initial_state.book_state.dict() if initial_state else None
            }
    
    def get_book_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the generated book"""
        if not result.get("success"):
            return {"error": "Book generation was not successful"}
        
        book_state = result["book_state"]
        
        return {
            "title": book_state["parameters"]["title"],
            "genre": book_state["parameters"]["genre"],
            "age_group": book_state["parameters"]["age_group"],
            "theme": book_state["parameters"]["theme"],
            "num_pages": len(book_state["pages"]),
            "characters": [char["name"] for char in book_state["characters"]],
            "status": book_state["status"],
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", [])
        }


def main():
    """Main function to demonstrate the storybook generator"""
    
    # Example book parameters
    book_params = BookParameters(
        title="The Brave Little Mouse",
        genre="adventure",
        age_group="4-6",
        theme="courage",
        num_pages=8,
        main_character_name="Milo",
        setting="A cozy house and magical garden",
        additional_notes="Include a lesson about helping others"
    )
    
    # Create the generator
    generator = StorybookGenerator()
    
    # Generate the storybook
    result = generator.generate_storybook(book_params)
    
    # Print summary
    summary = generator.get_book_summary(result)
    print("\n📖 Book Summary:")
    print(f"Title: {summary['title']}")
    print(f"Genre: {summary['genre']}")
    print(f"Age Group: {summary['age_group']}")
    print(f"Pages: {summary['num_pages']}")
    print(f"Characters: {', '.join(summary['characters'])}")
    print(f"Status: {summary['status']}")
    
    if summary.get("errors"):
        print(f"\n❌ Errors: {len(summary['errors'])}")
        for error in summary["errors"]:
            print(f"  - {error}")
    
    if summary.get("warnings"):
        print(f"\n⚠️ Warnings: {len(summary['warnings'])}")
        for warning in summary["warnings"][:5]:  # Show first 5 warnings
            print(f"  - {warning}")


if __name__ == "__main__":
    main()