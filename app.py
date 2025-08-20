import streamlit as st
import base64
import io
from PIL import Image
import json
import os
from typing import Dict, Any

from main import StorybookGenerator
from models.schemas import BookParameters, Genre, AgeGroup, Theme


def main():
    st.set_page_config(
        page_title="Multi-Agent Storybook Generator",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📚 Multi-Agent Storybook Generator")
    st.markdown("Create personalized children's books using AI agents specialized in different aspects of book creation.")
    
    # Initialize session state
    if 'generator' not in st.session_state:
        st.session_state.generator = StorybookGenerator()
    
    if 'book_result' not in st.session_state:
        st.session_state.book_result = None
    
    # Sidebar for book parameters
    with st.sidebar:
        st.header("📖 Book Parameters")
        
        # Basic information
        title = st.text_input("Book Title", "The Brave Little Mouse")
        genre = st.selectbox("Genre", [g.value for g in Genre], index=0)
        age_group = st.selectbox("Age Group", [a.value for a in AgeGroup], index=1)
        theme = st.selectbox("Theme", [t.value for t in Theme], index=0)
        
        # Advanced parameters
        with st.expander("Advanced Settings"):
            num_pages = st.slider("Number of Pages", 6, 20, 12)
            main_character = st.text_input("Main Character Name (optional)")
            setting = st.text_input("Setting (optional)")
            additional_notes = st.text_area("Additional Notes (optional)")
        
        # Generate button
        if st.button("🚀 Generate Storybook", type="primary", use_container_width=True):
            with st.spinner("Generating your storybook..."):
                # Create book parameters
                book_params = BookParameters(
                    title=title,
                    genre=genre,
                    age_group=age_group,
                    theme=theme,
                    num_pages=num_pages,
                    main_character_name=main_character if main_character else None,
                    setting=setting if setting else None,
                    additional_notes=additional_notes if additional_notes else None
                )
                
                # Generate the storybook
                result = st.session_state.generator.generate_storybook(book_params)
                st.session_state.book_result = result
    
    # Main content area
    if st.session_state.book_result:
        result = st.session_state.book_result
        
        if result.get("success"):
            display_book_result(result)
        else:
            st.error(f"❌ Book generation failed: {result.get('error', 'Unknown error')}")
    else:
        display_welcome_screen()


def display_welcome_screen():
    """Display welcome screen with information about the system"""
    
    st.markdown("""
    ## Welcome to the Multi-Agent Storybook Generator! 🎉
    
    This system uses specialized AI agents to create personalized children's books:
    
    ### 🤖 Our AI Agents:
    
    **📚 Book & Character Planner**
    - Defines story arc, setting, and characters
    - Ensures age-appropriate content structure
    
    **🔍 Consistency Planner**
    - Maintains coherence across chapters and themes
    - Validates character development and plot flow
    
    **✍️ Chapter Writer**
    - Creates engaging, age-appropriate text
    - Balances story elements and reading level
    
    **🎨 Visual Designer**
    - Designs illustrations for each page
    - Creates character reference sheets
    
    **👁️ Image Consistency Agent**
    - Ensures uniform character designs
    - Maintains visual style throughout the book
    
    ### 🎯 Features:
    - **Balanced Layout**: 50% text, 50% illustrations on each page
    - **Age-Appropriate**: Content tailored for different age groups
    - **Consistent Design**: Uniform characters and visual style
    - **Interactive**: Real-time generation with progress tracking
    
    ### 🚀 Getting Started:
    1. Fill in the book parameters in the sidebar
    2. Click "Generate Storybook"
    3. Watch as our AI agents create your book!
    """)
    
    # Show example
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Example Book**\n\nTitle: The Brave Little Mouse\nGenre: Adventure\nAge: 4-6 years\nTheme: Courage")
    
    with col2:
        st.success("**What You'll Get**\n\n• Complete story with illustrations\n• Character reference sheet\n• Consistency reports\n• Age-appropriate content")
    
    with col3:
        st.warning("**Requirements**\n\n• OpenAI API key in .env file\n• Internet connection\n• Patience for generation time")


def display_book_result(result: Dict[str, Any]):
    """Display the generated book results"""
    
    book_state = result["book_state"]
    task_results = result["task_results"]
    
    # Book summary
    st.success("🎉 Storybook generated successfully!")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📖 Book Overview", 
        "📄 Pages", 
        "🎨 Illustrations", 
        "👥 Characters", 
        "📊 Reports"
    ])
    
    with tab1:
        display_book_overview(book_state, result)
    
    with tab2:
        display_pages(book_state, task_results)
    
    with tab3:
        display_illustrations(task_results)
    
    with tab4:
        display_characters(book_state, task_results)
    
    with tab5:
        display_reports(result)


def display_book_overview(book_state: Dict, result: Dict):
    """Display book overview information"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Book Information")
        st.write(f"**Title:** {book_state['parameters']['title']}")
        st.write(f"**Genre:** {book_state['parameters']['genre']}")
        st.write(f"**Age Group:** {book_state['parameters']['age_group']}")
        st.write(f"**Theme:** {book_state['parameters']['theme']}")
        st.write(f"**Pages:** {len(book_state['pages'])}")
        st.write(f"**Status:** {book_state['status']}")
        
        if book_state['parameters']['main_character_name']:
            st.write(f"**Main Character:** {book_state['parameters']['main_character_name']}")
        
        if book_state['parameters']['setting']:
            st.write(f"**Setting:** {book_state['parameters']['setting']}")
    
    with col2:
        st.subheader("📈 Generation Stats")
        
        # Count characters
        num_characters = len(book_state['characters'])
        st.metric("Characters", num_characters)
        
        # Count pages
        num_pages = len(book_state['pages'])
        st.metric("Pages", num_pages)
        
        # Count errors and warnings
        errors = result.get('errors', [])
        warnings = result.get('warnings', [])
        st.metric("Errors", len(errors))
        st.metric("Warnings", len(warnings))
    
    # Story arc
    if book_state.get('story_arc'):
        st.subheader("📖 Story Arc")
        story_arc = book_state['story_arc']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**Beginning**")
            st.write(story_arc['beginning'])
        
        with col2:
            st.warning("**Middle**")
            st.write(story_arc['middle'])
        
        with col3:
            st.success("**End**")
            st.write(story_arc['end'])
        
        if story_arc.get('moral_lesson'):
            st.info(f"**Moral Lesson:** {story_arc['moral_lesson']}")


def display_pages(book_state: Dict, task_results: Dict):
    """Display all pages of the book"""
    
    st.subheader("📄 Book Pages")
    
    for i, page in enumerate(book_state['pages']):
        with st.expander(f"Page {page['page_number']}: {page['text'][:50]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Text:**")
                st.write(page['text'])
                
                st.write("**Characters Present:**")
                st.write(", ".join(page['characters_present']))
                
                st.write("**Setting:**")
                st.write(page['setting_description'])
                
                st.write("**Mood:**")
                st.write(page['mood'])
            
            with col2:
                st.write("**Illustration Description:**")
                st.write(page['illustration_description'])
                
                # Show illustration if available
                illustrations = task_results.get("illustrations", {})
                if page['page_number'] in illustrations:
                    image_data = illustrations[page['page_number']]['image_base64']
                    image = base64.b64decode(image_data)
                    st.image(image, caption=f"Page {page['page_number']} Illustration")


def display_illustrations(task_results: Dict):
    """Display illustrations and visual elements"""
    
    st.subheader("🎨 Illustrations")
    
    # Character reference sheet
    if "character_reference_sheet" in task_results:
        st.write("**👥 Character Reference Sheet**")
        ref_sheet = task_results["character_reference_sheet"]
        image_data = ref_sheet['image_base64']
        image = base64.b64decode(image_data)
        st.image(image, caption="Character Reference Sheet")
    
    # Individual page illustrations
    illustrations = task_results.get("illustrations", {})
    if illustrations:
        st.write("**📄 Page Illustrations**")
        
        # Create a grid of illustrations
        cols = st.columns(3)
        for i, (page_num, illustration) in enumerate(illustrations.items()):
            col_idx = i % 3
            with cols[col_idx]:
                image_data = illustration['image_base64']
                image = base64.b64decode(image_data)
                st.image(image, caption=f"Page {page_num}")
    
    # Illustration designs
    designs = task_results.get("illustration_designs", {})
    if designs:
        st.write("**🎨 Illustration Designs**")
        for page_num, design in designs.items():
            with st.expander(f"Page {page_num} Design"):
                st.json(design)


def display_characters(book_state: Dict, task_results: Dict):
    """Display character information"""
    
    st.subheader("👥 Characters")
    
    characters = book_state['characters']
    
    for i, character in enumerate(characters):
        with st.expander(f"{character['name']} - {character['role']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Description:**")
                st.write(character['description'])
                
                st.write("**Personality:**")
                st.write(character['personality'])
                
                st.write("**Role:**")
                st.write(character['role'])
            
            with col2:
                st.write("**Appearance:**")
                st.write(character['appearance'])
                
                st.write("**Visual Style:**")
                st.write(character['visual_style'])
                
                # Character consistency check
                char_consistency = task_results.get(f"character_consistency_{character['name']}", {})
                if char_consistency:
                    st.write("**Consistency Status:**")
                    if char_consistency.get("status") == "consistent":
                        st.success("✅ Consistent")
                    else:
                        st.warning("⚠️ Issues found")
                        for issue in char_consistency.get("issues", []):
                            st.write(f"- {issue}")


def display_reports(result: Dict):
    """Display consistency reports and analysis"""
    
    st.subheader("📊 Reports & Analysis")
    
    # Errors and warnings
    errors = result.get('errors', [])
    warnings = result.get('warnings', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if errors:
            st.error("❌ Errors")
            for error in errors:
                st.write(f"- {error}")
        else:
            st.success("✅ No errors found")
    
    with col2:
        if warnings:
            st.warning("⚠️ Warnings")
            for warning in warnings[:10]:  # Show first 10 warnings
                st.write(f"- {warning}")
            if len(warnings) > 10:
                st.write(f"... and {len(warnings) - 10} more warnings")
        else:
            st.success("✅ No warnings found")
    
    # Consistency reports
    task_results = result.get('task_results', {})
    
    if "consistency_check" in task_results:
        st.write("**🔍 Content Consistency Report**")
        consistency = task_results["consistency_check"]
        st.json(consistency)
    
    if "visual_consistency_check" in task_results:
        st.write("**👁️ Visual Consistency Report**")
        visual_consistency = task_results["visual_consistency_check"]
        st.json(visual_consistency)
    
    if "environment_consistency_report" in task_results:
        st.write("**🌍 Environment Consistency Report**")
        env_report = task_results["environment_consistency_report"]
        st.json(env_report)
    
    # Download option
    st.subheader("💾 Download")
    
    if st.button("📥 Download Book Data (JSON)"):
        # Create downloadable JSON
        download_data = {
            "book_state": result["book_state"],
            "task_results": result["task_results"],
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", [])
        }
        
        json_str = json.dumps(download_data, indent=2)
        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"{result['book_state']['parameters']['title'].replace(' ', '_')}_book_data.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()