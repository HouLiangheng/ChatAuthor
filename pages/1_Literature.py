import streamlit as st
from openai import AzureOpenAI
import time

# 设置页面配置
st.set_page_config(page_title="文字分析", layout="wide")

# 自定义CSS样式
st.markdown("""
<style>
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
    /* 聊天容器样式 */
    .chat-container {
        background-color: #F0F2F5;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        min-height: 400px;
        overflow-y: auto;
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
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # 添加欢迎消息
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": "你好！我是你的文学风格分析助手。请输入任何文字，我会帮你分析它的写作风格和可能的文学影响。",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

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
    1. 输入任何文字进行分析
    2. 系统会判断是否为已发表作品
    3. 提供详细的风格分析
    4. 建议相似作品参考
    """)

    # 添加清除历史记录的按钮
    if st.button("清除聊天记录"):
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": "你好！我是你的文学风格分析助手。请输入任何文字，我会帮你分析它的写作风格和可能的文学影响。",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }]
        st.rerun()

with col1:
    st.title("文字风格分析")

    # 显示聊天历史
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.chat_history:
            # 添加时间戳
            st.markdown(f'<div class="timestamp">{message["timestamp"]}</div>', unsafe_allow_html=True)

            # 根据角色使用不同的气泡样式
            bubble_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
            st.markdown(f'<div class="{bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="clearfix"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 输入区域
    with st.container():
        text_input = st.text_area("输入文字", key="text_input", height=100)
        col1, col2, col3 = st.columns([6, 2, 2])
        with col2:
            analyze_button = st.button("分析", use_container_width=True)

    if text_input and analyze_button:
        # 添加用户输入到历史记录
        st.session_state.chat_history.append({
            "role": "user",
            "content": text_input,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

        # 判断是否是已发表的作品
        identification_prompt = """
        你是一个知道所有国家文学作品的搜索引擎，请判断以下文字是否是知名文学作品。
        如果是文学作品，请指出：
        1. 作品名称
        2. 作者
        3. 发表时间
        4. 出处

        如果确定不是为已发表作品，请回答："需要进行风格分析"。
        请仅回答上述信息，不要做任何风格分析。
        """

        with st.spinner("分析中..."):
            identification_response = client.chat.completions.create(
                model="gpt-35-turbo",
                messages=[
                    {"role": "system", "content": identification_prompt},
                    {"role": "user", "content": text_input}
                ],
                max_tokens=1000,
                temperature=0.3
            )

            identification_result = identification_response.choices[0].message.content

            if "需要进行风格分析" in identification_result:
                style_prompt = """
                你是一个读过大量文学作品的文学爱好者，需要帮我找到所有与输入文字有共鸣的作者：

                请从以下几个方面进行分析:
                1. 这段文字讨论的"主题"；哪些其他作家也讨论过类似的主题
                2. 其中表达的"意向"与哪个作家类似，类似的地方是
                3. 如果这位作家与我就这段文字进行讨论，你觉得他会说什么

                请用对话的语气详细说明你的分析理由。
                """

                style_response = client.chat.completions.create(
                    model="gpt-35-turbo",
                    messages=[
                        {"role": "system", "content": style_prompt},
                        {"role": "user", "content": text_input}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                analysis = style_response.choices[0].message.content
            else:
                analysis = identification_result

            # 添加助手回复到历史记录
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": analysis,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

        # 清空输入框并刷新页面
        st.rerun()