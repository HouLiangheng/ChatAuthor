from openai import AzureOpenAI
import streamlit as st
import base64
# 设置API客户端
client = AzureOpenAI(
    azure_endpoint="https://hkust.azure-api.net",
    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01"
)

def read_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
def call_openai(messages, temperature=None):
    try:
        if temperature is None:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=temperature
            )

        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return ""
    
def encode_image(image_path):
#   with open(image_path, "rb") as image_file:
    return base64.b64encode(image_path.read()).decode('utf-8')