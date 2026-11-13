from agents.base_agent import BaseAgent


class HulkAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Hulk",
            role="Obstacle Removal",
            abilities=[
                "Rock Destruction",
                "Debris Clearing",
                "Heavy Lifting"
            ]
        )

        # Persistent task memory
        self.total_rocks = 3
        self.rocks_removed = 0

        # Resource consumption per rock
        self.energy_per_rock = 30
        self.damage_per_rock = 10

    def execute_task(self, task):

        operation_log = []
        energy_used = 0

        if self.health <= 0:

            return self.fail_task(
                action="Clearing lunar obstacles",
                task=task,
                reason="Hulk's health is depleted."
            )

        self.receive_task(task)

        # Resume from the next unfinished rock
        for rock_number in range(
            self.rocks_removed + 1,
            self.total_rocks + 1
        ):

            # Check health before starting the next rock
            if self.health <= 0:

                operation_log.append({
                    "rock": rock_number,
                    "status": "Failed",
                    "reason": "Hulk's health is depleted.",
                    "health_remaining": self.health
                })

                break

            # Check energy
            if self.energy < self.energy_per_rock:

                operation_log.append({
                    "rock": rock_number,
                    "status": "Failed",
                    "reason": "Insufficient energy",
                    "energy_remaining": self.energy,
                    "health_remaining": self.health
                })

                break

            # Consume energy
            self.use_energy(self.energy_per_rock)

            # Take damage
            self.take_damage(self.damage_per_rock)

            # Update completed work
            self.rocks_removed += 1
            energy_used += self.energy_per_rock

            operation_log.append({
                "rock": rock_number,
                "status": "Completed",
                "energy_used": self.energy_per_rock,
                "energy_remaining": self.energy,
                "damage_taken": self.damage_per_rock,
                "health_remaining": self.health
            })

        # Check if all rocks are removed
        if self.rocks_removed == self.total_rocks:

            result = self.complete_task(
                action="Smashing lunar obstacles",
                task=task,
                finding="All three dangerous rocks have been removed.",
                energy_used=energy_used
            )

            result["rocks_removed"] = self.rocks_removed
            result["total_rocks"] = self.total_rocks
            result["operation_log"] = operation_log

            return result

        # Task failed before completion
        self.status = "Failed"

        if self.health <= 0:

            reason = "Hulk's health is depleted."

        else:

            reason = "Insufficient energy to complete all operations."

        return {
            "agent": self.name,
            "action": "Smashing lunar obstacles",
            "task": task,
            "finding": (
                f"Hulk removed {self.rocks_removed} out of "
                f"{self.total_rocks} rocks."
            ),
            "status": "Failed",
            "reason": reason,
            "rocks_removed": self.rocks_removed,
            "total_rocks": self.total_rocks,
            "remaining_rocks": (
                self.total_rocks - self.rocks_removed
            ),
            "energy_remaining": self.energy,
            "health": self.health,
            "operation_log": operation_log
        }