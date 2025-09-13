# floatchat
FloatChat - AI-Powered Conversational Interface for ARGO Ocean Data Discovery and Visualization
# 🌊 FloatChat – Interactive Argo Float Data Dashboard

FloatChat is a simple, user-friendly dashboard to **view and explore Argo ocean float data**.  
Even non-technical users can see where floats are, what data they collected, and chat with the dashboard to ask questions in plain language.

---

## 📝 Problem Statement

Argo floats collect a huge amount of ocean data (temperature, salinity, pressure, etc.).  
This data is stored in scientific formats that are **hard for students, researchers and policy-makers** to access quickly.  
We wanted to create a **clean, interactive tool** that turns complex files into **easy-to-use maps, charts and chat responses**.

---

## ✅ Our Solution

- **Lightweight Python dashboard** that reads processed Argo data from small `.pkl` / SQLite files (no heavy `.nc` files).
- **Map view**: see floats on an interactive map with location and depth.
- **Data view**: browse temperature / salinity profiles in tabular or graph form.
- **Chatbot**: type a question like “show floats near India in 2020” and instantly get filtered results.
- **One-click deploy**: can be run locally or hosted easily.

---

## 🗂️ Project Structure

| File / Folder            | Description |
|--------------------------|-------------|
| `app.py`                 | Main entry point for running the dashboard |
| `dashboard.py`           | Code for the interactive map and data visualisation |
| `dashboard_chatbot.py`   | Natural-language chat/QA component |
| `read_argo.py`           | Functions to read and clean Argo data files |
| `to_sqlite.py` / `argo.db`| Pre-converted SQLite database for fast queries |
| `argo_df.pkl` / `argo_df_india.pkl`| Small ready-to-use datasets |
| `requirements.txt`       | All Python dependencies |
| `.gitignore`             | Ignored files (big `.nc` files, etc.) |

---

## 🚀 How to Run Locally

1. **Clone the repo**
   ```bash
   git clone https://github.com/RanaAkshat/floatchat.git

# Create & activate a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python app.py


