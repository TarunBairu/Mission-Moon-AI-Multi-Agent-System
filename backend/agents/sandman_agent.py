from agents.base_agent import BaseAgent


class SandmanAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Sandman",
            role="Terrain Analysis and Preparation",
            abilities=[
                "Surface Analysis",
                "Crater Filling",
                "Terrain Levelling"
            ]
        )

        self.craters_filled = 0
        self.terrain_operations = 0

    def execute_task(self, task):

        energy_required = 20

        # Check agent health
        if self.health <= 0:

            return self.fail_task(
                action="Preparing lunar terrain",
                task=task,
                reason="Sandman's health is depleted."
            )

        # Check available energy
        if self.energy < energy_required:

            return self.fail_task(
                action="Preparing lunar terrain",
                task=task,
                reason="Insufficient energy to prepare lunar terrain."
            )

        # Start task
        self.receive_task(task)

        # Consume energy
        self.use_energy(energy_required)

        self.terrain_operations += 1
        self.craters_filled += 1

        return self.complete_task(
            action="Preparing lunar terrain",
            task=task,
            finding="Uneven terrain analyzed and levelled successfully.",
            energy_used=energy_required
        )