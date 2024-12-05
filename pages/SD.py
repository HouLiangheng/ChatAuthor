import streamlit as st
import replicate
import os
from PIL import Image
import requests
from io import BytesIO
from pages.toolbox.toolbox import call_openai, read_prompt, encode_image

# 设置页面配置
st.set_page_config(page_title="AI 历史人物肖像生成", layout="wide")
st.title("AI 历史人物肖像生成器")

# Replicate API密钥设置
os.environ["REPLICATE_API_TOKEN"] = 


def get_character_description(name):
    """使用现有的GPT接口获取人物描述"""
    prompt = f"""请详细分析历史人物"{name}"，按以下JSON格式返回（不要添加任何其他内容）：
    {{
        "name": "人物名",
        "gender": "性别（男性/女性）",
        "era": "所处年代",
        "age": "最著名时期的年龄段（年轻/中年/老年）",
        "title": "称号或职位",
        "appearance": "面部和体态特征",
        "clothing": "典型服饰描述",
        "style": "整体风格特征",
        "additional": "其他特征"
    }}
    """

    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai(messages)
        return eval(response)
    except Exception as e:
        st.error(f"GPT API 错误: {str(e)}")
        return None


def build_prompt(char_info):
    """构建Stable Diffusion的提示词"""
    prompt = f"""ultra realistic portrait of {char_info['name']}, 
    {char_info['title']} from {char_info['era']}, 
    {char_info['age']} {char_info['gender']}, 
    {char_info['appearance']}, 
    wearing {char_info['clothing']}, 
    {char_info['style']}, 
    {char_info['additional']}, 
    masterpiece, historical accuracy, highly detailed face, 
    traditional Chinese style, 8k uhd, detailed face"""

    return prompt


def generate_image(prompt, model_version, steps, scale, negative_prompt):
    """使用Stable Diffusion生成图像"""
    try:
        if model_version == "stable-diffusion-v1-5":
            model = "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4"
        else:
            model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"

        output = replicate.run(
            model,
            input={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": steps,
                "guidance_scale": scale,
            }
        )

        if output and len(output) > 0:
            response = requests.get(output[0])
            return Image.open(BytesIO(response.content))
        return None
    except Exception as e:
        st.error(f"图像生成错误: {str(e)}")
        return None


# 侧边栏设置
with st.sidebar:
    st.header("生成设置")

    model_version = st.selectbox(
        "模型版本",
        ["stable-diffusion-xl", "stable-diffusion-v1-5"]
    )

    with st.expander("高级设置"):
        steps = st.slider("推理步数", 20, 100, 50)
        scale = st.slider("引导比例", 1.0, 20.0, 7.5)
        negative_prompt = st.text_area(
            "反向提示词",
            "lowres, bad anatomy, bad hands, text, error, missing fingers, " +
            "extra digit, fewer digits, cropped, worst quality, low quality, " +
            "normal quality, jpeg artifacts, signature, watermark, username, blurry, " +
            "wrong gender, wrong age, deformed face"
        )

# 主界面
name = st.text_input("输入历史人物名称", placeholder="例如：李白")

if st.button("生成肖像"):
    if not name:
        st.warning("请输入人物名称")
    else:
        with st.spinner("正在分析人物信息..."):
            char_info = get_character_description(name)

        if char_info:
            with st.expander("查看人物分析结果"):
                st.json(char_info)

            prompt = build_prompt(char_info)

            with st.expander("查看生成提示词"):
                st.write(prompt)

            with st.spinner("正在生成肖像..."):
                image = generate_image(
                    prompt,
                    model_version,
                    steps,
                    scale,
                    negative_prompt
                )

            if image:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.image(image, use_column_width=True)

                with col2:
                    st.subheader("人物信息")
                    st.write(f"姓名: {char_info['name']}")
                    st.write(f"时代: {char_info['era']}")
                    st.write(f"称号: {char_info['title']}")

                    # 下载按钮
                    img_bytes = BytesIO()
                    image.save(img_bytes, format='PNG')
                    st.download_button(
                        label="下载图像",
                        data=img_bytes.getvalue(),
                        file_name=f"{name}_portrait.png",
                        mime="image/png"
                    )

# 页脚
st.markdown("---")
st.markdown("""
使用说明：
1. 输入历史人物名称
2. 系统会自动分析人物特征并生成合适的提示词
3. 可以在侧边栏调整生成参数
4. 展开面板可查看详细的分析结果和生成提示词
""")