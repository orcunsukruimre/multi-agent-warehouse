# 🤖 Multi-Agent Warehouse Decision Support System

> **[🇹🇷 Türkçe](README.md)** | **[🇬🇧 English](README_EN.md)**

**Agentic AI-powered warehouse management system with GPT-4 and Human-in-the-Loop decision making.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-red)](https://streamlit.io/)
[![GPT-4](https://img.shields.io/badge/GPT--4-OpenAI-green)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📖 Medium Article

Detailed article about this project:

**📝 [Agentic AI for Warehouse Management - A Real-World Human-in-the-Loop Application](https://medium.com/data-science-collective/agentic-ai-for-warehouse-management-a-real-world-human-in-the-loop-application-7c9c6653e174)**

*In-depth explanation of system design, how 4 expert agents work together, human-in-the-loop approach, and real-world applications.*

---

## 🎯 Features

### 🤖 Agentic AI
- **4 Expert Agents** - Each operates autonomously in its domain
- **GPT-4 Integration** - Intelligent summaries for input and results
- **Automatic Assignment** - Optimization → Heuristic fallback
- **Human-in-the-Loop** - Human approval for critical decisions

### ⚖️ Compliance Monitoring
- **Daily Limit** - Maximum 10 tours/operator (435 minutes / 7.25 hours)
- **Automatic Check** - Labor law compliance (simplified)
- **Risk Analysis** - CRITICAL/HIGH/MEDIUM/LOW levels

### 📊 Visualization
- **Dynamic Dashboard** - Real-time progress bars
- **4 Charts** - Tour, product, volume, balance analysis
- **Excel Export** - Download assignment lists

---

## 🚀 Quick Start

### 1️⃣ Requirements
```bash
pip install -r requirements.txt
```

### 2️⃣ Set OpenAI API Key

**Method 1: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="sk-proj-YOUR-API-KEY-HERE"
```

**Method 2: .env File**

Create a `.env` file:
```
OPENAI_API_KEY=sk-proj-YOUR-API-KEY-HERE
```

⚠️ **Important:** Never upload your API key to GitHub! The `.gitignore` file automatically excludes `.env`.

### 3️⃣ Run the Application

**Streamlit Web Interface (Recommended):**
```bash
streamlit run app.py
```

Opens automatically in browser: `http://localhost:8501`

**Terminal Interface:**
```bash
python3 main.py
```

---

## 📋 Usage Flow

### 1️⃣ Automatic Summary
System analyzes current state using GPT-4:
- Number of work orders (74 tours)
- Total products and volume (5,177 items, 14,491 desi)
- Operator status (6 active, 2 on leave/sick)

### 2️⃣ Start Assignment
One-click automatic assignment:
- Optimization algorithm (PuLP)
- Falls back to heuristic if optimization fails
- Dynamic progress bars

### 3️⃣ Compliance Check
Automatic legal compliance audit:
- 11+ tours = CRITICAL VIOLATION
- 0-10 tours = COMPLIANT

### 4️⃣ Decision Point (Human-in-the-Loop)
If non-compliant, system presents 2 options:
- **A) Hire +1 Operator** - All work completed (~$20-25)
- **B) Reduce Workload** - Cost savings ($0)

### 5️⃣ Results
- LLM final summary (GPT-4)
- Per-operator table
- 4 detailed charts
- Excel download

---

## 🏗️ Project Structure
```
multi_agent_warehouse/
├── app.py                      # Streamlit web interface
├── main.py                     # Terminal interface
├── agents/
│   ├── assignment_agent.py     # Main orchestrator
│   ├── inventory_agent.py      # Workload analysis
│   ├── workforce_agent.py      # Workforce analysis
│   └── compliance_agent.py     # Legal compliance
├── tools/
│   ├── optimizer.py            # Assignment algorithms
│   ├── llm_summarizer.py       # GPT-4 integration
│   └── visualizer.py           # Chart generation
├── data/
│   └── warehouse_data.py       # Data source
├── config/
│   └── regulations.yaml        # Compliance rules
├── outputs/                    # Excel and charts
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md                   # Turkish
└── README_EN.md               # English
```

---

## 🔧 Technical Details

### Technologies Used
- **Python 3.9+**
- **Streamlit** - Web interface
- **GPT-4** - OpenAI API
- **PuLP** - Mathematical optimization
- **Pandas** - Data processing
- **Matplotlib** - Visualization

### Assignment Algorithm

**Optimization (PuLP):**
```python
# Objective: Maximize workload balance
maximize: M1*y + M2*z + Σ(product_count)

# Constraints:
1. Each job to one person: Σ(x[i,j]) = 1
2. Tour balance: tour[i] ≥ average * z
3. Volume balance: desi[i] ≥ average * y
4. Balance ratio: z ≤ 0.53 * y
```

**Heuristic (Fallback):**
```python
# Round-robin balanced distribution
1. Sort work orders by volume/count ratio
2. Distribute to operators sequentially
```

### Compliance Rules
```yaml
working_hours:
  daily_minutes: 435        # 7.25 hours
  minutes_per_tour: 40      # Tour duration
  max_tours_per_day: 10     # Limit

violations:
  tour_limit_exceeded:
    threshold: 11           # Violation
    risk_level: "CRITICAL"
```

---

## 🧪 Test Scenarios

### Scenario 1: Normal Capacity (6 Active Operators)
```
✅ 74 work orders → 74 assigned
✅ Compliance: COMPLIANT
✅ Risk: LOW
```

### Scenario 2: Limited Capacity (4 Active Operators)
```
⚠️  74 work orders → Initial assignment non-compliant
👤 Decision: A) +1 Operator
✅ 74 work orders → 74 assigned
✅ Compliance: COMPLIANT
```

### Scenario 3: Workload Reduction
```
⚠️  74 work orders → Initial assignment non-compliant
👤 Decision: B) Reduce Workload
✅ 60 work orders → 60 assigned
⚠️  14 work orders postponed
```

---

## 📐 System Assumptions

### Operational Parameters
- **One tour duration:** 40 minutes
- **Daily work:** 435 minutes (7.25 hours)
- **Maximum tour/operator:** 10 tours/day

### Test Data
- **Total work orders:** 74 tours
- **Total products:** 5,177 items
- **Total volume:** 14,491 desi
- **Operators:** 8 total (6 active, 2 on leave/sick)

---

## ⚠️ Known Issues

### Mac M1/M2/M3/M4 Optimization
PuLP optimization may not work on some Apple Silicon systems. System automatically falls back to heuristic algorithm (guaranteed solution).

**Solution:** Install GLPK solver:
```bash
brew install glpk
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

MIT License 

---

## 👤 Author

**Dr. Şükrü İmre**
- 📧 Email: orcunimre@hotmail.com
- 💼 LinkedIn: [Şükrü İmre] (https://tr.linkedin.com/in/şükrü-imre-phd-8b779141)
- 📝 Medium: [@sukruimre](https://medium.com/@sukruimre)

---

## 🙏 Acknowledgments

- OpenAI GPT-4
- Streamlit Community
- PuLP Optimization Library
- Python Community

---

## 📚 Related Articles

- **[Agentic AI for Warehouse Management (EN)](https://medium.com/data-science-collective/agentic-ai-for-warehouse-management-a-real-world-human-in-the-loop-application-7c9c6653e174)** - Detailed article about this project
- **[LLM Agents in Warehouse (EN)](https://medium.com/data-science-collective/how-can-llm-agents-be-utilized-in-warehouses-e14703434a0d)** - Previous work (2 agents)

---

**⭐ If you find this helpful, don't forget to star the repository!**

---

*This is a research project. It is not a production warehouse application but a prototype demonstrating how agentic AI can be applied.*