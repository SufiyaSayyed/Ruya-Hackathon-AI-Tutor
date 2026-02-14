"""
Perception Agent - Processes raw observations and extracts relevant features

Role:
- Analyze student input (text, answers, requests)
- Extract intent and context
- Identify emotional state and confidence level
- Parse exercise submissions
- Extract key features for other agents
"""

from typing import Dict, Any
import re
from config import Config

class PerceptionAgent:
    """
    Agent responsible for processing and understanding student interactions
    
    Key responsibilities:
    1. Parse student input
    2. Extract intent (what does student want?)
    3. Identify context (what topic, difficulty?)
    4. Detect emotional state (confident, frustrated, confused?)
    5. Extract features for planning agent
    """
    
    def __init__(self):
        """Initialize perception agent"""
        print("👁️ Perception Agent initialized")
        
        # Intent patterns (simple rule-based for hackathon)
        self.intent_patterns = {
            'request_exercise': [
                r'exercise', r'practice', r'quiz', r'test', r'question'
            ],
            'ask_explanation': [
                r'explain', r'what is', r'how does', r'help me understand'
            ],
            'request_feedback': [
                r'feedback', r'how am i doing', r'progress', r'performance'
            ],
            'express_confusion': [
                r"don't understand", r"confused", r"unclear", r"lost"
            ],
            'express_confidence': [
                r"easy", r"understand", r"got it", r"makes sense"
            ]
        }
    
    def process(self, interaction_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process student interaction and extract features
        
        Args:
            interaction_type: Type of interaction
            context: Additional context data
            
        Returns:
            Dict with extracted features
        """
        
        # Extract features based on interaction type
        if interaction_type == "request_exercise":
            return self._process_exercise_request(context)
        
        elif interaction_type == "submit_answer":
            return self._process_answer_submission(context)
        
        elif interaction_type == "explain_concept":
            return self._process_explanation_request(context)
        
        elif interaction_type == "provide_feedback":
            return self._process_feedback_request(context)
        
        else:
            return self._process_general_input(context)
    
    def _process_exercise_request(self, context: Dict) -> Dict:
        """Process request for exercise"""
        
        # Extract preferences if mentioned
        text = context.get('text', '').lower()
        
        # Detect topic preference
        topic = self._extract_topic(text)
        
        # Detect difficulty preference
        difficulty = self._extract_difficulty(text)
        
        return {
            'intent': 'request_exercise',
            'topic': topic,
            'difficulty': difficulty,
            'confidence_level': self._detect_confidence(text),
            'timestamp': context.get('timestamp')
        }
    
    def _process_answer_submission(self, context: Dict) -> Dict:
        """Process student's answer submission"""
        
        exercise = context.get('exercise', {})
        answer = context.get('student_answer', '')
        
        # Analyze answer characteristics
        answer_length = len(answer.split())
        has_numbers = bool(re.search(r'\d', answer))
        has_special_chars = bool(re.search(r'[^\w\s]', answer))
        
        # Detect confidence from answer style
        confidence = 'medium'
        if '?' in answer or 'maybe' in answer.lower():
            confidence = 'low'
        elif '!' in answer or len(answer) > 50:
            confidence = 'high'
        
        return {
            'intent': 'submit_answer',
            'exercise_id': exercise.get('id'),
            'topic': exercise.get('topic'),
            'answer_length': answer_length,
            'answer_features': {
                'has_numbers': has_numbers,
                'has_special_chars': has_special_chars
            },
            'confidence_level': confidence
        }
    
    def _process_explanation_request(self, context: Dict) -> Dict:
        """Process request for concept explanation"""
        
        text = context.get('text', '').lower()
        
        # Try to identify specific concept
        concept = self._extract_topic(text)
        
        # Detect confusion level
        confusion_level = 'medium'
        if any(word in text for word in ['very confused', 'completely lost', 'no idea']):
            confusion_level = 'high'
        elif any(word in text for word in ['bit confused', 'slightly unclear']):
            confusion_level = 'low'
        
        return {
            'intent': 'explain_concept',
            'topic': concept,
            'confusion_level': confusion_level,
            'confidence_level': 'low'  # Asking for help implies lower confidence
        }
    
    def _process_feedback_request(self, context: Dict) -> Dict:
        """Process request for performance feedback"""
        
        return {
            'intent': 'request_feedback',
            'topic': 'general',
            'confidence_level': 'medium'
        }
    
    def _process_general_input(self, context: Dict) -> Dict:
        """Process general/unclassified input"""
        
        text = context.get('text', '').lower()
        
        # Detect intent from patterns
        intent = 'general'
        for intent_type, patterns in self.intent_patterns.items():
            if any(re.search(pattern, text) for pattern in patterns):
                intent = intent_type
                break
        
        return {
            'intent': intent,
            'topic': self._extract_topic(text),
            'confidence_level': self._detect_confidence(text)
        }
    
    def _extract_topic(self, text: str) -> str:
        """Extract topic from text"""
        
        topic_keywords = {
            'vocabulary': ['vocabulary', 'vocab', 'word', 'collocation'],
            'reading': ['reading', 'comprehension', 'passage'],
            'writing': ['writing', 'essay', 'composition'],
            'speaking': ['speaking', 'pronunciation', 'fluency'],
            'grammar': ['grammar', 'tense', 'sentence']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                return f'ielts_{topic}'
        
        return 'ielts_vocabulary'  # Default
    
    def _extract_difficulty(self, text: str) -> str:
        """Extract difficulty preference from text"""
        
        if any(word in text for word in ['easy', 'beginner', 'basic', 'simple']):
            return 'beginner'
        elif any(word in text for word in ['hard', 'difficult', 'advanced', 'challenging']):
            return 'advanced'
        else:
            return 'intermediate'
    
    def _detect_confidence(self, text: str) -> str:
        """Detect confidence level from text"""
        
        # Positive confidence indicators
        positive_indicators = ['confident', 'sure', 'understand', 'got it', 'easy']
        # Negative confidence indicators
        negative_indicators = ['confused', 'lost', "don't understand", 'difficult', 'hard']
        
        positive_count = sum(1 for word in positive_indicators if word in text)
        negative_count = sum(1 for word in negative_indicators if word in text)
        
        if positive_count > negative_count:
            return 'high'
        elif negative_count > positive_count:
            return 'low'
        else:
            return 'medium'
    
    def analyze_answer_quality(self, answer: str, expected: str) -> Dict:
        """
        Analyze quality of student answer
        
        Args:
            answer: Student's answer
            expected: Expected/correct answer
            
        Returns:
            Dict with quality metrics
        """
        
        # Simple similarity check (for hackathon)
        answer_lower = answer.lower().strip()
        expected_lower = expected.lower().strip()
        
        # Exact match
        exact_match = answer_lower == expected_lower
        
        # Partial match
        answer_words = set(answer_lower.split())
        expected_words = set(expected_lower.split())
        
        if expected_words:
            overlap = len(answer_words & expected_words) / len(expected_words)
        else:
            overlap = 0.0
        
        # Length comparison
        length_ratio = len(answer) / max(len(expected), 1)
        
        return {
            'exact_match': exact_match,
            'word_overlap': overlap,
            'length_ratio': length_ratio,
            'answer_length': len(answer),
            'expected_length': len(expected)
        }
