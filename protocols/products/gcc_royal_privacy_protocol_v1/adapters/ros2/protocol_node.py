from dataclasses import dataclass

@dataclass
class ProtocolState:
    country: str
    venue: str
    privacy_mode: bool = False
    royal_mode: bool = False
    min_distance_m: float = 2.0
    max_eye_contact_sec: float = 2.0
    response_only: bool = True

def resolve_state(base, country_cfg, privacy_cfg=None, royal_cfg=None):
    state = ProtocolState(
        country=country_cfg["name"],
        venue="unknown",
        min_distance_m=base["gcc_base"]["proximity"]["default_min_distance_m"],
        max_eye_contact_sec=base["gcc_base"]["gaze"]["max_direct_eye_contact_sec"],
        response_only=not base["gcc_base"]["interaction"]["initiate_conversation"],
    )

    if "proximity" in country_cfg:
        state.min_distance_m = country_cfg["proximity"]["default_min_distance_m"]
    if "gaze" in country_cfg:
        state.max_eye_contact_sec = country_cfg["gaze"]["max_direct_eye_contact_sec"]

    if privacy_cfg:
        state.privacy_mode = True
        state.min_distance_m = max(state.min_distance_m, privacy_cfg["proximity"]["default_min_distance_m"])
        state.max_eye_contact_sec = min(state.max_eye_contact_sec, privacy_cfg["gaze"]["max_direct_eye_contact_sec"])
        state.response_only = True

    if royal_cfg:
        state.royal_mode = True
        state.min_distance_m = max(state.min_distance_m, royal_cfg["proximity"]["default_min_distance_m"])
        state.max_eye_contact_sec = min(state.max_eye_contact_sec, royal_cfg["gaze"]["max_direct_eye_contact_sec"])
        state.response_only = True

    return state
