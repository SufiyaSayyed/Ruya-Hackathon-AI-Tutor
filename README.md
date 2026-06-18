# IELTS Personalized Learning Tutor
## Multi-Agent Self-Learning System for Hackathon

A sophisticated adaptive learning system that uses a multi-agent architecture to provide personalized IELTS tutoring. Built for a 5-hour hackathon challenge.

---

## System Architecture

This system implements a **4-agent architecture** for intelligent, adaptive learning:

### **Agent 1: Perception Agent** 
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

### **Agent 2: Memory Agent** 
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

### **Agent 3: Planning Agent** 
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

### **Agent 4: Evaluation Agent** 
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

##  Multi-Agent Orchestration

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
<!-- 
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

--- -->