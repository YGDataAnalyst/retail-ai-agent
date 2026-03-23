import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from database import setup_database  # Import the setup_database function
from agent import create_retail_agent  # Import the agent creation function

db_engine = setup_database()
agent_executor = create_retail_agent(db_engine)  # The brain is now separate!

st.set_page_config(page_title="AI Data Agent", layout="wide")

# 5. SIDEBAR (Management)
with st.sidebar:
    st.title("⚙️ Settings")
    st.success("Connected to retail_pro.db")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.info("This agent uses Llama-3.3 to translate your questions into SQL queries.")

# 6. UI HEADER
st.title("📊 Retail Intelligence Agent")
st.markdown(
    """
Welcome! Use the buttons below for quick insights or type your custom question in the chat.
"""
)

# 7. INITIALIZE HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []


# 8. QUICK ACTIONS (Buttons)
def handle_quick_question(question):
    # This function adds the question and triggers the response immediately
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = agent_executor.invoke({"input": question})
            output = response["output"]
            st.markdown(output)

            # Automatic charting for sales queries
            if "sales" in question.lower() or "trend" in question.lower():
                query = "SELECT date, SUM(quantity * sale_price) as total FROM fact_sales s JOIN dim_products p ON s.product_id = p.product_id GROUP BY date"
                df = pd.read_sql(query, db_engine)
                st.line_chart(df.set_index("date"))

    st.session_state.messages.append({"role": "assistant", "content": output})
    st.rerun()


st.subheader("💡 Quick Actions")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📋 Total Sales"):
        handle_quick_question("Show me the total sales table by date")
with col2:
    if st.button("⚠️ Stock Alert"):
        handle_quick_question(
            "Which products have low stock, quantity, and what are their categories?"
        )
with col3:
    if st.button("🏆 Top Managers"):
        handle_quick_question("Who are the managers of the stores with most sales?")

st.divider()

# 9. CHAT HISTORY DISPLAY
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 10. CHAT INPUT
if prompt := st.chat_input("Ask about products, sales, or managers..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching database..."):
            response = agent_executor.invoke({"input": prompt})
            full_response = response["output"]
            st.markdown(full_response)

            # Optional: Automatic Charting logic for manual input
            if "chart" in prompt.lower() or "graph" in prompt.lower():
                try:
                    # Basic sales chart logic
                    query = "SELECT date, SUM(quantity * sale_price) as total FROM fact_sales s JOIN dim_products p ON s.product_id = p.product_id GROUP BY date"
                    df = pd.read_sql(query, db_engine)
                    st.line_chart(df.set_index("date"))
                except:
                    st.warning("I couldn't generate a chart for this specific request.")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
