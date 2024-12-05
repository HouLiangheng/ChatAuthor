import streamlit as st
from pages.toolbox.toolbox import call_openai, read_prompt
import time
from PIL import Image
import io

# 设置页面配置
st.set_page_config(page_title="图像分析与画家对话", layout="wide")

# CSS和JS保持不变
with open('pages/styles/main.css', 'r', encoding='utf-8') as css_file:
    css_content = css_file.read()

with open('pages/scripts/theme.js', 'r', encoding='utf-8') as js_file:
    js_content = js_file.read()

st.markdown(f"""
<style>
{css_content}
</style>

<script>
{js_content}
</script>
""", unsafe_allow_html=True)

# 初始化会话状态
if "paintings_chat_history" not in st.session_state:
    st.session_state.paintings_chat_history = []
    st.session_state.paintings_chat_history.append({
        "role": "assistant",
        "content": "你好！请上传一张图片，我会帮你分析画作风格并匹配相似的画家<br>Hello! Please upload an image and I will help you analyze the style of the painting and match it with similar painters.",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

if "current_artist" not in st.session_state:
    st.session_state.current_artist = None

if "artist_info" not in st.session_state:
    st.session_state.artist_info = None

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# 创建两列布局
col1, col2 = st.columns([7, 3])

with col2:
    # 如果已经有了画家信息，显示画家简介
    if st.session_state.artist_info:
        st.markdown("### 当前画家信息")
        st.markdown(f'<div class="writer-info">{st.session_state.artist_info}</div>', unsafe_allow_html=True)

with col1:
    st.title("图像分析与画家对话")

    # 显示聊天历史
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.paintings_chat_history:
            st.markdown(f'<div class="timestamp">{message["timestamp"]}</div>', unsafe_allow_html=True)
            bubble_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
            if "image_data" in message:
                st.markdown(f'<div class="{bubble_class}">', unsafe_allow_html=True)
                st.image(message["image_data"], width=300)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="{bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="clearfix"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 输入区域
    with st.container():
        if not st.session_state.analysis_done:
            uploaded_file = st.file_uploader("上传图片", type=['png', 'jpg', 'jpeg'])
            analyze_button = st.button("分析", use_container_width=True)

            if uploaded_file and analyze_button:
                # 读取图片数据
                image_data = uploaded_file.getvalue()

                # 添加用户上传的图片到历史记录
                st.session_state.paintings_chat_history.append({
                    "role": "user",
                    "content": "上传了一张图片",
                    "image_data": image_data,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

                with st.spinner("分析中..."):
                    # 分析图片风格和匹配画家
                    analysis_prompt = read_prompt('pages/prompt/art_style.txt')  # 需要创建新的艺术风格分析提示

                    # 这里需要使用支持图像分析的API
                    analysis_result = call_openai(
                        messages=[
                            {"role": "system", "content": analysis_prompt},
                            {"role": "user", "content": "分析这张图片的艺术风格"}
                        ],
                        image = image_data  # 需要修改API调用以支持图像输入
                    )

                    # 分离画家信息和分析结果
                    parts = analysis_result.split("[ARTIST_INFO]")
                    analysis_text = parts[0].strip()
                    artist_info = parts[1].strip() if len(parts) > 1 else ""

                    # 保存画家信息
                    st.session_state.artist_info = artist_info
                    st.session_state.analysis_done = True

                    # 添加分析结果到对话
                    st.session_state.paintings_chat_history.append({
                        "role": "assistant",
                        "content": analysis_text + "\n\n现在你可以开始与这位画家对话了。",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })

                st.rerun()
        else:
            # 与画家对话模式
            chat_input = st.text_input("与画家对话", key="chat_input")

            if st.button("发送", use_container_width=True) and chat_input:
                # 添加用户输入到历史记录
                st.session_state.paintings_chat_history.append({
                    "role": "user",
                    "content": chat_input,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

                # 生成画家回复
                artist_prompt = read_prompt('pages/prompt/artist_cosplay.txt')  # 需要创建新的画家角色扮演提示

                with st.spinner("思考中..."):
                    # 获取历史对话记录
                    recent_history = st.session_state.paintings_chat_history[-10:]
                    messages = [{"role": "system", "content": artist_prompt}]

                    for msg in recent_history:
                        if msg["role"] == "user":
                            messages.append({"role": "user", "content": msg["content"]})
                        elif msg["role"] == "assistant":
                            messages.append({"role": "assistant", "content": msg["content"]})

                    artist_reply = call_openai(messages=messages, temperature=0.7)

                    # 添加画家回复到对话
                    st.session_state.paintings_chat_history.append({
                        "role": "assistant",
                        "content": artist_reply,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })

                st.rerun()

            if st.button("清除对话记录", use_container_width=True):
                st.session_state.paintings_chat_history = [{
                    "role": "assistant",
                    "content": "你好！请上传一张图片，我会帮你分析画作风格并匹配相似的画家<br>Hello! Please upload an image and I will help you analyze the style of the painting and match it with similar painters.",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }]
                st.session_state.current_artist = None
                st.session_state.artist_info = None
                st.session_state.analysis_done = False
                st.rerun()