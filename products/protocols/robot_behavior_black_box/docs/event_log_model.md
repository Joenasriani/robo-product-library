# Event Log Model

Robot Behavior Black Box uses structured event records to support post-task operational review. The model separates observed facts from reviewer notes.

## Core fields

- robot_id
- event_time
- zone
- task_state
- review_signal
- action_taken
- human_override
- outcome
- reviewer

## Review outputs

- Event summary
- Incident severity
- Root-cause hypothesis
- Corrective action recommendation
- SOP update recommendation

## Truth rule

Root cause is a hypothesis unless confirmed by qualified technical review, vendor data, facility records, or repeated evidence.
