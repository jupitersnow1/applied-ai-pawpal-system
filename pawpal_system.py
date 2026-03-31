"""
PawPal+ Backend Logic Layer

Contains the core domain classes for pet care scheduling:
- Task: Individual care activity
- Pet: Pet entity with associated tasks
- Owner: Pet owner managing multiple pets
- Scheduler: Orchestrates daily plan generation
- ScheduleEntry: A scheduled task with time slot
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import List, Dict, Optional

PRIORITY_LEVELS = {"low": 1, "medium":2, "high":3}
VALID_FREQUENCIES = {"daily", "weekly", "once"}


@dataclass
class Task:
    """Represents a single pet care activity."""
    
    id: str
    description: str
    duration_min: int
    priority: str = "medium"
    frequency: str = "daily"
    constraints: Dict[str, str] = field(default_factory=dict)
    is_complete: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.duration_min, int) or isinstance(self.duration_min, bool):
            raise ValueError("duration_min must be an integer")
        if self.duration_min <= 0:
            raise ValueError("duration_min must be greater than zero")
        if self.priority not in PRIORITY_LEVELS:
            raise ValueError(f"priority must be one of {list(PRIORITY_LEVELS.keys())}")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(VALID_FREQUENCIES)}")
    
    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_complete = True
    
    def priority_score(self) -> float:
        """Calculate a numeric score for prioritization."""
        base = PRIORITY_LEVELS.get(self.priority, 1)
        return base * 10.0 / self.duration_min
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary format."""
        return{
            "id" : self.id, 
            "description": self.description, 
            "duration_min": self.duration_min, 
            "priority": self.priority, 
            "frequency": self.frequency, 
            "constraints": self.constraints,
            "is_complete": self.is_complete
        }


@dataclass
class Pet:
    """Represents a pet with associated care tasks."""
    
    id: str
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)
    preferences: Dict[str, str] = field(default_factory=dict)
    
    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID. Returns True if successful."""
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                self.tasks.pop(i)
                return True
        return False
    
    def edit_task(self, task_id: str, **updates) -> bool:
        """Edit a task's attributes. Returns True if successful."""
        for t in self.tasks:
            if t.id == task_id:
                for k, v in updates.items():
                    if hasattr(t, k):
                        setattr(t, k, v)
                return True
        return False
    
    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.is_complete]
    
    def get_tasks_by_priority(self) -> List[Task]:
        """Return tasks sorted by priority (highest first)."""
        return sorted(self.get_pending_tasks(), key=lambda t: PRIORITY_LEVELS.get(t.priority, 1), reverse=True)


@dataclass
class Owner:
    """Represents a pet owner managing multiple pets."""
    
    id: str
    name: str
    available_time_min: int
    pets: List[Pet] = field(default_factory=list)
    global_preferences: Dict[str, str] = field(default_factory=dict)
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        pass
    
    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by ID. Returns True if successful."""
        pass
    
    def get_all_tasks(self) -> List[Task]:
        """Return all pending tasks across all pets."""
        pass
    
    def total_time_needed(self) -> int:
        """Calculate total minutes needed for all pending tasks."""
        pass


@dataclass
class ScheduleEntry:
    """A task scheduled for a specific time slot."""
    
    task: Task
    pet: Pet
    start: datetime
    end: datetime


@dataclass
class Scheduler:
    """Orchestrates daily schedule generation based on tasks and constraints."""
    
    owner: Owner
    date: date = field(default_factory=date.today)
    schedule: List[ScheduleEntry] = field(default_factory=list)
    overflow_tasks: List[Task] = field(default_factory=list)
    
    def build_daily_plan(self, start_time: time = None) -> List[ScheduleEntry]:
        """
        Generate a daily plan for the owner.
        
        Returns a list of scheduled task entries.
        Populates self.overflow_tasks with tasks that didn't fit.
        """
        pass
    
    def apply_constraints(self, tasks: List[Task]) -> List[Task]:
        """Filter tasks based on owner constraints (time, preferences, etc.)."""
        pass
    
    def explain_decision(self) -> str:
        """Generate a human-readable explanation of why tasks were scheduled."""
        pass
