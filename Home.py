import streamlit as st

# 设置页面配置
st.set_page_config(
    page_title="Find Your ArtSoul",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"  # 在手机上默认收起侧边栏
)

# 页面标题和介绍
st.title("🎨 Find Your ArtSoul")

# 添加一些页面间距
st.markdown("<br>", unsafe_allow_html=True)

# 创建两列布局用于放置卡片
col1, col2 = st.columns(2)

with col1:
    # 文学分析卡片
    st.markdown("""
    <div style="
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #1f77b4;
        text-align: center;
        background-color: rgba(31, 119, 180, 0.1);
        height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;">
        <div>
            <h2 style="color: #1f77b4;">📚 Literature</h2>
            <p style="font-size: 16px;">
                输入文本进行风格分析<br>
                了解文学作品的独特特点<br>
                获取详细的写作风格报告
            </p >
        </div>
        <a href="Literature" target="_self" style="
            display: inline-block;
            padding: 12px 48px;
            background-color: #1f77b4;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
            font-weight: bold;">
            开始分析
        </a >
    </div>
    """, unsafe_allow_html=True)

with col2:
    # 绘画分析卡片
    st.markdown("""
    <div style="
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #ff7f0e;
        text-align: center;
        background-color: rgba(255, 127, 14, 0.1);
        height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;">
        <div>
            <h2 style="color: #ff7f0e;">🎨 Painting</h2>
            <p style="font-size: 16px;">
                上传图片进行艺术分析<br>
                探索绘画作品的风格特征<br>
                获取专业的艺术评析
            </p >
        </div>
        <a href="Paintings" target="_self" style="
            display: inline-block;
            padding: 12px 48px;
            background-color: #ff7f0e;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
            font-weight: bold;">
            开始分析
        </a >
    </div>
    """, unsafe_allow_html=True)

# 添加一些页面间距
st.markdown("<br>", unsafe_allow_html=True)

# 添加使用说明
st.markdown("""
<div style="
    margin-top: 20px;">
</div>
""", unsafe_allow_html=True)

# 添加页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>© ISDN3150 ArtSoul | All analysis results are for reference only</small>
</div>
""", unsafe_allow_html=True)

# 添加自定义 CSS
st.markdown("""
<style>
    /* 隐藏 Streamlit 默认的汉堡菜单 */
    #MainMenu {visibility: hidden;}

    /* 调整页面边距 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        div[data-testid="column"] {
            width: 100% !important;
            margin-bottom: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)