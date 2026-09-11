"""截图工具：隐藏 GitLab Duo 营销横幅。

GitLab 页面底部常出现"尝试 GitLab Duo Agent 平台"营销横幅，
固定在视口底部、遮挡截图有效信息。本模块在截图前将其隐藏。

用法（在 shot() 函数里 page.screenshot() 之前调一次）：

    from shot_utils import hide_duo_banner
    hide_duo_banner(page)
    page.screenshot(...)
"""


def hide_duo_banner(page):
    """隐藏 GitLab Duo 营销横幅——它固定在页面底部，遮挡截图有效信息。

    三重策略兜底，不依赖单一选择器：
    1. data-testid 含 duo/banner 的元素，且文本含 Duo
    2. class 含 duo-banner/promotional-banner/gl-banner 的元素
    3. 文本含"尝试"+"Duo"、位于视口底部 30%、高度 < 200px 的容器
    """
    try:
        page.evaluate("""() => {
            // 1. data-testid
            document.querySelectorAll(
                '[data-testid*="duo" i], [data-testid*="banner" i]'
            ).forEach(el => {
                if ((el.innerText || '').includes('Duo')) el.style.display = 'none';
            });
            // 2. class
            document.querySelectorAll(
                '.duo-banner, .gl-banner, [class*="duo-banner"], [class*="promotional-banner"]'
            ).forEach(el => {
                if ((el.innerText || '').includes('Duo')) el.style.display = 'none';
            });
            // 3. 文本兜底
            const vh = window.innerHeight;
            document.querySelectorAll('div, aside, footer').forEach(el => {
                const text = (el.innerText || '').trim();
                const rect = el.getBoundingClientRect();
                if (text.includes('尝试') && text.includes('Duo')
                    && text.length < 200
                    && rect.top > vh * 0.7 && el.offsetHeight < 200) {
                    el.style.display = 'none';
                }
            });
        }""")
    except Exception:
        pass
