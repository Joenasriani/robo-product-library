Compatibility Guide

Supported Platforms (Tested / Mapped)

- ROS2-based humanoids (generic middleware integration)
- SoftBank Pepper (adapter mapping provided)
- Engineered Arts Ameca (expression + gaze mapping provided)
- Unitree humanoids (navigation + distance mapping provided)

Required Capabilities

- Speech TTS (Arabic + English)
- Speech ASR (recommended for interaction)
- People detection
- Distance estimation
- Gaze control or head tracking

Optional Enhancements

- Face tracking (for better gaze alignment)
- Badge detection (for VIP / metadata triggers)
- Camera privacy lock (for restricted zones)
- Remote operator dashboard

Limitations

- Behavior depends on robot execution layer quality
- Navigation stack must be configured separately
- Voice quality depends on TTS provider

Integration Type

- Policy-layer integration (non-invasive)
- Can run alongside existing navigation + AI stacks
