class BaseAgent:

    def __init__(self, name, role, abilities):

        self.name = name
        self.role = role
        self.abilities = abilities

        self.status = "Ready"
        self.energy = 100
        self.health = 100

    def receive_task(self, task):

        if self.health <= 0:
            self.status = "Unavailable"

            return {
                "agent": self.name,
                "task": task,
                "status": "Failed",
                "reason": "Agent health is depleted."
            }

        self.status = "Working"

        return {
            "agent": self.name,
            "task": task,
            "status": self.status
        }

    def use_energy(self, amount):

        if amount < 0:
            raise ValueError("Energy consumption cannot be negative.")

        if self.energy < amount:
            return False

        self.energy -= amount

        return True

    def take_damage(self, amount):

        if amount < 0:
            raise ValueError("Damage cannot be negative.")

        self.health = max(0, self.health - amount)

    def complete_task(self, action, task, finding, energy_used):

        self.status = "Ready"

        return {
            "agent": self.name,
            "action": action,
            "task": task,
            "finding": finding,
            "status": "Completed",
            "energy_used": energy_used,
            "energy_remaining": self.energy,
            "health": self.health
        }

    def fail_task(self, action, task, reason):

        self.status = "Failed"

        return {
            "agent": self.name,
            "action": action,
            "task": task,
            "finding": reason,
            "status": "Failed",
            "reason": reason,
            "energy_remaining": self.energy,
            "health": self.health
        }

    def execute_task(self, task):

        raise NotImplementedError(
            "Each superhero must implement its own task execution."
        )

    def send_message(self, message):

        return {
            "agent": self.name,
            "message": message
        }