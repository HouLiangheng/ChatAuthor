import streamlit as st

# 设置页面配置
st.set_page_config(page_title="艺术风格分析", layout="wide")

# 主页面
st.title("艺术风格分析器")

st.markdown("""
## 欢迎使用艺术风格分析器！

请从左侧边栏选择功能：

1. **图片分析**: 上传图片进行艺术风格分析
2. **文字分析**: 输入文字进行文学风格分析

""")

# 添加页面底部信息
st.markdown("---")
st.markdown("*注：分析结果仅供参考，艺术创作和文学创作都是独特的个人表达。*")