# cloud_cost_comparator_groq.py

import streamlit as st
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.tools import tool
from langchain_groq import ChatGroq
import os

# Set Groq API key
os.environ["GROQ_API_KEY"] = "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"

#############################
# 🔧 Define Tool Functions  #
#############################

@tool
def compare_aws_azure(instance_type: str, region: str, storage_gb: int) -> str:
    """Compare pricing between AWS and Azure for a given instance type, region, and storage in GB.
    Note: This is a mock function. Replace with real API logic if needed.
    """
    aws_base_price = 0.1  # per hour
    azure_base_price = 0.12
    aws_storage_price = 0.10  # per GB
    azure_storage_price = 0.095

    aws_total = aws_base_price + (aws_storage_price * storage_gb / 100)
    azure_total = azure_base_price + (azure_storage_price * storage_gb / 100)

    return (
        f"AWS ({region}): ${aws_total:.4f}/hr for {instance_type} + {storage_gb}GB\n"
        f"Azure ({region}): ${azure_total:.4f}/hr for {instance_type} + {storage_gb}GB\n"
        f"💡 Recommendation: {'AWS' if aws_total < azure_total else 'Azure'} is cheaper"
    )

##########################
# 🤖 LangChain + Groq Init #
##########################

llm = ChatGroq(
    model="llama3-70b-8192",

    temperature=0
)

tools = [compare_aws_azure]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

##########################
# 🌐 Streamlit Frontend  #
##########################

st.set_page_config(page_title="Cloud Cost Comparison Assistant", page_icon="☁️")

st.title("☁️ Cloud Cost Comparison Assistant (Groq + LangChain)")
st.write("Compare pricing between AWS and Azure based on instance type, region, and storage.")

with st.form("comparison_form"):
    instance_type = st.text_input("Instance Type (e.g., t3.medium)", "t3.medium")
    region = st.text_input("Region (e.g., us-east-1)", "us-east-1")
    storage_gb = st.number_input("Storage (GB)", min_value=10, max_value=1000, value=100)

    submitted = st.form_submit_button("Compare")

    if submitted:
        user_query = f"Compare pricing for {instance_type} in {region} with {storage_gb}GB storage."
        response = agent.run(user_query)
        st.markdown("### 📊 Result")
        st.text(response)
