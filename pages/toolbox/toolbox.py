from openai import AzureOpenAI
import streamlit as st
import base64
import requests
import time
import asyncio
import websockets
import json

# 设置API客户端
client = AzureOpenAI(
    azure_endpoint="https://hkust.azure-api.net",
    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01"
)

tripo3d_api_key = st.secrets["TRIPO3D_API_KEY"]
tripo3d_url = "https://api.tripo3d.ai/v2/openapi/task"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {tripo3d_api_key}"
}


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

def call_tripo3d(prompt):
    data = {
        "type": "text_to_model",
        "prompt": prompt
    }

    response = requests.post(tripo3d_url, headers=headers, json=data)

    return response.json()




async def get_tripo3d_result(tid):
  url = f"wss://api.tripo3d.ai/v2/openapi/task/watch/{tid}"
  headers = {
      "Authorization": f"Bearer {tripo3d_api_key}"
  }
  async with websockets.connect(url, additional_headers=headers) as websocket:
      while True:
          message = await websocket.recv()
          try:
              data = json.loads(message)
              status = data['data']['status']
              if status not in ['running', 'queued']:
                  break
          except json.JSONDecodeError:
              print("Received non-JSON message:", message)
              break
  return data

