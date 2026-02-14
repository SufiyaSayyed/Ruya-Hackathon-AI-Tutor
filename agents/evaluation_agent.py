"""
Evaluation Agent (Reward System) - Assesses action quality and provides learning signals

Role:
- Evaluate student answers
- Calculate performance scores
- Generate constructive feedback
- Provide learning signals for system improvement
- Track progress metrics
"""

from typing import Dict, Any, List
import re
from config import Config

class EvaluationAgent:
    """
    Agent responsible for evaluation and feedback
    
    Key responsibilities:
    1. Evaluate answer correctness
    2. Generate constructive feedback
    3. Calculate performance scores
    4. Identify common mistakes
    5. Provide personalized guidance
    """
    
    def __init__(self):
        """Initialize evaluation agent"""
        print("📊 Evaluation Agent initialized")
        
        # Feedback templates based on performance
        self.feedback_templates = {
            'excellent': [
                "Outstanding! You've mastered {concept}. {encouragement}",
                "Perfect understanding! {concept} is clearly one of your strengths. {next_step}"
            ],
            'good': [
                "Great work! You've got a solid grasp of {concept}. {encouragement}",
                "Well done! Your understanding of {concept} is developing nicely. {next_step}"
            ],
            'partial': [
                "Good effort! You understand parts of {concept}, but let's refine your approach. {hint}",
                "You're on the right track with {concept}. {specific_feedback} {next_step}"
            ],
            'poor': [
                "I can see you're trying, but {concept} needs more practice. {hint}",
                "Let's work on {concept} together. {specific_feedback} {encouragement}"
            ]
        }
    
    def evaluate_answer(
        self,
        exercise: Dict,
        student_answer: str,
        student_profile: Dict
    ) -> Dict[str, Any]:
        """
        Evaluate student's answer
        
        Args:
            exercise: The exercise question and solution
            student_answer: Student's submitted answer
            student_profile: Student's profile for personalization
            
        Returns:
            Dict with evaluation results
        """
        
        expected_solution = exercise.get('solution', '')
        exercise_id = exercise.get('id', 'unknown')
        
        # Calculate correctness score
        score, is_correct = self._calculate_score(student_answer, expected_solution)
        
        # Determine understanding level
        understanding_level = self._assess_understanding(score)
        
        # Generate feedback
        feedback = self._generate_answer_feedback(
            score=score,
            is_correct=is_correct,
            exercise=exercise,
            student_answer=student_answer,
            student_profile=student_profile
        )
        
        # Identify mistakes if incorrect
        mistakes = self._identify_mistakes(
            student_answer, 
            expected_solution
        ) if not is_correct else []
        
        return {
            'score': score,
            'is_correct': is_correct,
            'understanding_level': understanding_level,
            'feedback': feedback,
            'mistakes': mistakes,
            'exercise_id': exercise_id,
            'hint': self._generate_hint(exercise, score)
        }
    
    def _calculate_score(
        self,
        student_answer: str,
        expected_solution: str
    ) -> tuple[float, bool]:
        """
        Calculate correctness score
        
        Returns:
            (score, is_correct) tuple
        """
        
        # Normalize answers
        student_lower = student_answer.lower().strip()
        expected_lower = expected_solution.lower().strip()
        
        # Exact match
        if student_lower == expected_lower:
            return (1.0, True)
        
        # Check for common variations
        # Remove punctuation for comparison
        student_clean = re.sub(r'[^\w\s]', '', student_lower)
        expected_clean = re.sub(r'[^\w\s]', '', expected_lower)
        
        if student_clean == expected_clean:
            return (0.95, True)  # Correct but minor formatting difference
        
        # Word-level comparison for partial credit
        student_words = set(student_clean.split())
        expected_words = set(expected_clean.split())
        
        if not expected_words:
            return (0.0, False)
        
        # Calculate word overlap
        overlap = len(student_words & expected_words)
        total = len(expected_words)
        overlap_ratio = overlap / total
        
        # Partial credit scoring
        if overlap_ratio >= 0.8:
            return (0.7, False)  # Mostly correct
        elif overlap_ratio >= 0.5:
            return (0.5, False)  # Partially correct
        elif overlap_ratio >= 0.3:
            return (0.3, False)  # Some understanding
        else:
            return (0.1, False)  # Incorrect
    
    def _assess_understanding(self, score: float) -> str:
        """Assess understanding level from score"""
        
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.7:
            return 'good'
        elif score >= 0.4:
            return 'partial'
        else:
            return 'weak'
    
    def _generate_answer_feedback(
        self,
        score: float,
        is_correct: bool,
        exercise: Dict,
        student_answer: str,
        student_profile: Dict
    ) -> str:
        """
        Generate personalized feedback for the answer
        
        Considers:
        - Correctness level
        - Learning style
        - Past performance
        - Specific mistakes
        """
        
        understanding = self._assess_understanding(score)
        concept = exercise.get('topic', 'this concept').replace('_', ' ').title()
        
        # Get base feedback template
        if understanding in self.feedback_templates:
            template = self.feedback_templates[understanding][0]
        else:
            template = "Let's review {concept}. {next_step}"
        
        # Generate components
        if is_correct:
            encouragement = "Keep up this excellent work!"
            next_step = "Ready for a more challenging exercise?"
            specific_feedback = ""
            hint = ""
        else:
            encouragement = "Don't worry - learning takes practice!"
            next_step = "Let's try another similar exercise to reinforce this."
            specific_feedback = self._generate_specific_feedback(
                student_answer, 
                exercise.get('solution', ''),
                exercise
            )
            hint = f"Hint: {exercise.get('hints', ['Review the examples'])[0]}"
        
        # Format feedback
        feedback = template.format(
            concept=concept,
            encouragement=encouragement,
            next_step=next_step,
            specific_feedback=specific_feedback,
            hint=hint
        )
        
        # Add personalization based on learning style
        learning_style = student_profile.get('learning_style', 'visual')
        if learning_style == 'visual' and not is_correct:
            feedback += "\n\nTry visualizing the concept or writing it down to help remember."
        elif learning_style == 'analytical' and not is_correct:
            feedback += "\n\nBreak down the concept into smaller parts and analyze each component."
        
        return feedback
    
    def _generate_specific_feedback(
        self,
        student_answer: str,
        expected: str,
        exercise: Dict
    ) -> str:
        """Generate specific feedback about the mistake"""
        
        student_words = set(student_answer.lower().split())
        expected_words = set(expected.lower().split())
        
        missing_words = expected_words - student_words
        extra_words = student_words - expected_words
        
        feedback_parts = []
        
        if missing_words:
            feedback_parts.append(
                f"You're missing key elements: {', '.join(list(missing_words)[:3])}"
            )
        
        if extra_words and len(extra_words) > len(expected_words) * 0.5:
            feedback_parts.append(
                "Your answer includes unnecessary elements. Focus on the core concept."
            )
        
        if not feedback_parts:
            feedback_parts.append("Review the correct answer and compare it with yours.")
        
        return " ".join(feedback_parts)
    
    def _identify_mistakes(
        self,
        student_answer: str,
        expected: str
    ) -> List[str]:
        """Identify specific mistakes"""
        
        mistakes = []
        
        student_lower = student_answer.lower()
        expected_lower = expected.lower()
        
        # Check length difference
        if len(student_answer) < len(expected) * 0.5:
            mistakes.append("Answer too brief - missing key information")
        elif len(student_answer) > len(expected) * 2:
            mistakes.append("Answer too verbose - focus on essentials")
        
        # Check for common issues
        if not student_answer.strip():
            mistakes.append("Empty answer provided")
        
        expected_words = set(expected_lower.split())
        student_words = set(student_lower.split())
        
        missing_important = expected_words - student_words
        if len(missing_important) > len(expected_words) * 0.5:
            mistakes.append("Missing critical vocabulary")
        
        return mistakes
    
    def _generate_hint(self, exercise: Dict, score: float) -> str:
        """Generate appropriate hint based on performance"""
        
        hints = exercise.get('hints', [])
        
        if not hints:
            return "Review the concept and try again."
        
        # Progressive hints based on score
        if score < 0.3:
            # Give first (easiest) hint
            return hints[0]
        elif score < 0.6 and len(hints) > 1:
            # Give more specific hint
            return hints[1] if len(hints) > 1 else hints[0]
        else:
            # Give most specific hint
            return hints[-1]
    
    def generate_feedback(self, student_profile: Dict) -> str:
        """
        Generate comprehensive performance feedback
        
        Args:
            student_profile: Student profile with performance data
            
        Returns:
            Formatted feedback string
        """
        
        metrics = student_profile['performance_metrics']
        skill_levels = student_profile['skill_levels']
        
        feedback_parts = []
        
        # Overall performance
        avg_accuracy = metrics.get('avg_accuracy', 0.0)
        feedback_parts.append(
            f"**Overall Performance:** {avg_accuracy*100:.0f}% accuracy"
        )
        
        # Skill levels
        feedback_parts.append("\n**Your Skill Levels:**")
        for skill, level in skill_levels.items():
            skill_name = skill.replace('_', ' ').title()
            category = Config.get_skill_level_category(level)
            feedback_parts.append(
                f"- {skill_name}: {level*100:.0f}% ({category.title()})"
            )
        
        # Strengths
        mastered = metrics.get('topics_mastered', [])
        if mastered:
            feedback_parts.append(f"\n**Strengths:** You've mastered {', '.join(mastered)}! 🎉")
        
        # Areas for improvement
        struggling = metrics.get('topics_struggling', [])
        if struggling:
            feedback_parts.append(
                f"\n**Focus Areas:** Keep practicing {', '.join(struggling)}."
            )
            feedback_parts.append(
                "💡 Tip: Regular practice on these topics will boost your scores!"
            )
        
        # Encouragement
        if avg_accuracy < 0.5:
            feedback_parts.append(
                "\n🌟 You're building your foundation. Stay consistent and you'll see improvement!"
            )
        elif avg_accuracy < 0.7:
            feedback_parts.append(
                "\n🚀 Great progress! You're developing strong skills. Keep pushing forward!"
            )
        else:
            feedback_parts.append(
                "\n⭐ Excellent work! You're performing at a high level. Keep challenging yourself!"
            )
        
        return "\n".join(feedback_parts)
    
    def calculate_reward(
        self,
        performance: float,
        difficulty: str,
        improvement: float
    ) -> float:
        """
        Calculate reward signal for reinforcement learning
        
        Higher rewards for:
        - Good performance
        - Appropriate difficulty
        - Improvement over time
        
        Args:
            performance: Score (0-1)
            difficulty: Difficulty level
            improvement: Change from previous
            
        Returns:
            Reward value
        """
        
        # Base reward from performance
        reward = performance
        
        # Bonus for appropriate difficulty (not too easy)
        if difficulty == 'intermediate' and performance > 0.7:
            reward += 0.2
        elif difficulty == 'advanced' and performance > 0.6:
            reward += 0.3
        
        # Bonus for improvement
        if improvement > 0.1:
            reward += 0.2
        
        # Penalty for repeated failures
        if performance < 0.3:
            reward -= 0.1
        
        return max(0.0, min(1.0, reward))  # Clip to [0, 1]
