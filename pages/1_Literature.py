import streamlit as st
from pages.toolbox import client, read_prompt
import time

identification_prompt = read_prompt('pages/prompt/existing_writing.txt')
writer_prompt = read_prompt('pages/prompt/cosplay.txt')

# 设置页面配置
st.set_page_config(page_title="文字分析与作家对话", layout="wide")


# 在CSS样式部分修改如下内容
st.markdown("""
<link rel="stylesheet" href="pages/styles/main.css">
<script src="pages/scripts/theme.js"></script>
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
                    # identification_prompt = """
                    # 请判断以下文字是否是已发表的文学作品。如果是，请提供：
                    # 1. 作品名称
                    # 2. 作者
                    # 3. 发表时间
                    # 4. 出处
                    # 如果不是已发表作品，请回复："原创文字，需要进行风格分析"
                    # """

                    identification_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": identification_prompt},
                            {"role": "user", "content": text_input}
                        ]
                    )
                    identification_result = identification_response.choices[0].message.content

                    if "原创文字" in identification_result:
                        # 步骤2：进行风格分析和作家匹配
                        # analysis_prompt = """
                        # 请详细分析这段文字的写作风格，并：
                        # 1. 找出最相似的作家（限定1位）
                        # 2. 分析相似之处（包括主题、意象、语言特点等）
                        # 3. 生成这位作家的详细信息（生平、创作特点、代表作品）
                        # 请对输入的文字进行全面分析，按以下结构组织回答：
                    
                        # 请详细分析文字风格特点，包括：
                        # - 写作手法和语言特色
                        # - 情感表达方式
                        # - 主题意象特点
                        # - 最相似的作家（限定1位）及相似之处
                        
                        # [WRITER_INFO]
                        # 关于这位作家：
                        # - 基本信息和主要成就
                        # - 创作特点和代表作品
                        # - 具体说明为什么这段文字与该作家风格相似
                        # - 举例说明最具代表性的对应特征
                        
                        # 请用自然流畅的语言表述，避免生硬的条目式陈述。
                        # """
                        analysis_prompt = read_prompt('pages/prompt/writing_style.txt')

                        analysis_response = client.chat.completions.create(
                            model="gpt-4o",
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
                        # analysis_prompt = f"""
                        # 基于这个已发表作品的信息：
                        # {identification_result}
    
                        # 请生成关于这位作者的详细信息，按以下结构组织：
                        # [WRITER_INFO]
                        # 关于这位作家：
                        # - 基本信息和主要成就
                        # - 创作特点和代表作品
                        # - 写作风格特征
                        # - 思想内涵特点
    
                        # 请用自然流畅的语言表述，避免生硬的条目式陈述。
                        # """
                        analysis_prompt = read_prompt('pages/prompt/writer_info.txt')
                        
                        analysis_response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": analysis_prompt},
                                {"role": "user", "content": text_input}
                            ]
                        )
                        analysis_result = analysis_response.choices[0].message.content

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
                # writer_prompt = f"""
                # 你现在扮演{st.session_state.writer_info}中描述的这位作家。请严格按照以下要求回答：

                # 角色要求：
                # 1. 完全沉浸在这位作家的时代背景中，只谈论在他/她生平年代内发生的事
                # 2. 使用符合那个时代的用语和表达方式
                # 3. 只能引用以下内容：
                #    - 自己的作品
                #    - 同时代认识的作家的作品
                #    - 在自己生平年代前的古籍或作品
                # 4. 不能提及或评论在自己去世之后发生的事件

                # 回答要求：
                # 1. 在回答中自然融入自己的作品片段或诗句（如果是诗人的话）
                # 2. 谈吐要符合自己的性格特征和思想倾向
                # 3. 可以提及自己的创作经历和生活经历
                # 4. 可以分享与其他作家的交往经历（仅限同时代认识的作家）
                # 5. 适时表达自己的创作理念和文学主张

                # 特别注意：
                # - 始终保持在自己生平年代的视角
                # - 对于超出生平年代的问题，可以礼貌表示"这已经超出了我的年代"
                # - 表达方式要符合作家的文风和语言特色

                # 用户的问题是：{chat_input}
                # """

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

                    writer_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        temperature=0.7  # 适当增加创造性，但不要太过随意
                    )

                    writer_reply = writer_response.choices[0].message.content

                    # 添加作家回复到对话
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": writer_reply,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })

                st.rerun()
