import pytest
from pawpal_system import Task


def test_task_methods():
    task = Task(id="t1", description="Feed", duration_min=15, priority="high")
    
    assert not task.is_complete
    task.mark_complete()
    assert task.is_complete
    
    assert task.priority_score() == 3 * 10.0 / 15  # 2.0
    
    task_dict = task.to_dict()
    assert task_dict["id"] == "t1"
    assert task_dict["description"] == "Feed"
    assert task_dict["priority"] == "high"


def test_task_invalid_duration():
    with pytest.raises(ValueError, match="duration_min must be greater than zero"):
        Task(id="t2", description="Walk", duration_min=0, priority="medium")

    with pytest.raises(ValueError, match="duration_min must be greater than zero"):
        Task(id="t3", description="Brush", duration_min=-10, priority="low")

    with pytest.raises(ValueError, match="duration_min must be an integer"):
        Task(id="t1", description="Bath", duration_min='', priority="high")


def test_task_invalid_priority():
    with pytest.raises(ValueError, match="priority must be one of"):
        Task(id="t4", description="Walk", duration_min=15, priority="urgent")

    with pytest.raises(ValueError, match="priority must be one of"):
        Task(id="t5", description="Groom", duration_min=20, priority="unknown")


def test_task_mark_complete_idempotent():
    task = Task(id="t6", description="Check teeth", duration_min=10, priority="low")
    assert not task.is_complete

    task.mark_complete()
    assert task.is_complete

    task.mark_complete()
    assert task.is_complete


if __name__ == "__main__":
    pytest.main(["-q"])