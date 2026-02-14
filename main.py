"""
IELTS Personalized Learning Tutor - Main Streamlit Application
Multi-Agent Self-Learning System for Hackathon Demo
"""

import streamlit as st
import json
import os
from datetime import datetime
from orchestrator import LearningOrchestrator
from config import Config

# Page configuration
st.set_page_config(
    page_title="IELTS AI Tutor",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = LearningOrchestrator()
    st.session_state.current_student = None
    st.session_state.chat_history = []
    st.session_state.current_exercise = None

def main():
    st.title("🎓 IELTS Personalized Learning Tutor")
    st.markdown("### Multi-Agent Adaptive Learning System")
    
    # Sidebar for student selection and metrics
    with st.sidebar:
        st.header("Student Profile")
        
        # Student selection
        student_profiles = st.session_state.orchestrator.memory_agent.load_student_profiles()
        student_ids = list(student_profiles.keys())
        
        selected_student = st.selectbox(
            "Select Student",
            student_ids,
            format_func=lambda x: student_profiles[x]['name']
        )
        
        if st.button("Load Student"):
            st.session_state.current_student = selected_student
            st.session_state.chat_history = []
            st.success(f"Loaded: {student_profiles[selected_student]['name']}")
        
        # Display student metrics if loaded
        if st.session_state.current_student:
            st.markdown("---")
            profile = student_profiles[st.session_state.current_student]
            
            st.subheader("Skill Levels")
            for skill, level in profile['skill_levels'].items():
                st.metric(
                    skill.replace('_', ' ').title(),
                    f"{level*100:.0f}%",
                    delta=None
                )
            
            st.markdown("---")
            st.subheader("Performance Metrics")
            st.write(f"**Avg Accuracy:** {profile['performance_metrics']['avg_accuracy']*100:.0f}%")
            st.write(f"**Learning Style:** {profile['learning_style'].title()}")
            
            # Show struggling topics
            if profile['performance_metrics']['topics_struggling']:
                st.warning("**Needs Practice:**")
                for topic in profile['performance_metrics']['topics_struggling']:
                    st.write(f"- {topic.replace('_', ' ').title()}")
    
    # Main content area
    if not st.session_state.current_student:
        st.info("👈 Please select a student from the sidebar to begin")
        
        # Show system architecture
        st.markdown("---")
        st.subheader("System Architecture")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🤖 Multi-Agent System:**
            - **Perception Agent**: Analyzes student input and context
            - **Memory Agent**: Manages student profiles and learning history
            - **Planning Agent**: Selects optimal learning actions
            - **Evaluation Agent**: Assesses performance and provides feedback
            """)
        
        with col2:
            st.markdown("""
            **🎯 Features:**
            - Adaptive difficulty adjustment
            - Personalized exercise selection
            - Real-time performance tracking
            - Context-aware explanations
            - Self-improving feedback loop
            """)
        
        return
    
    # Chat interface
    st.subheader("Learning Session")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                st.chat_message("assistant").write(message['content'])
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Get Personalized Exercise", use_container_width=True):
            handle_exercise_request()
    
    with col2:
        if st.button("💡 Explain Concept", use_container_width=True):
            handle_concept_explanation()
    
    with col3:
        if st.button("📊 Get Feedback", use_container_width=True):
            handle_feedback_request()
    
    # Exercise submission area
    if st.session_state.current_exercise:
        st.markdown("---")
        st.subheader("Current Exercise")
        
        exercise = st.session_state.current_exercise
        st.write(f"**Question:** {exercise['question']}")
        
        user_answer = st.text_input("Your Answer:", key="answer_input")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Submit Answer"):
                handle_answer_submission(user_answer, exercise)
        
        with col2:
            if st.button("Show Hints"):
                show_hints(exercise)

def handle_exercise_request():
    """Request a personalized exercise from the orchestrator"""
    with st.spinner("Analyzing your profile and selecting optimal exercise..."):
        result = st.session_state.orchestrator.process_interaction(
            student_id=st.session_state.current_student,
            interaction_type="request_exercise",
            context={}
        )
        
        st.session_state.chat_history.append({
            'role': 'user',
            'content': "I'd like to practice with an exercise."
        })
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': result['response']
        })
        
        if 'exercise' in result:
            st.session_state.current_exercise = result['exercise']
        
        st.rerun()

def handle_concept_explanation():
    """Request concept explanation"""
    with st.spinner("Preparing personalized explanation..."):
        result = st.session_state.orchestrator.process_interaction(
            student_id=st.session_state.current_student,
            interaction_type="explain_concept",
            context={}
        )
        
        st.session_state.chat_history.append({
            'role': 'user',
            'content': "Can you explain a concept I'm struggling with?"
        })
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': result['response']
        })
        
        st.rerun()

def handle_feedback_request():
    """Request performance feedback"""
    with st.spinner("Analyzing your learning progress..."):
        result = st.session_state.orchestrator.process_interaction(
            student_id=st.session_state.current_student,
            interaction_type="provide_feedback",
            context={}
        )
        
        st.session_state.chat_history.append({
            'role': 'user',
            'content': "How am I doing? What should I focus on?"
        })
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': result['response']
        })
        
        st.rerun()

def handle_answer_submission(answer, exercise):
    """Handle student's answer submission"""
    if not answer.strip():
        st.warning("Please enter an answer before submitting.")
        return
    
    with st.spinner("Evaluating your answer..."):
        result = st.session_state.orchestrator.process_interaction(
            student_id=st.session_state.current_student,
            interaction_type="submit_answer",
            context={
                'exercise': exercise,
                'student_answer': answer
            }
        )
        
        st.session_state.chat_history.append({
            'role': 'user',
            'content': f"My answer: {answer}"
        })
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': result['response']
        })
        
        st.session_state.current_exercise = None
        st.rerun()

def show_hints(exercise):
    """Display hints for the current exercise"""
    if 'hints' in exercise and exercise['hints']:
        st.info("**Hints:**")
        for i, hint in enumerate(exercise['hints'], 1):
            st.write(f"{i}. {hint}")
    else:
        st.warning("No hints available for this exercise.")

if __name__ == "__main__":
    main()
