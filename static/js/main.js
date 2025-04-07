/**
 * 美食智能管理系统主JavaScript文件
 * 包含全局通用的功能和初始化
 */

// 当文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // 初始化所有弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // 设置闪现消息自动消失
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // 设置导航栏活动项
    setActiveNavItem();
    
    // 后续可以添加更多通用功能...
});

/**
 * 根据当前页面URL设置导航栏活动项
 */
function setActiveNavItem() {
    // 获取当前URL路径
    var path = window.location.pathname;
    
    // 获取所有导航链接
    var navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    // 遍历导航链接，找到匹配当前路径的链接并设置为活动状态
    navLinks.forEach(function(link) {
        var href = link.getAttribute('href');
        if (href && path.startsWith(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/' && path === '/') {
            link.classList.add('active');
        }
    });
}

/**
 * 显示加载动画
 * @param {HTMLElement} element - 要显示加载动画的元素
 */
function showLoading(element) {
    // 创建加载动画元素
    var loadingEl = document.createElement('div');
    loadingEl.className = 'text-center py-3 loading-spinner';
    loadingEl.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">加载中...</span></div><p class="mt-2">加载中...</p>';
    
    // 清空元素内容并添加加载动画
    if (element) {
        element.innerHTML = '';
        element.appendChild(loadingEl);
    }
    
    return loadingEl;
}

/**
 * 移除加载动画
 * @param {HTMLElement} element - 包含加载动画的元素
 */
function hideLoading(element) {
    if (element) {
        var spinner = element.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise<boolean>} - 成功返回true，失败返回false
 */
function copyToClipboard(text) {
    // 使用现代Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text)
            .then(() => true)
            .catch(() => {
                // 如果API失败，回退到传统方法
                return fallbackCopyToClipboard(text);
            });
    }
    // 回退到传统方法
    return Promise.resolve(fallbackCopyToClipboard(text));
}

/**
 * 回退方法：复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {boolean} - 成功返回true，失败返回false
 */
function fallbackCopyToClipboard(text) {
    // 创建一个临时textarea元素
    const textArea = document.createElement('textarea');
    textArea.value = text;
    
    // 设置样式以避免闪烁
    textArea.style.position = 'fixed';
    textArea.style.top = '-999999px';
    textArea.style.left = '-999999px';
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    let success = false;
    try {
        // 尝试执行复制命令
        success = document.execCommand('copy');
    } catch (err) {
        console.error('无法复制文本: ', err);
    }
    
    // 移除临时元素
    document.body.removeChild(textArea);
    return success;
}

/**
 * 格式化日期时间
 * @param {Date|string} dateTime - 日期时间对象或字符串
 * @param {string} format - 格式化模板，默认为 'YYYY-MM-DD HH:mm'
 * @returns {string} - 格式化后的日期时间字符串
 */
function formatDateTime(dateTime, format = 'YYYY-MM-DD HH:mm') {
    const date = new Date(dateTime);
    
    if (isNaN(date.getTime())) {
        return '无效日期';
    }
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
}
