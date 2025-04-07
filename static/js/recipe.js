/**
 * 美食智能管理系统 - 菜谱详情页面相关功能
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化星级评分系统
    initRatingSystem();
    
    // 初始化分享按钮
    initShareButtons();
    
    // 初始化打印功能
    initPrintFunction();
});

/**
 * 初始化星级评分系统
 */
function initRatingSystem() {
    // 获取评分表单和星星元素
    const ratingForm = document.getElementById('ratingForm');
    const stars = document.querySelectorAll('.star-rating input');
    
    if (ratingForm && stars.length > 0) {
        // 为每个星星添加点击事件，点击后自动提交表单
        stars.forEach(star => {
            star.addEventListener('change', function() {
                ratingForm.submit();
            });
        });
    }
}

/**
 * 初始化分享按钮
 */
function initShareButtons() {
    // 获取所有分享按钮
    const shareButtons = document.querySelectorAll('.share-btn');
    
    // 为每个分享按钮添加点击事件
    shareButtons.forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.getAttribute('data-platform');
            shareRecipe(platform);
        });
    });
    
    // 特殊处理复制链接按钮
    const copyLinkButton = document.getElementById('copyLink');
    if (copyLinkButton) {
        copyLinkButton.addEventListener('click', function() {
            const currentUrl = window.location.href;
            copyToClipboard(currentUrl).then(success => {
                if (success) {
                    // 显示成功消息
                    const successMessage = document.getElementById('shareSuccess');
                    if (successMessage) {
                        successMessage.classList.remove('d-none');
                        // 3秒后隐藏成功消息
                        setTimeout(() => {
                            successMessage.classList.add('d-none');
                        }, 3000);
                    }
                }
            });
        });
    }
}

/**
 * 分享菜谱到不同平台
 * @param {string} platform - 分享平台
 */
function shareRecipe(platform) {
    // 获取当前页面URL和标题
    const currentUrl = encodeURIComponent(window.location.href);
    const pageTitle = encodeURIComponent(document.title);
    
    // 根据不同平台打开对应的分享链接
    switch(platform) {
        case 'wechat':
            // 微信分享通常是通过显示二维码进行的
            alert('请使用微信扫一扫功能，扫描当前页面的二维码进行分享');
            break;
        case 'weibo':
            // 分享到微博
            window.open(`http://service.weibo.com/share/share.php?url=${currentUrl}&title=${pageTitle}`, '_blank');
            break;
        case 'qq':
            // 分享到QQ空间
            window.open(`http://connect.qq.com/widget/shareqq/index.html?url=${currentUrl}&title=${pageTitle}`, '_blank');
            break;
        // 其他平台可以继续添加...
    }
}

/**
 * 初始化打印功能
 */
function initPrintFunction() {
    const printButton = document.getElementById('printRecipe');
    
    if (printButton) {
        printButton.addEventListener('click', function() {
            // 打印当前页面
            preparePrintView();
            window.print();
            restoreAfterPrint();
        });
    }
}

/**
 * 准备打印视图 - 隐藏不需要打印的元素
 */
function preparePrintView() {
    // 在body上添加一个打印模式的类
    document.body.classList.add('print-mode');
    
    // 隐藏导航栏、页脚和其他不需要打印的元素
    const elementsToHide = [
        'nav',
        'footer',
        '.share-buttons',
        '.btn', // 隐藏所有按钮
        '#copyLink',
        '#printRecipe'
    ];
    
    elementsToHide.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.setAttribute('data-print-hidden', 'true');
            el.style.display = 'none';
        });
    });
}

/**
 * 打印后恢复视图
 */
function restoreAfterPrint() {
    // 移除打印模式类
    document.body.classList.remove('print-mode');
    
    // 恢复被隐藏的元素
    const hiddenElements = document.querySelectorAll('[data-print-hidden="true"]');
    hiddenElements.forEach(el => {
        el.removeAttribute('data-print-hidden');
        el.style.display = '';
    });
}

/**
 * 切换收藏状态
 * @param {number} recipeId - 菜谱ID
 */
function toggleFavorite(recipeId) {
    // 获取收藏按钮
    const favoriteBtn = document.querySelector('.favorite-btn');
    
    if (favoriteBtn) {
        // 切换按钮状态
        const isFavorite = favoriteBtn.classList.contains('btn-danger');
        
        if (isFavorite) {
            // 取消收藏
            favoriteBtn.classList.remove('btn-danger');
            favoriteBtn.classList.add('btn-outline-danger');
            favoriteBtn.innerHTML = '<i class="fas fa-heart"></i> 收藏';
        } else {
            // 添加收藏
            favoriteBtn.classList.remove('btn-outline-danger');
            favoriteBtn.classList.add('btn-danger');
            favoriteBtn.innerHTML = '<i class="fas fa-heart"></i> 已收藏';
        }
    }
}

/**
 * 计算烹饪时间总和
 * @param {number} prepTime - 准备时间（分钟）
 * @param {number} cookTime - 烹饪时间（分钟）
 * @returns {string} - 格式化后的总时间
 */
function calculateTotalTime(prepTime, cookTime) {
    const totalMinutes = prepTime + cookTime;
    
    if (totalMinutes < 60) {
        return `${totalMinutes}分钟`;
    }
    
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    
    if (minutes === 0) {
        return `${hours}小时`;
    }
    
    return `${hours}小时${minutes}分钟`;
}
