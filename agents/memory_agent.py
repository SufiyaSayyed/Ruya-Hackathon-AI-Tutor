"""
Memory Agent - Stores, retrieves, and manages experiences

Role:
- Maintain student profiles
- Track learning history
- Store performance metrics
- Provide relevant context to other agents
- Update knowledge based on interactions
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime
from config import Config

class MemoryAgent:
    """
    Agent responsible for memory management and context retrieval
    
    Key responsibilities:
    1. Load and save student profiles
    2. Track interaction history
    3. Update skill levels based on performance
    4. Retrieve relevant past experiences
    5. Manage long-term and short-term memory
    """
    
    def __init__(self):
        """Initialize memory agent"""
        print("🧠 Memory Agent initialized")
        
        self.student_profiles = self.load_student_profiles()
        self.session_memory = {}  # Short-term memory for current session
    
    def load_student_profiles(self) -> Dict:
        """Load all student profiles from file"""
        
        try:
            with open(Config.STUDENT_PROFILES_PATH, 'r') as f:
                profiles = json.load(f)
                print(f"📚 Loaded {len(profiles)} student profiles")
                return profiles
        except FileNotFoundError:
            print("⚠️ Student profiles not found, creating default profiles")
            return self._create_default_profiles()
    
    def _create_default_profiles(self) -> Dict:
        """Create default student profiles if none exist"""
        
        default_profiles = {
            "student_123": {
                "id": "student_123",
                "name": "Demo IELTS Student",
                "skill_levels": {
                    "ielts_vocabulary": 0.45,
                    "ielts_reading_skills": 0.35
                },
                "learning_style": "visual",
                "interaction_history": [],
                "performance_metrics": {
                    "avg_accuracy": 0.40,
                    "topics_mastered": [],
                    "topics_struggling": ["basic_collocations", "skimming_for_main_idea"]
                }
            }
        }
        
        # Save default profiles
        self.save_student_profiles(default_profiles)
        return default_profiles
    
    def save_student_profiles(self, profiles: Dict = None):
        """Save student profiles to file"""
        
        if profiles is None:
            profiles = self.student_profiles
        
        try:
            os.makedirs(Config.DATA_DIR, exist_ok=True)
            with open(Config.STUDENT_PROFILES_PATH, 'w') as f:
                json.dump(profiles, f, indent=2)
            print("💾 Student profiles saved")
        except Exception as e:
            print(f"⚠️ Error saving profiles: {e}")
    
    def get_student_profile(self, student_id: str) -> Dict:
        """
        Retrieve student profile
        
        Args:
            student_id: Student identifier
            
        Returns:
            Student profile dict
        """
        
        if student_id not in self.student_profiles:
            print(f"⚠️ Student {student_id} not found, creating new profile")
            return self._create_new_student_profile(student_id)
        
        return self.student_profiles[student_id]
    
    def _create_new_student_profile(self, student_id: str) -> Dict:
        """Create a new student profile"""
        
        new_profile = {
            "id": student_id,
            "name": f"Student {student_id}",
            "skill_levels": {
                "ielts_vocabulary": 0.3,  # Start at beginner
                "ielts_reading_skills": 0.3
            },
            "learning_style": "visual",
            "interaction_history": [],
            "performance_metrics": {
                "avg_accuracy": 0.0,
                "topics_mastered": [],
                "topics_struggling": []
            }
        }
        
        self.student_profiles[student_id] = new_profile
        self.save_student_profiles()
        
        return new_profile
    
    def update_skill_level(
        self,
        student_id: str,
        topic: str,
        performance: float,
        learning_rate: float = 0.1
    ):
        """
        Update student's skill level based on performance
        
        Uses exponential moving average to update skill level
        
        Args:
            student_id: Student identifier
            topic: Topic/skill being practiced
            performance: Performance score (0.0-1.0)
            learning_rate: How quickly to update (0.0-1.0)
        """
        
        profile = self.get_student_profile(student_id)
        
        # Get current skill level
        current_skill = profile['skill_levels'].get(topic, 0.3)
        
        # Update with exponential moving average
        new_skill = current_skill * (1 - learning_rate) + performance * learning_rate
        
        # Update profile
        profile['skill_levels'][topic] = new_skill
        
        # Update overall accuracy
        all_performances = [
            h.get('performance', 0.5) 
            for h in profile.get('interaction_history', [])
            if 'performance' in h
        ]
        all_performances.append(performance)
        
        profile['performance_metrics']['avg_accuracy'] = sum(all_performances) / len(all_performances)
        
        # Update mastery/struggling lists
        self._update_topic_lists(profile, topic, new_skill)
        
        # Save updates
        self.save_student_profiles()
        
        if Config.DEBUG_MODE:
            print(f"📈 Updated {topic}: {current_skill:.2f} → {new_skill:.2f}")
    
    def _update_topic_lists(self, profile: Dict, topic: str, skill_level: float):
        """Update lists of mastered and struggling topics"""
        
        mastered = profile['performance_metrics']['topics_mastered']
        struggling = profile['performance_metrics']['topics_struggling']
        
        # Remove from both lists first
        if topic in mastered:
            mastered.remove(topic)
        if topic in struggling:
            struggling.remove(topic)
        
        # Add to appropriate list
        if skill_level >= Config.MASTERY_THRESHOLD:
            if topic not in mastered:
                mastered.append(topic)
        elif skill_level < Config.STRUGGLING_THRESHOLD:
            if topic not in struggling:
                struggling.append(topic)
    
    def record_interaction(
        self,
        student_id: str,
        interaction_data: Dict
    ):
        """
        Record a learning interaction
        
        Args:
            student_id: Student identifier
            interaction_data: Data about the interaction
        """
        
        profile = self.get_student_profile(student_id)
        
        # Add timestamp if not present
        if 'timestamp' not in interaction_data:
            interaction_data['timestamp'] = datetime.now().isoformat()
        
        # Add to history
        profile['interaction_history'].append(interaction_data)
        
        # Keep only recent history (last 100 interactions)
        if len(profile['interaction_history']) > 100:
            profile['interaction_history'] = profile['interaction_history'][-100:]
        
        # Save
        self.save_student_profiles()
    
    def get_relevant_history(
        self,
        student_id: str,
        topic: str = None,
        n: int = 5
    ) -> List[Dict]:
        """
        Get relevant interaction history
        
        Args:
            student_id: Student identifier
            topic: Filter by topic (optional)
            n: Number of interactions to retrieve
            
        Returns:
            List of recent relevant interactions
        """
        
        profile = self.get_student_profile(student_id)
        history = profile.get('interaction_history', [])
        
        # Filter by topic if specified
        if topic:
            history = [h for h in history if h.get('topic') == topic]
        
        # Return most recent n
        return history[-n:] if len(history) > n else history
    
    def get_performance_trend(
        self,
        student_id: str,
        topic: str = None,
        window: int = 10
    ) -> Dict:
        """
        Analyze performance trend
        
        Args:
            student_id: Student identifier
            topic: Specific topic (optional)
            window: Number of recent interactions to analyze
            
        Returns:
            Dict with trend analysis
        """
        
        history = self.get_relevant_history(student_id, topic, window)
        
        if not history:
            return {
                'trend': 'neutral',
                'average': 0.0,
                'recent_average': 0.0,
                'improvement': 0.0
            }
        
        # Get performances
        performances = [h.get('performance', 0.5) for h in history if 'performance' in h]
        
        if not performances:
            return {
                'trend': 'neutral',
                'average': 0.0,
                'recent_average': 0.0,
                'improvement': 0.0
            }
        
        # Calculate metrics
        overall_avg = sum(performances) / len(performances)
        
        # Compare first half vs second half
        mid = len(performances) // 2
        if mid > 0:
            first_half_avg = sum(performances[:mid]) / mid
            second_half_avg = sum(performances[mid:]) / (len(performances) - mid)
            improvement = second_half_avg - first_half_avg
        else:
            first_half_avg = overall_avg
            second_half_avg = overall_avg
            improvement = 0.0
        
        # Determine trend
        if improvement > 0.1:
            trend = 'improving'
        elif improvement < -0.1:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'average': overall_avg,
            'recent_average': second_half_avg,
            'improvement': improvement,
            'n_interactions': len(performances)
        }
    
    def get_session_context(self, student_id: str) -> Dict:
        """Get context for current session"""
        
        if student_id not in self.session_memory:
            self.session_memory[student_id] = {
                'exercises_attempted': 0,
                'current_topic': None,
                'session_start': datetime.now().isoformat()
            }
        
        return self.session_memory[student_id]
    
    def update_session_context(self, student_id: str, updates: Dict):
        """Update session context"""
        
        context = self.get_session_context(student_id)
        context.update(updates)
