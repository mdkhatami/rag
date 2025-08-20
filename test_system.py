#!/usr/bin/env python3
"""
Test script for the Multi-Agent Storybook Generator
Demonstrates different book generation scenarios
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import StorybookGenerator
from models.schemas import BookParameters, Genre, AgeGroup, Theme


def test_toddler_book():
    """Test generating a book for toddlers (2-4 years)"""
    print("\n" + "="*60)
    print("🧸 TESTING TODDLER BOOK (2-4 years)")
    print("="*60)
    
    book_params = BookParameters(
        title="The Happy Little Duck",
        genre="animal",
        age_group="2-4",
        theme="friendship",
        num_pages=6,
        main_character_name="Quacky",
        setting="A peaceful pond",
        additional_notes="Use simple, repetitive language and bright colors"
    )
    
    return generate_and_display_book(book_params)


def test_preschool_book():
    """Test generating a book for preschoolers (4-6 years)"""
    print("\n" + "="*60)
    print("🎨 TESTING PRESCHOOL BOOK (4-6 years)")
    print("="*60)
    
    book_params = BookParameters(
        title="The Magic Garden Adventure",
        genre="fantasy",
        age_group="4-6",
        theme="imagination",
        num_pages=10,
        main_character_name="Lily",
        setting="A magical garden with talking flowers",
        additional_notes="Include rhyming text and magical elements"
    )
    
    return generate_and_display_book(book_params)


def test_early_reader_book():
    """Test generating a book for early readers (6-8 years)"""
    print("\n" + "="*60)
    print("📚 TESTING EARLY READER BOOK (6-8 years)")
    print("="*60)
    
    book_params = BookParameters(
        title="The Space Explorer's Quest",
        genre="space",
        age_group="6-8",
        theme="courage",
        num_pages=12,
        main_character_name="Zara",
        setting="A spaceship exploring distant planets",
        additional_notes="Include educational elements about space and teamwork"
    )
    
    return generate_and_display_book(book_params)


def test_middle_reader_book():
    """Test generating a book for middle readers (8-10 years)"""
    print("\n" + "="*60)
    print("🌟 TESTING MIDDLE READER BOOK (8-10 years)")
    print("="*60)
    
    book_params = BookParameters(
        title="The Mystery of the Ancient Library",
        genre="mystery",
        age_group="8-10",
        theme="learning",
        num_pages=16,
        main_character_name="Alex",
        setting="An old library with hidden passages",
        additional_notes="Include puzzle-solving elements and character development"
    )
    
    return generate_and_display_book(book_params)


def generate_and_display_book(book_params: BookParameters):
    """Generate a book and display the results"""
    try:
        # Create the generator
        generator = StorybookGenerator()
        
        # Generate the book
        result = generator.generate_storybook(book_params)
        
        # Display results
        if result.get("success"):
            display_book_results(result, book_params)
            return True
        else:
            print(f"❌ Book generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during book generation: {str(e)}")
        return False


def display_book_results(result: dict, book_params: BookParameters):
    """Display the results of book generation"""
    book_state = result["book_state"]
    task_results = result["task_results"]
    
    print(f"\n✅ Book generated successfully!")
    print(f"📖 Title: {book_state['parameters']['title']}")
    print(f"🎭 Genre: {book_state['parameters']['genre']}")
    print(f"👶 Age Group: {book_state['parameters']['age_group']}")
    print(f"🎯 Theme: {book_state['parameters']['theme']}")
    print(f"📄 Pages: {len(book_state['pages'])}")
    print(f"👥 Characters: {len(book_state['characters'])}")
    
    # Display characters
    print(f"\n👥 Characters:")
    for char in book_state['characters']:
        print(f"  - {char['name']} ({char['role']}): {char['description'][:50]}...")
    
    # Display story arc
    if book_state.get('story_arc'):
        story_arc = book_state['story_arc']
        print(f"\n📖 Story Arc:")
        print(f"  Beginning: {story_arc['beginning'][:100]}...")
        print(f"  Middle: {story_arc['middle'][:100]}...")
        print(f"  End: {story_arc['end'][:100]}...")
        if story_arc.get('moral_lesson'):
            print(f"  Moral: {story_arc['moral_lesson']}")
    
    # Display first few pages
    print(f"\n📄 Sample Pages:")
    for i, page in enumerate(book_state['pages'][:3]):  # Show first 3 pages
        print(f"  Page {page['page_number']}: {page['text'][:80]}...")
        print(f"    Characters: {', '.join(page['characters_present'])}")
        print(f"    Mood: {page['mood']}")
    
    # Display statistics
    print(f"\n📊 Generation Statistics:")
    print(f"  Errors: {len(result.get('errors', []))}")
    print(f"  Warnings: {len(result.get('warnings', []))}")
    
    # Display consistency reports
    if "consistency_check" in task_results:
        consistency = task_results["consistency_check"]
        print(f"\n🔍 Consistency Check:")
        for category, issues in consistency.items():
            if isinstance(issues, list) and issues:
                print(f"  {category}: {len(issues)} issues")
            elif isinstance(issues, dict) and issues:
                total_issues = sum(len(issue_list) for issue_list in issues.values())
                print(f"  {category}: {total_issues} issues")
    
    # Display visual elements
    if "illustrations" in task_results:
        print(f"\n🎨 Visual Elements:")
        print(f"  Page Illustrations: {len(task_results['illustrations'])}")
    
    if "character_reference_sheet" in task_results:
        print(f"  Character Reference Sheet: ✅ Generated")


def run_all_tests():
    """Run all test scenarios"""
    print("🚀 MULTI-AGENT STORYBOOK GENERATOR - TEST SUITE")
    print("="*60)
    
    # Check if API key is available
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        return
    
    # Run tests
    test_results = []
    
    test_results.append(("Toddler Book", test_toddler_book()))
    test_results.append(("Preschool Book", test_preschool_book()))
    test_results.append(("Early Reader Book", test_early_reader_book()))
    test_results.append(("Middle Reader Book", test_middle_reader_book()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")


def test_single_book():
    """Test a single book generation with custom parameters"""
    print("🎯 SINGLE BOOK TEST")
    print("="*60)
    
    # Custom book parameters
    book_params = BookParameters(
        title="The Friendly Dragon's Tea Party",
        genre="fantasy",
        age_group="4-6",
        theme="friendship",
        num_pages=8,
        main_character_name="Sparkle",
        setting="A cozy dragon cave",
        additional_notes="Include tea party elements and friendship themes"
    )
    
    generate_and_display_book(book_params)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the Multi-Agent Storybook Generator")
    parser.add_argument("--single", action="store_true", help="Run single book test")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    
    args = parser.parse_args()
    
    if args.single:
        test_single_book()
    else:
        run_all_tests()