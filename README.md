# 🚀 FutureYou AI – Career Intelligence System

An end-to-end AI-powered career intelligence platform that analyses your skills,
resume, and GitHub profile to predict the best career path and build a personalised
learning roadmap.

---

## 📁 Project Structure

```
FutureYou-AI/
├── app.py                        # Streamlit frontend (all pages)
├── model/
│   ├── train_model.py            # Model training script
│   ├── career_model.pkl          # Trained RandomForest (generated)
│   ├── label_encoder.pkl         # Label encoder (generated)
│   └── model_meta.json           # Skill list & career profiles (generated)
├── utils/
│   ├── career_predictor.py       # Inference: predict_careers(), simulate_skill_addition()
│   ├── resume_parser.py          # PDF parsing + TF-IDF skill extraction
│   ├── github_analyzer.py        # GitHub REST API integration
│   ├── skill_gap.py              # Skill gap analysis
│   └── roadmap_generator.py      # Phased learning roadmap builder
├── database/
│   └── db.py                     # SQLite persistence layer
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone / download
```bash
git clone https://github.com/yourname/FutureYou-AI.git
cd FutureYou-AI
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the ML model
```bash
python model/train_model.py
```
This generates `model/career_model.pkl`, `model/label_encoder.pkl`, and
`model/model_meta.json`.  You only need to do this **once**.

### 5. Launch the app
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser.

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **Resume Parser** | Upload a PDF resume; skills are extracted via keyword + TF-IDF matching |
| **Career Prediction** | RandomForest model trained on 4 000 synthetic samples across 10 careers |
| **Skill Gap Analyzer** | Per-career gap breakdown: matched / missing required / missing bonus |
| **Roadmap Generator** | Phased, resource-linked learning plan with time estimates |
| **Career Simulator** | Add a hypothetical skill and see real-time probability shifts |
| **GitHub Analyzer** | Infers skills from your public repos & languages via GitHub API |
| **History** | All analyses persisted in SQLite |

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit + Plotly
- **ML model**: scikit-learn RandomForestClassifier (99% test accuracy)
- **NLP**: TF-IDF keyword matching (custom, no heavy dependencies)
- **Database**: SQLite (zero config)
- **APIs**: GitHub REST API v3

---

## 🔑 Optional: GitHub API Token

Without a token, GitHub allows ~60 requests/hour per IP.  
To raise the limit, set the env variable:
```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
```
Then modify `utils/github_analyzer.py` to read it:
```python
import os
token = os.getenv("GITHUB_TOKEN")
data  = analyze_github("username", token=token)
```

---

## 📊 Model Details

- **Algorithm**: RandomForestClassifier (300 trees, max_depth=18)
- **Training data**: 4 000 synthetic labelled examples (400 per class)
- **Features**: 66-dimensional binary skill vector
- **Classes**: 10 career paths
- **Test accuracy**: 99%

---

## 🤝 Contributing

Pull requests are welcome! Key areas for improvement:
- Add more career paths in `model/train_model.py`
- Integrate a real skill dataset (LinkedIn, O*NET)
- Add LLM-powered roadmap narration
- Export roadmap to PDF

---

## 📄 Licence

MIT – free to use, modify, and distribute.
