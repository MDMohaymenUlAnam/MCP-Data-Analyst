from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server
from pydantic import BaseModel
from typing import List, Optional, Dict
from io import StringIO
import pandas as pd
import numpy as np
import scipy
import sklearn
import statsmodels.api as sm
from mcp.types import TextContent
from mcp.shared.exceptions import McpError
import asyncio
import os

INTERNAL_ERROR = "internal_error"

# Initialize FastMCP
mcp = FastMCP("CSV Analyst", dependencies=["pandas", "numpy", "scipy", "scikit-learn", "statsmodels"])

# In-memory script manager
class ScriptRunner:
    def __init__(self):
        self.data: Dict[str, pd.DataFrame] = {}
        self.df_count = 0
        self.notes: List[str] = []

    def load_data(self, file_path: str, df_name: Optional[str] = None):
        self.df_count += 1
        if not df_name:
            df_name = f"df_{self.df_count}"

        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            elif ext == ".json":
                df = pd.read_json(file_path)
            else:
                raise ValueError("Unsupported file type. Supported types: .csv, .xlsx, .xls, .json")

            self.data[df_name] = df
            self.notes.append(f"✅ Loaded `{file_path}` as `{df_name}`")
            return [TextContent(type="text", text=f"✅ Loaded `{file_path}` as `{df_name}`")]

        except Exception as e:
            raise McpError(INTERNAL_ERROR, f"File load error: {str(e)}") from e

    def safe_eval(self, script: str, save_to_memory: Optional[List[str]] = None):
        local_vars = {**self.data}
        stdout = StringIO()
        try:
            old_stdout = __import__('sys').stdout
            __import__('sys').stdout = stdout
            exec(script, {'pd': pd, 'np': np, 'scipy': scipy, 'sklearn': sklearn, 'statsmodels': sm}, local_vars)
            __import__('sys').stdout = old_stdout
        except Exception as e:
            raise McpError(INTERNAL_ERROR, f"Script error: {str(e)}") from e

        if save_to_memory:
            for name in save_to_memory:
                if name in local_vars:
                    self.data[name] = local_vars[name]
                    self.notes.append(f"💾 Saved variable `{name}` to memory.")

        output = stdout.getvalue() or "✅ Script ran without output."
        self.notes.append(f"📄 Script output: {output}")
        return [TextContent(type="text", text=output)]

runner = ScriptRunner()

# Tool input schemas
class LoadDataInput(BaseModel):
    file_path: str
    df_name: Optional[str] = None

class RunScriptInput(BaseModel):
    script: str
    save_to_memory: Optional[List[str]] = None

# Define tools
@mcp.tool()
def load_data(input: LoadDataInput) -> List[TextContent]:
    return runner.load_data(input.file_path, input.df_name)

@mcp.tool()
def run_script(input: RunScriptInput) -> List[TextContent]:
    return runner.safe_eval(input.script, input.save_to_memory)

# Define resource
@mcp.resource("csv://notes")
def notes_log() -> str:
    return "\n".join(runner.notes)

# Define prompt
@mcp.prompt()
def executive_summary(file_path: str, topic: str = "Business performance") -> str:
    return f"""
You are a Senior Data Analyst preparing insights for upper management.

You have access to a dataset at the following path:
<file_path>
{file_path}
</file_path>

Your task is to analyze the dataset with a focus on:
<topic>
{topic}
</topic>

Follow these instructions:

1. **Load the dataset** using the `load_data` tool. (Supports .csv, .xlsx, .xls, .json)

2. **Understand the business context**:
   - What is the dataset about?
   - What decisions might a business leader need to make based on this data?

3. **Perform exploratory and strategic analysis**:
   Use the `run_script` tool to compute and explain:
   - Key metrics (e.g., revenue, churn rate, user activity, region-wise performance)
   - Growth or decline trends (over time, by product/region)
   - Top and bottom performers (e.g., top-selling products, high-risk zones)
   - Operational or financial risks (e.g., missing data, anomalies)
   - Any seasonality or pattern detection that may impact planning

4. **Summarize your findings** for executive understanding. Use business-friendly language and clear bullets:
   - 📈 What’s improving?
   - 📉 What’s declining?
   - ⚠️ Any critical risks or alerts?
   - 📌 Strategic recommendations

Example output:
"""
    
# Main entry point with stdio stream
if __name__ == "__main__":
    async def run_server():
        async with stdio_server() as (read_stream, write_stream):
            await mcp.run(read_stream, write_stream)

    asyncio.run(run_server())
