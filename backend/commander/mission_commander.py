
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

        task_lower = task.lower()

        # --------------------------------------
        # IRON MAN: ROCK DESTRUCTION
        # --------------------------------------

        if (
            agent_name == "Iron Man"
            and ("rock" in task_lower or "obstacle" in task_lower)
            and "platform" not in task_lower
        ):

            hulk = self.agents["Hulk"]

            remaining_rocks = max(
                0,
                hulk.total_rocks - hulk.rocks_removed
            )

            if remaining_rocks == 0:

                result = {
                    "agent": "Iron Man",
                    "task": task,
                    "status": "Failed",
                    "finding": "No remaining rocks require removal.",
                    "reason": "All detected rocks have already been cleared."
                }

            else:

                result = agent.destroy_rocks(
                    task=task,
                    rocks_to_destroy=remaining_rocks
                )

                # Synchronize shared rock-removal progress
                rocks_destroyed = result.get(
                    "rocks_destroyed", 0
                )

                hulk.rocks_removed += rocks_destroyed

                # Prevent the count from exceeding total rocks
                hulk.rocks_removed = min(
                    hulk.rocks_removed,
                    hulk.total_rocks
                )
        # --------------------------------------
        # OTHER AGENTS AND TASKS
        # --------------------------------------

        else:

            result = agent.execute_task(task)

        # --------------------------------------
        # UPDATE MISSION STATE
        # --------------------------------------

        self.state.update_agent(
            agent_name,
            result
        )

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

        mission_data = self.state.get_state()

        # Ask Groq AI for its recommendation
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

        # --------------------------------------
        # IDENTIFY REQUIRED CAPABILITY
        # --------------------------------------

        required_capability = None
        decision_name = "Review Required"
        task_type = None

        if agent_name == "Spider-Man":

            if "rock" in finding_lower or "obstacle" in finding_lower:

                required_capability = "rock_removal"
                decision_name = "Clear Lunar Obstacles"
                task_type = "rock_removal"

            else:

                required_capability = "Surface Analysis"
                decision_name = "Prepare Lunar Terrain"
                task_type = "terrain"

        elif agent_name == "Hulk":

            if "removed" in finding_lower:

                required_capability = "Surface Analysis"
                decision_name = "Prepare Lunar Terrain"
                task_type = "terrain"

        elif agent_name == "Iron Man":

            if "destroyed" in finding_lower:

                required_capability = "Surface Analysis"
                decision_name = "Prepare Lunar Terrain"
                task_type = "terrain"

            elif "constructed" in finding_lower:

                decision_name = "Mission Ready"

        elif agent_name == "Sandman":

            if "levelled" in finding_lower:

                required_capability = "Landing Platform Construction"
                decision_name = "Construct Landing Platform"
                task_type = "construction"

        # --------------------------------------
        # PYTHON VALIDATION
        # --------------------------------------

        def is_suitable(candidate_name):

            candidate = self.agents.get(candidate_name)

            if candidate is None:
                return False

            if candidate.health <= 0:
                return False

            if candidate.status == "Unavailable":
                return False

            if required_capability == "rock_removal":

                if candidate_name == "Hulk":

                    remaining = (
                        candidate.total_rocks
                        - candidate.rocks_removed
                    )

                    # Allow partial progress so the existing
                    # recovery system can handle failures.
                    return (
                        remaining > 0
                        and candidate.energy >= candidate.energy_per_rock
                        and "Rock Destruction" in candidate.abilities
                    )

                if candidate_name == "Iron Man":

                    remaining = (
                        self.agents["Hulk"].total_rocks
                        - self.agents["Hulk"].rocks_removed
                    )

                    return (
                        remaining > 0
                        and candidate.energy >= candidate.energy_per_rock
                        and "Repulsor Rock Destruction" in candidate.abilities
                    )

                return False

            if required_capability:

                return (
                    required_capability in candidate.abilities
                    and candidate.energy >= (
                        20 if required_capability == "Surface Analysis"
                        else 25
                    )
                )

            return False

        # --------------------------------------
        # SELECT AI-RECOMMENDED AGENT
        # --------------------------------------

        accepted = False
        final_agent = None
        final_reason = ai_reason

        if decision_name == "Mission Ready":

            accepted = True
            final_decision = "Mission Ready"

        elif is_suitable(recommended_agent):

            final_agent = recommended_agent
            accepted = True
            final_decision = decision_name

        else:

            # ----------------------------------
            # PYTHON FALLBACK
            # ----------------------------------

            if required_capability == "rock_removal":

                candidates = ["Hulk", "Iron Man"]

            elif required_capability == "Surface Analysis":

                candidates = ["Sandman"]

            elif required_capability == "Landing Platform Construction":

                candidates = ["Iron Man"]

            else:

                candidates = []

            for candidate_name in candidates:

                if is_suitable(candidate_name):

                    final_agent = candidate_name
                    break

            if final_agent:

                final_decision = decision_name

                final_reason = (
                    "Groq recommended "
                    + recommended_agent
                    + ", but Python validation selected "
                    + final_agent
                    + " because the recommended agent "
                    "was not suitable."
                )

            else:

                final_decision = "No Suitable Agent"
                final_reason = (
                    "No available agent has the required "
                    "capability, health and energy."
                )

        # --------------------------------------
        # RETURN COMMANDER DECISION
        # --------------------------------------

        return {

            "decision": final_decision,

            "next_agent": final_agent,

            "task_type": task_type,

            "reason": final_reason,

            "ai_recommendation": recommended_agent,

            "ai_confidence": ai_confidence,

            "ai_source": ai_source,

            "ai_accepted": accepted

        }



    # ==========================================
    # FIND SUITABLE RECOVERY AGENT
    # ==========================================


    # ==========================================
    # RECOVERY DECISION
    # ==========================================

    def decide_recovery(self, agent_name, result):

        agent = self.agents[agent_name]

        # HEALTH-BASED RECOVERY
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

        # ENERGY-BASED RECOVERY
        if "energy" in result.get("reason", "").lower():

            recovery_agent_name = "Iron Man"
            recovery_agent = self.agents.get(recovery_agent_name)

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

        current_agent = "Spider-Man"

        current_task = (
            "Scout the lunar surface and identify dangerous areas."
        )

        while current_agent is not None:

            # ----------------------------------
            # STEP 1: ASSIGN TASK
            # ----------------------------------

            self.communicate(
                "Mission Commander",
                current_agent,
                f"New task assigned: {current_task}"
            )

            result = self.assign_task(
                current_agent,
                current_task
            )

            # ----------------------------------
            # STEP 2: AGENT REPORTS FINDING
            # ----------------------------------

            self.communicate(
                current_agent,
                "Mission Commander",
                result.get("finding", "Task execution finished.")
            )

            # ----------------------------------
            # STEP 3: EVALUATE RESULT
            # ----------------------------------

            evaluation = self.evaluate_task_result(result)

            result["evaluation"] = evaluation

            # ----------------------------------
            # STEP 4: HANDLE FAILURE AND RECOVERY
            # ----------------------------------

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

            # ----------------------------------
            # STEP 5: ASK GROQ AND VALIDATE
            # ----------------------------------

            decision = self.analyze_agent_finding(
                current_agent,
                result.get("finding", "")
            )

            selected_agent = decision["next_agent"]

            self.state.add_event(
                "Mission Decision",
                (
                    f"Commander selected {selected_agent}. "
                    f"AI recommendation: "
                    f"{decision['ai_recommendation']}. "
                    f"Reason: {decision['reason']}"
                ) if selected_agent else decision["reason"]
            )

            # ----------------------------------
            # STEP 6: CHECK MISSION COMPLETION
            # ----------------------------------

            if decision["decision"] == "Mission Ready":

                current_agent = None
                break

            if selected_agent is None:

                self.state.status = "Mission Suspended"
                self.state.stage = "No Suitable Agent Available"

                mission_data = self.state.get_state()
                mission_data["results"] = results

                return mission_data

            # ----------------------------------
            # STEP 7: SELECT TASK FROM TASK TYPE
            # ----------------------------------

            task_type = decision["task_type"]

            if task_type == "rock_removal":

                current_task = (
                    "Remove all remaining dangerous rocks "
                    "and obstacles around the lunar crater."
                )

            elif task_type == "terrain":

                current_task = (
                    "Analyze the crater and level the "
                    "surrounding lunar terrain."
                )

            elif task_type == "construction":

                current_task = (
                    "Construct and stabilize the lunar "
                    "landing platform."
                )

            else:

                self.state.status = "Mission Suspended"
                self.state.stage = "Unknown Task Type"

                mission_data = self.state.get_state()
                mission_data["results"] = results

                return mission_data
                        # ----------------------------------
            # STEP 8: MOVE TO THE NEXT AGENT
            # ----------------------------------

            current_agent = selected_agent

            self.state.progress = min(
                100,
                self.state.progress + 25
            )

        # --------------------------------------
        # STEP 9: COMPLETE THE MISSION
        # --------------------------------------

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