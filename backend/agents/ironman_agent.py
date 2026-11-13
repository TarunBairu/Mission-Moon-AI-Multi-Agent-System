from agents.base_agent import BaseAgent


class IronManAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="Iron Man",
            role="Platform Construction and Engineering",
            abilities=[
                "Landing Platform Construction",
                "Structural Validation",
                "Structural Repair",
                "Energy Support",
                "Repulsor Rock Destruction"
            ]
        )

        # Repulsor configuration
        self.energy_per_rock = 20

    def provide_energy_support(self, target_agent, amount):

        if self.health <= 0:

            return {
                "agent": self.name,
                "status": "Failed",
                "message": (
                    "Iron Man cannot provide support because "
                    "his health is depleted."
                )
            }

        if amount <= 0:

            return {
                "agent": self.name,
                "status": "Failed",
                "message": "Energy support amount must be greater than zero."
            }

        if self.energy < amount:

            return {
                "agent": self.name,
                "status": "Failed",
                "message": (
                    "Iron Man does not have sufficient energy "
                    "to provide support."
                )
            }

        self.use_energy(amount)

        target_agent.energy = min(
            100,
            target_agent.energy + amount
        )

        return {
            "agent": self.name,
            "target": target_agent.name,
            "status": "Completed",
            "energy_transferred": amount,
            "ironman_energy_remaining": self.energy,
            "target_energy_remaining": target_agent.energy,
            "message": (
                f"Iron Man provided {amount}% energy support "
                f"to {target_agent.name}."
            )
        }

    def destroy_rocks(self, task, rocks_to_destroy):

        operation_log = []
        rocks_destroyed = 0
        energy_used = 0

        if self.health <= 0:

            return self.fail_task(
                action="Destroying lunar rocks with repulsors",
                task=task,
                reason="Iron Man's health is depleted."
            )

        if rocks_to_destroy <= 0:

            return self.fail_task(
                action="Destroying lunar rocks with repulsors",
                task=task,
                reason="The number of rocks must be greater than zero."
            )

        self.receive_task(task)

        for rock_number in range(1, rocks_to_destroy + 1):

            if self.health <= 0:

                operation_log.append({
                    "rock": rock_number,
                    "status": "Failed",
                    "reason": "Iron Man's health is depleted."
                })

                break

            if self.energy < self.energy_per_rock:

                operation_log.append({
                    "rock": rock_number,
                    "status": "Failed",
                    "reason": "Insufficient energy",
                    "energy_remaining": self.energy
                })

                break

            # Fire repulsor beam
            self.use_energy(self.energy_per_rock)

            rocks_destroyed += 1
            energy_used += self.energy_per_rock

            operation_log.append({
                "rock": rock_number,
                "status": "Destroyed",
                "action": "Repulsor blast",
                "energy_used": self.energy_per_rock,
                "energy_remaining": self.energy
            })

        if rocks_destroyed == rocks_to_destroy:

            result = self.complete_task(
                action="Destroying lunar rocks with repulsors",
                task=task,
                finding=(
                    f"Iron Man destroyed {rocks_destroyed} rocks "
                    "using repulsor blasts."
                ),
                energy_used=energy_used
            )

            result["rocks_destroyed"] = rocks_destroyed
            result["operation_log"] = operation_log

            return result

        self.status = "Failed"

        return {
            "agent": self.name,
            "action": "Destroying lunar rocks with repulsors",
            "task": task,
            "finding": (
                f"Iron Man destroyed {rocks_destroyed} out of "
                f"{rocks_to_destroy} rocks."
            ),
            "status": "Failed",
            "reason": "Insufficient energy to destroy all rocks.",
            "rocks_destroyed": rocks_destroyed,
            "remaining_rocks": rocks_to_destroy - rocks_destroyed,
            "energy_remaining": self.energy,
            "health": self.health,
            "operation_log": operation_log
        }

    def execute_task(self, task):

        energy_required = 25

        if self.health <= 0:

            return self.fail_task(
                action="Constructing landing platform",
                task=task,
                reason="Iron Man's health is depleted."
            )

        if self.energy < energy_required:

            return self.fail_task(
                action="Constructing landing platform",
                task=task,
                reason=(
                    "Insufficient energy to construct "
                    "the landing platform."
                )
            )

        self.receive_task(task)

        self.use_energy(energy_required)

        return self.complete_task(
            action="Constructing landing platform",
            task=task,
            finding="Landing platform constructed and ready for validation.",
            energy_used=energy_required
        )