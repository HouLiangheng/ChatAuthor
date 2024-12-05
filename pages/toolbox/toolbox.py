from openai import AzureOpenAI
import streamlit as st
import base64
import requests
import time
import asyncio
import websockets
import json
from io import BytesIO
from PIL import Image

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

def get_tripo3d_result_polling(tid):
    url = f"https://api.tripo3d.ai/v2/openapi/task/{tid}"
    response = requests.get(url, headers=headers)
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

def process_and_save_image(result):
    try:
        image_url = result['data']['result']['rendered_image']['url']
        print(f"Downloading image from: {image_url}")

        response = requests.get(image_url)
        if response.status_code == 200:
            # 从二进制数据加载图片
            image = Image.open(BytesIO(response.content))

            # 获取非透明区域的边界框
            if image.mode in ('RGBA', 'LA'):
                # 获取alpha通道
                alpha = image.split()[-1]
                # 获取非透明像素的边界框
                bbox = alpha.getbbox()
                if bbox:
                    # 裁剪到主体区域
                    image = image.crop(bbox)

            # 计算新的尺寸（放大1.5倍）
            new_size = (int(image.size[0] * 2), int(image.size[1] * 2))
            # 使用LANCZOS重采样方法放大图像
            image = image.resize(new_size, Image.Resampling.LANCZOS)

            # 创建一个更大的黑色背景（为了保持居中，加上额外的边距）
            padding = 100  # 可以调整这个值来改变边距
            background_size = (image.size[0] + padding * 2, image.size[1] + padding * 2)
            background = Image.new('RGB', background_size, (0, 0, 0))

            # 将放大后的图像粘贴到背景中央
            paste_position = ((background_size[0] - image.size[0]) // 2,
                              (background_size[1] - image.size[1]) // 2)

            if image.mode in ('RGBA', 'LA'):
                background.paste(image, paste_position, mask=image.convert('RGBA').split()[-1])
            else:
                background.paste(image, paste_position)

            return background
        else:
            print(f"Failed to download image: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def get_character_description(name):
    """使用现有的GPT接口获取人物描述"""
    prompt = f"""请详细分析历史人物"{name}",然后生成对应的人物头像prompt，按以下JSON格式返回（不要添加任何其他内容）：
    {{
        "name": "人物名",
        "gender": "性别（男性/女性）",
        "era": "所处年代",
        "age": "最著名时期的年龄段（年轻/中年/老年）",
        "title": "称号或职位",
        "appearance": "面部特征",,
        "style": "整体风格特征",
        "additional": "其他特征"
    }}
    """

    messages = [{"role": "user", "content": prompt}]
    response = call_openai(messages)
    response = response.strip()  # Remove leading/trailing whitespace
    response = response.replace("```json", "").replace("```", "")  # Remove markdown code blocks
    
    try:
        # First try to parse as JSON
        return json.loads(response)
    except json.JSONDecodeError as e:
        try:
            print(f"JSON parsing failed: {e}")
            # If JSON parsing fails, try cleaning the string further
            response = response.replace("'", '"')  # Replace single quotes with double quotes
            return json.loads(response)
        except Exception as e:
            print(f"All parsing attempts failed: {e}")
            print("无法解析GPT API的返回内容")
            return {}
        
def build_prompt(char_info):
    """构建Stable Diffusion的提示词"""
    prompt = f"""超写实古代人物头像，{char_info['name']}，
    {char_info['era']}时期的{char_info['title']}，
    {char_info['age']}的{char_info['gender']}，
    面部特征：{char_info['appearance']}，
    整体风格：{char_info['style']}"""

    return prompt

def generate_icon(writer):
    char_info = get_character_description(writer)
    if char_info:
        prompt = build_prompt(char_info)
        count = 0
        image = None
        response = call_tripo3d(prompt)
        while True:
            count += 1
            result = get_tripo3d_result_polling(response['data']['task_id'])
            print(result)
            print(type(result))
            print(count)

            if isinstance(result, dict):
                data = result
            else:
                try:
                    data = json.loads(result)
                except json.JSONDecodeError:
                    print("Received non-JSON message:", result)
                    break
            
            status = data['data']['status']
            print(status)
            if status not in ['running', 'queued']:
                break
        image = process_and_save_image(data)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    else:
        return None
