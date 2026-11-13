class MissionState:

    def __init__(self):

        self.mission_name = "Mission Moon"
        self.status = "Ready"
        self.stage = "Reconnaissance"
        self.progress = 0

        # ----------------------------------
        # AGENT STATUS
        # ----------------------------------

        self.agent_status = {
            "Spider-Man": "Ready",
            "Hulk": "Ready",
            "Iron Man": "Ready",
            "Sandman": "Ready"
        }

        self.agent_health = {
            "Spider-Man": 100,
            "Hulk": 100,
            "Iron Man": 100,
            "Sandman": 100
        }

        self.agent_energy = {
            "Spider-Man": 100,
            "Hulk": 100,
            "Iron Man": 100,
            "Sandman": 100
        }

        # ----------------------------------
        # MISSION MEMORY
        # ----------------------------------

        self.findings = {}

        self.activity_log = []

        self.task_history = []

        self.mission_events = []

        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0

    # ======================================
    # UPDATE AGENT INFORMATION
    # ======================================

    def update_agent(self, agent_name, result):

        self.agent_status[agent_name] = result["status"]

        self.findings[agent_name] = result["finding"]

        # Update task statistics

        self.total_tasks += 1

        if result["status"] == "Completed":

            self.completed_tasks += 1

        else:

            self.failed_tasks += 1

        # Store detailed task history

        task_record = {
            "agent": agent_name,
            "task": result["task"],
            "action": result["action"],
            "finding": result["finding"],
            "status": result["status"],
            "energy_used": result.get("energy_used", 0),
            "energy_remaining": result.get(
                "energy_remaining",
                self.agent_energy[agent_name]
            ),
            "health": result.get(
                "health",
                self.agent_health[agent_name]
            )
        }

        self.task_history.append(task_record)

        # Store activity log

        self.activity_log.append({
            "agent": agent_name,
            "action": result["action"],
            "finding": result["finding"],
            "status": result["status"]
        })

    # ======================================
    # RECORD MISSION EVENTS
    # ======================================

    def add_event(self, event_type, description):

        event = {
            "event_type": event_type,
            "description": description
        }

        self.mission_events.append(event)

        return event

    # ======================================
    # GET COMPLETE MISSION STATE
    # ======================================

    def get_state(self):

        return {
            "mission": self.mission_name,

            "status": self.status,

            "stage": self.stage,

            "progress": self.progress,

            "agent_status": self.agent_status,

            "agent_health": self.agent_health,

            "agent_energy": self.agent_energy,

            "findings": self.findings,

            "activity_log": self.activity_log,

            "task_history": self.task_history,

            "mission_events": self.mission_events,

            "statistics": {
                "total_tasks": self.total_tasks,
                "completed_tasks": self.completed_tasks,
                "failed_tasks": self.failed_tasks
            }
        }