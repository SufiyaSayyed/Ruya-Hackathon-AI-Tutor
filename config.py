"""
Configuration file for the IELTS Learning Tutor System
Contains all settings, paths, and prompts for the multi-agent system
"""

import os

class Config:
    """Central configuration for the learning tutor system"""
    
    # File paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    KNOWLEDGE_BASE_PATH = os.path.join(DATA_DIR, 'knowledge_base.json')
    STUDENT_PROFILES_PATH = os.path.join(DATA_DIR, 'student_profiles.json')
    
    # Model settings (using open-source models)
    # For hackathon: Use Ollama with local models or API-based open models
    LLM_MODEL = "llama3.2"  # Can use Ollama, or replace with HuggingFace API
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Agent thresholds
    MASTERY_THRESHOLD = 0.75  # 75% accuracy = mastered
    STRUGGLING_THRESHOLD = 0.50  # Below 50% = struggling
    
    # Learning parameters
    DIFFICULTY_ADJUSTMENT_RATE = 0.1
    MEMORY_DECAY_FACTOR = 0.95
    EXPLORATION_RATE = 0.2  # 20% chance to try different approach
    
    # System prompts for different agents
    PERCEPTION_PROMPTS = {
        'analyze_input': """Analyze the student's response and extract:
1. Intent (request_exercise, submit_answer, ask_question, etc.)
2. Topic preference (if mentioned)
3. Difficulty preference (if mentioned)
4. Emotional state indicators (confident, frustrated, confused)

Student input: {input_text}
Current context: {context}

Return JSON format:
{{
    "intent": "...",
    "topic": "...",
    "difficulty": "...",
    "emotional_state": "...",
    "key_phrases": [...]
}}
""",
        
        'evaluate_answer': """Evaluate this student answer for correctness and understanding:

Exercise: {exercise}
Expected solution: {solution}
Student answer: {answer}

Assess:
1. Correctness (0.0-1.0)
2. Partial credit if applicable
3. Common mistakes identified
4. Understanding level

Return JSON:
{{
    "score": 0.0-1.0,
    "is_correct": true/false,
    "feedback": "...",
    "mistakes": [...],
    "understanding_level": "weak/partial/good/excellent"
}}
"""
    }
    
    PLANNING_PROMPTS = {
        'select_action': """Based on student profile, select the best learning action:

Student Profile:
- Current skill level: {skill_level}
- Recent performance: {recent_performance}
- Learning style: {learning_style}
- Struggling topics: {struggling_topics}

Available actions:
1. provide_exercise: Give practice exercise
2. teach_concept: Explain a concept
3. provide_feedback: Give performance summary
4. encourage: Provide motivation

Context: {context}

Select action and parameters. Consider:
- Zone of proximal development (not too hard, not too easy)
- Spaced repetition for struggling topics
- Learning style preferences
- Recent performance patterns

Return JSON:
{{
    "action": "...",
    "topic": "...",
    "difficulty": "...",
    "reasoning": "..."
}}
"""
    }
    
    EVALUATION_PROMPTS = {
        'generate_feedback': """Generate personalized feedback for the student:

Student: {student_name}
Recent performance: {performance_data}
Skill levels: {skill_levels}
Learning goals: {goals}

Create encouraging, specific, actionable feedback that:
1. Acknowledges progress
2. Identifies specific strengths
3. Highlights areas for improvement
4. Provides concrete next steps
5. Matches student's learning style: {learning_style}

Keep tone: {tone} (encouraging/analytical/supportive)
"""
    }
    
    # Response templates
    RESPONSE_TEMPLATES = {
        'exercise_intro': {
            'visual': "Here's a visual exercise to help you practice {topic}. Focus on the examples and patterns.",
            'analytical': "Let's analyze {topic} systematically. This exercise will test your understanding.",
            'kinesthetic': "Time to practice {topic} hands-on! Work through this exercise step by step.",
            'auditory': "Listen carefully to this {topic} exercise. Read it aloud if it helps."
        },
        
        'correct_answer': [
            "Excellent work! 🎉 Your answer is correct. You clearly understand {concept}.",
            "Perfect! ✅ You've got it. This shows strong mastery of {concept}.",
            "Great job! 👏 That's exactly right. Keep up this excellent work."
        ],
        
        'incorrect_answer': [
            "Not quite right, but I can see your thinking. Let's work on {concept} together.",
            "Good effort! The correct approach involves {hint}. Let's practice more.",
            "Close! You're on the right track. Focus on {specific_issue} and try again."
        ],
        
        'encouragement': [
            "You're making great progress! Keep practicing and you'll master this.",
            "Don't get discouraged - learning takes time. You're improving with each attempt!",
            "I can see your effort paying off. Stay consistent and you'll reach your goals."
        ]
    }
    
    # Skill level descriptions
    SKILL_DESCRIPTIONS = {
        0.0-0.3: "beginner",
        0.3-0.6: "intermediate", 
        0.6-0.8: "advanced",
        0.8-1.0: "expert"
    }
    
    @staticmethod
    def get_skill_level_category(score):
        """Convert numeric skill score to category"""
        if score < 0.3:
            return "beginner"
        elif score < 0.6:
            return "intermediate"
        elif score < 0.8:
            return "advanced"
        else:
            return "expert"
    
    @staticmethod
    def get_difficulty_for_skill(skill_level):
        """Determine appropriate difficulty based on skill level"""
        category = Config.get_skill_level_category(skill_level)
        
        # Zone of proximal development: slightly above current level
        if category == "beginner":
            return "beginner"
        elif category == "intermediate":
            return "intermediate"
        else:
            return "intermediate"  # Keep most at intermediate for IELTS
    
    # Logging
    DEBUG_MODE = True
    LOG_AGENT_DECISIONS = True
