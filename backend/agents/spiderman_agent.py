from agents.base_agent import BaseAgent


class SpiderManAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Spider-Man",
            role="Navigation and Scouting",
            abilities=[
                "Web Rescue",
                "Route Detection",
                "Area Scouting"
            ]
        )

        self.scans_completed = 0

    def execute_task(self, task):

        energy_required = 15

        # Check agent health
        if self.health <= 0:

            return self.fail_task(
                action="Scanning lunar surface",
                task=task,
                reason="Spider-Man's health is depleted."
            )

        # Check available energy
        if self.energy < energy_required:

            return self.fail_task(
                action="Scanning lunar surface",
                task=task,
                reason="Insufficient energy to complete scouting."
            )

        # Start task
        self.receive_task(task)

        # Consume energy
        self.use_energy(energy_required)

        self.scans_completed += 1

        return self.complete_task(
            action="Scanning lunar surface",
            task=task,
            finding=(
    "Three dangerous rocks detected near the lunar landing area. "
    "Obstacle removal is required before terrain preparation."
),
            energy_used=energy_required
        )