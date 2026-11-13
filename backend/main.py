from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from commander.mission_commander import MissionCommander


app = FastAPI(title="Mission Moon AI Backend")


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==========================================
# INITIALIZE MISSION COMMANDER
# ==========================================

commander = MissionCommander()


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Mission Moon Backend is Running!"
    }


# ==========================================
# GET MISSION STATE
# ==========================================

@app.get("/mission")
def mission():

    return commander.state.get_state()


# ==========================================
# START NORMAL MISSION
# ==========================================

@app.post("/mission/start")
def start_mission():

    return commander.start_mission()


# ==========================================
# AGENT COMMUNICATION
# ==========================================

@app.post("/mission/communicate")
def communicate():

    messages = commander.coordinate_agents()

    return {
        "communication_status": "Completed",
        "total_messages": len(messages),
        "messages": messages,
        "mission_state": commander.state.get_state()
    }


# ==========================================
# COORDINATE NORMAL MISSION
# ==========================================

@app.post("/mission/coordinate")
def coordinate_mission():

    return commander.coordinate_mission()

@app.post("/mission/test/automatic-recovery")
def test_automatic_recovery():

    # Reset the mission
    commander.reset_mission()

    # Force Hulk to start with insufficient energy
    hulk = commander.agents["Hulk"]

    hulk.energy = 50

    commander.state.agent_energy["Hulk"] = 50

    # Run the mission inside the FastAPI application
    return commander.coordinate_mission()


@app.post("/mission/test/hulk-health-failure")
def test_hulk_health_failure():

    # Reset mission
    commander.reset_mission()

    # Configure Hulk's health
    hulk = commander.agents["Hulk"]
    hulk.health = 20

    commander.state.agent_health["Hulk"] = 20

    # Configure Iron Man's energy for successful recovery
    ironman = commander.agents["Iron Man"]
    ironman.energy = 100

    commander.state.agent_energy["Iron Man"] = 100

    # Execute mission
    print("DEBUG: Hulk health =", hulk.health)
    print("DEBUG: Iron Man energy =", ironman.energy)
    print("DEBUG: Iron Man state energy =", commander.state.agent_energy["Iron Man"])
    result = commander.coordinate_mission()

    return result

@app.post("/mission/test/hulk-health-insufficient-energy")
def test_hulk_health_insufficient_energy():

    # Reset mission
    commander.reset_mission()

    # Set Hulk's health to 20
    hulk = commander.agents["Hulk"]
    hulk.health = 20

    commander.state.agent_health["Hulk"] = 20

    # Set Iron Man's energy to 30
    ironman = commander.agents["Iron Man"]
    ironman.energy = 30

    commander.state.agent_energy["Iron Man"] = 30

    # Execute mission
    result = commander.coordinate_mission()

    return result


@app.post("/mission/analyze-finding")
def analyze_finding(agent_name: str, finding: str):

    return commander.analyze_agent_finding(
        agent_name,
        finding
    )

# ==========================================
# COMMUNICATION STATISTICS
# ==========================================

@app.get("/mission/communications")
def communication_statistics():

    return commander.get_communication_statistics()


# ==========================================
# AGENT COMMUNICATION HISTORY
# ==========================================

@app.get("/mission/communications/{agent_name}")
def agent_communication(agent_name: str):

    return {
        "agent": agent_name,
        "messages": commander.get_agent_communication(agent_name)
    }


# ==========================================
# SCENARIO 1: HULK ENERGY FAILURE
# ==========================================

@app.post("/mission/scenario/hulk-energy-recovery")
def hulk_energy_recovery():

    return commander.run_hulk_energy_scenario()


# ==========================================
# RESET MISSION
# ==========================================

@app.post("/mission/reset")
def reset_mission():

    return commander.reset_mission()