import os
import mimetypes
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    FilePurpose,
    CodeInterpreterTool,
    MessageRole,
    ListSortOrder
)
from pathlib import Path

import logging
from azure.identity import AzureCliCredential

# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("azure.identity").setLevel(logging.DEBUG)

credential = AzureCliCredential()
# -------------------------------------------------------
# Load environment
# -------------------------------------------------------
load_dotenv()

# Optional: set a display name for generated files/images (override via AUTHOR_NAME env var)
AUTHOR_NAME = os.getenv("AUTHOR_NAME", "Sazid Hasan1")

AGENT_PROJECT_ENDPOINT = os.getenv(
    "AGENT_PROJECT_ENDPOINT",
    "https://try-to-solve.services.ai.azure.com/api/projects/financial-solve" 
)
AGENT_MODEL_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME_GPT_4_mini", "gpt-4o-mini")
print("__file__:", __file__)
print("dirname:", os.path.dirname(__file__))
print("cwd:", os.getcwd())

# Fix CSV path to match actual file location
CSV_PATH = os.path.join(os.path.dirname(__file__), "nifty_500_quarterly_results.csv")

print(f" CSV path: {CSV_PATH}")

# -------------------------------------------------------
# Azure Agent Client
# -------------------------------------------------------
agent_client = AgentsClient(
    endpoint=AGENT_PROJECT_ENDPOINT,
    credential=credential
)

# -------------------------------------------------------
# Upload CSV file to the agent
# -------------------------------------------------------

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"CSV file not found at {CSV_PATH}. Please check the file location.")

with open(CSV_PATH, "r", encoding="utf-8") as f:
    csv_content = f.read()

file_name = os.path.basename(CSV_PATH)

upload_result = agent_client.files.upload_and_poll(
    file=(file_name, csv_content),
    purpose=FilePurpose.AGENTS
)
print("Uploaded file:", upload_result.id)

code_interpreter = CodeInterpreterTool(file_ids=[upload_result.id])
#agent_client.delete_agent("<old_agent_id>")

# create agent with code interpreter tool and tools_resources
agent = agent_client.create_agent(
    model="gpt-4o-mini",
    name="data-analysis-agent-sazid2",
    instructions="You are helpful agent",
    tools=code_interpreter.definitions,
    tool_resources=code_interpreter.resources,
    description="nifty_500_quarterly_results.",
)
print("Agent ID:", agent.id)
print("Agent Name:", agent.name)

# create a thread
thread = agent_client.threads.create()
print(f"Created thread, thread ID: {thread.id}")

# create a message
message = agent_client.messages.create(
    thread_id=thread.id,
    role=MessageRole.USER,
    content="""
You are a helpful data-analysis agent.

Instructions:
General rules:
- Always load the uploaded CSV into a pandas DataFrame.
- Infer schema using these expected columns:
 name,NSE_code,BSE_code,sector,industry,revenue,operating_expenses,operating_profit,operating_profit_margin,depreciation,interest,profit_before_tax,tax,net_profit,EPS,profit_TTM,EPS_TTM
- Convert numeric-looking strings into numeric types.
- When generating charts, ALWAYS:
    • Use matplotlib or seaborn
    • Display the figure
    • Save the figure as a PNG using the EXACT filename I specify
    • Do NOT generate random filenames
    • Do NOT overwrite files unless I explicitly say so

TASKS:

1) Create a bar chart for operating_profit in the Financials sector.
   Save it EXACTLY as:
   financials_operating_profit_Sazid.png

2) Create a table showing the top 10 companies by operating_profit.
   make the table and make it in top_10_companies_by_operating_profit.png.

3) Provide a short written summary of the operating_profit performance and save it as operating_profit_summary_Sazid.txt. 

4) Create a bar chart for the top 10 companies by operating_profit.
   Save it EXACTLY as:
   operating_profit_top10_Sazid.png

5) For EACH of the following columns, create a separate bar chart of the top 10 companies:
   - revenue
   - operating_expenses
   - operating_profit_margin
   - depreciation
   - interest
   - profit_before_tax

   For each chart, save the PNG using this exact naming pattern:
   financials_{column_name}_Sazid.png
   Example: financials_revenue_Sazid.png



"""
)
print(f"Created message, message ID: {message.id}")


# 1) Create a bar chart for top 10 companies for all the columns including revenue, operating expenses, operanting profit margin, depriciaiton, interest and profit before tax seperately.
# 2) save the charts as 'financials_{column_name}_Sazid.png' using plt.savefig() where {column_name} is the name of the column used for the bar chart.

# create and execute a run
run = agent_client.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id
)
print(f"Run finished with status: {run.status}")

if run.status == "failed":
    # Check if you got "Rate limit is exceeded.", then you want to get more quota
    print(f"Run failed: {run.last_error}")

# delete the original file from the agent to free up space (note: this does not delete your version of the file)
# agent_client.files.delete(upload_result.id)
# print("Deleted file")

# print the messages from the agent
messages = agent_client.messages.list(thread_id=thread.id)

# Display all messages from the agent
print("\n" + "="*80)
print("AGENT OUTPUT")
print("="*80 + "\n")

for msg in messages:
    if msg.get('content'):
        for content_item in msg['content']:
            content_type = content_item.get('type')
            
            if content_type == 'text':
                text_content = content_item.get('text', {})
                if isinstance(text_content, dict):
                    text_value = text_content.get('value', '')
                else:
                    text_value = str(text_content)
                print(text_value)
            
            elif content_type == 'image_file':
                file_id = content_item.get('image_file', {}).get('file_id')
                if file_id:
                    print(f"\n[Chart/Image generated by agent - File ID: {file_id} - For: {AUTHOR_NAME}]\n")

# import os

# def save_agent_file(agent_client, file_id: str, save_path: str):
#     # Many samples use something like agent_client.files.download(...)
#     # If your SDK returns bytes/stream, write them to disk.
#     content = agent_client.files.download(file_id=file_id)  # may be bytes or a stream-like object

#     os.makedirs(os.path.dirname(save_path), exist_ok=True)

#     if isinstance(content, (bytes, bytearray)):
#         data = content
#     else:
#         # stream-like
#         data = content.read()

#     with open(save_path, "wb") as f:
#         f.write(data)




# 1. When a CSV file is uploaded, load it into a DataFrame and infer the schema based on these expected column names:
#    name, ASX_Code, sector, industry, revenue, operating_expenses, operating_profit,
#    operating_profit_margin, depreciation, interest, profit_before_tax, tax,
#    net_profit, EPS, profit_TTM, EPS_TTM.

# 2. Convert numeric fields that may appear as strings into numeric types.

# 3. When I ask for charts:
#    - Use Python via the code interpreter.
#    - Generate clear visualizations using matplotlib or seaborn.
#    - Always display the generated figure.
#    - For bar charts:
#        • Use the numeric column I specify (e.g., operating_profit).
#        • Optionally filter the dataset based on any criteria I provide.
#        • Use an appropriate label column (e.g., name) on the x-axis.
#    - If no filter is specified, create the bar chart using the full dataset.

# 4. When I ask for tables or rankings:
#    - Use DataFrame operations (filter, sort, group).
#    - Return a clean, readable table.

# 5. After completing all tasks:
#    - Display charts first,
#    - Then tables,
#    - Then provide a short written summary.
# 6) After completing all tasks:
#    - Display all charts
#    - Display all tables
#    - Then provide a short summary
# Now, please analyze the uploaded CSV file and:
# # 1) Create a bar chart for operating_profit in the Financials sector.
# # 2) Save the chart as 'financials_operating_profit_Sazid.png' using plt.savefig().
# # 2) Generate a table showing the top 10 performing companies by operating_profit.
# # 3) Provide a brief summary of the financial performance of the companies in the dataset based on the operating profit.
# # 4) Save the chart as 'operating_profit_10_companies.png' using plt.savefig().



# # Example usage:
# save_agent_file(agent_client, file_id, "outputs/financials_operating_profit.png")


