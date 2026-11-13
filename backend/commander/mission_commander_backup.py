
from agents.spiderman_agent import SpiderManAgent
from agents.hulk_agent import HulkAgent
from agents.ironman_agent import IronManAgent
from agents.sandman_agent import SandmanAgent

from communication.message_bus import MessageBus
from state.mission_state import MissionState
from ai.mission_advisor import mission_advisor


class MissionCommander:

    def __init__(self):

        self.agents = {
            "Spider-Man": SpiderManAgent(),
            "Hulk": HulkAgent(),
            "Iron Man": IronManAgent(),
            "Sandman": SandmanAgent()
        }

        self.state = MissionState()
        self.message_bus = MessageBus()

    # ==========================================
    # TASK ASSIGNMENT
    # ==========================================

    def assign_task(self, agent_name, task):

        agent = self.agents[agent_name]

        result = agent.execute_task(task)

        self.state.update_agent(agent_name, result)

        self.state.agent_health[agent_name] = agent.health
        self.state.agent_energy[agent_name] = agent.energy

        return result
    
    # ==========================================
    # TASK RESULT EVALUATION
    # ==========================================

    def evaluate_task_result(self, result):

        if result["status"] == "Completed":

            return {
                "decision": "Continue",
                "reason": "Task completed successfully.",
                "next_action": "Assign the next mission task."
            }

        return {
            "decision": "Recovery Required",
            "reason": result.get(
                "reason",
                "Agent could not complete the assigned task."
            ),
            "next_action": "Evaluate available recovery options."
        }

        # ==========================================
    # AI-POWERED MISSION DECISION
    # ==========================================

    def analyze_agent_finding(self, agent_name, finding):

        # Get current mission information
        mission_data = self.state.get_state()

        # Ask Groq AI to analyze the finding
        ai_decision = mission_advisor.analyze_mission(
            mission_state=mission_data,
            agent_name=agent_name,
            finding=finding
        )

        recommended_agent = ai_decision["recommended_agent"]

        ai_reason = ai_decision["reason"]
        ai_confidence = ai_decision["confidence"]
        ai_source = ai_decision["source"]

        finding_lower = finding.lower()

        # ------------------------------------------
        # PYTHON VALIDATION
        # ------------------------------------------

        expected_agent = None
        decision_name = "Review Required"
        validation_reason = ""

        # Spider-Man decision
        if agent_name == "Spider-Man":

            if (
                "rock" in finding_lower
                or "obstacle" in finding_lower
            ):

                expected_agent = "Hulk"
                decision_name = "Assign Hulk"

                validation_reason = (
                    "Obstacles detected. Hulk is the "
                    "designated obstacle-removal agent."
                )

            else:

                expected_agent = "Sandman"
                decision_name = "Assign Sandman"

                validation_reason = (
                    "Terrain preparation is required."
                )

        # Hulk decision
        elif agent_name == "Hulk":

            if "removed" in finding_lower:

                expected_agent = "Sandman"
                decision_name = "Assign Sandman"

                validation_reason = (
                    "Obstacle removal is completed."
                )

        # Sandman decision
        elif agent_name == "Sandman":

            if "levelled" in finding_lower:

                expected_agent = "Iron Man"
                decision_name = "Assign Iron Man"

                validation_reason = (
                    "Terrain preparation is completed."
                )

        # Iron Man decision
        elif agent_name == "Iron Man":

            if "constructed" in finding_lower:

                expected_agent = None
                decision_name = "Mission Ready"

                validation_reason = (
                    "Landing platform construction is completed."
                )

        # ------------------------------------------
        # VALIDATE AI RECOMMENDATION
        # ------------------------------------------

        accepted = False

        if expected_agent is None:

            if decision_name == "Mission Ready":

                accepted = True

        elif recommended_agent == expected_agent:

            agent = self.agents[recommended_agent]

            if agent.health > 0:

                accepted = True

        # ------------------------------------------
        # FINAL COMMANDER DECISION
        # ------------------------------------------

        if accepted:

            final_reason = ai_reason

            if not final_reason:
                final_reason = validation_reason

            final_decision = decision_name
            final_agent = expected_agent

        else:

            # Python controls the final decision.
            # Existing recovery logic handles unavailable agents.

            final_decision = decision_name
            final_agent = expected_agent

            final_reason = (
                "AI recommendation: "
                + recommended_agent
                + ". Python validation selected the safe "
                "mission workflow. "
                + validation_reason
            )

        # ------------------------------------------
        # RETURN DECISION
        # ------------------------------------------

        return {

            "decision": final_decision,

            "next_agent": final_agent,

            "reason": final_reason,

            "ai_recommendation": recommended_agent,

            "ai_confidence": ai_confidence,

            "ai_source": ai_source,

            "ai_accepted": accepted

        }
        # ==========================================
    # RECOVERY DECISION
    # ==========================================

    def decide_recovery(self, agent_name, result):

        agent = self.agents[agent_name]

        # --------------------------------------
        # HEALTH-BASED RECOVERY
        # --------------------------------------

        if agent.health <= 0:

            if agent_name == "Hulk":

                remaining_rocks = (
                    agent.total_rocks - agent.rocks_removed
                )

                recovery_agent = self.find_recovery_agent(
                    failed_agent_name=agent_name,
                    remaining_rocks=remaining_rocks
                )

                if recovery_agent is not None:

                    return {
                        "decision": "Delegate Task",
                        "recovery_agent": recovery_agent["agent_name"],
                        "reason": (
                            "Hulk's health is depleted. "
                            "The remaining rocks must be delegated."
                        )
                    }

            return {
                "decision": "Suspend",
                "reason": (
                    f"{agent_name} has depleted health "
                    "and no suitable recovery agent is available."
                )
            }

        # --------------------------------------
        # ENERGY-BASED RECOVERY
        # --------------------------------------

        if "energy" in result.get("reason", "").lower():

            recovery_agent_name = "Iron Man"

            recovery_agent = self.agents.get(
                recovery_agent_name
            )

            if (
                recovery_agent is not None
                and recovery_agent.health > 0
                and recovery_agent.energy > 0
            ):

                return {
                    "decision": "Provide Energy Support",
                    "recovery_agent": recovery_agent_name,
                    "reason": (
                        "Hulk has insufficient energy. "
                        "Iron Man can provide energy support."
                    )
                }

            return {
                "decision": "Suspend",
                "reason": (
                    "No healthy agent with available energy "
                    "can provide recovery support."
                )
            }

        return {
            "decision": "Suspend",
            "reason": (
                "The failure reason does not match "
                "a supported recovery strategy."
            )
        }


    # ==========================================
    # FIND SUITABLE RECOVERY AGENT
    # ==========================================

    def find_recovery_agent(
        self,
        failed_agent_name,
        remaining_rocks
    ):

        for agent_name, agent in self.agents.items():

            if agent_name == failed_agent_name:
                continue

            if agent.health <= 0:
                continue

            # Check rock-removal capability
            if "Rock Destruction" in agent.abilities:

                required_energy = remaining_rocks * 30

                if agent.energy >= required_energy:

                    return {
                        "agent_name": agent_name,
                        "energy_required": required_energy
                    }

            elif "Repulsor Rock Destruction" in agent.abilities:

                required_energy = remaining_rocks * 20

                if agent.energy >= required_energy:

                    return {
                        "agent_name": agent_name,
                        "energy_required": required_energy
                    }

        return None
       
    def delegate_hulk_task_to_ironman(self, task):

        hulk = self.agents["Hulk"]

        remaining_rocks = (
            hulk.total_rocks - hulk.rocks_removed
        )

        # Dynamically find a suitable recovery agent
        recovery_agent_info = self.find_recovery_agent(
            failed_agent_name="Hulk",
            remaining_rocks=remaining_rocks
        )

        if recovery_agent_info is None:

            self.state.status = "Mission Suspended"
            self.state.stage = "No Recovery Agent Available"

            return {
                "status": "Recovery Failed",
                "reason": "No suitable agent is available for task delegation."
            }

        recovery_agent_name = recovery_agent_info["agent_name"]
        recovery_agent = self.agents[recovery_agent_name]

        delegated_task = (
            f"Destroy {remaining_rocks} remaining lunar rocks "
            "using repulsor blasts."
        )

        # Commander assigns the task
        self.communicate(
            "Mission Commander",
            recovery_agent_name,
            delegated_task
        )

        self.communicate(
            recovery_agent_name,
            "Mission Commander",
            "Acknowledged. Preparing to execute the delegated task."
        )

        # Execute using the selected agent
        delegation_result = recovery_agent.destroy_rocks(
            task=delegated_task,
            rocks_to_destroy=remaining_rocks
        )

        # Update mission state
        self.state.update_agent(
            recovery_agent_name,
            delegation_result
        )

        self.state.agent_energy[recovery_agent_name] = recovery_agent.energy
        self.state.agent_health[recovery_agent_name] = recovery_agent.health

        self.communicate(
            recovery_agent_name,
            "Mission Commander",
            delegation_result["finding"]
        )

        if delegation_result["status"] == "Completed":

            self.state.add_event(
                "Task Delegation",
                (
                    f"{recovery_agent_name} successfully destroyed "
                    f"{remaining_rocks} remaining rocks after Hulk's failure."
                )
            )

            self.state.status = "Recovery Successful"
            self.state.stage = "Obstacle Clearance Recovered"

            self.communicate(
                "Mission Commander",
                "All",
                f"{recovery_agent_name} successfully cleared the remaining obstacles."
            )

            return {
                "status": "Recovery Successful",
                "decision": "Delegate Task",
                "recovery_agent": recovery_agent_name,
                "delegation_result": delegation_result
            }

        self.state.status = "Mission Suspended"
        self.state.stage = "Delegation Failed"

        self.state.add_event(
            "Recovery Failed",
            f"{recovery_agent_name} could not destroy the remaining rocks."
        )

        return {
            "status": "Recovery Failed",
            "decision": "Delegate Task",
            "recovery_agent": recovery_agent_name,
            "delegation_result": delegation_result
        }
    # ==========================================
    # AUTOMATIC RECOVERY EXECUTION
    # ==========================================

    def execute_recovery(self, agent_name, task, failed_result):

        # Step 1: Evaluate recovery options

        decision = self.decide_recovery(
            agent_name,
            failed_result
        )
                # Handle health-based task delegation
        if decision["decision"] == "Delegate Task":

            return self.delegate_hulk_task_to_ironman(task)

        if decision["decision"] == "Suspend":

            self.state.status = "Mission Suspended"
            self.state.stage = "Recovery Not Available"

            self.state.add_event(
                "Recovery Failed",
                decision["reason"]
            )

            return {
                "status": "Suspended",
                "decision": decision,
                "message": decision["reason"]
            }

        # Step 2: Identify recovery and target agents

        recovery_agent_name = decision["recovery_agent"]

        recovery_agent = self.agents[recovery_agent_name]

        target_agent = self.agents[agent_name]

        # Step 3: Calculate required energy

        if agent_name == "Hulk":

            remaining_rocks = (
                target_agent.total_rocks
                - target_agent.rocks_removed
            )

            required_energy = remaining_rocks * 30

            energy_deficit = max(
                0,
                required_energy - target_agent.energy
            )

        else:

            energy_deficit = 0

        # Step 4: Request recovery support

        if energy_deficit > 0:

            self.communicate(
                agent_name,
                "Mission Commander",
                (
                    f"I have insufficient energy to complete my task. "
                    f"I require {energy_deficit} energy units."
                )
            )

            self.communicate(
                "Mission Commander",
                recovery_agent_name,
                (
                    f"{agent_name} requires {energy_deficit} "
                    "energy units. Please provide support."
                )
            )

        # Step 5: Check recovery agent resources

        if recovery_agent.energy < energy_deficit:

            failure_message = (
                f"{recovery_agent_name} does not have "
                "sufficient energy to provide support."
            )

            self.communicate(
                recovery_agent_name,
                "Mission Commander",
                failure_message
            )

            self.state.status = "Mission Suspended"

            self.state.stage = "Insufficient Recovery Resources"

            self.state.add_event(
                "Recovery Failed",
                failure_message
            )

            return {
                "status": "Suspended",
                "decision": decision,
                "message": failure_message
            }

        # Step 6: Provide energy support

        if energy_deficit > 0:

            support_result = recovery_agent.provide_energy_support(
                target_agent,
                energy_deficit
            )

            self.state.agent_energy[recovery_agent_name] = (
                recovery_agent.energy
            )

            self.state.agent_energy[agent_name] = (
                target_agent.energy
            )

            # Recovery agent reports support result

            self.communicate(
                recovery_agent_name,
                "Mission Commander",
                support_result["message"]
            )

            self.state.add_event(
                "Energy Support",
                support_result["message"]
            )

            if support_result["status"] != "Completed":

                self.state.status = "Recovery Failed"

                return {
                    "status": "Recovery Failed",
                    "decision": decision,
                    "support_result": support_result
                }

        else:

            support_result = None

        # Step 7: Notify target agent to resume task

        self.communicate(
            "Mission Commander",
            agent_name,
            "Recovery completed. Resume your unfinished task."
        )

        # Step 8: Retry unfinished task

        retry_result = self.assign_task(
            agent_name,
            task
        )

        # Agent reports retry result

        self.communicate(
            agent_name,
            "Mission Commander",
            retry_result["finding"]
        )

        # Step 9: Evaluate retry result

        retry_evaluation = self.evaluate_task_result(
            retry_result
        )

        retry_result["evaluation"] = retry_evaluation

        if retry_evaluation["decision"] == "Continue":

            self.state.status = "Recovery Successful"

            self.state.stage = f"{agent_name} Task Recovered"

            self.state.add_event(
                "Recovery Completed",
                (
                    f"{agent_name} successfully completed "
                    "the task after recovery."
                )
            )

            return {
                "status": "Recovery Successful",
                "decision": decision,
                "support_result": support_result,
                "retry_result": retry_result
            }

        # Step 10: Recovery failed

        self.state.status = "Mission Suspended"

        self.state.stage = "Recovery Attempt Failed"

        self.state.add_event(
            "Recovery Failed",
            f"{agent_name} could not complete the task after recovery."
        )

        return {
            "status": "Recovery Failed",
            "decision": decision,
            "support_result": support_result,
            "retry_result": retry_result
        }
    # ==========================================
    # AGENT COMMUNICATION
    # ==========================================

    def communicate(self, sender, receiver, message):

        message_data = self.message_bus.send_message(
        sender,
        receiver,
        message
    )

        self.state.activity_log.append({
        "agent": sender,
        "action": "Communication",
        "finding": message
    })

        self.state.add_event(
        event_type="Communication",
        description=(
            f"{sender} sent a message to {receiver}: {message}"
        )
    )

        return message_data


    # ==========================================
# COMMUNICATION HISTORY
# ==========================================

    def get_agent_communication(self, agent_name):

        return self.message_bus.get_agent_messages(agent_name)


    def get_communication_statistics(self):

        return self.message_bus.get_statistics()
    # ==========================================
    # NORMAL MISSION
    # ==========================================

    def start_mission(self):

        self.state.status = "In Progress"

        tasks = [
            (
                "Spider-Man",
                "Scout the lunar surface and identify a safe landing route"
            ),
            (
                "Hulk",
                "Remove large rocks and obstacles from the landing area"
            ),
            (
                "Sandman",
                "Analyze and level the lunar terrain"
            ),
            (
                "Iron Man",
                "Construct and stabilize the landing platform"
            )
        ]

        results = []

        for index, (agent_name, task) in enumerate(tasks):

            result = self.assign_task(agent_name, task)

            results.append(result)

            if result["status"] != "Completed":

                self.state.status = "Failed"
                self.state.stage = f"{agent_name} Task Failed"

                mission_data = self.state.get_state()
                mission_data["results"] = results

                return mission_data

            self.state.progress = (index + 1) * 25

        self.state.status = "Preparation Complete"
        self.state.stage = "Preparation Finished"

        mission_data = self.state.get_state()
        mission_data["results"] = results

        return mission_data

        # ==========================================
        # COMMUNICATION DEMO
        # ==========================================

    def coordinate_agents(self):

        messages = []

        messages.append(self.communicate(
            "Spider-Man",
            "Mission Commander",
            "Dangerous crater found near the landing zone."
        ))

        messages.append(self.communicate(
            "Mission Commander",
            "Sandman",
            "Analyze the crater and prepare the terrain."
        ))

        messages.append(self.communicate(
            "Sandman",
            "Mission Commander",
            "Crater identified. Terrain preparation is required."
        ))

        messages.append(self.communicate(
            "Mission Commander",
            "Hulk",
            "Clear rocks around the crater."
        ))

        messages.append(self.communicate(
            "Hulk",
            "Mission Commander",
            "Nearby rocks have been cleared."
        ))

        return messages

    # ==========================================
    # COORDINATED MISSION
    # ==========================================

    def coordinate_mission(self):

        self.state.status = "In Progress"

        results = []

        # Initial task
        current_agent = "Spider-Man"

        current_task = (
            "Scout the lunar surface and identify dangerous areas."
        )

        # Dynamic mission execution
        while current_agent is not None:

            # Step 1: Assign task
            self.communicate(
                "Mission Commander",
                current_agent,
                f"New task assigned: {current_task}"
            )

            result = self.assign_task(
                current_agent,
                current_task
            )

            # Step 2: Agent reports finding
            self.communicate(
                current_agent,
                "Mission Commander",
                result["finding"]
            )

            # Step 3: Evaluate task result
            evaluation = self.evaluate_task_result(result)

            result["evaluation"] = evaluation

            # Step 4: Handle failure and recovery
            if evaluation["decision"] != "Continue":

                self.state.add_event(
                    "Task Failure",
                    f"{current_agent} failed: {evaluation['reason']}"
                )

                self.state.status = "Recovery Required"

                self.state.stage = f"{current_agent} Task Failed"

                recovery_result = self.execute_recovery(
                    current_agent,
                    current_task,
                    result
                )

                result["recovery"] = recovery_result

                if recovery_result["status"] != "Recovery Successful":

                    self.state.status = "Mission Suspended"

                    results.append(result)

                    mission_data = self.state.get_state()
                    mission_data["results"] = results

                    return mission_data

                self.communicate(
                    "Mission Commander",
                    "All",
                    f"{current_agent} recovered successfully. "
                    "Mission execution will continue."
                )

            results.append(result)

            # Step 5: Analyze agent finding
            decision = self.analyze_agent_finding(
                current_agent,
                result["finding"]
            )

            self.state.add_event(
                "Mission Decision",
                (
                    f"Commander selected {decision['next_agent']} "
                    f"because: {decision['reason']}"
                ) if decision["next_agent"] else decision["reason"]
            )

            # Step 6: Select next agent
            current_agent = decision["next_agent"]

            # Step 7: Prepare next task
            if current_agent == "Hulk":

                current_task = (
                    "Remove rocks and obstacles around the crater."
                )

            elif current_agent == "Sandman":

                current_task = (
                    "Analyze the crater and level the surrounding terrain."
                )

            elif current_agent == "Iron Man":

                current_task = (
                    "Construct and stabilize the lunar landing platform."
                )

            # Update progress
            self.state.progress = min(
                100,
                self.state.progress + 25
            )

        # Step 8: Complete mission
        self.state.status = "Preparation Complete"

        self.state.stage = "Landing Platform Ready"

        self.state.progress = 100

        mission_data = self.state.get_state()

        mission_data["results"] = results

        return mission_data

    # ==========================================
    # SCENARIO 1: HULK ENERGY FAILURE AND RECOVERY
    # ==========================================

    def run_hulk_energy_scenario(self):

        self.reset_mission()

        self.state.status = "In Progress"
        self.state.stage = "Reconnaissance"

        results = []

        hulk = self.agents["Hulk"]
        ironman = self.agents["Iron Man"]

        # --------------------------------------
        # STEP 1: SCENARIO CONDITIONS
        # --------------------------------------

        hulk.energy = 50

        self.state.agent_energy["Hulk"] = hulk.energy

        rocks_detected = 3

        self.communicate(
            "Spider-Man",
            "Mission Commander",
            f"I detected {rocks_detected} dangerous rocks near the landing zone."
        )

        self.state.stage = "Obstacle Detection"
        self.state.progress = 10

        # --------------------------------------
        # STEP 2: ASSIGN HULK
        # --------------------------------------

        task = "Remove three dangerous rocks from the landing area."

        self.communicate(
            "Mission Commander",
            "Hulk",
            task
        )

        hulk_result = self.assign_task("Hulk", task)

        results.append(hulk_result)

        self.communicate(
            "Hulk",
            "Mission Commander",
            hulk_result["finding"]
        )

        # --------------------------------------
        # STEP 3: CHECK HULK'S RESULT
        # --------------------------------------

        if hulk_result["status"] == "Completed":

            self.state.status = "Task Completed"
            self.state.stage = "Obstacles Cleared"
            self.state.progress = 80

            mission_data = self.state.get_state()
            mission_data["results"] = results

            return mission_data

        self.state.stage = "Recovery Required"

        self.communicate(
            "Mission Commander",
            "All",
            "Hulk cannot complete the task. Evaluating recovery options."
        )

        # --------------------------------------
        # STEP 4: CALCULATE REQUIRED ENERGY
        # --------------------------------------

        remaining_rocks = hulk.total_rocks - hulk.rocks_removed

        energy_per_rock = 30

        required_energy = remaining_rocks * energy_per_rock

        energy_deficit = required_energy - hulk.energy

        self.communicate(
            "Mission Commander",
            "Iron Man",
            f"Hulk needs {energy_deficit} additional energy to finish the task."
        )

        # --------------------------------------
        # STEP 5: CHECK IRON MAN'S RESOURCES
        # --------------------------------------

        if ironman.energy < energy_deficit:

            self.state.status = "Mission Suspended"
            self.state.stage = "Insufficient Recovery Resources"

            mission_data = self.state.get_state()
            mission_data["results"] = results

            return mission_data

        # --------------------------------------
        # STEP 6: IRON MAN PROVIDES SUPPORT
        # --------------------------------------

        support_result = ironman.provide_energy_support(
            target_agent=hulk,
            amount=energy_deficit
        )

        self.state.agent_energy["Iron Man"] = ironman.energy
        self.state.agent_energy["Hulk"] = hulk.energy

        self.state.activity_log.append({
            "agent": "Iron Man",
            "action": "Energy Support",
            "finding": support_result["message"]
        })

        self.communicate(
            "Iron Man",
            "Mission Commander",
            support_result["message"]
        )

        if support_result["status"] != "Completed":

            self.state.status = "Recovery Failed"
            self.state.stage = "Energy Support Failed"

            mission_data = self.state.get_state()
            mission_data["results"] = results
            mission_data["support_result"] = support_result

            return mission_data

        # --------------------------------------
        # STEP 7: RETRY HULK'S TASK
        # --------------------------------------

        self.communicate(
            "Mission Commander",
            "Hulk",
            "Energy support received. Resume the unfinished work."
        )

        retry_result = self.assign_task(
            "Hulk",
            "Continue removing the remaining dangerous rocks."
        )

        results.append(retry_result)

        self.communicate(
            "Hulk",
            "Mission Commander",
            retry_result["finding"]
        )

        # --------------------------------------
        # STEP 8: VERIFY TASK COMPLETION
        # --------------------------------------

        all_rocks_removed = (
            retry_result["status"] == "Completed"
            and hulk.rocks_removed == rocks_detected
        )

        if all_rocks_removed:

            self.state.status = "Task Completed"
            self.state.stage = "All Obstacles Cleared"
            self.state.progress = 80

            self.communicate(
                "Mission Commander",
                "All",
                "All dangerous rocks removed successfully."
            )

        else:

            self.state.status = "Mission Suspended"
            self.state.stage = "Obstacle Clearance Incomplete"

            self.communicate(
                "Mission Commander",
                "All",
                "Obstacle clearance incomplete. Further recovery is required."
            )

        # --------------------------------------
        # STEP 9: RETURN MISSION DATA
        # --------------------------------------

        mission_data = self.state.get_state()

        mission_data["scenario"] = "Hulk Energy Failure and Recovery"
        mission_data["rocks_detected"] = rocks_detected
        mission_data["results"] = results
        mission_data["support_result"] = support_result

        return mission_data

    # ==========================================
    # RESET MISSION
    # ==========================================

    def reset_mission(self):

        for agent in self.agents.values():

            agent.status = "Ready"
            agent.health = 100
            agent.energy = 100

            if agent.name == "Hulk":

                agent.rocks_removed = 0
                agent.total_rocks = 3

            elif agent.name == "Spider-Man":

                agent.scans_completed = 0

            elif agent.name == "Sandman":

                agent.craters_filled = 0
                agent.terrain_operations = 0

        self.state = MissionState()
        self.message_bus = MessageBus()

        return {
            "message": "Mission successfully reset!",
            "mission_state": self.state.get_state()
        }