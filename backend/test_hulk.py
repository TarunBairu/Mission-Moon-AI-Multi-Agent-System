from agents.hulk_agent import HulkAgent


# =====================================
# TEST 1: Hulk has 100% energy
# =====================================

print("\n========== TEST 1: FULL ENERGY ==========")

hulk = HulkAgent()

result = hulk.execute_task(
    "Remove three dangerous rocks from the landing area."
)

print("Result:", result["status"])
print("Rocks removed:", result["rocks_removed"])
print("Energy remaining:", hulk.energy)

for operation in result["operation_log"]:
    print(operation)


# =====================================
# TEST 2: Hulk has only 50% energy
# =====================================

print("\n========== TEST 2: LOW ENERGY ==========")

hulk = HulkAgent()

# Simulate an agent that has already consumed 50 energy
hulk.energy = 50

result = hulk.execute_task(
    "Remove three dangerous rocks from the landing area."
)

print("Result:", result["status"])
print("Rocks removed:", result["rocks_removed"])
print("Energy remaining:", hulk.energy)
print("Reason:", result["reason"])

for operation in result["operation_log"]:
    print(operation)