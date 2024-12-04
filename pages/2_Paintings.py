import streamlit as st
import base64
import requests
from openai import AzureOpenAI

# 设置页面配置
st.set_page_config(page_title="图片分析", layout="wide")

# 初始化会话状态
if "image_history" not in st.session_state:
    st.session_state.image_history = []

# 设置API客户端
client = AzureOpenAI(
    azure_endpoint="https://hkust.azure-api.net",
    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01"
)


# Function to encode the image from bytes
def encode_image_from_bytes(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')


# 主界面
st.title("图片艺术风格分析")

uploaded_file = st.file_uploader("上传图片", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # 显示上传的图片
    st.image(uploaded_file, caption="上传的图片")

    # 获取图片字节数据
    bytes_data = uploaded_file.getvalue()
    base64_image = encode_image_from_bytes(bytes_data)

    # GPT-4V 配置
    headers = {
        "Content-Type": "application/json",
        "api-key": st.secrets["AZURE_OPENAI_API_KEY"]
    }

    if st.button("分析图片"):
        with st.spinner("正在分析中..."):
            vision_payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """作为一位专业的艺术评论家，请分析这幅图片的艺术风格，从以下几个方面进行：
                                1. 这个作品像哪位艺术家的风格
                                2. 最像哪一个具体的作品
                                3. 在哪些方面最为相似（包括构图、色彩、笔触等）
                                4. 作品表达的含义和情感
                                请详细说明你的分析理由。"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }

            vision_response = requests.post(
                "https://hkust.azure-api.net/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-06-01",
                headers=headers,
                json=vision_payload
            )

            if vision_response.status_code == 200:
                analysis = vision_response.json()['choices'][0]['message']['content']

                # 创建对话框显示分析结果
                with st.chat_message("assistant"):
                    st.write(analysis)

                # 添加到对话历史
                st.session_state.image_history.append({
                    "analysis": analysis
                })
            else:
                st.error(f"分析错误: {vision_response.status_code}")
                st.error(vision_response.text)

# 显示历史记录
if st.session_state.image_history:
    st.divider()
    st.subheader("历史分析记录")
    for i, entry in enumerate(reversed(st.session_state.image_history)):
        with st.chat_message("assistant"):
            st.write(f"**分析 {len(st.session_state.image_history) - i}：**")
            st.write(entry['analysis'])

    # 添加清除历史记录的按钮
    if st.button("清除历史记录"):
        st.session_state.image_history = []
        st.experimental_rerun()