from commander.mission_commander import MissionCommander


commander = MissionCommander()

# Simulate Hulk's energy failure

hulk = commander.agents["Hulk"]

hulk.energy = 20

failed_result = {
    "agent": "Hulk",
    "status": "Failed",
    "reason": "Insufficient energy to complete all operations.",
    "finding": "Hulk could not remove all rocks."
}

# Ask Mission Commander to evaluate recovery

decision = commander.decide_recovery(
    "Hulk",
    failed_result
)

print("\nMISSION COMMANDER RECOVERY DECISION")
print("-----------------------------------")

print(decision)