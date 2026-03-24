# 🤖 Retail AI Data Agent

An intelligent assistant that translates natural language into SQL queries to analyze retail performance, stock levels, and store management.

## 📁 Project Structure
- `data/`: Contains the SQLite database.
- `src/`: Core application logic (`app.py`, `database.py`).
<!-- - `test_queries.ipynb`: Technical validation of SQL logic. -->

## 🚀 Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Set up your `.env` file with `GROQ_API_KEY`.
3. Initialize the DB: `python src/database.py`
4. Run the app: `streamlit run src/app.py`

## 📊 Key Features
- **Natural Language Querying**: Ask questions like "Who is the best manager?"
- **Automated Visualization**: Sales trends generated automatically.
- **Stock Alerts**: Real-time identification of low-inventory items.