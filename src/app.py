import streamlit as st
import pandas as pd
import plotly.express as px
from database import setup_database  # Import the setup_database function
from agent import create_retail_agent  # Import the agent creation function

# 1. Professional Page Setup

st.set_page_config(page_title="Retail Insights AI", layout="wide", page_icon="📈")

st.markdown(
    """
    <style>
    .main { background-color: #fcfcfc; }
    .stButton>button {
        border-radius: 10px;
        height: 3.5em;
        background-color: white;
        border: 1px solid #e0e0e0;
        transition: 0.3s;
        font-weight: bold;
    }
    .stButton>button:hover {
        border-color: #4A90E2;
        background-color: #f0f7ff;
        color: #4A90E2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# 2. System Initialization
@st.cache_resource
def get_agent():
    db_engine = setup_database()
    return create_retail_agent(db_engine), db_engine


agent_executor, db_engine = get_agent()

# 3. Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3094/3094851.png", width=80)
    st.title("Admin Panel")
    st.success("Database Connected")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.pending_query = None
        st.rerun()
    st.divider()
    st.info("System: Llama-3.3 + LangChain Agent")

# 4. Header Section
st.title("📊 Retail Intelligence Agent")
st.markdown("Empowering retail decisions through AI-driven data exploration.")

# 5. Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Quick Action Buttons
st.write("### 💡 Quick Actions")
cols = st.columns(3)
quick_queries = [
    {"label": "📈 Daily Sales Trend", "q": "Show daily sales trend in a line chart"},
    {
        "label": "📊 Category Insights",
        "q": "Show a list of the top selling product categories for the top performing managers, including their store city and total profit.",
    },
    {
        "label": "🏆 Top Managers",
        "q": "Show top managers by total profit in a bar chart",
    },
]

for i, q in enumerate(quick_queries):
    if cols[i].button(q["label"]):
        st.session_state.pending_query = q["q"]
        st.rerun()

# 7. Main Query Input
prompt = st.chat_input("Ask about sales, stock, or performance...")

query_to_run = None
if st.session_state.pending_query:
    query_to_run = st.session_state.pending_query
    st.session_state.pending_query = None
elif prompt:
    query_to_run = prompt

if query_to_run:
    st.session_state.messages.append({"role": "user", "content": query_to_run})
    with st.chat_message("user"):
        st.markdown(query_to_run)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data infrastructure..."):
            try:
                res = agent_executor.invoke({"input": query_to_run})
                output = res["output"]
                st.markdown(output)

                # --- ENHANCED VISUALIZATION ENGINE ---
                q_lower = query_to_run.lower()

                # Only visualize if explicit keywords are present (avoiding ghost charts for single item queries)
                visual_keywords = [
                    "chart",
                    "graph",
                    "plot",
                    "trend",
                    "visualize",
                    "ranking",
                    "bar chart",
                    "line chart",
                ]
                should_visualize = any(word in q_lower for word in visual_keywords)

                if should_visualize:
                    st.divider()
                    st.subheader("Visual Analysis")

                    # 1. Sales Trend
                    if "sales" in q_lower or "trend" in q_lower:
                        sql = "SELECT date, SUM(quantity * sale_price) as total_sales FROM fact_sales fs JOIN dim_products dp ON fs.product_id = dp.product_id GROUP BY date ORDER BY date"
                        df = pd.read_sql(sql, db_engine)
                        if not df.empty:
                            fig = px.line(
                                df,
                                x=df.columns[0],
                                y=df.columns[1],
                                title="Daily Sales Performance",
                                labels={
                                    df.columns[1]: "Revenue ($)",
                                    df.columns[0]: "Date",
                                },
                                markers=True,
                                template="plotly_white",
                            )
                            # fig.update_traces(line_color='#4A90E2', line_width=3)
                            st.plotly_chart(fig, use_container_width=True)

                    # 2. Stock Levels (Red for critical)
                    elif "category" in q_lower:
                        sql = """
                            SELECT dp.category, ds.city, SUM((dp.sale_price - dp.cost) * fs.quantity) as profit
                            FROM fact_sales fs
                            JOIN dim_products dp ON fs.product_id = dp.product_id
                            JOIN dim_stores ds ON fs.store_id = ds.store_id
                            GROUP BY dp.category, ds.city ORDER BY profit DESC
                        """
                        df = pd.read_sql(sql, db_engine)
                        if not df.empty:
                            # Gráfico de barras desglosado por ciudad para mayor detalle
                            fig = px.bar(
                                df,
                                x="category",
                                y="profit",
                                color="city",
                                barmode="group",
                                title="Profit by Category and City",
                                color_discrete_sequence=px.colors.qualitative.Prism,
                            )
                            st.plotly_chart(fig, use_container_width=True)

                    # 3. Manager Profit (Multiple tables join)
                    elif "manager" in q_lower:
                        sql = """
                            SELECT ds.manager, SUM((dp.sale_price - dp.cost) * fs.quantity) as total_profit
                            FROM fact_sales fs
                            JOIN dim_products dp ON fs.product_id = dp.product_id
                            JOIN dim_stores ds ON fs.store_id = ds.store_id
                            GROUP BY ds.manager ORDER BY total_profit DESC
                        """
                        df = pd.read_sql(sql, db_engine)
                        if not df.empty:
                            fig = px.bar(
                                df,
                                x="manager",
                                y="total_profit",
                                title="Total Profit by Store Manager",
                                labels={
                                    "total_profit": "Profit ($)",
                                    "manager": "Manager",
                                },
                                color="total_profit",
                                color_continuous_scale="Bluered_r",
                            )
                            fig.update_layout(coloraxis_showscale=False)
                            st.plotly_chart(fig, use_container_width=True)

                st.session_state.messages.append(
                    {"role": "assistant", "content": output}
                )

            except Exception as e:
                st.error(f"Analytical Exception: {str(e)}")
