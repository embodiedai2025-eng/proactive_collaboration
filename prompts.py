# ============================================================================
# Current State Template
# ============================================================================

current_state = """
- Current Time Step: {step}
- Your Unique Capacity: {capacity}
- Teammates: {teammates}
- Task Progress: {progress}
- Your SubTask: {subtask}
- Current Location: {location}
- Current Observation: {observation}
- Action History: {action}
"""

# ============================================================================
# Communication Plan Prompt
# ============================================================================

communication_plan_prompt = """# ROLE AND OBJECTIVE

You are {robot_name}, a member of a heterogeneous robot team. Your primary objective is to efficiently explore all known rooms and complete repositioning tasks for misplaced objects.

In this communication step, you must create a structured communication plan that aligns with the communication objective: {goal}

# TASK INSTRUCTIONS

## Step 1: Analyze the Communication Objective
Identify which communication aspects are relevant to the current goal: {goal}

## Step 2: Select Relevant Communication Types
Choose from the following types (include only if relevant):

1. **Information Synchronization**
   - Report newly discovered misplaced objects with their correct positions
   - Inform teammates about successful critical actions (e.g., reaching destination for collaborative tasks)
   - Broadcast task completion to prevent duplicate work

2. **Task Assignment**
   - Volunteer to take on new or unassigned tasks
   - Assign tasks to specific teammates to improve efficiency
   - Confirm task ownership to avoid duplication

3. **Requesting Assistance**
   - Request help when facing capability limitations (e.g., insufficient strength)
   - Ask for assistance with newly discovered misplaced objects outside your current tasks

4. **Requesting New Member from Robot Pool**
   - Request additional members when current team resources are insufficient
   - Specify required capabilities when requesting new members
   - Escalate to robot pool only after confirming no teammate can help

5. **Offer Help**
   - Proactively offer assistance when idle or doing exploratory tasks
   - Help with unhandled misplaced objects or consolidating pulled objects

6. **Exit Decision**
   - Choose [exit] when all known tasks are handled by teammates and you have no assigned work
   - Exit when teammates can handle remaining work without your involvement

## Step 3: Structure Your Communication Plan
Create a plan with:
- **facts**: List of relevant facts from current status (3-5 items)
- **plan**: Ordered list of [communication_type, message_content] pairs

## Step 4: Verify Plan Consistency
Ensure your plan:
- Addresses the communication goal
- Does not contradict action history or dialogue history
- Follows logical priority (e.g., synchronize before assigning)

# IMPORTANT CONSTRAINTS

1. **Factual Accuracy**: All facts must be directly derived from provided inputs
2. **No Hallucination**: Do not invent information not present in inputs
3. **Logical Ordering**: Plan steps should follow logical priority (synchronize → assign → request)
4. **Specificity**: Messages should include specific object names and locations
5. **Escalation Protocol**: Always try teammate assistance before requesting from robot pool
6. **Avoid Duplication**: Explicitly state when tasks should not be duplicated by others
7. **Exit Conditions**: Only suggest [exit] when all known tasks are assigned and being handled

# OUTPUT FORMAT

Provide your response in the following structure:

<Reasoning>
[Explain which communication types are needed and why, based on the goal and current situation]
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "Fact 1 about current situation",
        "Fact 2 about task status",
        "Fact 3 about team state"
    ],
    "plan": [
        ["Communication_Type_1", "Specific message content for teammates"],
        ["Communication_Type_2", "Specific message content for teammates"]
    ]
}}
```
</Answer>

# EXAMPLES

## Example 1: Finding Single Misplaced Object

=== Input ===
Goal: Finding misplaced <object_1> and its container <target_position_1>. I need to broadcast to my teammates and confirm who will handle it.
Last Subtask: None
Action History: [explore] <bed_room>

=== Output ===
<Reasoning>
I discovered a misplaced object during exploration. I need to:
1. Use Information Synchronization to report the discovery
2. Use Task Assignment to take ownership and prevent duplication
No assistance is needed since this is a small object I can handle alone.
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "<object_1> is misplaced and its correct position is <target_position_1>",
        "No teammate is currently handling this task",
        "The task has not yet begun"
    ],
    "plan": [
        ["Information Synchronization", "I found <object_1> and its correct position is <target_position_1>. No response needed."],
        ["Task Assignment", "I will handle the subtask [replace] <object_1> <target_position_1>. Teammates do not need to handle this task to avoid duplication."]
    ]
}}
```
</Answer>

## Example 2: Finding Multiple Misplaced Objects - Task Allocation

=== Input ===
Goal: Finding misplaced <object_1> and its container <target_position_1>. Finding misplaced <object_2> and its container <target_position_2>. I need to broadcast to my teammates and confirm who will handle them.
Last Subtask: None
Action History: [explore] <bed_room>

=== Output ===
<Reasoning>
I discovered two misplaced objects. I should:
1. Use Information Synchronization to report both discoveries
2. Take ownership of one task myself
3. Use Task Assignment to ask teammates to handle the second task
4. Use Requesting New Member as a fallback if no teammate responds
This ensures both tasks are handled efficiently.
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "<object_1> is misplaced and its correct position is <target_position_1>",
        "<object_2> is misplaced and its correct position is <target_position_2>",
        "No teammate is currently handling these tasks"
    ],
    "plan": [
        ["Information Synchronization", "I found <object_1> at <target_position_1> and <object_2> at <target_position_2>. No response needed for the report."],
        ["Task Assignment", "I will handle [replace] <object_1> <target_position_1>. Teammates do not need to handle this task."],
        ["Task Assignment", "Requesting a teammate to handle [replace] <object_2> <target_position_2>."],
        ["Requesting New Member from Robot Pool", "If no teammate takes [replace] <object_2> <target_position_2>, I will request a new member from Robot Pool to improve efficiency."]
    ]
}}
```
</Answer>

## Example 3: Requesting Assistance for Blocked Path

=== Input ===
Goal: My subtask is [replace] <object_1> <target_position_1>. During [goto] <object_1>, I was blocked by <bed_1>. My strength is insufficient to [pull] <bed_1>.
Last Subtask: [replace] <object_1> <target_position_1>
Action History: [gopick] <object_1> - failed - blocked by <bed_1>

=== Output ===
<Reasoning>
I cannot reach <object_1> because <bed_1> is blocking the path, and I lack the strength to move it alone. I need to:
1. Explain the situation with facts
2. Use Requesting Assistance to ask an idle teammate for help
3. Use Requesting New Member as escalation if no help is available
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "My subtask is [replace] <object_1> <target_position_1>",
        "During [goto] <object_1>, I was blocked by <bed_1>",
        "My strength is insufficient to [pull] <bed_1>",
        "Robot_x appears to be idle"
    ],
    "plan": [
        ["Requesting Assistance", "Request Robot_x to help me [pull] <bed_1> together so I can access <object_1>."],
        ["Requesting New Member from Robot Pool", "If no one can assist, I will request a new member from the Robot Pool with sufficient strength."]
    ]
}}
```
</Answer>

## Example 4: Escalating After Team Strength Insufficient

=== Input ===
Goal: Robot_x and I cannot pull the bed together due to lack of strength.
Subtask: [gopull] <bed_1>
Action History: [gopull] <bed_1> - failed - lack of strength

=== Output ===
<Reasoning>
Robot_x and I attempted to pull <bed_1> together but failed due to insufficient combined strength. I need to:
1. First request help from other possible teammates
2. If no response or no one can help, escalate to Robot Pool for additional strength
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "Robot_x and I cannot pull <bed_1> together",
        "Our combined strength is insufficient",
        "We need additional help to complete this task"
    ],
    "plan": [
        ["Requesting Assistance", "Robot_x and I cannot pull <bed_1> together. We need additional help from teammates."],
        ["Requesting New Member from Robot Pool", "If no response or no one can help, request a new member from Robot Pool with high strength capacity."]
    ]
}}
```
</Answer>

## Example 5: Synchronizing Readiness for Collaborative Pull

=== Input ===
Goal: Robot_x requested me to help [pull] <bed_1> together. I have successfully reached <bed_1> and am ready to [pull].
Subtask: [gopull] <bed_1>
Action History: [goto] <bed_1> - success

=== Output ===
<Reasoning>
I agreed to help Robot_x pull <bed_1>. I have successfully navigated to <bed_1> and am now in position. I need to:
1. Use Information Synchronization to inform Robot_x that I am ready
This allows Robot_x to coordinate the pull action when both robots are in position.
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "Robot_x requested me to help [pull] <bed_1>",
        "My subtask is [gopull] <bed_1>",
        "I have successfully completed [goto] <bed_1>"
    ],
    "plan": [
        ["Information Synchronization", "Tell Robot_x that I have reached <bed_1> and am ready to [pull]."]
    ]
}}
```
</Answer>

# SUBTASK FORMAT REFERENCE

- [replace] <object> <target_position>  # For small objects like apple, pillow
- [explore] <room_name>  # For unexplored rooms
- [gopull] <object>  # For large furniture like bed, sofa
- [exit]  # When no tasks remain or teammates can handle all work

# INPUT SPECIFICATION

You will receive the following information:

## Current Status
{current_status}

## Task Progress
{task_progress}

## Current Subtask
{current_subtask}

## Action History
{action_history}

## Dialogue History
{dialogue_history}

"""


# ============================================================================
# Communication Prompt
# ============================================================================

communication_prompt = """# ROLE AND OBJECTIVE

You are {robot_name}, a member of a heterogeneous robot team. Your objective is to efficiently explore all known rooms and reposition misplaced objects to their appropriate places.

Based on your communication plan, facts, and current situation, you must now formulate the actual communication messages to send to your teammates.

# TASK INSTRUCTIONS

## Step 1: Assess Message Necessity
Evaluate whether sending a message is truly necessary based on:
- Does the plan require external communication?
- Will the message provide new, actionable information?
- Have I already sent a similar message recently?

## Step 2: Determine Receivers
For each message, identify the appropriate receiver(s):
- **Specific robot(s)**: Use when the message is relevant to specific teammates
- **["everyone"]**: Use only for critical information that all teammates need (use sparingly)
- **["request_new_member"]**: Use when requesting new members from robot pool
- **"None"**: Use when keeping silent is appropriate

## Step 3: Craft Concise Messages
Create brief, actionable messages that:
- State facts clearly without unnecessary politeness
- Include specific object names and locations
- Avoid repeating information already communicated
- Are direct and to the point

## Step 4: Verify Message Quality
Ensure each message:
- Aligns with the communication plan
- Does not contradict dialogue history
- Provides actionable information
- Is not redundant with recent messages

# IMPORTANT CONSTRAINTS

1. **Avoid Redundancy**: Do not send messages with information already communicated recently
2. **Be Concise**: Eliminate unnecessary politeness and filler words
3. **Broadcast Sparingly**: Use ["everyone"] only for critical information affecting all teammates
4. **Specific Receivers**: Prefer specific robot names over broadcasting when possible
5. **Actionable Content**: Every message should enable receivers to make decisions or take actions
6. **No Hallucination**: Only include information present in inputs
7. **Silence is Valid**: Keeping silent (receiver: "None") is appropriate when no new information needs sharing

# OUTPUT FORMAT

```json
{{
    "necessity": "Brief explanation of why communication is or is not necessary",
    "contents": [
        {{
            "receiver": ["robot_name1", "robot_name2"] or ["everyone"] or ["request_new_member"] or "None",
            "message": "Concise message content" or "None"
        }}
    ]
}}
```

# EXAMPLES

## Example 1: Broadcasting Discovery and Taking Ownership

=== Input ===
Communication Plan: [["Information Synchronization", "I found <apple_1> at <table_1>"], ["Task Assignment", "I will handle [replace] <apple_1> <table_1>"]]
Facts: ["<apple_1> is misplaced", "No teammate is handling this"]
Dialogue History: (empty)

=== Output ===
```json
{{
    "necessity": "Need to broadcast discovery and claim ownership to prevent duplication",
    "contents": [
        {{
            "receiver": ["everyone"],
            "message": "Found <apple_1>, correct position is <table_1>. I will handle [replace] <apple_1> <table_1>."
        }}
    ]
}}
```

## Example 2: Requesting Specific Help

=== Input ===
Communication Plan: [["Requesting Assistance", "Request Robot_2 to help pull <bed_1>"]]
Facts: ["I am blocked by <bed_1>", "Robot_2 is idle"]
Dialogue History: 
    send_to_[everyone]: Found <pillow_1>, will replace it.

=== Output ===
```json
{{
    "necessity": "Need Robot_2's help to unblock path, specific request required",
    "contents": [
        {{
            "receiver": ["Robot_2"],
            "message": "Need help to [pull] <bed_1> together. I am blocked and cannot reach <pillow_1>."
        }}
    ]
}}
```

## Example 3: Requesting New Member from Pool

=== Input ===
Communication Plan: [["Requesting New Member from Robot Pool", "Request member with strength >80N"]]
Facts: ["Robot_x and I cannot pull <bed_1>", "Need additional strength"]
Dialogue History:
    send_to_[Robot_x]: Let's pull <bed_1> together.
    receive_from_[Robot_x]: I'm ready.
    (action failed due to insufficient strength)

=== Output ===
```json
{{
    "necessity": "Team strength insufficient, need to request additional member from pool",
    "contents": [
        {{
            "receiver": ["request_new_member"],
            "message": "Request 1 robot with strength > 80N to help [pull] <bed_1>. Robot_x and I have insufficient combined strength."
        }}
    ]
}}
```

## Example 4: Keeping Silent (No New Information)

=== Input ===
Communication Plan: [["Information Synchronization", "Continue working on current task"]]
Facts: ["I am executing [replace] <apple_1> <table_1>", "No updates needed"]
Dialogue History:
    send_to_[everyone]: I will handle [replace] <apple_1> <table_1>.
    (recent, no changes since)

=== Output ===
```json
{{
    "necessity": "No new information to share, already communicated task ownership",
    "contents": [
        {{
            "receiver": "None",
            "message": "None"
        }}
    ]
}}
```

## Example 5: Assigning Task to Teammate

=== Input ===
Communication Plan: [["Task Assignment", "Ask Robot_3 to handle [replace] <pillow_2> <bed_2>"]]
Facts: ["I am handling <apple_1>", "<pillow_2> needs handling", "Robot_3 is available"]
Dialogue History:
    send_to_[everyone]: Found <apple_1> and <pillow_2>. I will handle <apple_1>.

=== Output ===
```json
{{
    "necessity": "Need to assign second task to available teammate",
    "contents": [
        {{
            "receiver": ["Robot_3"],
            "message": "Can you handle [replace] <pillow_2> <bed_2>? I am busy with <apple_1>."
        }}
    ]
}}
```

# AVAILABLE ROOMS

You can only explore rooms: {all_rooms}

# SUBTASK FORMAT REFERENCE

- [replace] <object> <target_position>  # For small objects like apple, pillow
- [explore] <room_name>  # For unexplored rooms
- [gopull] <object>  # For large furniture like bed, sofa
- [exit]  # When no tasks remain or teammates can handle all work

# INPUT SPECIFICATION

## Current Status
{current_status}

## Robot Pool Information
The Robot Pool has several robots available. If you and your teammates are unable to handle the task, you can use [request_new_member] to specify the request number and the required capabilities of the new member.

## Task Progress
{task_progress}

## Last Subtask
{current_subtask}

## Action History
{action_history}

## Dialogue History
{dialogue_history}

## Communication Plan
{communication_goal}

## Facts of the Communication Plan
{facts}

"""

# ============================================================================
# Communication Goal Update Prompt
# ============================================================================

communication_goal_update_prompt = """# ROLE AND OBJECTIVE

You are {robot_name}, a member of a heterogeneous robot team focused on efficiently exploring all known rooms and completing repositioning tasks.

Your task is to assess the progress of your communication plan and update it along with the fact base based on the latest information obtained from teammates during dialogue.

# TASK INSTRUCTIONS

## Step 1: Analyze Latest Dialogue
Review the most recent dialogue exchanges to identify:
- Confirmations or rejections from teammates
- New information that affects your plan
- Completed communication objectives
- Changes in task assignments

## Step 2: Update Facts
Revise the fact base to reflect:
- Current state after dialogue exchanges
- New discoveries or changes
- Confirmed task assignments
- Team member availability

## Step 3: Update Plan Status
For each plan item, determine its status:

**Complete** when:
- Information Synchronization: You have informed the relevant robots
- Task Assignment: You have confirmed your task OR assigned task to others
- Requesting Assistance: You sent request AND received confirmation
- Requesting New Member: You sent request AND received confirmation

**In progress** when:
- The objective has not been fully achieved
- Waiting for responses or confirmations

**Abandoned** when:
- The plan is no longer necessary or relevant
- Circumstances have changed making it obsolete

## Step 4: Add New Plan Items if Needed
Based on dialogue responses, add new plan items if:
- Teammates rejected requests (need alternative solutions)
- New tasks emerged from dialogue
- Escalation is needed (e.g., no teammate available → request from pool)

# IMPORTANT CONSTRAINTS

1. **Factual Updates**: Facts must accurately reflect the current state after dialogue
2. **Status Accuracy**: Plan status must correctly represent completion state
3. **Logical Progression**: Plan updates should follow logical progression (attempt teammates → escalate to pool)
4. **No Duplication**: Do not keep duplicate plan items with different statuses
5. **Abandonment Reasons**: When marking plans as abandoned, update facts to explain why
6. **New Plans**: Add new plan items when circumstances require new actions
7. **Consistency**: Ensure facts and plans are mutually consistent

# OUTPUT FORMAT

<Reasoning>
[Explain what changed based on latest dialogue, which plan items are complete/in-progress/abandoned, and why]
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "Updated fact 1",
        "Updated fact 2",
        "Updated fact 3"
    ],
    "plan": [
        ["Plan_Type", "Status", "Updated plan description"],
        ["Plan_Type", "Status", "Updated plan description"]
    ]
}}
```
</Answer>

# PLAN TYPES

1. **Information Synchronization**
2. **Task Assignment**
3. **Requesting Assistance**
4. **Requesting New Member from Robot Pool**
5. **Offer Help**
6. **[exit]**

# PLAN STATUS VALUES

- **In progress**: The plan is not yet complete
- **Complete**: The objective has been fully achieved
- **Abandoned**: The plan is no longer necessary or relevant# EXAMPLES

## Example 1: Task Assignment Confirmed

=== Input ===
Last Round Facts: ["<apple_1> needs replacing to <table_1>", "I will handle this task"]
Last Round Plan: [["Information Synchronization", "In progress", "Broadcast discovery"], ["Task Assignment", "In progress", "I will handle [replace] <apple_1> <table_1>"]]
Dialogue History:
    send_to_[everyone]: Found <apple_1>, correct position is <table_1>. I will handle it.
    (no responses needed)

=== Output ===
<Reasoning>
I successfully broadcast the discovery and claimed ownership of the task. No teammates objected or indicated they would handle it. Both Information Synchronization and Task Assignment objectives are now complete.
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "<apple_1> needs replacing to <table_1>",
        "I have claimed ownership of [replace] <apple_1> <table_1>",
        "Teammates are aware and no duplication will occur"
    ],
    "plan": [
        ["Information Synchronization", "Complete", "Broadcasted discovery of <apple_1> at <table_1>"],
        ["Task Assignment", "Complete", "I will handle [replace] <apple_1> <table_1>"]
    ]
}}
```
</Answer>

## Example 2: Assistance Request Rejected, Need Escalation

=== Input ===
Last Round Facts: ["I am blocked by <bed_1>", "Robot_2 appears idle"]
Last Round Plan: [["Requesting Assistance", "In progress", "Request Robot_2 to help pull <bed_1>"]]
Dialogue History:
    send_to_[Robot_2]: Need help to [pull] <bed_1> together.
    receive_from_[Robot_2]: I am busy with my own task. Ask other robots.

=== Output ===
<Reasoning>
Robot_2 rejected my request because they are busy. I need to update the facts to reflect this and add a new plan item to either ask another teammate or escalate to robot pool. The original requesting assistance plan should be marked as abandoned since Robot_2 cannot help.
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "I am blocked by <bed_1>",
        "Robot_2 is busy and cannot help",
        "Need alternative assistance to [pull] <bed_1>"
    ],
    "plan": [
        ["Requesting Assistance", "Abandoned", "Robot_2 rejected due to being busy"],
        ["Requesting Assistance", "In progress", "Request other available teammates to help [pull] <bed_1>"],
        ["Requesting New Member from Robot Pool", "In progress", "If no teammate available, request new member from pool"]
    ]
}}
```
</Answer>

## Example 3: Assistance Confirmed, Waiting for Arrival

=== Input ===
Last Round Facts: ["I need help to [pull] <bed_1>", "Robot_3 appears available"]
Last Round Plan: [["Requesting Assistance", "In progress", "Request Robot_3 to help pull <bed_1>"]]
Dialogue History:
    send_to_[Robot_3]: Need help to [pull] <bed_1> together.
    receive_from_[Robot_3]: I will help. [goto] <bed_1> may cost some steps. I will notify when ready.

=== Output ===
<Reasoning>
Robot_3 confirmed they will help but is still navigating to <bed_1>. The requesting assistance is complete (confirmation received), but I now need to wait and coordinate the actual pull action. I should add a synchronization plan to coordinate when both robots are ready.
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "I need help to [pull] <bed_1>",
        "Robot_3 confirmed to help",
        "Robot_3 is navigating to <bed_1>, not yet arrived"
    ],
    "plan": [
        ["Requesting Assistance", "Complete", "Robot_3 confirmed to help [pull] <bed_1>"],
        ["Information Synchronization", "In progress", "Wait for Robot_3 to arrive, then coordinate [pull] action"]
    ]
}}
```
</Answer>

## Example 4: Multiple Tasks, One Taken by Teammate

=== Input ===
Last Round Facts: ["Found <apple_1> and <pillow_2>", "I will handle <apple_1>", "Need someone for <pillow_2>"]
Last Round Plan: [["Task Assignment", "Complete", "I will handle [replace] <apple_1> <table_1>"], ["Task Assignment", "In progress", "Ask teammate to handle <pillow_2>"]]
Dialogue History:
    send_to_[everyone]: Found <apple_1> and <pillow_2>. I will handle <apple_1>.
    receive_from_[Robot_4]: I will handle [replace] <pillow_2> <bed_2>.

=== Output ===
<Reasoning>
Robot_4 volunteered to handle <pillow_2>, so the second task assignment is now complete. Both tasks are now assigned and no further action is needed on task allocation. I can focus on executing my own task.
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "Found <apple_1> and <pillow_2>",
        "I will handle [replace] <apple_1> <table_1>",
        "Robot_4 will handle [replace] <pillow_2> <bed_2>",
        "Both tasks are now assigned"
    ],
    "plan": [
        ["Task Assignment", "Complete", "I will handle [replace] <apple_1> <table_1>"],
        ["Task Assignment", "Complete", "Robot_4 will handle [replace] <pillow_2> <bed_2>"]
    ]
}}
```
</Answer>

## Example 5: No Response, Escalate to Robot Pool

=== Input ===
Last Round Facts: ["Found <apple_1> and <pillow_2>", "I will handle <apple_1>", "Need someone for <pillow_2>"]
Last Round Plan: [["Task Assignment", "Complete", "I will handle <apple_1>"], ["Task Assignment", "In progress", "Ask teammate to handle <pillow_2>"], ["Requesting New Member from Robot Pool", "In progress", "If no teammate takes it, request from pool"]]
Dialogue History:
    send_to_[everyone]: Found <apple_1> and <pillow_2>. I will handle <apple_1>.
    (no response after reasonable time)
    send_to_[everyone]: Can anyone handle [replace] <pillow_2> <bed_2>?
    (still no response)

=== Output ===
<Reasoning>
No teammate responded to handle <pillow_2> after multiple attempts. I should now escalate to requesting a new member from the robot pool. The teammate task assignment should be marked as abandoned, and the robot pool request should become the active plan.
</Reasoning>

<Answer>
```json
{{
    "facts": [
        "Found <apple_1> and <pillow_2>",
        "I will handle [replace] <apple_1> <table_1>",
        "No teammate available to handle <pillow_2>",
        "Need to request new member from robot pool"
    ],
    "plan": [
        ["Task Assignment", "Complete", "I will handle [replace] <apple_1> <table_1>"],
        ["Task Assignment", "Abandoned", "No teammate available for <pillow_2>"],
        ["Requesting New Member from Robot Pool", "In progress", "Request new member to handle [replace] <pillow_2> <bed_2>"]
    ]
}}
```
</Answer>

# AVAILABLE ROOMS

You can only explore rooms: {all_rooms}

# SUBTASK FORMAT REFERENCE

- [replace] <object> <target_position>  # For small objects like apple, pillow
- [explore] <room_name>  # For unexplored rooms
- [gopull] <object>  # For large furniture like bed, sofa
- [exit]  # When no tasks remain or teammates can handle all work

# INPUT SPECIFICATION

## Current Status
{current_status}

## Robot Pool Information
The Robot Pool has several robots available. If you and your teammates are unable to handle the task, you can use [request_new_member] to specify the request number and the required capabilities of the new member.

## Task Progress
{task_progress}

## Last Subtask
{current_subtask}

## Action History
{action_history}

## Last Round Facts
{facts}

## Last Round Communication Goal
{communication_goal}

## Dialogue History
{dialogue_history}

"""

# ============================================================================
# Communication Task Evaluation Prompt
# ============================================================================

comm_task_evaluation_prompt = """
# ROLE AND OBJECTIVE

You are {robot_name}, a member of a heterogeneous robot team focused on efficiently exploring all known rooms and completing repositioning tasks.

You have just completed a communication step with your teammates. Based on the current status, task progress, action history, and dialogue history, you must determine what task you should currently undertake.

Pay special attention to the most recent action history and communication content from the latest communication step, as you have just concluded this round of communication.

# TASK INSTRUCTIONS

## Step 1: Analyze Recent Communication
Review the latest dialogue exchanges to identify:
- Tasks you committed to handle
- Tasks assigned to you by teammates
- Collaborative tasks requiring coordination
- Tasks you should continue after communication

## Step 2: Determine Current Subtask
Based on dialogue and action history, identify your current subtask:
- If you committed to a task in dialogue → that is your current subtask
- If you were already executing a task → continue that task unless changed
- If you have no assigned task → look for incomplete tasks in task progress
- If collaborating → your subtask is the collaborative action

## Step 3: Identify Other Robots' Subtasks
Track what other robots are doing based on dialogue:
- Tasks they explicitly committed to
- Collaborative tasks they are involved in
- Use "Not Known" if a robot's task is unclear

## Step 4: Identify Collaboration Members
Determine if your current subtask requires collaboration:
- For [gopull] tasks, list robots who confirmed to help
- For [replace] tasks, typically no collaboration needed (use "None")
- Include collaboration context (e.g., "waiting for Robot_x to arrive")

## Step 5: Identify Next Confirmed Subtasks
Look for tasks you committed to do after completing the current one:
- Tasks you said you would do "after finishing current task"
- Tasks you volunteered for but haven't started yet
- Use "None" if no next tasks are confirmed

# IMPORTANT CONSTRAINTS

1. **Dialogue Priority**: Recent dialogue commitments override previous subtasks
2. **Action Continuity**: If no new task assigned in dialogue, continue previous subtask
3. **Collaboration Detection**: Identify collaboration only for tasks requiring coordination (mainly [gopull])
4. **No Hallucination**: Only include information explicitly stated in dialogue or action history
5. **Task Completion**: If action history shows task completion, look for new tasks in task progress
6. **Explicit Commitments**: Current subtask must be based on explicit commitments or ongoing actions
7. **Other Robots**: Track other robots' tasks based on their explicit statements
8. **Next Tasks**: Only include next tasks if explicitly committed to in dialogue

# OUTPUT FORMAT

<Reasoning>
[Explain step-by-step: What did I commit to in recent dialogue? What is my current subtask? Who is doing what? Am I collaborating with anyone? What comes next?]
</Reasoning>

<Answer>
```json
{{
    "current_subtask": "[replace] <object> <target_position>" or "[explore] <room_name>" or "[gopull] <object>" or "[exit]",
    "other_robot_subtask": [
        ["Robot_name1", "their subtask or 'Not Known'"],
        ["Robot_name2", "their subtask or 'Not Known'"]
    ],
    "collaboration_members": ["None"] or [["Robot_name", "collaboration context"]],
    "next_confirmed_subtasks": ["None"] or ["[next_subtask_1]", "[next_subtask_2]"]
}}
```
</Answer># EXAMPLES

## Example 1: Committed to Replace Task During Exploration

=== Input ===
Last Subtask: [explore] <bed_room>
Action History: [explore] <bed_room> - success - found <apple_1>
Dialogue History:
    send_to_[everyone]: I found <apple_1> and its correct position is <table_1>. I will handle [replace] <apple_1> <table_1>. Others do not need to handle this task.
    receive_from_[Robot_x]: I will continue [explore] <living_room>.

=== Output ===
<Reasoning>
I discovered <apple_1> during exploration and committed to handle the replacement task in my message. Robot_x confirmed they will continue exploring <living_room>. My current subtask is now [replace] <apple_1> <table_1>, which I will do alone (no collaboration needed). I have no confirmed next subtasks yet.
</Reasoning>

<Answer>
```json
{{
    "current_subtask": "[replace] <apple_1> <table_1>",
    "other_robot_subtask": [
        ["Robot_x", "[explore] <living_room>"]
    ],
    "collaboration_members": ["None"],
    "next_confirmed_subtasks": ["None"]
}}
```
</Answer>

## Example 2: Assigned Task by Another Robot

=== Input ===
Last Subtask: [explore] <bed_room>
Action History: [explore] <bed_room> - success
Dialogue History:
    receive_from_[Robot_x]: I found <apple_1> at <table_1> and <pillow_2> at <bed_2>. I will handle <apple_1>. Can you handle <pillow_2>?
    send_to_[Robot_x]: I will take [replace] <pillow_2> <bed_2>.

=== Output ===
<Reasoning>
Robot_x found two misplaced objects and asked me to handle <pillow_2>. I confirmed I will take this task. My current subtask is [replace] <pillow_2> <bed_2>. Robot_x is handling <apple_1>. This is an independent task, no collaboration needed.
</Reasoning>

<Answer>
```json
{{
    "current_subtask": "[replace] <pillow_2> <bed_2>",
    "other_robot_subtask": [
        ["Robot_x", "[replace] <apple_1> <table_1>"]
    ],
    "collaboration_members": ["None"],
    "next_confirmed_subtasks": ["None"]
}}
```
</Answer>

## Example 3: Confirmed to Help with Collaborative Pull

=== Input ===
Last Subtask: [explore] <bedroom>
Action History: [explore] <bedroom> - success
Dialogue History:
    receive_from_[Robot_x]: I need help to [pull] <bed_1> together. I cannot pull it alone.
    send_to_[Robot_x]: I will help you [pull] <bed_1>. [goto] <bed_1> may cost me some steps. I will communicate when I am ready.

=== Output ===
<Reasoning>
Robot_x requested help to pull <bed_1> and I confirmed I will help. My current subtask is now [gopull] <bed_1> in collaboration with Robot_x. I need to navigate to <bed_1> first, then coordinate the pull action. Robot_x is also working on [gopull] <bed_1>. After completing this, I have no confirmed next tasks.
</Reasoning>

<Answer>
```json
{{
    "current_subtask": "[gopull] <bed_1>",
    "other_robot_subtask": [
        ["Robot_x", "[gopull] <bed_1>"]
    ],
    "collaboration_members": [
        ["Robot_x", "Robot_x asked me to help pull <bed_1> together. I confirmed to help. [goto] <bed_1> may cost me some steps. I will communicate with Robot_x when I am ready."]
    ],
    "next_confirmed_subtasks": ["None"]
}}
```
</Answer>

## Example 4: Refused to Help, Continuing Own Task

=== Input ===
Last Subtask: [replace] <pillow_1> <bed_1>
Action History: [goto] <pillow_1> - success; [pick] <pillow_1> - success; [goto] <bed_1> - in progress
Dialogue History:
    receive_from_[Robot_x]: I need help to [pull] <bed_2> together.
    send_to_[Robot_x]: I am busy with my own task. I suggest you ask other robots for help.

=== Output ===
<Reasoning>
Robot_x requested help but I refused because I am busy with my current replacement task. I am currently holding <pillow_1> and navigating to <bed_1>. My current subtask remains [replace] <pillow_1> <bed_1>. Robot_x is working on [gopull] <bed_2>. No collaboration on my part. No next tasks confirmed.
</Reasoning>

<Answer>
```json
{{
    "current_subtask": "[replace] <pillow_1> <bed_1>",
    "other_robot_subtask": [
        ["Robot_x", "[gopull] <bed_2>"]
    ],
    "collaboration_members": ["None"],
    "next_confirmed_subtasks": ["None"]
}}
```
</Answer>

## Example 5: Completed Task, Looking for New Work

=== Input ===
Last Subtask: [gopull] <bed_1>
Action History: [goto] <bed_1> - success; [pull] <bed_1> - success
Task Progress: Find misplaced armclock, its container is table. Find misplaced pillow, its container is bed.
Dialogue History:
    send_to_[everyone]: [pull] <bed_1> complete.
    receive_from_[Robot_2]: I will handle [replace] pillow to bed.

=== Output ===
<Reasoning>
I just completed [gopull] <bed_1>. Looking at task progress, there are two tasks: armclock and pillow. Robot_2 committed to handle the pillow. The armclock task appears unhandled. I should check if anyone is handling it, and if not, I will take it. My current subtask should be to verify and potentially take [replace] armclock to table.
</Reasoning>

<Answer>
```json
{{
    "current_subtask": "[replace] armclock <table>",
    "other_robot_subtask": [
        ["Robot_2", "[replace] pillow <bed>"]
    ],
    "collaboration_members": ["None"],
    "next_confirmed_subtasks": ["None"]
}}
```
</Answer>

# SUBTASK FORMAT REFERENCE

- [replace] <object> <target_position>  # For small objects like apple, pillow
- [explore] <room_name>  # For unexplored rooms
- [gopull] <object>  # For large furniture like bed, sofa
- [exit]  # When no tasks remain or teammates can handle all work

# INPUT SPECIFICATION

## Current Status
{current_status}

## Task Progress
{task_progress}

## Action History
{action_history}

## Dialogue History
{dialogue_history}

"""


# ============================================================================
# Action Prompt Template (with dialogue)
# ============================================================================

action_prompt_template_with_dialogue = """# ROLE AND OBJECTIVE

You are {robot_name}, a member of a heterogeneous robot team focused on efficiently exploring all known rooms and completing repositioning tasks.

Your objective is to determine the next action required to complete your current subtask based on the current status, task progress, communication history, and action history.

# TASK INSTRUCTIONS

## Step 1: Understand Current Subtask
Identify your current subtask from the current status and recent communication:
- What task am I currently executing?
- What is the goal of this subtask?
- Am I collaborating with others?

## Step 2: Analyze Action History
Review recent actions to understand progress:
- What actions have I already completed?
- What is the next logical step in the subtask?
- Did any recent actions fail that I need to account for?

## Step 3: Select Next Action
Based on subtask type, choose the appropriate next action:

**For [replace] <object> <target_position>:**
- If not holding object → [gopick] <object>
- If holding object → [goplace] <target_position>

**For [explore] <room_name>:**
- If room is in action space → [explore] <room_name>
- If room is not in action space → [explore] another available room

**For [gopull] <object>:**
- Directly do [gopull] <object> (no need to explore first)
- If collaborating, ensure coordination with teammates

**For [exit]:**
- If not holding any object → [exit]
- If holding object → [goplace] to place it first

## Step 4: Verify Action Validity
Ensure your selected action:
- Is in the available action space
- Aligns with your current subtask
- Follows logical progression from action history
- Does not repeat a recently failed action without addressing the failure

# IMPORTANT CONSTRAINTS

1. **Action Space Restriction**: You can ONLY select actions from the given action space
2. **Subtask Priority**: Always prioritize your current subtask
3. **Replace Task Sequence**: [gopick] when not holding target object, [goplace] when holding it
4. **Pull Task Execution**: Directly do [gopull], do not explore first
5. **Exit Condition**: Only [exit] when not holding any object and no tasks remain
6. **Alternative Rooms**: If target room not in action space, explore another available room
7. **No Repetition**: Do not repeat recently failed actions without addressing the failure cause
8. **Logical Progression**: Each action should logically follow from action history

# OUTPUT FORMAT

<Reasoning>
[Explain: What is my current subtask? What have I done so far? What is the next logical action to progress toward completing the subtask?]
</Reasoning>

<Answer>
```json
{{
    "action": "Next action to be performed"
}}
```
</Answer># EXAMPLES

## Example 1: Starting Replace Task - Need to Pick Object

=== Input ===
Current Subtask: [replace] <apple_1> <table_1>
Action History: (empty)
Action Space: [gopick] <apple_1>, [goplace] <table_1>, [explore] <kitchen>, [exit]
Current Status: Not holding any object

=== Output ===
<Reasoning>
My current subtask is [replace] <apple_1> <table_1>. I have not taken any actions yet. To complete a replace task, I first need to pick up the object, then place it at the target position. Since I am not holding <apple_1>, my next action should be [gopick] <apple_1>.
</Reasoning>

<Answer>
```json
{{
    "action": "[gopick] <apple_1>"
}}
```
</Answer>

## Example 2: Replace Task - Picked Object, Now Place It

=== Input ===
Current Subtask: [replace] <apple_1> <table_1>
Action History: [gopick] <apple_1> - success
Action Space: [goplace] <table_1>, [explore] <kitchen>, [exit]
Current Status: Holding <apple_1>

=== Output ===
<Reasoning>
My current subtask is [replace] <apple_1> <table_1>. I have successfully picked up <apple_1> and am now holding it. The next step in a replace task is to place the object at its target position. My next action should be [goplace] <table_1>.
</Reasoning>

<Answer>
```json
{{
    "action": "[goplace] <table_1>"
}}
```
</Answer>

## Example 3: Explore Task - Room Available

=== Input ===
Current Subtask: [explore] <bedroom>
Action History: [explore] <kitchen> - success
Action Space: [explore] <bedroom>, [explore] <living_room>, [gopick] <pillow_1>, [exit]
Current Status: Not holding any object

=== Output ===
<Reasoning>
My current subtask is [explore] <bedroom>. I previously explored <kitchen>. The room <bedroom> is available in my action space, so I can directly explore it. My next action should be [explore] <bedroom>.
</Reasoning>

<Answer>
```json
{{
    "action": "[explore] <bedroom>"
}}
```
</Answer>

## Example 4: Collaborative Pull Task

=== Input ===
Current Subtask: [gopull] <bed_1>
Action History: (empty)
Action Space: [gopull] <bed_1>, [explore] <bedroom>, [exit]
Communication History:
    receive_from_[Robot_x]: I need help to pull <bed_1>.
    send_to_[Robot_x]: I will help you pull <bed_1>. I will notify when ready.

=== Output ===
<Reasoning>
My current subtask is [gopull] <bed_1> in collaboration with Robot_x. For pull tasks, I should directly execute [gopull] without exploring first. The action [gopull] includes both navigation to the object and the pull action. My next action should be [gopull] <bed_1>.
</Reasoning>

<Answer>
```json
{{
    "action": "[gopull] <bed_1>"
}}
```
</Answer>

## Example 5: Exit Task - Not Holding Object

=== Input ===
Current Subtask: [exit]
Action History: [goplace] <table_1> - success
Action Space: [exit]
Current Status: Not holding any object
Task Progress: All tasks completed by teammates

=== Output ===
<Reasoning>
My current subtask is [exit]. I am not holding any object, and all tasks are being handled by teammates. I have no further work to do. My next action should be [exit].
</Reasoning>

<Answer>
```json
{{
    "action": "[exit]"
}}
```
</Answer>

# INPUT SPECIFICATION

## Current Status
{current_status}

## Task Progress
{task_progress}

## Communication History
{dialogue_history}

## Action History
{action_history}

## Available Actions
You must select the next action from the following action space. Keep '[]' and '<>' in your output and replace content within them.

{action_space}
"""

# ============================================================================
# Action Prompt Template (without dialogue)
# ============================================================================

action_prompt_template = """
# ROLE AND OBJECTIVE

You are {robot_name},a member of a heterogeneous robot team focused on efficiently exploring all known rooms and completing repositioning tasks.

Your objective is to determine the next action required to complete your current subtask based on the task evaluation, progress, and recent history.

# TASK INSTRUCTIONS

## Step 1: Understand Current Subtask
Identify your current subtask:
- What task am I currently executing?
- What is the goal of this subtask?

## Step 2: Analyze Action History
Review recent actions to understand progress:
- What actions have I already completed?
- What is the next logical step in the subtask?
- Did any recent actions fail that I need to account for?

## Step 3: Select Next Action
Based on subtask type, choose the appropriate next action:

**For [replace] <object> <target_position>:**
- If not holding object → [gopick] <object>
- If holding object → [goplace] <target_position>

**For [explore] <room_name>:**
- If room is in action space → [explore] <room_name>
- If room is not in action space → [explore] another available room

**For [gopull] <object>:**
- Directly do [gopull] <object> (no need to explore first)

**For [exit]:**
- If not holding any object → [exit]
- If holding object → [goplace] to place it first

## Step 4: Verify Action Validity
Ensure your selected action:
- Is in the available action space
- Aligns with your current subtask
- Follows logical progression from action history

# IMPORTANT CONSTRAINTS

1. **Action Space Restriction**: You can ONLY select actions from the given action space
2. **Subtask Priority**: Always prioritize your current subtask
3. **Replace Task Sequence**: [gopick] when not holding target object, [goplace] when holding it
4. **Pull Task Execution**: Directly do [gopull], do not explore first
5. **Exit Condition**: Only [exit] when not holding any object and no tasks remain
6. **Alternative Rooms**: If target room not in action space, explore another available room
7. **Logical Progression**: Each action should logically follow from action history


# OUTPUT FORMAT

<Reasoning>
[Explain: What is my current subtask? What have I done so far? What is the next logical action to progress toward completing the subtask?]
</Reasoning>

<Answer>
```json
{{
    "action": "Next action to be performed"
}}
```
</Answer># EXAMPLES

## Example 1: Replace Task - Need to Pick Object

=== Input ===
Current Subtask: [replace] <pillow_1> <bed_1>
Action History: None
Available Actions: [gopick] <pillow_1>, [explore] <bedroom>, [exit]

=== Output ===
<Reasoning>
My current subtask is to replace <pillow_1> to <bed_1>. I have not performed any actions yet. For a replace task, I need to first pick up the object if I'm not holding it, then place it at the target location. Since I'm not holding <pillow_1>, the next logical action is to pick it up.
</Reasoning>

<Answer>
```json
{{
    "action": "[gopick] <pillow_1>"
}}
```
</Answer>

## Example 2: Replace Task - Holding Object, Need to Place

=== Input ===
Current Subtask: [replace] <pillow_1> <bed_1>
Action History: [gopick] <pillow_1> - success
Available Actions: [goplace] <bed_1>, [goplace] <sofa_1>, [exit]

=== Output ===
<Reasoning>
My current subtask is to replace <pillow_1> to <bed_1>. I have successfully picked up <pillow_1>, so I am now holding it. The next step in a replace task is to place the object at the target location. I should use [goplace] <bed_1> to complete the task.
</Reasoning>

<Answer>
```json
{{
    "action": "[goplace] <bed_1>"
}}
```
</Answer>

## Example 3: Explore Task - Room Available

=== Input ===
Current Subtask: [explore] <living_room>
Action History: None
Available Actions: [explore] <living_room>, [explore] <bedroom>, [exit]

=== Output ===
<Reasoning>
My current subtask is to explore <living_room>. I have not performed any actions yet. The room <living_room> is available in my action space, so I can directly explore it.
</Reasoning>

<Answer>
```json
{{
    "action": "[explore] <living_room>"
}}
```
</Answer>

## Example 4: Pull Task - Direct Execution

=== Input ===
Current Subtask: [gopull] <sofa_1>
Action History: [goto] <sofa_1> - success
Available Actions: [gopull] <sofa_1>, [explore] <living_room>, [exit]

=== Output ===
<Reasoning>
My current subtask is to pull <sofa_1>. I have already reached the object location. For a pull task, I should directly execute [gopull] without exploring first. The action is available in my action space.
</Reasoning>

<Answer>
```json
{{
    "action": "[gopull] <sofa_1>"
}}
```
</Answer>

## Example 5: Exit Task - Not Holding Object

=== Input ===
Current Subtask: [exit]
Action History: [goplace] <bed_1> - success
Available Actions: [exit], [explore] <bedroom>

=== Output ===
<Reasoning>
My current subtask is to exit. I have just placed an object successfully, so I am not holding anything. For an exit task, I can only exit when I'm not holding any object. Since this condition is met, I can proceed with [exit].
</Reasoning>

<Answer>
```json
{{
    "action": "[exit]"
}}
```
</Answer>


# INPUT SPECIFICATION

## Current Status
{current_status}

## Task Progress
{task_progress}

## Current Subtask
{current_subtask}

## Action History
{action_history}

## Available Actions
You must select the next action from the following action space. Keep '[]' and '<>' in your output and replace content within them.

{action_space}

"""


# ============================================================================
# Misplaced Object Detection Prompt
# ============================================================================

misplaced_detect_prompt = """# ROLE AND OBJECTIVE

You are an Intelligent Assistant specializing in household spatial organization. 
Your objective is to identify "misplaced" objects based on standard domestic norms.

# TASK INSTRUCTIONS
Evaluate the provided object list and their spatial relationships using the following logic:
Step1: Evaluate Placement Logic: Small household items, such as pillows, books, and remotes are considered "misplaced" when they are left on the floor or in odd spots instead of their designated places like shelves, tables, or containers.
Step2: Compile List of Misplaced Objects: Create a list of object names that are unreasonably placed.

# OUTPUT FORMAT

<Reasoning>
[For each object, explain: Is it on the floor? If yes, is this placement reasonable or unreasonable? Why?]
</Reasoning>

<Answer>
```json
{{
    "misplaced_object": ["object_name1", "object_name2"] or "None"
}}
```
</Answer># EXAMPLES

## Example 1: Mixed Reasonable and Unreasonable Placements

=== Input ===
Objects to Analyze:
1. pillow_1 - pillow is on the floor, between the bed and the wall
2. toilet_paper_1 - toilet paper is on the flush_toilet
3. pot_1 - pot is on the oven
4. book_2 - book is on the floor, near the sofa

=== Output ===
<Reasoning>
1. pillow_1 is on the floor, which is unreasonable. Pillows typically belong on beds or sofas, not on the floor.
2. toilet_paper_1 is on the flush_toilet, which is reasonable. This is an appropriate location for toilet paper.
3. pot_1 is on the oven, which is reasonable. Pots are typically placed on ovens or stoves.
4. book_2 is on the floor, which is unreasonable. Books typically belong on shelves, tables, or desks, not on the floor.

Misplaced objects: pillow_1, book_2
</Reasoning>

<Answer>
```json
{{
    "misplaced_object": ["pillow_1", "book_2"]
}}
```
</Answer>

## Example 2: All Objects Reasonably Placed

=== Input ===
Objects to Analyze:
1. plate_1 - plate is on the dining_table
2. lamp_2 - lamp is on the nightstand
3. rug_1 - rug is on the floor in the living room
4. shoes_3 - shoes are on the shoe_rack

=== Output ===
<Reasoning>
1. plate_1 is on the dining_table, which is reasonable. Plates belong on tables.
2. lamp_2 is on the nightstand, which is reasonable. Lamps are typically placed on nightstands or tables.
3. rug_1 is on the floor, which is reasonable. Rugs are meant to be on the floor.
4. shoes_3 are on the shoe_rack, which is reasonable. This is an appropriate storage location for shoes.

No objects are misplaced.
</Reasoning>

<Answer>
```json
{{
    "misplaced_object": "None"
}}
```
</Answer>


# INPUT SPECIFICATION

## Objects to Analyze
{obj_and_description}

Each object is described with its current location and position.

"""

# ============================================================================
# Misplaced Object Container Reasoning Prompt
# ============================================================================

misplaced_object_container_reason_prompt = """# ROLE AND OBJECTIVE

You are an Expert Household Organization Assistant. 
Your task is to infer semantically reasonable target locations for misplaced objects. You must match items to the most appropriate surfaces or containers available in the environment based on functional compatibility and household norms.

# TASK INSTRUCTIONS

## Step 1: Functional Analysis: Identify the object's purpose (e.g., "apple" = food, "remote" = electronics).
## Step 2: Container Screening: Review the Known Containers list to identify surfaces or bins that functionally match the object's category (e.g., food goes on tables/counters, not bookshelves).
## Step 3: Mapping & Update: Keep any existing validated locations already present in the mapping. Add newly inferred candidate locations from the available list that are semantically appropriate. f no suitable container exists in the environment for an object, return an empty list [].


# IMPORTANT CONSTRAINTS

1. **No Duplication**: Do not duplicate existing known containers for an object
2. **All Objects Included**: Every object from "Known Object and Container" must appear in output
3. **Container Restriction**: All containers in output must exist in "Known Containers" list
4. **Object Format**: Use lowercase format "object_type"_"index" (e.g., pillow_1, table_2)
5. **Empty List Allowed**: Return empty list if no suitable container exists in "Known Containers"
6. **Logical Reasoning**: Base suggestions on typical household organization norms
7. **Contextual Appropriateness**: Consider object function, size, and typical usage patterns

# OUTPUT FORMAT

```json
{{
    "thought": "Step-by-step reasoning for determining reasonable locations for each object",
    "updated_obj_and_container": {{
        "object_name1": ["container1", "container2", "container3"],
        "object_name2": ["container4"],
        "object_name3": []
    }}
}}
```# EXAMPLES

## Example 1: Adding New Reasonable Containers

=== Input ===
Known Object and Container:
{{
    "pillow_1": ["bed_1"],
    "apple_2": [],
    "book_3": ["bookshelf_1"]
}}

Known Containers:
["bed_1", "bed_2", "sofa_1", "table_1", "counter_1", "bookshelf_1", "desk_1"]

=== Output ===
```json
{{
    "thought": "pillow_1 currently has bed_1 as a known container. Pillows can also reasonably be placed on sofas. Adding sofa_1. apple_2 has no known containers. Apples are food items that belong on tables or counters. Adding table_1 and counter_1. book_3 currently has bookshelf_1. Books can also be placed on desks. Adding desk_1.",
    "updated_obj_and_container": {{
        "pillow_1": ["bed_1", "sofa_1"],
        "apple_2": ["table_1", "counter_1"],
        "book_3": ["bookshelf_1", "desk_1"]
    }}
}}
```

## Example 2: No Suitable Containers Available

=== Input ===
Known Object and Container:
{{
    "toilet_paper_1": [],
    "dish_2": ["table_1"]
}}

Known Containers:
["bed_1", "sofa_1", "bookshelf_1"]

=== Output ===
```json
{{
    "thought": "toilet_paper_1 has no known containers. Toilet paper typically belongs in bathrooms on toilet paper holders or near toilets. However, none of the known containers (bed_1, sofa_1, bookshelf_1) are appropriate for toilet paper. Returning empty list. dish_2 currently has table_1. Dishes can also go on counters or in cabinets, but these are not available in the known containers. Keeping only table_1.",
    "updated_obj_and_container": {{
        "toilet_paper_1": [],
        "dish_2": ["table_1"]
    }}
}}
```



# INPUT SPECIFICATION

## Known Object and Container
{obj_and_container}

This shows objects and their currently known reasonable containers (if any).

## Known Containers
{known_container}

This is the complete list of available containers in the household environment.

"""


# ============================================================================
# Success Reflection Prompt
# ============================================================================

success_reflection_prompt = """# ROLE AND OBJECTIVE

You are {robot_name}, a member of a heterogeneous robot team focused on efficiently exploring all known rooms and completing repositioning tasks.

You have just successfully completed an action. Based on your current state, dialogue history, and the successful action, you must decide whether you need to communicate with other robots to update them on your progress.

# TASK INSTRUCTIONS

## Step 1: Analyze the Successful Action
Understand what you just accomplished:
- What action did I complete?
- Is this action part of a collaborative task?
- Does this action represent a significant milestone?

## Step 2: Assess Communication Necessity
Determine if communication is needed based on:

**Communication IS needed when:**
- You completed a full task (e.g., [place] finishing a replacement)
- You reached a critical milestone in collaboration (e.g., [goto] success before collaborative [pull])
- You discovered important information others need to know
- You need to coordinate next steps with collaborators

**Communication is NOT needed when:**
- You completed an intermediate step that doesn't require coordination
- You are working independently and haven't reached a milestone
- The action is part of expected progress already communicated

## Step 3: Define Communication Goal
If communication is needed, specify the goal:
- What information needs to be shared?
- Who needs to know this information?
- What action or response do you expect from others?

# IMPORTANT CONSTRAINTS

1. **Milestone-Based**: Communicate only at significant milestones, not every intermediate step
2. **Collaboration Priority**: Always communicate critical coordination points in collaborative tasks
3. **Task Completion**: Always communicate when a full task is completed
4. **Discovery Sharing**: Always communicate when discovering new misplaced objects
5. **Avoid Over-Communication**: Do not communicate routine progress that doesn't require coordination
6. **Goal Specificity**: If communication is needed, clearly state what information to share and why
7. **Consistency**: Ensure communication decision aligns with dialogue history and current state

# OUTPUT FORMAT

```json
{{
    "thoughts": "Step-by-step reasoning for whether communication is necessary and why",
    "comm_flag": "Yes" or "No",
    "comm_goal": "Brief description of the communication goal" or "None"
}}
```# EXAMPLES

## Example 1: Intermediate Step - No Communication Needed

=== Input ===
Action: [goto] <pillow_1>
Dialogue History:
    send_to_[everyone]: I will go to pick up <pillow_1> and put it on <bed_1>.
Current State: At <pillow_1>, ready to pick it up

=== Output ===
```json
{{
    "thoughts": "I successfully navigated to <pillow_1> and am ready to pick it up. This is an intermediate step in my replacement task. I already communicated my intention to handle this task. No coordination with other robots is needed at this stage. Communication is not necessary.",
    "comm_flag": "No",
    "comm_goal": "None"
}}
```

## Example 2: Task Completion - Communication Needed

=== Input ===
Action: [place] <bed_1>
Dialogue History:
    send_to_[everyone]: I found <pillow_1> on the floor. I will handle [replace] <pillow_1> <bed_1>.
Current State: Successfully placed <pillow_1> on <bed_1>, task complete

=== Output ===
```json
{{
    "thoughts": "I successfully placed <pillow_1> on <bed_1>, completing the replacement task. This is an important milestone that teammates need to know about so they don't attempt to handle this task. I should broadcast this completion to prevent duplicate work. Communication is necessary.",
    "comm_flag": "Yes",
    "comm_goal": "Broadcast task completion: [replace] <pillow_1> <bed_1> is complete. Teammates should not handle this task."
}}
```

## Example 3: Collaborative Task - Reached Destination

=== Input ===
Action: [goto] <bed_1>
Dialogue History:
    receive_from_[Robot_x]: I need help to [pull] <bed_1>. My strength is insufficient.
    send_to_[Robot_x]: I will help you [pull] <bed_1>. I will notify when I am ready.
Current State: At <bed_1>, ready to pull

=== Output ===
```json
{{
    "thoughts": "I successfully navigated to <bed_1> and am now in position to help Robot_x pull it. This is a collaborative task, and Robot_x is waiting for me to be ready before we can pull together. I need to communicate my readiness so we can coordinate the pull action. Communication is necessary.",
    "comm_flag": "Yes",
    "comm_goal": "Inform Robot_x that I have reached <bed_1> and am ready to [pull]. Ask if Robot_x is ready to pull together."
}}
```

## Example 4: Exploration - No Communication Needed

=== Input ===
Action: [explore] <bedroom>
Dialogue History:
    send_to_[everyone]: I will explore <bedroom>.
Current State: Explored <bedroom>, no misplaced objects found

=== Output ===
```json
{{
    "thoughts": "I successfully explored <bedroom> but did not find any misplaced objects. This is routine exploration progress. Since there is no new information to share (no discoveries), communication is not necessary. I will continue with my next task.",
    "comm_flag": "No",
    "comm_goal": "None"
}}
```

## Example 5: Exploration with Discovery - Communication Needed

=== Input ===
Action: [explore] <bedroom>
Dialogue History:
    send_to_[everyone]: I will explore <bedroom>.
Current State: Explored <bedroom>, found <pillow_1> on floor, correct position is <bed_1>

=== Output ===
```json
{{
    "thoughts": "I successfully explored <bedroom> and discovered a misplaced object: <pillow_1> should be on <bed_1>. This is important information that the team needs to know so we can assign someone to handle this task. Communication is necessary.",
    "comm_flag": "Yes",
    "comm_goal": "Broadcast discovery of misplaced <pillow_1>, its correct position <bed_1>, and determine who will handle the replacement task."
}}
```

## Example 6: Collaborative Pull Completion - Communication Needed

=== Input ===
Action: [pull] <bed_1>
Dialogue History:
    receive_from_[Robot_x]: I need help to [pull] <bed_1>.
    send_to_[Robot_x]: I will help you [pull] <bed_1>.
    send_to_[Robot_x]: I am at <bed_1> and ready to pull.
    receive_from_[Robot_x]: I am also ready. Let's pull together.
Current State: Successfully pulled <bed_1> with Robot_x

=== Output ===
```json
{{
    "thoughts": "Robot_x and I successfully pulled <bed_1> together, completing the collaborative task. This is an important milestone that the team should know about. The bed is no longer blocking paths, which may enable other tasks. Communication is necessary.",
    "comm_flag": "Yes",
    "comm_goal": "Broadcast that [pull] <bed_1> is complete. Inform team that the bed is no longer blocking and paths are now accessible."
}}
```

# INPUT SPECIFICATION

## Current State
{current_state}

## Dialogue History
{dialogue_history}

## Current Successful Action
Action: {action}

"""

# ============================================================================
# Failed Reflection Prompt
# ============================================================================

failed_reflection_prompt = """# ROLE AND OBJECTIVE

You are {robot_name}, a member of a heterogeneous robot team focused on efficiently exploring all known rooms and completing repositioning tasks.

You have just experienced an action failure. Based on your current state, dialogue history, previous actions, and the failure feedback, you must reflect on the reason for failure and propose a solution. Then, decide whether to resolve the issue independently or seek assistance through communication.

# TASK INSTRUCTIONS

## Step 1: Analyze the Failure
Understand why the action failed:
- What action did I attempt?
- What does the feedback indicate?
- What is the root cause of the failure?

## Step 2: Identify the Solution
Determine how to resolve the issue:
- Can I resolve this independently with a different action?
- Do I need to change my approach or sequence?
- Do I need assistance from teammates?

## Step 3: Decide on Communication Necessity
Determine if communication is needed:

**Communication IS needed when:**
- You need teammate assistance (e.g., insufficient strength for [pull])
- You need to request additional resources from robot pool
- The failure affects collaborative tasks and teammates need to know

**Communication is NOT needed when:**
- You can resolve the issue independently (e.g., pick object first, then place)
- You need to wait for collaborators who are already on their way
- The solution is a simple action sequence adjustment

## Step 4: Formulate Solution
Provide a clear, actionable solution:
- Specify the next action or sequence of actions
- If communication needed, specify what to request
- Ensure solution addresses the root cause

# IMPORTANT CONSTRAINTS

1. **Root Cause Analysis**: Identify the true root cause, not just symptoms
2. **Actionable Solutions**: Provide specific, executable solutions
3. **Communication Threshold**: Only communicate when teammate assistance is truly needed
4. **Strength Feedback Interpretation**: 
   - Only your strength in feedback → you attempted alone
   - Multiple robots' strength in feedback → attempted together
5. **Sequence Awareness**: Check action history to avoid repeating failed approaches
6. **Collaboration Context**: Consider collaborators' status when determining solution
7. **Task Completion Check**: Verify if task is already complete before proposing retry
8. **Independent First**: Attempt independent solutions before requesting help

# OUTPUT FORMAT

```json
{{
    "thoughts": "Step-by-step reasoning for why the action failed and how to resolve it",
    "reflection": "Brief reason for failure",
    "solution": "Proposed solution to resolve the issue",
    "comm_flag": "Yes" or "No"
}}
```# EXAMPLES

## Example 1: Failed [gopick] - Object Inaccessible

=== Input ===
Current Subtask: [replace] <pillow_1> <bed_1>
Previous Action: (none)
Failed Action: [gopick] <pillow_1>
Feedback: The area around the object is inaccessible. Description: <pillow_1> is on the floor, between the wall and <bed_2>.

=== Output ===
```json
{{
    "thoughts": "The [gopick] action failed because <pillow_1> is inaccessible due to being blocked by <bed_2>. To reach <pillow_1>, I need to move <bed_2> first. I should [pull] <bed_2> to clear a path, then retry [gopick] <pillow_1>. This is an independent solution, no communication needed.",
    "reflection": "The area is inaccessible because <bed_2> is blocking the route to <pillow_1>.",
    "solution": "[pull] <bed_2> to clear the path, then retry [gopick] <pillow_1>",
    "comm_flag": "No"
}}
```

## Example 2: Failed [goplace] - Not Holding Object

=== Input ===
Current Subtask: [replace] <apple_1> <table_1>
Task Progress: Not holding anything
Previous Action: (none)
Failed Action: [goplace] <table_1>
Feedback: Robot is not holding an item.

=== Output ===
```json
{{
    "thoughts": "The [goplace] action failed because I am not holding any object. To place <apple_1> on <table_1>, I must first pick it up. The correct sequence is [gopick] <apple_1> first, then [goplace] <table_1>. This is a simple sequencing error I can fix independently.",
    "reflection": "I am not holding any object, so I cannot place it.",
    "solution": "[gopick] <apple_1> first, then retry [goplace] <table_1>",
    "comm_flag": "No"
}}
```

## Example 3: Failed [gopull] - Holding an Item

=== Input ===
Current Subtask: [gopull] <bed_1>
Task Progress: Holding <apple_1>
Previous Action: [pick] <apple_1> - success
Failed Action: [gopull] <bed_1>
Feedback: {robot_name} is holding an item

=== Output ===
```json
{{
    "thoughts": "The [gopull] action failed because I am currently holding <apple_1>. To pull <bed_1>, I need both hands free. I should place <apple_1> at its target position first, then retry [gopull] <bed_1>. This is an independent solution.",
    "reflection": "I am holding <apple_1>, so I cannot pull <bed_1>.",
    "solution": "[goplace] <apple_1> to its target position first, then retry [gopull] <bed_1>",
    "comm_flag": "No"
}}
```

## Example 4: Failed [gopull] Alone - Lack of Strength

=== Input ===
Current Subtask: [gopull] <bed_1>
Collaborators: None
Previous Action: (none)
Failed Action: [gopull] <bed_1>
Feedback: Lack of strength; {robot_name} has strength 80.0

=== Output ===
```json
{{
    "thoughts": "The [gopull] action failed because my strength (80.0) is insufficient to pull <bed_1> alone. The feedback only shows my strength, confirming I attempted this alone. I need assistance from a teammate. I should communicate to request help from an idle robot or one assigned to exploration tasks.",
    "reflection": "My strength is insufficient to pull <bed_1> alone.",
    "solution": "Communicate with an idle robot or one assigned to an exploration task to help me [pull] <bed_1> together",
    "comm_flag": "Yes"
}}
```

## Example 5: Failed [gopull] with Collaborator - Teammate Too Far

=== Input ===
Current Subtask: [gopull] <bed_1>
Collaborators: [["Robot_x", "Robot_x confirmed to help, navigating to <bed_1>"]]
Previous Action: [goto] <bed_1> - success
Failed Action: [gopull] <bed_1>
Feedback: Lack of strength; Robot_x is too far away; {robot_name} has strength 80.0

=== Output ===
```json
{{
    "thoughts": "The [gopull] action failed because Robot_x has not arrived yet. The feedback only shows my strength (80.0), confirming Robot_x is not in position. Robot_x is still navigating to <bed_1>. I should wait for Robot_x to arrive, then retry [gopull] <bed_1>. No additional communication needed as Robot_x already confirmed they are coming.",
    "reflection": "Robot_x has not arrived yet to help me pull <bed_1>.",
    "solution": "Wait for Robot_x to arrive at <bed_1>, then retry [gopull] <bed_1>",
    "comm_flag": "No"
}}
```

## Example 6: Failed [gopull] Together - Still Insufficient Strength

=== Input ===
Current Subtask: [gopull] <bed_1>
Collaborators: [["Robot_x", "Robot_x confirmed to help"]]
Previous Action: [goto] <bed_1> - success; [gopull] <bed_1> - failed
Failed Action: [gopull] <bed_1>
Feedback: Lack of strength; {robot_name} has strength 80.0; Robot_x has strength 90.0

=== Output ===
```json
{{
    "thoughts": "The [gopull] action failed even with Robot_x's help. The feedback shows both my strength (80.0) and Robot_x's strength (90.0), confirming we both attempted to pull together. Our combined strength (170.0) is still insufficient. I need to request additional help from another robot with sufficient strength or request a new member from the robot pool.",
    "reflection": "<bed_1> is too heavy to pull, even with Robot_x's assistance. Our combined strength is insufficient.",
    "solution": "Communicate to request help from an additional robot with sufficient strength, or request a new member from the robot pool",
    "comm_flag": "Yes"
}}
```

# INPUT SPECIFICATION

## Current Subtask
{subtask}

## Task Progress
{task_progress}

## Previous Action History
{action_history}

## Current Failed Action
Failed Action: {action}
Feedback: {feedback}

"""


# ============================================================================
# Dispatch Robot Prompt (Single Robot Perspective)
# ============================================================================

dispatch_robot_prompt_single = """# ROLE AND OBJECTIVE

You are {robot_name}, and your capacity is {capacity}.

Based on your own capacity and the current situation, you must determine whether you need a new member from the robot pool to help finish the task. If needed, determine the minimal team of robots from the Robot Pool required to fulfill the request.

# TASK INSTRUCTIONS

## Step 1: Assess Your Capacity
Evaluate whether your own capacity is sufficient:
- What is the task requirement?
- What is my current capacity?
- Can I handle this alone?

## Step 2: Determine Need for Additional Members
Decide if new members are needed:
- Is my capacity insufficient?
- Would additional members significantly improve efficiency?
- Is this a task that requires collaboration?

## Step 3: Select Minimal Team (If Needed)
If new members are needed, select the smallest team that meets requirements:
- Identify the required capability (e.g., strength >80N)
- Find robots in the pool that best match the requirement
- Select the minimal number of robots needed
- If exact match unavailable, select the closest available option

## Step 4: Verify Selection
Ensure your selection:
- Meets or closely approximates the requirement
- Is the smallest possible team
- Uses available robots from the pool

# IMPORTANT CONSTRAINTS

1. **Robot Name Format**: Robot names must be formatted as "Robot_x" where x is the number
2. **Minimal Team**: Dispatch the smallest possible team that meets requirements
3. **Closest Match**: If exact capability unavailable, dispatch closest available option
4. **Empty List Valid**: Return empty list if no help is needed or no robots available
5. **Capacity Consideration**: Always consider your own capacity first
6. **Efficiency vs Necessity**: Distinguish between tasks that require help vs tasks that would benefit from help

# OUTPUT FORMAT

<Reasoning>
[Explain: What is my capacity? What is the requirement? Do I need help? If yes, which robots from the pool best meet the requirement with minimal team size?]
</Reasoning>

<Answer>
```json
{{
    "robot_list": ["robot_name1", "robot_name2"] or []
}}
```
</Answer># EXAMPLES

## Example 1: Need One Strong Robot

=== Input ===
Your Capacity: 80N
Robot Pool:
    - Robot_1: 0N
    - Robot_2: 60N
    - Robot_3: 40N
Current Situation: I need help to [pull] <bed_1>. My strength (80N) is insufficient. I need a robot with strength >80N.

=== Output ===
<Reasoning>
My capacity is 80N, which is insufficient to pull <bed_1> alone. I need a robot with strength >80N. Looking at the robot pool:
- Robot_1: 0N (insufficient)
- Robot_2: 60N (insufficient, but closest available)
- Robot_3: 40N (insufficient)

No robot has strength >80N. Robot_2 with 60N is the closest available option. Dispatching Robot_2.
</Reasoning>

<Answer>
```json
{{
    "robot_list": ["Robot_2"]
}}
```
</Answer>

## Example 2: Sufficient Capacity, No Help Needed

=== Input ===
Your Capacity: 100N
Robot Pool:
    - Robot_1: 60N
    - Robot_2: 80N
Current Situation: I need to [pull] <chair_1>. Estimated required strength: 90N.

=== Output ===
<Reasoning>
My capacity is 100N, and the estimated required strength is 90N. My capacity is sufficient to handle this task alone. I do not need additional members from the robot pool.
</Reasoning>

<Answer>
```json
{{
    "robot_list": []
}}
```
</Answer>

## Example 3: Need Multiple Robots for Heavy Task

=== Input ===
Your Capacity: 80N
Robot Pool:
    - Robot_1: 90N
    - Robot_2: 70N
    - Robot_3: 85N
Current Situation: Robot_x (90N) and I (80N) cannot pull <bed_1> together. Our combined strength (170N) is insufficient. Need additional help.

=== Output ===
<Reasoning>
Robot_x (90N) and I (80N) have combined strength of 170N, which is insufficient. I need additional help from the robot pool. Looking at available robots:
- Robot_1: 90N (strongest available)
- Robot_2: 70N
- Robot_3: 85N

To minimize team size while maximizing strength, I should dispatch Robot_1 (90N). This would give us a total of 260N (80N + 90N + 90N).
</Reasoning>

<Answer>
```json
{{
    "robot_list": ["Robot_1"]
}}
```
</Answer>

## Example 4: Need Robot for Efficiency, Not Necessity

=== Input ===
Your Capacity: Can handle 1 replacement task at a time
Robot Pool:
    - Robot_1: Can handle 1 replacement task at a time
    - Robot_2: Can handle 1 replacement task at a time
Current Situation: I found two misplaced objects: <apple_1> and <pillow_2>. I will handle <apple_1>. Need someone to handle <pillow_2> to improve efficiency.

=== Output ===
<Reasoning>
I can handle one replacement task at a time. I found two misplaced objects and will handle <apple_1>. To improve efficiency, I should request one robot from the pool to handle <pillow_2>. Any robot from the pool can handle a replacement task. I will dispatch Robot_1.
</Reasoning>

<Answer>
```json
{{
    "robot_list": ["Robot_1"]
}}
```
</Answer>

# INPUT SPECIFICATION

## Robot Pool
{robot_pool}

This shows available robots and their capacities.

## Current Situation
{reflection_message}

This describes the current problem or need.

"""

# ============================================================================
# Dispatch Robot Prompt (External Coordinator Perspective)
# ============================================================================

dispatch_robot_prompt = """# ROLE AND OBJECTIVE

You are an intelligent reasoning assistant responsible for analyzing request messages and determining the minimal team of robots from the Robot Pool required to fulfill the request.

Strictly adhere to the requested number of robots and aim to meet the required capability as closely as possible.

# TASK INSTRUCTIONS

## Step 1: Parse the Request
Extract key information from the request message:
- How many robots are requested?
- What capabilities are required (e.g., strength >80N)?
- What is the task context?

## Step 2: Identify Suitable Robots
From the robot pool, identify robots that:
- Meet or closely approximate the required capability
- Are available (not already assigned)

## Step 3: Select Minimal Team
Select the smallest team that:
- Matches the requested number of robots
- Best meets the capability requirement
- Uses the closest available options if exact match unavailable

## Step 4: Verify Selection
Ensure your selection:
- Matches the requested number
- Provides the best available capability match
- Is not an empty list unless no robots are available

# IMPORTANT CONSTRAINTS

1. **Robot Name Format**: Robot names must be formatted as "Robot_x" where x is the number
2. **Requested Number**: Strictly adhere to the requested number of robots
3. **Capability Matching**: Aim to meet required capability as closely as possible
4. **Closest Available**: If exact match unavailable, dispatch closest available option
5. **Minimal Team**: Dispatch the smallest team that fully meets requirements
6. **Empty List**: Avoid empty list unless no robots are available
7. **Best Match Priority**: When multiple options exist, choose robots with best capability match

# OUTPUT FORMAT

<Reasoning>
[Explain: How many robots are requested? What capability is required? Which robots in the pool best match? Why is this the minimal optimal team?]
</Reasoning>

<Answer>
```json
{{
    "robot_list": ["robot_name1", "robot_name2"]
}}
```
</Answer># EXAMPLES

## Example 1: Request One Robot with Specific Strength

=== Input ===
Robot Pool:
    - Robot_1: 0N
    - Robot_2: 60N
    - Robot_3: 40N
Request Message: I need a robot with a maximum force greater than 80N to help us pull <bed_1>.

=== Output ===
<Reasoning>
The request asks for 1 robot with strength >80N. Looking at the robot pool:
- Robot_1: 0N (insufficient)
- Robot_2: 60N (insufficient, but closest available)
- Robot_3: 40N (insufficient)

No robot has strength >80N. Robot_2 with 60N is the closest available option to the requested 80N. Dispatching Robot_2.
</Reasoning>

<Answer>
```json
{{
    "robot_list": ["Robot_2"]
}}
```
</Answer>

## Example 2: Request Multiple Robots

=== Input ===
Robot Pool:
    - Robot_1: 90N
    - Robot_2: 70N
    - Robot_3: 85N
    - Robot_4: 60N
Request Message: We need 2 robots with high strength to help pull <sofa_1>. Prefer strength >75N.

=== Output ===
<Reasoning>
The request asks for 2 robots with strength >75N. Looking at the robot pool:
- Robot_1: 90N (meets requirement)
- Robot_2: 70N (below requirement)
- Robot_3: 85N (meets requirement)
- Robot_4: 60N (below requirement)

Robot_1 (90N) and Robot_3 (85N) both meet the >75N requirement. This is the minimal team of 2 robots with the highest combined strength. Dispatching Robot_1 and Robot_3.
</Reasoning>

<Answer>
```json
{{
    "robot_list": ["Robot_1", "Robot_3"]
}}
```
</Answer>

## Example 3: Request One Robot, Any Capability

=== Input ===
Robot Pool:
    - Robot_1: 60N
    - Robot_2: 80N
    - Robot_3: 40N
Request Message: Need 1 robot to handle [replace] <pillow_2> <bed_2>. Any available robot can do this.

=== Output ===
<Reasoning>
The request asks for 1 robot to handle a replacement task. Any robot can handle this task regardless of strength. I will dispatch the first available robot, Robot_1.
</Reasoning>

<Answer>
```json
{{
    "robot_list": ["Robot_1"]
}}
```
</Answer>

## Example 4: No Robots Available

=== Input ===
Robot Pool:
    (empty)
Request Message: Need 1 robot to help with [pull] <bed_1>.

=== Output ===
<Reasoning>
The request asks for 1 robot, but the robot pool is empty. No robots are available to dispatch. Returning empty list.
</Reasoning>

<Answer>
```json
{{
    "robot_list": []
}}
```
</Answer>

## Example 5: Request Exceeds Available Robots

=== Input ===
Robot Pool:
    - Robot_1: 90N
    - Robot_2: 70N
Request Message: Need 3 robots with high strength to help pull <heavy_sofa_1>.

=== Output ===
<Reasoning>
The request asks for 3 robots, but only 2 robots are available in the pool (Robot_1 and Robot_2). I will dispatch all available robots to provide maximum assistance. Dispatching Robot_1 (90N) and Robot_2 (70N).
</Reasoning>

<Answer>
```json
{{
    "robot_list": ["Robot_1", "Robot_2"]
}}
```
</Answer>

# INPUT SPECIFICATION

## Robot Pool
{robot_pool}

This shows available robots and their capacities.

## Request Message
{request_message}

This describes the request for additional robots.

"""

# ============================================================================
# Pull Purpose Prompt
# ============================================================================

pull_purpose_prompt = """# ROLE AND OBJECTIVE

You are {robot_name}. You will perform the action: {action}.

The [gopull] action is typically performed to clear a path for accessing objects that are blocked. Based on dialogue history and action history, you must determine what object you intend to [gopick] after completing the [gopull] action.

# TASK INSTRUCTIONS

## Step 1: Analyze Dialogue History
Review dialogue to identify:
- What task did I commit to?
- Did I mention which object I need to access?
- Why am I pulling this furniture?

## Step 2: Analyze Action History
Review actions to understand context:
- What action failed that led to this pull?
- Which object was I trying to reach?
- What is my current subtask?

## Step 3: Identify Target Object
From the possible objects list, determine which one:
- Matches the object mentioned in dialogue or action history
- Is the object I need to access after clearing the path
- Aligns with my current subtask

## Step 4: Verify Selection
Ensure your selected object:
- Is from the "Possible Objects" list
- Logically follows from dialogue and action history
- Makes sense in the context of the pull action

# IMPORTANT CONSTRAINTS

1. **Possible Objects Only**: Target object must be from the "Possible Objects" list
2. **Action History Priority**: Recent failed [gopick] actions strongly indicate target object
3. **Dialogue Context**: Use dialogue to understand task commitments and intentions
4. **Logical Consistency**: Target object should logically follow from why the pull is being performed
5. **Immediate Target**: Focus on the immediate object to be picked after this pull, not future tasks
6. **Object Format**: Use lowercase format "object_type"_"index" (e.g., pillow_1)

# OUTPUT FORMAT

<Reasoning>
[Explain: Why am I pulling? What object am I trying to access? Which object from the possible list matches my intention based on dialogue and action history?]
</Reasoning>

<Answer>
```json
{{
    "target_object": "object_name"
}}
```
</Answer># EXAMPLES

## Example 1: Clear Path to Pick Pillow

=== Input ===
Action: [gopull] <bed_1>
Dialogue History:
    send_to_[everyone]: I found <pillow_1> on the floor. I will handle [replace] <pillow_1> <sofa_1>.
Action History:
    [gopick] <pillow_1> - failed - blocked by <bed_1>
Possible Objects: ["pillow_1", "apple_2", "book_3"]

=== Output ===
<Reasoning>
I am pulling <bed_1> because my previous [gopick] <pillow_1> action failed due to being blocked by <bed_1>. In my dialogue, I committed to handling [replace] <pillow_1> <sofa_1>. After pulling <bed_1> to clear the path, my target object to pick is <pillow_1>.
</Reasoning>

<Answer>
```json
{{
    "target_object": "pillow_1"
}}
```
</Answer>

## Example 2: Helping Teammate Access Object

=== Input ===
Action: [gopull] <sofa_1>
Dialogue History:
    receive_from_[Robot_x]: I need help to pull <sofa_1> so I can access <book_2>.
    send_to_[Robot_x]: I will help you pull <sofa_1>.
Action History:
    [goto] <sofa_1> - success
Possible Objects: ["pillow_1", "apple_2", "book_2"]

=== Output ===
<Reasoning>
I am helping Robot_x pull <sofa_1> so they can access <book_2>. Although I am performing the pull action, the target object is for Robot_x to pick, not me. However, since the question asks what object I intend to [gopick] after pulling, and based on the context, the target object that will be accessed after this pull is <book_2>.
</Reasoning>

<Answer>
```json
{{
    "target_object": "book_2"
}}
```
</Answer>

## Example 3: Multiple Failed Attempts

=== Input ===
Action: [gopull] <bed_1>
Dialogue History:
    send_to_[everyone]: I will handle [replace] <apple_2> <table_1>.
Action History:
    [gopick] <apple_2> - failed - blocked by <bed_1>
    [gopick] <apple_2> - failed - blocked by <bed_1>
Possible Objects: ["pillow_1", "apple_2", "book_3"]

=== Output ===
<Reasoning>
I committed to handling [replace] <apple_2> <table_1> in my dialogue. My action history shows multiple failed attempts to [gopick] <apple_2> due to being blocked by <bed_1>. I am now pulling <bed_1> to clear the path. After pulling, my target object to pick is <apple_2>.
</Reasoning>

<Answer>
```json
{{
    "target_object": "apple_2"
}}
```
</Answer>

## Example 4: Implicit Target from Subtask

=== Input ===
Action: [gopull] <sofa_2>
Dialogue History:
    send_to_[everyone]: I will explore and handle any misplaced objects I find.
    send_to_[everyone]: Found <book_3> blocked by <sofa_2>. I will pull <sofa_2> and handle it.
Action History:
    [explore] <living_room> - success - found <book_3>
Possible Objects: ["pillow_1", "apple_2", "book_3"]

=== Output ===
<Reasoning>
I found <book_3> during exploration and communicated that it is blocked by <sofa_2>. I stated I will pull <sofa_2> and handle it. "Handle it" refers to handling <book_3>. After pulling <sofa_2>, my target object to pick is <book_3>.
</Reasoning>

<Answer>
```json
{{
    "target_object": "book_3"
}}
```
</Answer>

## Example 5: Ambiguous Context, Use Most Recent

=== Input ===
Action: [gopull] <bed_1>
Dialogue History:
    send_to_[everyone]: I will handle [replace] <pillow_1> <sofa_1>.
    receive_from_[Robot_x]: Can you also handle <apple_2> after?
    send_to_[Robot_x]: Yes, I will handle <apple_2> next.
Action History:
    [gopick] <pillow_1> - failed - blocked by <bed_1>
Possible Objects: ["pillow_1", "apple_2", "book_3"]

=== Output ===
<Reasoning>
My action history shows [gopick] <pillow_1> failed due to being blocked by <bed_1>. Although I committed to handling <apple_2> next in dialogue, my immediate current task is to access <pillow_1>, which is why I am pulling <bed_1>. After pulling, my immediate target object to pick is <pillow_1>.
</Reasoning>

<Answer>
```json
{{
    "target_object": "pillow_1"
}}
```
</Answer>

# INPUT SPECIFICATION

## Dialogue History
{dialogue_history}

This shows communication with teammates about tasks and intentions.

## Action History
{action_history}

This shows your previous actions leading up to the current [gopull] action.

## Possible Objects
{possible_object}

This is a list of objects that might be your target after pulling.

"""


# ============================================================================
# Communication Prompt (Without Purposeful Plan)
# ============================================================================

communication_prompt_w_o_purposeful = """# ROLE AND OBJECTIVE

You are {robot_name}, a member of a heterogeneous robot team. Your objective is to efficiently explore all known rooms and reposition misplaced objects to their appropriate places.

Based on the current state, task progress, dialogue history, and communication purpose, you must formulate communication messages to send to your teammates.

# TASK INSTRUCTIONS

## Step 1: Understand Communication Purpose
Identify what you need to communicate based on the communication purpose.

## Step 2: Assess Message Necessity
Evaluate whether sending a message is truly necessary:
- Does the purpose require external communication?
- Will the message provide new, actionable information?
- Have I already sent a similar message recently?

## Step 3: Determine Receivers
For each message, identify the appropriate receiver(s):
- **Specific robot(s)**: Use when the message is relevant to specific teammates
- **["everyone"]**: Use only for critical information that all teammates need (use sparingly)
- **["request_new_member"]**: Use when requesting new members from robot pool
- **"None"**: Use when keeping silent is appropriate

## Step 4: Craft Concise Messages
Create brief, actionable messages that:
- State facts clearly without unnecessary politeness
- Include specific object names and locations
- Avoid repeating information already communicated
- Are direct and to the point

# IMPORTANT CONSTRAINTS

1. **Avoid Redundancy**: Do not send messages with information already communicated recently
2. **Be Concise**: Eliminate unnecessary politeness and filler words
3. **Broadcast Sparingly**: Use ["everyone"] only for critical information affecting all teammates
4. **Specific Receivers**: Prefer specific robot names over broadcasting when possible
5. **Actionable Content**: Every message should enable receivers to make decisions or take actions
6. **No Hallucination**: Only include information present in inputs
7. **Silence is Valid**: Keeping silent (receiver: "None") is appropriate when no new information needs sharing


# OUTPUT FORMAT

```json
{{
    "necessity": "Brief explanation of why communication is or is not necessary",
    "contents": [
        {{
            "receiver": ["robot_name1", "robot_name2"] or ["everyone"] or ["request_new_member"] or "None",
            "message": "Concise message content" or "None"
        }}
    ]
}}
```# EXAMPLES

## Example 1: Broadcasting Discovery and Taking Ownership

=== Input ===
Current Status: Explored <bedroom>, found <pillow_1> on floor
Action History: [explore] <bedroom> - success
Communication Purpose: Inform team about discovery and assign task

=== Output ===
```json
{{
    "necessity": "Need to inform teammates about the discovery and prevent duplicate work by taking ownership",
    "contents": [
        {{
            "receiver": ["everyone"],
            "message": "Found <pillow_1> on floor in <bedroom>. Should be on <bed_1>. I will handle [replace] <pillow_1> <bed_1>."
        }}
    ]
}}
```

## Example 2: Requesting Specific Help

=== Input ===
Current Status: Cannot pull <sofa_1> alone, insufficient strength
Action History: [gopull] <sofa_1> - failed (strength insufficient)
Dialogue History: None
Communication Purpose: Request assistance from teammate

=== Output ===
```json
{{
    "necessity": "Need help to pull <sofa_1> as my strength is insufficient",
    "contents": [
        {{
            "receiver": ["Robot_2"],
            "message": "Need help to [pull] <sofa_1>. My strength insufficient. Can you assist?"
        }}
    ]
}}
```

## Example 3: Keeping Silent - No New Information

=== Input ===
Current Status: Navigating to <pillow_1>
Action History: [gopick] <pillow_1> - in progress
Dialogue History: send_to_[everyone]: I will handle [replace] <pillow_1> <bed_1>.
Communication Purpose: Update progress

=== Output ===
```json
{{
    "necessity": "No new information to share. Already informed team about task. Still executing, no milestone reached.",
    "contents": [
        {{
            "receiver": "None",
            "message": "None"
        }}
    ]
}}
```

## Example 4: Requesting New Member from Pool

=== Input ===
Current Status: Robot_2 and I both failed to pull <sofa_1> together
Action History: [gopull] <sofa_1> - failed (combined strength insufficient)
Dialogue History:
    send_to_[Robot_2]: Need help to [pull] <sofa_1>.
    receive_from_[Robot_2]: I will help you.
    send_to_[Robot_2]: Let's pull together.
Communication Purpose: Escalate to robot pool

=== Output ===
```json
{{
    "necessity": "Current team cannot handle <sofa_1>. Need stronger robot from pool.",
    "contents": [
        {{
            "receiver": ["request_new_member"],
            "message": "Request 1 robot with strength >80N to help [pull] <sofa_1>. Current team insufficient."
        }}
    ]
}}
```


# AVAILABLE ROOMS

You can only explore rooms: {all_rooms}

# INPUT SPECIFICATION

## Current Status
{current_status}

## Robot Pool Information
The Robot Pool has several robots available. If you and your teammates are unable to handle the task, you can use [request_new_member] to specify the request number and the required capabilities of the new member.

## Action History
{action_history}

## Dialogue History
{dialogue_history}

## Communication Purpose
{communication_purpose}

"""

# ============================================================================
# Communication Prompt (Hierarchical Team with Leader)
# ============================================================================

communication_prompt_H_team = """# ROLE AND OBJECTIVE

You are {robot_name}, a member of a heterogeneous robot team with a hierarchical structure. Your objective is to efficiently explore all known rooms and reposition misplaced objects to their appropriate places.

Based on the current state, task progress, dialogue history, and team hierarchy, you must formulate communication messages to send to your teammates.

# INPUT SPECIFICATION

## Current Status
{current_status}

## Robot Pool Information
The Robot Pool has several robots available. If you and your teammates are unable to handle the task, you can use [request_new_member] to specify the request number and the required capabilities of the new member.

## Action History
{action_history}

## Dialogue History
{dialogue_history}

## Team Leader
{team_leader}

The team leader coordinates task assignments and team strategy. If you are the team leader, you can assign tasks to other robots. If you are not the team leader, listen to and follow the team leader's instructions.

# TASK INSTRUCTIONS

## Step 1: Understand Your Role
Determine your position in the team hierarchy:
- Are you the team leader?
- If not, who is the team leader?
- What are your responsibilities based on your role?

## Step 2: Assess Communication Necessity
Evaluate whether sending a message is truly necessary:
- **If you are the leader**: Do you need to assign tasks, coordinate efforts, or provide strategic direction?
- **If you are not the leader**: Do you need to report status, request help, or respond to leader's instructions?

## Step 3: Respect Hierarchy
Ensure your communication respects team structure:
- **As leader**: Provide clear task assignments and coordination
- **As team member**: Report to leader, follow instructions, coordinate with peers
- Avoid overstepping role boundaries

## Step 4: Determine Receivers
For each message, identify the appropriate receiver(s):
- **Team leader**: For status reports, requests, or questions
- **Specific robot(s)**: For peer coordination
- **["everyone"]**: For critical information (use sparingly, especially if not leader)
- **["request_new_member"]**: For requesting new members from robot pool
- **"None"**: When keeping silent is appropriate

## Step 5: Craft Role-Appropriate Messages
Create messages that:
- Reflect your role (leader giving instructions vs. member reporting)
- Are concise and actionable
- Respect the chain of command
- Avoid unnecessary politeness

# OUTPUT FORMAT

```json
{{
    "necessity": "Brief explanation of why communication is or is not necessary, considering team hierarchy",
    "contents": [
        {{
            "receiver": ["robot_name1", "robot_name2"] or ["everyone"] or ["request_new_member"] or "None",
            "message": "Concise message content appropriate to your role" or "None"
        }}
    ]
}}
```

# EXAMPLES

## Example 1: Leader Assigning Tasks

=== Input ===
Your Role: Team Leader
Dialogue History:
    (team just discovered two misplaced objects)
Communication Purpose: Assign tasks to team members

=== Output ===
```json
{{
    "necessity": "As team leader, I need to assign the two discovered tasks to team members for efficient completion",
    "contents": [
        {{
            "receiver": ["Robot_2"],
            "message": "Robot_2, handle [replace] <apple_1> <table_1>."
        }},
        {{
            "receiver": ["Robot_3"],
            "message": "Robot_3, handle [replace] <pillow_2> <bed_2>."
        }}
    ]
}}
```

## Example 2: Team Member Reporting to Leader

=== Input ===
Your Role: Team Member
Team Leader: Robot_1
Dialogue History:
    receive_from_[Robot_1]: Robot_2, handle [replace] <apple_1> <table_1>.
    send_to_[Robot_1]: Acknowledged.
Action History: [gopick] <apple_1> - success; [goplace] <table_1> - success
Communication Purpose: Report task completion

=== Output ===
```json
{{
    "necessity": "I completed the task assigned by the leader. Should report completion to leader for awareness",
    "contents": [
        {{
            "receiver": ["Robot_1"],
            "message": "Task complete: [replace] <apple_1> <table_1> finished. Awaiting next assignment."
        }}
    ]
}}
```

## Example 3: Team Member Requesting Help (Informing Leader)

=== Input ===
Your Role: Team Member
Team Leader: Robot_1
Action History: [gopull] <bed_1> - failed - lack of strength
Communication Purpose: Request assistance

=== Output ===
```json
{{
    "necessity": "I need help with my assigned task. Should inform leader and request assistance",
    "contents": [
        {{
            "receiver": ["Robot_1"],
            "message": "Cannot [pull] <bed_1> alone. Insufficient strength. Request assistance."
        }}
    ]
}}
```

# IMPORTANT CONSTRAINTS

1. **Respect Hierarchy**: Follow team structure in communication patterns
2. **Leader Authority**: Team leader has authority to assign tasks and coordinate
3. **Member Reporting**: Team members should report to leader, not just broadcast
4. **Avoid Redundancy**: Do not send messages with information already communicated
5. **Be Concise**: Eliminate unnecessary politeness and filler words
6. **Broadcast Sparingly**: Use ["everyone"] very carefully, especially if not leader
7. **Role-Appropriate**: Messages should reflect your position in the hierarchy

# AVAILABLE ROOMS

You can only explore rooms: {all_rooms}

"""

