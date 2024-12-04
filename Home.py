import streamlit as st

# 设置页面配置
st.set_page_config(page_title="Find Your Match", layout="wide")

# 主页面
st.title("Find Your Match")

st.markdown("""
## Welcome to **Find Your Match**！

Please select the function from the left sidebar:

1. **Painting**: Which Artist Shares Your Views?
2. **Literature**: Which Writer Shares Your Views?

""")

# 添加页面底部信息
st.markdown("---")
st.markdown("*Note: All results are for informational purposes only. Artistic and literary creations are unique personal expressions.*")