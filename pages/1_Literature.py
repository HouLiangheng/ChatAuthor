import streamlit as st
from pages.toolbox import call_openai, read_prompt
import time


# 设置页面配置
st.set_page_config(page_title="文字分析与作家对话", layout="wide")

# 在CSS样式部分修改如下内容
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
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": "你好！请输入你的文字或喜欢的句子，我会帮你分析风格并匹配相似的作家。",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

if "current_writer" not in st.session_state:
    st.session_state.current_writer = None

if "writer_info" not in st.session_state:
    st.session_state.writer_info = None

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# 创建两列布局
col1, col2 = st.columns([7, 3])

with col2:
    st.markdown("### 功能说明")
    st.markdown("""
    1. 输入文字进行分析
    2. 系统判断是否为已发表作品
    3. 匹配相似作家风格
    4. 与作家进行对话交流
    """)

    # 如果已经有了作家信息，显示作家简介
    if st.session_state.writer_info:
        st.markdown("### 当前作家信息")
        st.markdown(f'<div class="writer-info">{st.session_state.writer_info}</div>', unsafe_allow_html=True)

    if st.button("清除对话记录"):
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": "你好！请输入你的文字或喜欢的句子，我会帮你分析风格并匹配相似的作家。",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }]
        st.session_state.current_writer = None
        st.session_state.writer_info = None
        st.session_state.analysis_done = False
        st.rerun()

with col1:
    st.title("文字分析与作家对话")

    # 显示聊天历史
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.chat_history:
            st.markdown(f'<div class="timestamp">{message["timestamp"]}</div>', unsafe_allow_html=True)
            bubble_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
            st.markdown(f'<div class="{bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="clearfix"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 输入区域
    with st.container():
        if not st.session_state.analysis_done:
            text_input = st.text_area("输入文字", key="text_input", height=100)
            analyze_button = st.button("分析", use_container_width=True)

            if text_input and analyze_button:
                # 添加用户输入到历史记录
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": text_input,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

                with st.spinner("分析中..."):
                    # 步骤1：判断是否是已发表作品
                    identification_prompt = read_prompt('pages/prompt/existing_writing.txt')
                    
                    identification_result = call_openai(
                        messages=[
                            {"role": "system", "content": identification_prompt},
                            {"role": "user", "content": text_input}
                        ]
                    )
                    if "原创文字" in identification_result:
                        # 步骤2：进行风格分析和作家匹配
                        analysis_prompt = read_prompt('pages/prompt/writing_style.txt')

                        analysis_response = call_openai(
                            messages=[
                                {"role": "system", "content": analysis_prompt},
                                {"role": "user", "content": text_input}
                            ]
                        )
                        analysis_result = analysis_response.choices[0].message.content

                        # 分离作家信息和分析结果
                        parts = analysis_result.split("[WRITER_INFO]")
                        analysis_text = parts[0].strip()
                        writer_info = parts[1].strip() if len(parts) > 1 else ""

                        # 保存作家信息
                        st.session_state.writer_info = writer_info
                        st.session_state.analysis_done = True

                        # 添加分析结果到对话
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": analysis_text + "\n\n现在你可以开始与这位作家对话了。",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                    else:
                        analysis_prompt = read_prompt('pages/prompt/writer_info.txt')
                        
                        analysis_result = call_openai(
                            messages=[
                                {"role": "system", "content": analysis_prompt},
                                {"role": "user", "content": text_input}
                            ]
                        )

                        # 提取作家信息
                        parts = analysis_result.split("[WRITER_INFO]")
                        writer_info = parts[1].strip() if len(parts) > 1 else ""

                        # 保存作家信息并设置分析完成状态
                        st.session_state.writer_info = writer_info
                        st.session_state.analysis_done = True

                        # 添加分析结果到对话
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"这是一段已发表的作品：\n\n{identification_result}\n\n现在你可以开始与这位作家对话了。",
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        })

                st.rerun()
        else:
            # 与作家对话模式
            chat_input = st.text_input("与作家对话", key="chat_input")
            if st.button("发送", use_container_width=True) and chat_input:
                # 添加用户输入到历史记录
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": chat_input,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

                # 生成作家回复
                # 在生成作家回复的部分，修改writer_prompt：
                writer_prompt = read_prompt('pages/prompt/cosplay.txt')

                with st.spinner("思考中..."):
                    # 获取历史对话记录（最近的5轮）用于上下文
                    recent_history = st.session_state.chat_history[-10:]
                    messages = [{"role": "system", "content": writer_prompt}]

                    # 添加历史对话作为上下文
                    for msg in recent_history:
                        if msg["role"] == "user":
                            messages.append({"role": "user", "content": msg["content"]})
                        elif msg["role"] == "assistant":
                            messages.append({"role": "assistant", "content": msg["content"]})

                    # 添加当前问题
                    messages.append({"role": "user", "content": chat_input})

                    writer_reply = call_openai(messages=messages, temperature=0.7)

                    # 添加作家回复到对话
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": writer_reply,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })

                st.rerun()
