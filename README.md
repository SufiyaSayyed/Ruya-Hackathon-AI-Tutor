# 🎓 IELTS Personalized Learning Tutor
## Multi-Agent Self-Learning System for Hackathon

A sophisticated adaptive learning system that uses a multi-agent architecture to provide personalized IELTS tutoring. Built for a 5-hour hackathon challenge.

---

## 🏗️ System Architecture

This system implements a **4-agent architecture** for intelligent, adaptive learning:

### **Agent 1: Perception Agent** 👁️
**Role:** Process raw observations and extract relevant features

**Responsibilities:**
- Parse student input (text, answers, requests)
- Extract intent (what does the student want?)
- Identify context (topic, difficulty preferences)
- Detect emotional state (confident, frustrated, confused)
- Analyze answer quality and patterns

**Implementation:**
- Rule-based pattern matching for intent detection
- Text analysis for confidence level assessment
- Feature extraction for planning agent

**File:** `agents/perception_agent.py`

---

### **Agent 2: Memory Agent** 🧠
**Role:** Store, retrieve, and manage experiences

**Responsibilities:**
- Maintain student profiles with skill levels
- Track complete interaction history
- Store performance metrics and trends
- Provide relevant context to other agents
- Update knowledge based on new interactions
- Implement spaced repetition memory

**Implementation:**
- JSON-based persistent storage
- Exponential moving average for skill updates
- History filtering and retrieval
- Performance trend analysis

**File:** `agents/memory_agent.py`

---

### **Agent 3: Planning Agent** 🎲
**Role:** Decide what action to take (Decision Engine)

**Responsibilities:**
- Analyze student state and context
- Select optimal learning action
- Implement adaptive difficulty (Zone of Proximal Development)
- Apply pedagogical strategies
- Balance exploration vs exploitation
- Implement spaced repetition scheduling

**Key Algorithms:**
- **Zone of Proximal Development (ZPD):** Content is slightly above current ability
- **Spaced Repetition:** Revisit topics at optimal intervals
- **Exploration/Exploitation:** 80% use best strategy, 20% explore alternatives
- **Adaptive Difficulty:** Adjust based on recent performance

**File:** `agents/planning_agent.py`

---

### **Agent 4: Evaluation Agent** 📊
**Role:** Assess action quality and provide learning signals

**Responsibilities:**
- Evaluate answer correctness
- Calculate performance scores
- Generate constructive feedback
- Identify specific mistakes
- Provide personalized guidance
- Generate reward signals for improvement

**Scoring Algorithm:**
- Exact match: 1.0 (100%)
- Close match: 0.95 (95%)
- High word overlap: 0.7 (70%)
- Partial understanding: 0.5 (50%)
- Some understanding: 0.3 (30%)
- Incorrect: 0.1 (10%)

**File:** `agents/evaluation_agent.py`

---

## 🔄 Multi-Agent Orchestration

The **Orchestrator** coordinates all agents in a learning loop:

```
1. PERCEPTION
   ↓ (Extract features from student input)
2. MEMORY
   ↓ (Retrieve student profile & history)
3. PLANNING
   ↓ (Decide optimal action)
4. EXECUTION
   ↓ (Perform selected action)
5. EVALUATION
   ↓ (Assess performance & update)
6. MEMORY UPDATE
   ↓ (Save new interaction)
[Loop back to 1]
```

**File:** `orchestrator.py`

---

## 📊 Learning Algorithms

### 1. **Adaptive Difficulty Adjustment**
```python
# Zone of Proximal Development
if skill_level < 0.3:
    difficulty = "beginner"
elif skill_level < 0.6:
    difficulty = "intermediate"
else:
    difficulty = "advanced"

# Adaptive increase for high performers
if recent_performance > 0.8:
    difficulty = increase_one_level(difficulty)
```

### 2. **Skill Level Update (Exponential Moving Average)**
```python
new_skill = current_skill * (1 - learning_rate) + performance * learning_rate
# Learning rate = 0.1 (10% weight to new performance)
```

### 3. **Student State Analysis**
```python
if avg_accuracy < 0.5 or len(struggling_topics) > 2:
    state = "struggling"  # Need more support
elif recent_avg > overall_avg + 0.1:
    state = "improving"  # Making progress
elif avg_accuracy >= 0.75:
    state = "mastered"   # High performer
```

### 4. **Action Selection Strategy**
```python
# State-based strategy
strategies = {
    'struggling': ['teach_concept', 'provide_exercise', 'encourage'],
    'improving': ['provide_exercise', 'teach_concept', 'provide_feedback'],
    'mastered': ['provide_exercise', 'provide_feedback', 'challenge']
}

# Exploration vs Exploitation
if random() < 0.2:
    action = explore_new_approach()
else:
    action = use_best_known_strategy()
```

---

## 🚀 Quick Start Guide

### **Prerequisites**
- Python 3.8+
- pip

### **Installation**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
streamlit run main.py
```

### **Usage**

1. **Select Student:** Choose from the sidebar (Demo or Advanced student)
2. **Interact:** 
   - Click "Get Personalized Exercise" for practice
   - Click "Explain Concept" for help with struggling topics
   - Click "Get Feedback" for performance summary
3. **Submit Answers:** Type your answer and click Submit
4. **View Progress:** Check sidebar for real-time skill metrics

---

## 📁 Project Structure

```
learning_tutor/
├── agents/
│   ├── __init__.py                  # Agent package
│   ├── perception_agent.py          # Feature extraction & intent detection
│   ├── memory_agent.py              # Profile & history management
│   ├── planning_agent.py            # Decision making & strategy
│   └── evaluation_agent.py          # Assessment & feedback
├── data/
│   ├── knowledge_base.json          # Learning materials & exercises
│   └── student_profiles.json        # Student data & metrics
├── orchestrator.py                  # Multi-agent coordinator
├── config.py                        # Configuration & settings
├── main.py                          # Streamlit UI application
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## 🎯 Key Features

### **1. Personalized Learning**
- Adapts to individual skill levels
- Respects learning styles (visual, analytical, etc.)
- Focuses on struggling areas

### **2. Intelligent Action Selection**
- Zone of Proximal Development (ZPD)
- Spaced repetition for struggling topics
- Exploration/exploitation balance

### **3. Comprehensive Evaluation**
- Partial credit for partial understanding
- Specific, actionable feedback
- Progressive hint system

### **4. Real-Time Adaptation**
- Skill levels update after each interaction
- Performance trends tracked
- Dynamic difficulty adjustment

### **5. Memory Management**
- Persistent student profiles
- Complete interaction history
- Session context tracking

---

## 🧪 Testing the System

### **Test Scenario 1: Beginner Student**
1. Select "Demo IELTS Student" (45% vocabulary skill)
2. Request exercise → Should get beginner-level exercise
3. Submit wrong answer → Should get encouraging feedback + hint
4. Request explanation → Should explain struggling topic

### **Test Scenario 2: Advanced Student**
1. Select "Advanced IELTS Student" (75% vocabulary skill)
2. Request exercise → Should get intermediate-level exercise
3. Submit correct answer → Should get positive feedback + harder exercise offer
4. Check feedback → Should show mastered topics

### **Test Scenario 3: Adaptive Learning**
1. Start with Demo student
2. Answer 3 exercises correctly → Skill level should increase
3. System should offer harder exercises
4. Check sidebar → Metrics should update in real-time

---

## 🎓 Pedagogical Principles

### **Zone of Proximal Development (ZPD)**
Content is slightly above current ability - challenging but achievable

### **Spaced Repetition**
Topics are revisited at optimal intervals for long-term retention

### **Formative Assessment**
Continuous feedback helps students understand and improve

### **Scaffolding**
Support is gradually reduced as competence increases

### **Personalization**
Instruction adapts to individual needs and learning styles

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Thresholds
MASTERY_THRESHOLD = 0.75      # 75% = mastered
STRUGGLING_THRESHOLD = 0.50   # <50% = struggling

# Learning parameters
DIFFICULTY_ADJUSTMENT_RATE = 0.1
EXPLORATION_RATE = 0.2        # 20% exploration

# Model settings (for future LLM integration)
LLM_MODEL = "llama3.2"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

---

## 🚧 Future Enhancements

1. **LLM Integration:** Use Ollama/HuggingFace for natural language generation
2. **Advanced Embedding:** Semantic similarity for answer evaluation
3. **More Topics:** Reading, writing, speaking, listening
4. **Analytics Dashboard:** Detailed progress visualization
5. **Recommendation Engine:** Suggest learning paths
6. **Multi-Modal:** Add image/audio support

---

## 📝 Implementation Notes

### **Why This Architecture?**

1. **Separation of Concerns:** Each agent has a clear, focused role
2. **Modularity:** Agents can be upgraded independently
3. **Testability:** Each agent can be tested in isolation
4. **Scalability:** Easy to add new agents or capabilities
5. **Transparency:** Agent decisions are logged and traceable

### **Time-Saving Design Decisions**

1. **Rule-Based Perception:** Fast, deterministic, no model needed
2. **JSON Storage:** Simple, human-readable, no database setup
3. **Template Responses:** Quick feedback generation
4. **Streamlit UI:** Rapid prototyping, no frontend code

### **Hackathon-Friendly**

- ✅ No external API dependencies
- ✅ Runs locally
- ✅ Minimal setup
- ✅ Clear demonstration value
- ✅ Extensible architecture

---

## 📚 Educational Value

This project demonstrates:

1. **Multi-Agent Systems:** Coordinating autonomous agents
2. **Reinforcement Learning:** Reward-based optimization
3. **Adaptive Systems:** Dynamic difficulty adjustment
4. **Educational Technology:** Pedagogically-sound design
5. **Software Engineering:** Clean architecture, modularity

---

## 🏆 Hackathon Pitch

**Problem:** One-size-fits-all education doesn't work. Students have different skill levels, learning styles, and needs.

**Solution:** An AI tutor with 4 specialized agents that:
- 👁️ Understands student needs
- 🧠 Remembers progress
- 🎲 Plans optimal learning paths
- 📊 Evaluates and adapts

**Impact:** Personalized learning at scale, adapting to each student in real-time.

**Tech:** Multi-agent architecture, reinforcement learning, adaptive algorithms.

**Demo:** Live interaction showing skill progression and adaptive difficulty.

---

## 👨‍💻 Author

Built for IELTS Learning Hackathon
Using multi-agent self-learning architecture

---

## 📄 License

MIT License - Feel free to use and modify!
