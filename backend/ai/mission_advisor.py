
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BACKEND_DIR / ".env")


# --------------------------------------------------
# MISSION ADVISOR
# --------------------------------------------------

class MissionAdvisor:

    def __init__(self):

        self.api_key = os.getenv("GROQ_API_KEY")

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b"
        )

        self.client = None

        if self.api_key:

            self.client = Groq(
                api_key=self.api_key,
                timeout=30.0,
                max_retries=1
            )

    # --------------------------------------------------
    # FALLBACK DECISION ENGINE
    # --------------------------------------------------

    def fallback_decision(self, mission_state, finding):

        energy = mission_state.get("agent_energy", {})
        health = mission_state.get("agent_health", {})

        finding_text = finding.lower()

        if "rock" in finding_text or "obstacle" in finding_text:

            if (
                health.get("Hulk", 0) > 0
                and energy.get("Hulk", 0) >= 30
            ):

                return {
                    "action": "Remove Obstacles",
                    "recommended_agent": "Hulk",
                    "reason": (
                        "Hulk has sufficient health and energy "
                        "to remove obstacles."
                    ),
                    "confidence": 0.70,
                    "source": "Fallback Rule Engine"
                }

            if (
                health.get("Iron Man", 0) > 0
                and energy.get("Iron Man", 0) >= 45
            ):

                return {
                    "action": "Repulsor Rock Removal",
                    "recommended_agent": "Iron Man",
                    "reason": (
                        "Iron Man can assist with obstacle removal."
                    ),
                    "confidence": 0.70,
                    "source": "Fallback Rule Engine"
                }

        return {
            "action": "Review Mission",
            "recommended_agent": "Mission Commander",
            "reason": (
                "The mission requires further evaluation."
            ),
            "confidence": 0.50,
            "source": "Fallback Rule Engine"
        }

    # --------------------------------------------------
    # AI MISSION ANALYSIS
    # --------------------------------------------------

    def analyze_mission(
        self,
        mission_state,
        agent_name,
        finding
    ):

        # Check Groq availability

        if not self.client:

            result = self.fallback_decision(
                mission_state,
                finding
            )

            result["source"] = (
                "Fallback - API key unavailable"
            )

            return result

        # Prepare mission context

        context = {

            "current_agent": agent_name,

            "finding": finding,

            "mission_status": mission_state.get("status"),

            "mission_stage": mission_state.get("stage"),

            "agent_status": mission_state.get(
                "agent_status",
                {}
            ),

            "agent_health": mission_state.get(
                "agent_health",
                {}
            ),

            "agent_energy": mission_state.get(
                "agent_energy",
                {}
            )
        }

        # System instructions

        system_prompt = """
You are the AI Mission Commander of Mission Moon,
a multi-agent lunar exploration simulation.

AVAILABLE AGENTS:

1. Spider-Man:
   Navigation, scouting and obstacle detection.
   Scouting energy cost: 15.

2. Hulk:
   Physical obstacle removal.
   Energy cost: 30 per rock.
   Health decreases by 10 per rock.

3. Sandman:
   Terrain analysis and levelling.
   Energy cost: 20.

4. Iron Man:
   Landing platform construction.
   Construction energy cost: 25.
   Repulsor rock removal energy cost: 20 per rock.
   Can transfer energy to other agents.

YOUR RESPONSIBILITIES:

1. Analyze the current mission state.
2. Understand the finding reported by the current agent.
3. Evaluate agent health and energy.
4. Recommend the most suitable next agent.
5. Consider recovery and delegation when necessary.
6. Explain why the recommended agent is suitable.

IMPORTANT RULES:

- Never recommend an agent with zero health.
- Check energy before recommending an agent.
- Consider agent capabilities.
- Do not claim that an action has already been executed.
- Python validates and executes all recommendations.
- Return only the requested JSON structure.

Do not include Markdown or additional text.
"""

        # --------------------------------------------------
        # CALL GROQ AI
        # --------------------------------------------------

        try:

            response = self.client.chat.completions.create(

                model=self.model,

                messages=[

                    {
                        "role": "system",
                        "content": system_prompt
                    },

                    {
                        "role": "user",
                        "content": (
                            "Analyze this mission state and recommend "
                            "the next action. Return JSON only:\n"
                            + json.dumps(context)
                        )
                    }

                ],

                response_format={

                    "type": "json_schema",

                    "json_schema": {

                        "name": "mission_decision",

                        "strict": True,

                        "schema": {

                            "type": "object",

                            "properties": {

                                "action": {
                                    "type": "string"
                                },

                                "recommended_agent": {
                                    "type": "string",
                                    "enum": [
                                        "Spider-Man",
                                        "Hulk",
                                        "Sandman",
                                        "Iron Man",
                                        "Mission Commander"
                                    ]
                                },

                                "reason": {
                                    "type": "string"
                                },

                                "confidence": {
                                    "type": "number"
                                }

                            },

                            "required": [
                                "action",
                                "recommended_agent",
                                "reason",
                                "confidence"
                            ],

                            "additionalProperties": False

                        }

                    }

                },

                reasoning_effort="low",

                max_completion_tokens=1200

            )

            # Extract AI response

            content = response.choices[0].message.content

            decision = json.loads(content)

            # Validate recommendation

            valid_agents = {

                "Spider-Man",
                "Hulk",
                "Sandman",
                "Iron Man",
                "Mission Commander"

            }

            recommended_agent = decision.get(
                "recommended_agent",
                "Mission Commander"
            )

            if recommended_agent not in valid_agents:

                raise ValueError(
                    "Invalid agent recommendation"
                )

            # Validate confidence

            confidence = float(
                decision.get("confidence", 0.5)
            )

            confidence = max(
                0.0,
                min(1.0, confidence)
            )

            # Return AI decision

            return {

                "action": str(
                    decision.get(
                        "action",
                        "Review Mission"
                    )
                ),

                "recommended_agent": recommended_agent,

                "reason": str(
                    decision.get(
                        "reason",
                        "No explanation provided."
                    )
                ),

                "confidence": confidence,

                "source": "Groq AI"

            }

        # --------------------------------------------------
        # ERROR HANDLING
        # --------------------------------------------------

        except Exception as error:

            print(
                "Mission Advisor Error:",
                str(error)
            )

            result = self.fallback_decision(
                mission_state,
                finding
            )

            result["source"] = (
                "Fallback - AI request failed"
            )

            return result


# --------------------------------------------------
# CREATE GLOBAL MISSION ADVISOR
# --------------------------------------------------

mission_advisor = MissionAdvisor()
