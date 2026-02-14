"""
Learning Orchestrator - Central coordinator for multi-agent system
Manages agent interactions and learning loop
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from agents.perception_agent import PerceptionAgent
from agents.memory_agent import MemoryAgent
from agents.planning_agent import PlanningAgent
from agents.evaluation_agent import EvaluationAgent
from config import Config


class LearningOrchestrator:
    """
    Central orchestrator that coordinates all agents in the learning system

    Flow:
    1. Perception Agent processes input
    2. Memory Agent retrieves relevant context
    3. Planning Agent decides action
    4. Action executed
    5. Evaluation Agent assesses and updates
    """

    def __init__(self):
        """Initialize all agents"""
        print("🚀 Initializing Learning Orchestrator...")

        # Initialize agents
        self.perception_agent = PerceptionAgent()
        self.memory_agent = MemoryAgent()
        self.planning_agent = PlanningAgent()
        self.evaluation_agent = EvaluationAgent()

        # Load knowledge base
        self.knowledge_base = self._load_knowledge_base()

        print("✅ All agents initialized successfully")

    def _load_knowledge_base(self) -> Dict:
        """Load knowledge base from file"""
        try:
            with open(Config.KNOWLEDGE_BASE_PATH, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Knowledge base not found, using empty knowledge base")
            return {"topics": {}}

    def process_interaction(
        self, student_id: str, interaction_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main processing pipeline for student interactions

        Args:
            student_id: Unique student identifier
            interaction_type: Type of interaction (request_exercise, submit_answer, etc.)
            context: Additional context data

        Returns:
            Dict with response and any additional data
        """

        if Config.DEBUG_MODE:
            print(f"\n{'='*60}")
            print(f"🎯 Processing Interaction: {interaction_type}")
            print(f"👤 Student: {student_id}")
            print(f"{'='*60}\n")

        # STEP 1: Perception - Process input and extract features
        perception_output = self.perception_agent.process(
            interaction_type=interaction_type, context=context
        )

        if Config.LOG_AGENT_DECISIONS:
            print(f"👁️ Perception Output: {perception_output}")

        # STEP 2: Memory - Retrieve student profile and history
        student_profile = self.memory_agent.get_student_profile(student_id)
        relevant_history = self.memory_agent.get_relevant_history(
            student_id=student_id,
            topic=perception_output.get("topic", "ielts_vocabulary"),
            n=5,
        )

        if Config.LOG_AGENT_DECISIONS:
            print(
                f"🧠 Memory: Retrieved profile and {len(relevant_history)} relevant interactions"
            )

        # STEP 3: Planning - Decide what action to take
        planning_decision = self.planning_agent.decide_action(
            student_profile=student_profile,
            perception_output=perception_output,
            history=relevant_history,
            knowledge_base=self.knowledge_base,
        )

        if Config.LOG_AGENT_DECISIONS:
            print(
                f"🎲 Planning Decision: {planning_decision['action']} - {planning_decision.get('reasoning', '')}"
            )

        # STEP 4: Execute the planned action
        action_result = self._execute_action(
            action=planning_decision["action"],
            parameters=planning_decision,
            student_profile=student_profile,
            context=context,
        )

        # STEP 5: Evaluation - Assess performance and update profile
        if interaction_type == "submit_answer":
            evaluation_result = self.evaluation_agent.evaluate_answer(
                exercise=context["exercise"],
                student_answer=context["student_answer"],
                student_profile=student_profile,
            )

            if Config.LOG_AGENT_DECISIONS:
                print(
                    f"📊 Evaluation: Score={evaluation_result['score']:.2f}, Correct={evaluation_result['is_correct']}"
                )

            # Update student profile based on performance
            self._update_student_profile(
                student_id=student_id,
                topic=context["exercise"]["topic"],
                performance=evaluation_result["score"],
                action=planning_decision["action"],
                exercise_id=context["exercise"]["id"],
            )

            # Merge evaluation into result
            action_result["evaluation"] = evaluation_result

        # Record interaction in memory
        self.memory_agent.record_interaction(
            student_id=student_id,
            interaction_data={
                "type": interaction_type,
                "action": planning_decision["action"],
                "timestamp": datetime.now().isoformat(),
                "context": perception_output,
            },
        )

        return action_result

    def _execute_action(
        self, action: str, parameters: Dict, student_profile: Dict, context: Dict
    ) -> Dict[str, Any]:
        """
        Execute the planned action

        Args:
            action: Action to execute
            parameters: Action parameters from planning agent
            student_profile: Current student profile
            context: Interaction context

        Returns:
            Dict with action results and response
        """

        if action == "provide_exercise":
            return self._provide_exercise(parameters, student_profile)

        elif action == "teach_concept":
            return self._teach_concept(parameters, student_profile)

        elif action == "provide_feedback":
            return self._provide_feedback(student_profile)

        elif action == "evaluate_answer":
            return self._evaluate_and_respond(context, student_profile)

        elif action == "encourage":
            return self._provide_encouragement(student_profile)

        else:
            return {
                "response": "I'm here to help you learn! What would you like to practice today?",
                "action": action,
            }

    def _provide_exercise(self, parameters: Dict, student_profile: Dict) -> Dict:
        """Provide a personalized exercise"""
        topic = parameters.get("topic", "ielts_vocabulary")
        difficulty = parameters.get("difficulty", "beginner")

        # Get exercise from knowledge base
        exercise = self._select_exercise(topic, difficulty, student_profile)

        if not exercise:
            return {
                "response": "I couldn't find an appropriate exercise right now. Let me explain a concept instead.",
                "action": "provide_exercise",
                "exercise": None,
            }

        # Generate personalized intro based on learning style
        learning_style = student_profile.get("learning_style", "visual")
        intro_template = Config.RESPONSE_TEMPLATES["exercise_intro"].get(
            learning_style, Config.RESPONSE_TEMPLATES["exercise_intro"]["visual"]
        )

        intro = intro_template.format(topic=topic.replace("_", " ").title())

        response = f"{intro}\n\n**Exercise ({difficulty.title()} Level)**\n\n{exercise['question']}"

        return {
            "response": response,
            "action": "provide_exercise",
            "exercise": exercise,
        }

    def _select_exercise(
        self, topic: str, difficulty: str, student_profile: Dict
    ) -> Dict:
        """Select an appropriate exercise from knowledge base"""

        # Navigate knowledge base
        if topic not in self.knowledge_base.get("topics", {}):
            topic = "ielts_vocabulary"  # Default fallback

        topic_data = self.knowledge_base["topics"][topic]

        # Get exercises for difficulty level
        if difficulty not in topic_data.get("difficulty_levels", {}):
            difficulty = "beginner"  # Fallback

        difficulty_data = topic_data["difficulty_levels"][difficulty]
        exercises = difficulty_data.get("exercises", [])

        if not exercises:
            return None

        # Select exercise (could use more sophisticated selection)
        # For now, rotate through exercises
        history = student_profile.get("interaction_history", [])
        completed_exercises = [
            h.get("exercise_id") for h in history if h.get("exercise_id")
        ]

        # Find an exercise not recently completed
        for exercise in exercises:
            if exercise["id"] not in completed_exercises[-5:]:  # Avoid last 5
                return {**exercise, "topic": topic, "difficulty": difficulty}

        # If all recently completed, return first one
        return {**exercises[0], "topic": topic, "difficulty": difficulty}

    def _teach_concept(self, parameters: Dict, student_profile: Dict) -> Dict:
        """Provide concept explanation"""

        # Find struggling topics
        struggling_topics = student_profile["performance_metrics"].get(
            "topics_struggling", []
        )

        if struggling_topics:
            topic = struggling_topics[0]  # Focus on first struggling topic
        else:
            topic = parameters.get("topic", "basic_collocations")

        # Get concept explanation from knowledge base
        explanation = self._get_concept_explanation(topic)

        response = f"""Let me help you understand **{topic.replace('_', ' ').title()}**:

{explanation}

Would you like to practice with an exercise on this concept?"""

        return {"response": response, "action": "teach_concept", "topic": topic}

    def _get_concept_explanation(self, concept: str) -> str:
        """Get explanation for a concept from knowledge base"""

        # Search through knowledge base for examples
        for topic_name, topic_data in self.knowledge_base.get("topics", {}).items():
            for difficulty, diff_data in topic_data.get(
                "difficulty_levels", {}
            ).items():
                for example in diff_data.get("examples", []):
                    if example.get("concept") == concept:
                        return f"**Example:** {example['code']}\n\n**Explanation:** {example['explanation']}"

        return f"This concept involves {concept.replace('_', ' ')}. Practice regularly to improve!"

    def _provide_feedback(self, student_profile: Dict) -> Dict:
        """Generate personalized feedback"""

        feedback = self.evaluation_agent.generate_feedback(student_profile)

        response = f"""**Your Learning Progress**

{feedback}

Keep up the great work! Let me know if you'd like to practice any specific area."""

        return {
            "response": response,
            "action": "provide_feedback",
            "feedback": feedback,
        }

    def _evaluate_and_respond(self, context: Dict, student_profile: Dict) -> Dict:
        """Evaluate answer and provide response"""

        exercise = context["exercise"]
        student_answer = context["student_answer"]

        # Evaluate the answer
        evaluation = self.evaluation_agent.evaluate_answer(
            exercise=exercise,
            student_answer=student_answer,
            student_profile=student_profile,
        )

        # Generate response based on correctness
        if evaluation["is_correct"]:
            response_template = Config.RESPONSE_TEMPLATES["correct_answer"][0]
            response = response_template.format(
                concept=exercise.get("topic", "this concept")
            )
            response += f"\n\n{evaluation['feedback']}"
        else:
            response_template = Config.RESPONSE_TEMPLATES["incorrect_answer"][0]
            response = response_template.format(
                concept=exercise.get("topic", "this concept"),
                hint=evaluation.get("hint", "reviewing the concept"),
            )
            response += f"\n\n**Correct Answer:** {exercise['solution']}"
            response += f"\n\n{evaluation['feedback']}"

        return {
            "response": response,
            "action": "evaluate_answer",
            "evaluation": evaluation,
        }

    def _provide_encouragement(self, student_profile: Dict) -> Dict:
        """Provide motivational message"""

        encouragement = Config.RESPONSE_TEMPLATES["encouragement"][0]

        return {"response": encouragement, "action": "encourage"}

    def _update_student_profile(
        self,
        student_id: str,
        topic: str,
        performance: float,
        action: str,
        exercise_id: str = None,
    ):
        """Update student profile based on performance"""

        self.memory_agent.update_skill_level(
            student_id=student_id, topic=topic, performance=performance
        )

        interaction = {
            "topic": topic,
            "performance": performance,
            "action": action,
            "timestamp": datetime.now().isoformat(),
        }

        if exercise_id is not None:
            interaction["exercise_id"] = exercise_id

        # self.memory_agent.record_interaction(
        #     student_id=student_id,
        #     interaction_data={
        #         "topic": topic,
        #         "performance": performance,
        #         "action": action,
        #         "timestamp": datetime.now().isoformat(),
        #     },
        # )
        self.memory_agent.record_interaction(
            student_id=student_id, interaction_data=interaction
        )
