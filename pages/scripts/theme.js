// 检测当前主题
function updateTheme() {
    const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
}

// 初始化主题
updateTheme();

// 监听主题变化
window.matchMedia('(prefers-color-scheme: dark)').addListener(updateTheme);  

// 等待页面加载完成
window.addEventListener('load', function() {
    // 监听所有按钮的点击事件
    function setupButtonListeners() {
        // 分析按钮
        const analyzeButtons = document.querySelectorAll('button[data-testid="stBaseButton-secondary"]');
        console.log("testing")
        analyzeButtons.forEach(button => {
            if (button.textContent.includes('分析')) {
                button.addEventListener('click', function() {
                    // 查找分析文本框并清空
                    const textArea = document.querySelector('textarea[aria-label="输入文字"]');
                    if (textArea) {
                        setTimeout(() => {
                            textArea.value = '';
                            // 触发输入事件以确保 Streamlit 能检测到变化
                            textArea.dispatchEvent(new Event('input', { bubbles: true }));
                        }, 100);
                    }
                });
            }
        });

        // 发送按钮
        const sendButtons = document.querySelectorAll('button[data-testid="stBaseButton-secondary"]');
        sendButtons.forEach(button => {
            if (button.textContent.includes('发送')) {
                button.addEventListener('click', function() {
                    // 查找对话文本框并清空
                    const chatInput = document.querySelector('input[aria-label="与作家对话"]');
                    if (chatInput) {
                        setTimeout(() => {
                            chatInput.value = '';
                            // 触发输入事件以确保 Streamlit 能检测到变化
                            chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                        }, 100);
                    }
                });
            }
        });
    }

    // 初始化按钮监听器
    setupButtonListeners();

    // 使用 MutationObserver 监听 DOM 变化
    const observer = new MutationObserver(function(mutations) {
        setupButtonListeners();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});