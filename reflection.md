# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

    I first began with relationship between the entities i identified from the list: Task, Owner, Pet, and Scheduler. I noticed a system:

    ![alt text](image.png)

- What classes did you include, and what responsibilities did you assign to each?

    Classes I included were, Task, Pet, Owner, ScheduleEntry, and Scheduler

    Task:
    
    + make id
    + generate a description
    + give approx duration time
    + determine priority
    + how frequent the task should be done
    + assign completion status


    Pet:

    + make id for pet
    + receive name
    + species type
    + age
    + tasks (* instance of class above)
    + preferences
    + ability to assign more tasks
    + ability to remove tasks
    + edit tasks
    + tasks still pending
    + list tasks by priority


    Owner:

    + has an id
    + name
    + availability time (min)
    + add pets (>=1)
    + remove pets
    + retrieve all tasks
    + total time needed to perform all pending tasks


    Scheduler:

    + has an owner
    + display date
    + list schedule
    + ability to build daily plan
    + explain decisions


**b. Design changes**

- Did your design change during implementation?

    Yes

- If yes, describe at least one change and why you made it.

    Initially, the Scheduler handled both planning logic and storing scheduled task details. This made it responsible for too much, so I have implemented ScheduleEntry class

    ScheduleEntry:
    
    + Tasks (* instance from the class Task)
    + Pet (* instance from Pet class)
    + start date & time
    + end date & time

    I introduced this class to improve separation of concerns and better encapsulate scheduling data.

    separated concerns:

    * Scheduler focuses on creating the schedule (logic)

    * ScheduleEntry represents individual scheduled items (data)

    This improves modularity and makes the design easier to extend and maintain. In other words, I abstracted the concept of a “scheduled task” into its own class instead of overloading the Scheduler.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
