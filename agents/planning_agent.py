"""
Planning Agent (Decision Engine) - Decides what action to take

Role:
- Analyze student state and context
- Select optimal learning action
- Implement adaptive difficulty
- Apply pedagogical strategies
- Balance exploration vs exploitation
"""

import random
from typing import Dict, List, Any
from config import Config

class PlanningAgent:
    """
    Agent responsible for planning and decision-making
    
    Key responsibilities:
    1. Decide what action to take (teach, exercise, feedback, etc.)
    2. Select appropriate difficulty level
    3. Choose relevant topics based on student needs
    4. Apply learning strategies (spaced repetition, scaffolding)
    5. Balance between mastery and exploration
    """
    
    def __init__(self):
        """Initialize planning agent"""
        print("🎲 Planning Agent initialized")
        
        # Action priorities based on pedagogical principles
        self.action_priorities = {
            'struggling': ['teach_concept', 'provide_exercise', 'encourage'],
            'improving': ['provide_exercise', 'teach_concept', 'provide_feedback'],
            'mastered': ['provide_exercise', 'provide_feedback', 'teach_concept']
        }
    
    def decide_action(
        self,
        student_profile: Dict,
        perception_output: Dict,
        history: List[Dict],
        knowledge_base: Dict
    ) -> Dict[str, Any]:
        """
        Decide the best action to take
        
        This is the core decision-making logic that determines what
        the tutor should do next based on student state.
        
        Args:
            student_profile: Current student profile
            perception_output: Output from perception agent
            history: Recent interaction history
            knowledge_base: Available learning materials
            
        Returns:
            Dict with action and parameters
        """
        
        # Extract key information
        intent = perception_output.get('intent', 'general')
        confidence = perception_output.get('confidence_level', 'medium')
        
        # Handle explicit requests first
        if intent == 'request_exercise':
            return self._plan_exercise(student_profile, perception_output, knowledge_base)
        
        elif intent == 'explain_concept' or intent == 'express_confusion':
            return self._plan_explanation(student_profile, perception_output)
        
        elif intent == 'request_feedback':
            return self._plan_feedback(student_profile)
        
        elif intent == 'submit_answer':
            return self._plan_evaluation(perception_output)
        
        # For general intent, use adaptive strategy
        else:
            return self._plan_adaptive_action(student_profile, history, knowledge_base)
    
    def _plan_exercise(
        self,
        student_profile: Dict,
        perception_output: Dict,
        knowledge_base: Dict
    ) -> Dict:
        """Plan exercise provision"""
        
        # Determine topic
        topic = self._select_topic(student_profile, perception_output)
        
        # Determine difficulty using Zone of Proximal Development
        difficulty = self._select_difficulty(student_profile, topic)
        
        return {
            'action': 'provide_exercise',
            'topic': topic,
            'difficulty': difficulty,
            'reasoning': f"Selected {difficulty} {topic} exercise based on skill level"
        }
    
    def _plan_explanation(
        self,
        student_profile: Dict,
        perception_output: Dict
    ) -> Dict:
        """Plan concept explanation"""
        
        # Focus on struggling topics
        struggling_topics = student_profile['performance_metrics'].get('topics_struggling', [])
        
        if struggling_topics:
            topic = struggling_topics[0]  # Prioritize first struggling topic
            reasoning = f"Explaining {topic} - identified as struggling area"
        else:
            topic = perception_output.get('topic', 'basic_collocations')
            reasoning = f"Explaining requested concept: {topic}"
        
        return {
            'action': 'teach_concept',
            'topic': topic,
            'difficulty': 'beginner',  # Start with basics for explanations
            'reasoning': reasoning
        }
    
    def _plan_feedback(self, student_profile: Dict) -> Dict:
        """Plan feedback provision"""
        
        return {
            'action': 'provide_feedback',
            'topic': 'general',
            'reasoning': 'Providing comprehensive performance feedback'
        }
    
    def _plan_evaluation(self, perception_output: Dict) -> Dict:
        """Plan answer evaluation"""
        
        return {
            'action': 'evaluate_answer',
            'topic': perception_output.get('topic', 'ielts_vocabulary'),
            'reasoning': 'Evaluating submitted answer'
        }
    
    def _plan_adaptive_action(
        self,
        student_profile: Dict,
        history: List[Dict],
        knowledge_base: Dict
    ) -> Dict:
        """
        Plan action adaptively based on student state
        
        This implements intelligent action selection using:
        1. Student performance level
        2. Recent history pattern
        3. Pedagogical best practices
        4. Exploration/exploitation balance
        """
        
        # Analyze student state
        state = self._analyze_student_state(student_profile, history)
        
        # Get appropriate action list
        action_list = self.action_priorities.get(state, self.action_priorities['improving'])
        
        # Exploration: occasionally try different actions
        if random.random() < Config.EXPLORATION_RATE:
            action = random.choice(['teach_concept', 'provide_exercise', 'encourage'])
            reasoning = f"Exploring different approach (state: {state})"
        else:
            # Exploitation: use best known action
            action = action_list[0]
            reasoning = f"Following strategy for {state} student"
        
        # Select topic
        topic = self._select_topic(student_profile, {})
        
        # Select difficulty
        difficulty = self._select_difficulty(student_profile, topic)
        
        return {
            'action': action,
            'topic': topic,
            'difficulty': difficulty,
            'reasoning': reasoning
        }
    
    def _analyze_student_state(
        self,
        student_profile: Dict,
        history: List[Dict]
    ) -> str:
        """
        Analyze student's current learning state
        
        Returns:
            'struggling', 'improving', or 'mastered'
        """
        
        avg_accuracy = student_profile['performance_metrics'].get('avg_accuracy', 0.5)
        struggling_topics = student_profile['performance_metrics'].get('topics_struggling', [])
        
        # Check recent trend
        if history:
            recent_performances = [
                h.get('performance', 0.5) for h in history[-3:]
                if 'performance' in h
            ]
            
            if recent_performances:
                recent_avg = sum(recent_performances) / len(recent_performances)
                
                # Improving if recent > overall
                if recent_avg > avg_accuracy + 0.1:
                    return 'improving'
        
        # Struggling if below threshold or has struggling topics
        if avg_accuracy < Config.STRUGGLING_THRESHOLD or len(struggling_topics) > 2:
            return 'struggling'
        
        # Mastered if high performance
        if avg_accuracy >= Config.MASTERY_THRESHOLD:
            return 'mastered'
        
        return 'improving'  # Default
    
    def _select_topic(
        self,
        student_profile: Dict,
        perception_output: Dict
    ) -> str:
        """
        Select appropriate topic for learning
        
        Priority:
        1. Explicit request from perception
        2. Struggling topics (spaced repetition)
        3. General skill improvement
        """
        
        # Check for explicit topic request
        if perception_output.get('topic'):
            return perception_output['topic']
        
        # Focus on struggling topics (spaced repetition principle)
        struggling = student_profile['performance_metrics'].get('topics_struggling', [])
        if struggling:
            return struggling[0]  # Pick first struggling topic
        
        # Otherwise, focus on lowest skill
        skill_levels = student_profile.get('skill_levels', {})
        if skill_levels:
            lowest_skill_topic = min(skill_levels.items(), key=lambda x: x[1])[0]
            return lowest_skill_topic
        
        return 'ielts_vocabulary'  # Default fallback
    
    def _select_difficulty(
        self,
        student_profile: Dict,
        topic: str
    ) -> str:
        """
        Select difficulty level using Zone of Proximal Development
        
        ZPD: Learning is most effective when content is slightly
        above current ability level (challenging but achievable)
        
        Args:
            student_profile: Student profile
            topic: Topic being taught
            
        Returns:
            Difficulty level string
        """
        
        # Get skill level for topic
        skill_levels = student_profile.get('skill_levels', {})
        skill_level = skill_levels.get(topic, 0.3)  # Default to beginner
        
        # Map skill to difficulty
        difficulty = Config.get_difficulty_for_skill(skill_level)
        
        # Adaptive adjustment: slightly increase difficulty if high confidence
        # This implements "desirable difficulty" principle
        recent_performance = student_profile['performance_metrics'].get('avg_accuracy', 0.5)
        
        if recent_performance > 0.8 and difficulty == 'beginner':
            difficulty = 'intermediate'
        
        return difficulty
    
    def apply_spaced_repetition(
        self,
        history: List[Dict],
        all_topics: List[str]
    ) -> str:
        """
        Apply spaced repetition algorithm
        
        Topics not practiced recently should be prioritized
        
        Args:
            history: Recent interaction history
            all_topics: All available topics
            
        Returns:
            Topic that should be practiced
        """
        
        # Get topics from recent history
        recent_topics = [h.get('topic') for h in history[-5:] if h.get('topic')]
        
        # Find topics not recently practiced
        for topic in all_topics:
            if topic not in recent_topics:
                return topic
        
        # If all recent, return least recent
        return all_topics[0] if all_topics else 'ielts_vocabulary'
    
    def should_provide_encouragement(
        self,
        student_profile: Dict,
        history: List[Dict]
    ) -> bool:
        """
        Decide if encouragement is needed
        
        Encouragement helps with:
        - Low confidence students
        - After series of failures
        - Long sessions without positive feedback
        """
        
        # Check recent failures
        if len(history) >= 3:
            recent_scores = [
                h.get('performance', 0.5) for h in history[-3:]
                if 'performance' in h
            ]
            
            if recent_scores and all(score < 0.5 for score in recent_scores):
                return True  # Multiple failures - encourage!
        
        # Check overall low performance
        if student_profile['performance_metrics'].get('avg_accuracy', 0.5) < 0.4:
            return True
        
        return False
