import pytest
from pawpal_system import Task, Pet


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


def test_task_to_dict_immutability():
    task = Task(id="t7", description="Play", duration_min=20, priority="medium")
    task_dict = task.to_dict()

    # ensure required fields exist
    expected_keys = {"id", "description", "duration_min", "priority", "frequency", "constraints", "is_complete"}
    assert set(task_dict.keys()) == expected_keys
    assert task_dict["id"] == "t7"
    assert task_dict["description"] == "Play"

    # mutate returned dict and verify original object is unchanged
    task_dict["description"] = "Naughty"
    task_dict["is_complete"] = True
    assert task.description == "Play"
    assert not task.is_complete


def test_task_priority_score_ordering():
    # create tasks with different priority/duration combos
    high_short = Task(id="hs", description="High short", duration_min=10, priority="high")  # score: 3*10/10 = 3.0
    high_long = Task(id="hl", description="High long", duration_min=30, priority="high")    # score: 3*10/30 = 1.0
    med_short = Task(id="ms", description="Med short", duration_min=10, priority="medium")  # score: 2*10/10 = 2.0
    low_any = Task(id="la", description="Low any", duration_min=20, priority="low")        # score: 1*10/20 = 0.5

    # assert relative ordering: high/short > med/short > high/long > low
    assert high_short.priority_score() > med_short.priority_score()
    assert med_short.priority_score() > high_long.priority_score()
    assert high_long.priority_score() > low_any.priority_score()

    # test sorting by score descending (higher score first)
    tasks = [low_any, high_long, med_short, high_short]
    sorted_tasks = sorted(tasks, key=lambda t: t.priority_score(), reverse=True)
    assert sorted_tasks[0] == high_short
    assert sorted_tasks[1] == med_short
    assert sorted_tasks[2] == high_long
    assert sorted_tasks[3] == low_any


def test_task_frequency_validation():
    # valid frequencies
    Task(id="fd", description="Feed daily", duration_min=15, priority="high", frequency="daily")
    Task(id="fw", description="Feed weekly", duration_min=15, priority="high", frequency="weekly")
    Task(id="fo", description="Feed once", duration_min=15, priority="high", frequency="once")

    # invalid frequency
    with pytest.raises(ValueError, match="frequency must be one of"):
        Task(id="fi", description="Feed invalid", duration_min=15, priority="high", frequency="monthly")

def test_pet_add_task():
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    
    pet.add_task(t1)
    assert len(pet.tasks) == 1
    assert pet.tasks[0].id == "t1"


def test_pet_remove_task():
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    t2 = Task(id="t2", description="Play", duration_min=30, priority="medium")
    
    pet.add_task(t1)
    pet.add_task(t2)
    
    assert pet.remove_task("t1") is True
    assert len(pet.tasks) == 1
    assert pet.tasks[0].id == "t2"
    
    assert pet.remove_task("nonexistent") is False


def test_pet_edit_task():
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    
    pet.add_task(t1)
    assert pet.edit_task("t1", duration_min=20) is True
    assert pet.tasks[0].duration_min == 20
    
    assert pet.edit_task("nonexistent", duration_min=25) is False


def test_pet_get_pending_tasks():
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    t2 = Task(id="t2", description="Play", duration_min=30, priority="medium")
    
    pet.add_task(t1)
    pet.add_task(t2)
    
    pending = pet.get_pending_tasks()
    assert len(pending) == 2
    
    t1.mark_complete()
    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].id == "t2"


def test_pet_get_tasks_by_priority():
    pet = Pet(id="p1", name="Mochi", species="cat", age=3)
    t1 = Task(id="t1", description="Feed", duration_min=15, priority="high")
    t2 = Task(id="t2", description="Play", duration_min=30, priority="low")
    t3 = Task(id="t3", description="Groom", duration_min=20, priority="medium")
    
    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)
    
    prioritized = pet.get_tasks_by_priority()
    assert len(prioritized) == 3
    assert prioritized[0].priority == "high"
    assert prioritized[1].priority == "medium"
    assert prioritized[2].priority == "low"

if __name__ == "__main__":
    pytest.main(["-q"])