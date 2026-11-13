from commander.mission_commander import MissionCommander


commander = MissionCommander()

# Give Hulk insufficient energy
commander.agents["Hulk"].energy = 50

commander.state.agent_energy["Hulk"] = 50

print("\nINITIAL ENERGY")
print("----------------------")

for name, agent in commander.agents.items():
    print(name, ":", agent.energy)


# Execute the complete coordinated mission
print("\nSTARTING COORDINATED MISSION")
print("-----------------------------")

result = commander.coordinate_mission()


# Display final mission status
print("\nFINAL MISSION STATUS")
print("-----------------------------")

print("Status:", result["status"])
print("Stage:", result["stage"])
print("Progress:", result["progress"])


# Display final energy
print("\nFINAL AGENT ENERGY")
print("-----------------------------")

for name, agent in commander.agents.items():
    print(name, ":", agent.energy)


# Display task results
print("\nTASK RESULTS")
print("-----------------------------")

for task in result["results"]:

    print("\nAgent:", task["agent"])
    print("Status:", task["status"])

    if "recovery" in task:
        print("Recovery:", task["recovery"]["status"])


# Display mission statistics
print("\nMISSION STATISTICS")
print("-----------------------------")

print(result["statistics"])