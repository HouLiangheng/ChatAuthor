import streamlit as st
from openai import AzureOpenAI

# 设置页面配置
st.set_page_config(page_title="文字分析", layout="wide")

# 初始化会话状态
if "text_history" not in st.session_state:
    st.session_state.text_history = []

# 设置API客户端
client = AzureOpenAI(
    azure_endpoint="https://hkust.azure-api.net",
    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01"
)

# 主界面
st.title("文字风格分析")

text_input = st.text_area("输入要分析的文字", height=200)

if text_input and st.button("分析文字风格"):
    # 首先判断是否是已发表的作品
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

    # 在对话框中显示结果
    with st.chat_message("assistant"):
        if "需要进行风格分析" in identification_result:
            style_prompt = """
            你是一个读过大量文学作品的文学爱好者，需要帮我找到所有与输入文字有共鸣的作者：

            再请从以下几个方面进行分析:
            1.这段文字讨论的"主题"；哪些其他作家也讨论过类似的主题
            2.其中表达的"意向"与哪个作家类似，类似的地方是
            3.如果这位作家与我就这段文字进行讨论，你觉得他会说什么
            请详细说明你的分析理由。
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
            st.write(analysis)
        else:
            analysis = identification_result
            st.write(analysis)

        # 添加到对话历史
        st.session_state.text_history.append({
            "text": text_input,
            "analysis": analysis
        })

# 显示历史记录
if st.session_state.text_history:
    st.divider()
    st.subheader("历史分析记录")
    for i, entry in enumerate(reversed(st.session_state.text_history)):
        with st.chat_message("assistant"):
            st.write(f"**分析 {len(st.session_state.text_history) - i}：**")
            st.write("**输入文本：**")
            st.write(entry['text'])
            st.write("**分析结果：**")
            st.write(entry['analysis'])

    # 添加清除历史记录的按钮
    if st.button("清除历史记录"):
        st.session_state.text_history = []
        st.experimental_rerun()