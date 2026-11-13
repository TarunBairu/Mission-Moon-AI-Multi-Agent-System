from commander.mission_commander import MissionCommander


commander = MissionCommander()

# --------------------------------
# STEP 1: PREPARE SCENARIO
# --------------------------------

hulk = commander.agents["Hulk"]
ironman = commander.agents["Iron Man"]

# Give Hulk insufficient energy
hulk.energy = 50

commander.state.agent_energy["Hulk"] = 50

print("\nINITIAL ENERGY")
print("------------------------")
print("Hulk:", hulk.energy)
print("Iron Man:", ironman.energy)


# --------------------------------
# STEP 2: ASSIGN TASK TO HULK
# --------------------------------

task = "Remove three dangerous rocks from the landing area."

print("\nHULK EXECUTES TASK")
print("------------------------")

failed_result = commander.assign_task(
    "Hulk",
    task
)

print(failed_result)


# --------------------------------
# STEP 3: CHECK FAILURE
# --------------------------------

if failed_result["status"] == "Failed":

    print("\nMISSION COMMANDER INITIATES RECOVERY")
    print("------------------------------------")

    recovery_result = commander.execute_recovery(
        agent_name="Hulk",
        task=task,
        failed_result=failed_result
    )

    print(recovery_result)


# --------------------------------
# STEP 4: FINAL RESOURCE STATUS
# --------------------------------

print("\nFINAL ENERGY")
print("------------------------")

print("Hulk:", hulk.energy)
print("Iron Man:", ironman.energy)

print("Rocks removed:", hulk.rocks_removed)

print("\nMISSION STATUS")
print("------------------------")

print(commander.state.status)