# This project demonstrates how to build an AI-powered financial analysis agent using Azure AI Foundry (GPT-4o-mini) that analyzes financial data from a CSV dataset.

Instead of calling external APIs, the agent reads structured data and generates insights such as:

   Top 10 companies by revenue
   Profit comparisons
   Financial trends
   Custom analytical queries
   
# 🚀 Features
✅ AI Agent powered by GPT-4o-mini
✅ CSV-based financial data analysis
✅ Natural language queries → structured insights
✅ Supports ranking, filtering, aggregation
✅ No external API required
✅ Extendable for advanced analytics

# 🧠 How It Works
User Query
   ↓
Azure AI Agent (GPT-4o-mini)
   ↓
Reads CSV Dataset
   ↓
Processes Data (Python / Pandas)
   ↓
Returns Insights (Top companies, trends, etc.)

#📂 Project Structure
.
├── data/
│   └── financial_data.csv     # Input dataset
├── outputs/                  # Optional generated files
├── createAgent_financial.py  # Main agent script
├── utils/
│   └── data_analysis.py      # CSV processing logic
├── README.md
└── requirements.txt

# ⚙️ Setup
1. Clone the repo
git clone https://github.com/your-username/financial-analysis-agent.git
cd financial-analysis-agent
2. Install dependencies
pip install -r requirements.txt
3. Set Azure environment
setx PROJECT_ENDPOINT "https://<your-resource>.services.ai.azure.com/api/projects/<your-project>"
4. Login to Azure
az login
▶️ Running the Project
python createAgent_financial.py
💬 Example Queries

You can ask the agent:

"Show top 10 companies by revenue"
"Which company has the highest profit?"
"Compare revenue vs expenses"
"List companies with profit greater than 50,000"
"Give me the worst performing companies"

ASX_100_quaterly_results
<img width="1981" height="1180" alt="assistant-1XfckjVP1u121PqQhKV5ih" src="https://github.com/user-attachments/assets/9e153423-1cd4-47b6-aa4d-9a92f19fd52c" />

nifty_500_quarterly_resutls
<img width="1589" height="1014" alt="assistant-J5bSsKWdH8gcAGCrcxBw1j" src="https://github.com/user-attachments/assets/dac6a8e3-54c3-4ae5-98b2-9a9f06d3194a" />

