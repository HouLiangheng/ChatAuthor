from openai import AzureOpenAI
import streamlit as st

# 设置API客户端
client = AzureOpenAI(
    azure_endpoint="https://hkust.azure-api.net",
    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01"
)

def read_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()