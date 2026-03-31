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

if __name__ == "__main__":
    pytest.main(["-q"])