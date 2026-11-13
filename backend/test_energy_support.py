from agents.hulk_agent import HulkAgent
from agents.ironman_agent import IronManAgent


hulk = HulkAgent()
ironman = IronManAgent()

# Simulate Hulk having limited initial energy
hulk.energy = 50

print("\n========== FIRST ATTEMPT ==========")

result = hulk.execute_task(
    "Remove three dangerous rocks."
)

print(result)

print("\nHulk energy:", hulk.energy)
print("Rocks removed:", hulk.rocks_removed)


# Iron Man provides support
print("\n========== IRON MAN SUPPORT ==========")

support = ironman.provide_energy_support(hulk, 40)

print(support)


# Hulk resumes the unfinished task
print("\n========== HULK RESUMES TASK ==========")

result = hulk.execute_task(
    "Continue removing the remaining rocks."
)

print(result)

print("\n========== FINAL STATUS ==========")

print("Hulk energy:", hulk.energy)
print("Iron Man energy:", ironman.energy)
print("Rocks removed:", hulk.rocks_removed)
print("Mission task:", result["status"])