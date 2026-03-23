import os
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

# Load the API Key
load_dotenv(find_dotenv())
api_key = os.getenv("GROQ_API_KEY")

# 3. SYSTEM PROMPT (Simplified for better reasoning)
SQL_PREFIX = """You are a professional Data Analyst for a Retail Company. 
The database uses English for table and column names.
TABLES AVAILABLE:
- dim_products: Contains product_id, product_name, category, cost, sale_price, current_stock.
- dim_stores: Contains store_id, city, manager.
- fact_sales: Contains sale_id, date, product_id, store_id, quantity.
BUSINESS RULES:
1. 'Margin' = (sale_price - cost) * quantity.
2. Always query the 'current_stock' column directly to find low stock. 
3. A 'Low Stock' alert is defined as any product where current_stock < 5.
4. When asked for 'Top Managers' or 'Most Sales', JOIN fact_sales with dim_stores and dim_products.
5. If a query fails, simplify the SQL. Avoid complex subqueries; use JOIN, GROUP BY, and ORDER BY instead.
6. Response Language: Always answer the user in ENGLISH.
7. Provide clear, conversational insights. Do not use JSON formatting unless explicitly asked.
8. To find 'Top Managers', JOIN 'fact_sales' with 'dim_stores', SUM the 'quantity', and ORDER BY the sum DESC.
9. When you have the final result from the database, you MUST start your last response with the exact words "Final Answer: " followed by your summary in English.
"""


def create_retail_agent(engine):
    # 1. Connect LangChain to your SQLite engine
    # We set sample_rows_in_table_info=10 so it sees the Ergonomic Mouse!
    db = SQLDatabase(engine, sample_rows_in_table_info=10)
    # 2. Setup the LLM (The engine of the brain)
    llm = ChatGroq(
        temperature=0, model_name="llama-3.3-70b-versatile", groq_api_key=api_key
    )

    # 3. Create the Agent = create_sql_agent(llm, db=db, verbose=True, prefix=SQL_PREFIX)
    agent_executor = create_sql_agent(
        llm,
        db=db,
        verbose=True,  # This lets you see the "thought process" in the terminal
        prefix=SQL_PREFIX,
        max_iterations=10,
        handle_parsing_errors=True,  # <--- THIS IS THE FIX
    )
    return agent_executor
