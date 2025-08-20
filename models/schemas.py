from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class AgeGroup(str, Enum):
    TODDLER = "2-4"
    PRESCHOOL = "4-6"
    EARLY_READER = "6-8"
    MIDDLE_READER = "8-10"


class Genre(str, Enum):
    FANTASY = "fantasy"
    ADVENTURE = "adventure"
    EDUCATIONAL = "educational"
    ANIMAL = "animal"
    MYSTERY = "mystery"
    FRIENDSHIP = "friendship"
    NATURE = "nature"
    SPACE = "space"


class Theme(str, Enum):
    COURAGE = "courage"
    FRIENDSHIP = "friendship"
    LEARNING = "learning"
    IMAGINATION = "imagination"
    KINDNESS = "kindness"
    PERSEVERANCE = "perseverance"
    FAMILY = "family"
    NATURE = "nature"


class BookParameters(BaseModel):
    """Input parameters for book generation"""
    title: str = Field(..., description="Book title")
    genre: Genre = Field(..., description="Book genre")
    age_group: AgeGroup = Field(..., description="Target age group")
    theme: Theme = Field(..., description="Main theme")
    num_pages: int = Field(default=12, ge=6, le=20, description="Number of pages")
    main_character_name: Optional[str] = Field(None, description="Main character name")
    setting: Optional[str] = Field(None, description="Story setting")
    additional_notes: Optional[str] = Field(None, description="Additional creative notes")


class Character(BaseModel):
    """Character definition"""
    name: str
    description: str
    personality: str
    appearance: str
    role: str  # main, supporting, antagonist, etc.
    visual_style: str  # description for consistent illustration


class StoryArc(BaseModel):
    """Overall story structure"""
    beginning: str
    middle: str
    end: str
    conflict: str
    resolution: str
    moral_lesson: Optional[str] = None


class Page(BaseModel):
    """Individual page content"""
    page_number: int
    text: str
    illustration_description: str
    characters_present: List[str]
    setting_description: str
    mood: str  # happy, sad, exciting, etc.


class BookState(BaseModel):
    """Complete book state"""
    parameters: BookParameters
    characters: List[Character]
    story_arc: Optional[StoryArc] = None
    pages: List[Page] = []
    consistency_notes: Dict[str, Any] = {}
    visual_style_guide: Dict[str, str] = {}
    current_page: int = 0
    status: str = "initialized"


class AgentState(BaseModel):
    """State passed between agents"""
    book_state: BookState
    current_task: str
    task_results: Dict[str, Any] = {}
    errors: List[str] = []
    warnings: List[str] = []


class IllustrationRequest(BaseModel):
    """Request for illustration generation"""
    page_number: int
    description: str
    characters: List[str]
    setting: str
    mood: str
    style_guide: Dict[str, str]
    previous_illustrations: List[str] = []  # descriptions of previous pages


class ConsistencyCheck(BaseModel):
    """Consistency validation results"""
    character_consistency: Dict[str, List[str]]
    plot_consistency: List[str]
    style_consistency: List[str]
    age_appropriateness: List[str]
    theme_alignment: List[str]