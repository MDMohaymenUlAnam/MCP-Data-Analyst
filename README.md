# 📊 MCP CSV Analyst

A flexible MCP server that helps you load and analyze CSV, Excel, and JSON data. It lets you run scripts safely, keep data in memory, and generate easy-to-understand summaries for decision-making.

---

## 🚀 Features

* Load .csv, .xlsx, .xls, and .json files into memory
* Named in-memory DataFrame storage and management
* Secure script evaluation using exec with safe Python libraries
  (pandas, numpy, scipy, scikit-learn, statsmodels)
* Running notes log for all tool actions
* Executive summary generation via prompt-driven instructions
* Easily integrable with CLI or agent frameworks via stdio

---

## 📦 Requirements

* Python 3.8 or later
* Recommended: virtual environment setup

To create a virtual environment:

python -m venv venv  
source venv/bin/activate  (Windows: venv\Scripts\activate)

---

## 📥 Installation

Install required dependencies:

pip install pandas numpy scipy scikit-learn statsmodels pydantic

---

## 🧠 How It Works

The tool is built using a FastMCP agent setup. It defines and exposes the following capabilities:

* load_data: Load a supported file into memory as a named DataFrame
* run_script: Run custom analysis scripts safely using the in-memory data
* csv://notes: View a chronological log of notes and outputs
* executive_summary: Generate business-focused insights from data using structured prompts

---

## 🛠 Usage

### ▶️ Run the system

Run the following command to start the MCP stdio server:

python main.py

---


## 📄 License

MIT License

---
