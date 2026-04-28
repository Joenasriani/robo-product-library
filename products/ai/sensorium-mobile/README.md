# Sensorium Mobile

Robotics mobile sensor bridge packaged as an independent sellable product.

This app converts a smartphone into a real-time sensor node streaming:
- Camera
- IMU (motion)
- GPS
- Audio

via WebSocket to a backend bridge, with optional ROS2 publishing.

## Positioning

This is NOT a demo or placeholder.
This is a real runnable product, but:
- ROS2 publishing depends on buyer environment
- requires installation support

Recommended marketplace state: inquiry_only

## Usage (developer level)

1. Install dependencies
   npm ci

2. Run checks
   npm run check
   npm test

3. Start app
   npm run dev

4. Connect mobile device via HTTPS

## ROS2 mode

Requires:
- Ubuntu + ROS2
- rclnodejs

## Deliverables

- manifest.yaml
- SENSORIUM_FIX_REPORT.md
- bundle (see BUNDLE_UPLOAD_REQUIRED.md)

## Notes

This product is aligned with RoboMarket architecture:
create → validate → publish → sell → route → build → QA → ship → support
