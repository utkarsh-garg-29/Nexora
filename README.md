# Nexora — AI-Powered Placement Intelligence Platform

> Helping B.Tech CSE students know exactly where they stand, which companies to target, and what to do next.

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/nexora.git
cd nexora

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your OpenAI API key
cp .env.example .env
# Edit .env and paste your key

# 5. Run the app
streamlit run app.py
```

App opens at: http://localhost:8501

## Project Structure

```
nexora/
├── app.py              # Streamlit UI
├── analyzer.py         # Scoring engine + company matcher + OpenAI
├── companies.json      # Company database
├── .env                # API key (never commit this)
├── .env.example        # Template for .env
├── requirements.txt    # Python dependencies
└── README.md
```
