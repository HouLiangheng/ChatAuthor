// 检测当前主题
function updateTheme() {
    const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
}

// 初始化主题
updateTheme();

// 监听主题变化
window.matchMedia('(prefers-color-scheme: dark)').addListener(updateTheme);  
