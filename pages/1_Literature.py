import streamlit as st
from openai import AzureOpenAI
import time

# 设置页面配置
st.set_page_config(page_title="文字分析与作家对话", layout="wide")


st.markdown("""
<style>
    /* 移除标题下方的默认边距 */
    .stTitle {
        margin-bottom: 0 !important;
    }

    /* 聊天气泡样式 */
    .user-bubble {
        background-color: #95EC69;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        float: right;
        clear: both;
    }

    .assistant-bubble {
        background-color: white;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        float: left;
        clear: both;
    }


    /* 时间戳样式 */
    .timestamp {
        color: #999;
        font-size: 12px;
        text-align: center;
        margin: 10px 0;
        clear: both;
    }

    /* 清除浮动 */
    .clearfix {
        clear: both;
        display: block;
        content: "";
    }

    /* 作家信息卡片样式 */
    .writer-info {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    /* 输入区域样式 */
    .stTextArea textarea {
        border-radius: 10px;
    }

    /* 按钮样式 */
    .stButton button {
        border-radius: 20px;
        background-color: #07C160;
        color: white;
    }

    /* 自定义功能说明区域样式 */
    .function-desc {
        background-color: #F7F7F7;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
</style>
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

# 设置API客户端
client = AzureOpenAI(
    azure_endpoint="https://hkust.azure-api.net",
    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01"
)

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
                    identification_prompt = """
                    请判断以下文字是否是已发表的文学作品。如果是，请提供：
                    1. 作品名称
                    2. 作者
                    3. 发表时间
                    4. 出处
                    如果不是已发表作品，请回复："原创文字，需要进行风格分析"
                    """

                    identification_response = client.chat.completions.create(
                        model="gpt-35-turbo",
                        messages=[
                            {"role": "system", "content": identification_prompt},
                            {"role": "user", "content": text_input}
                        ]
                    )
                    identification_result = identification_response.choices[0].message.content

                    if "原创文字" in identification_result:
                        # 步骤2：进行风格分析和作家匹配
                        analysis_prompt = """
                        请详细分析这段文字的写作风格，并：
                        1. 找出最相似的作家（限定1位）
                        2. 分析相似之处（包括主题、意象、语言特点等）
                        3. 生成这位作家的详细信息（生平、创作特点、代表作品）
                        请将回答分为两部分：
                        第一部分：
                        风格分析和相似度说明
                        第二部分：
                        作家信息（用[WRITER_INFO]标记开始）
                        说明作家的基本信息和在什么情况下和这段文字最匹配。
                        """

                        analysis_response = client.chat.completions.create(
                            model="gpt-35-turbo",
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
                        # 如果是已发表作品，显示作品信息
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"这是一段已发表的作品：\n\n{identification_result}",
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
                writer_prompt = f"""
                你现在扮演之前分析中提到的作家。请以该作家的风格、语气和思维方式回答用户的问题。
                注意：
                1. 保持作家的写作风格和语言特点
                2. 基于作家的思想和创作理念回答
                3. 可以引用作家的作品片段
                4. 表现作家的性格特征

                用户的问题是：{chat_input}
                """

                with st.spinner("思考中..."):
                    writer_response = client.chat.completions.create(
                        model="gpt-35-turbo",
                        messages=[
                            {"role": "system", "content": writer_prompt},
                            {"role": "user", "content": chat_input}
                        ]
                    )

                    writer_reply = writer_response.choices[0].message.content

                    # 添加作家回复到对话
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": writer_reply,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })

                st.rerun()
