# Event Log Model

Robot Behavior Black Box uses structured event records to support post-task operational review. The model separates observed facts from reviewer notes.

## Core fields

| Field | Purpose |
|---|---|
| robot_id | Identifies the robot or fleet unit. |
| event_time | Timestamp of the event. |
| zone | Facility area where the event occurred. |
| task_state | Robot workflow state at the time. |
| review_signal | Signal, timeout, sensor note, or operator note that explains why the event was reviewed. |
| action_taken | What the robot or human actor did next. |
| human_override | Whether a human intervened. |
| outcome | Operational result. |
| reviewer | Person or team reviewing the record. |

## Review outputs

- Event summary
- Incident severity
- Root-cause hypothesis
- Corrective action recommendation
- SOP update recommendation

## Truth rule

Root cause is a hypothesis unless confirmed by qualified technical review, vendor data, facility records, or repeated evidence.
