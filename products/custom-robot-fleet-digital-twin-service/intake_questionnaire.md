# Intake Questionnaire

Use this questionnaire before quoting or delivering a customer-specific fleet digital twin package.

## Buyer profile

1. Company name
2. Country and city
3. Industry
4. Main contact
5. Intended audience for the demo

## Facility information

1. What type of facility should be represented?
2. Do you have a floor plan, CAD drawing, sketch, or zone map?
3. What are the important zones?
4. What static obstacles should be shown?
5. Are there restricted areas or one-way paths?

## Machine information

1. What robot or machine models should be represented?
2. How many units should appear in the simulation?
3. What are the payload limits?
4. What are the approximate speed limits?
5. What battery or runtime assumptions should be used?
6. Are there attachments, carts, lifts, arms, sensors, or special payloads?

## Workflow information

1. What tasks should the system demonstrate?
2. What is the normal source-to-destination flow?
3. What tasks need priority handling?
4. What should happen when a robot is unavailable?
5. What events should appear in the operator log?

## Exception scenarios

1. Low battery
2. Blocked path
3. Temporary human presence
4. Machine unavailable
5. Communication loss
6. Over-payload request
7. Emergency stop
8. Other scenarios

## Integration feasibility

1. Do the machines expose an API?
2. Is telemetry available?
3. Is command access permitted?
4. Is vendor documentation available?
5. Is the target environment ROS 2, PLC, REST, MQTT, WebSocket, WMS, ERP, or another system?
6. Is this only for simulation, or should a later integration phase be assessed?
