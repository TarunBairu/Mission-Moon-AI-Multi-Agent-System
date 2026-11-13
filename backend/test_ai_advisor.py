from state.mission_state import MissionState
from ai.mission_advisor import mission_advisor

state = MissionState()

result = mission_advisor.analyze_mission(
    mission_state=state.get_state(),
    agent_name="Spider-Man",
    finding="Three dangerous rocks detected near the lunar landing area."
)

print("\n========== AI MISSION ADVISOR ==========")
print("Action:", result["action"])
print("Recommended Agent:", result["recommended_agent"])
print("Reason:", result["reason"])
print("Confidence:", result["confidence"])
print("Source:", result["source"])
print("========================================")