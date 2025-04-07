/**
 * 美食智能管理系统 - 社区功能相关JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化社区帖子相关功能
    initCommunityPosts();
    
    // 初始化评论功能
    initCommentSystem();
    
    // 初始化社区分享功能
    initPostSharing();
});

/**
 * 初始化社区帖子相关功能
 */
function initCommunityPosts() {
    // 点赞功能
    const likeButtons = document.querySelectorAll('.like-btn');
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 更新视觉效果（实际提交通过表单完成）
            const likeCount = this.querySelector('.like-count');
            if (likeCount) {
                const currentCount = parseInt(likeCount.textContent);
                likeCount.textContent = currentCount + 1;
            }
            
            // 禁用按钮防止重复点赞
            this.disabled = true;
            this.classList.add('liked');
        });
    });
    
    // 帖子搜索功能
    const postSearchInput = document.getElementById('postSearch');
    if (postSearchInput) {
        postSearchInput.addEventListener('keyup', function() {
            filterPosts(this.value);
        });
    }
}

/**
 * 根据关键词过滤帖子
 * @param {string} keyword - 搜索关键词
 */
function filterPosts(keyword) {
    const lowercasedKeyword = keyword.toLowerCase();
    const posts = document.querySelectorAll('.post-item');
    
    posts.forEach(post => {
        const title = post.querySelector('.post-title').textContent.toLowerCase();
        const content = post.querySelector('.post-content').textContent.toLowerCase();
        
        if (title.includes(lowercasedKeyword) || content.includes(lowercasedKeyword)) {
            post.style.display = '';
        } else {
            post.style.display = 'none';
        }
    });
    
    // 显示搜索结果数量
    const visiblePosts = document.querySelectorAll('.post-item:not([style*="display: none"])');
    const resultCounter = document.getElementById('searchResultCount');
    
    if (resultCounter) {
        resultCounter.textContent = visiblePosts.length;
        resultCounter.parentElement.style.display = keyword ? '' : 'none';
    }
}

/**
 * 初始化评论系统
 */
function initCommentSystem() {
    // 评论表单处理
    const commentForm = document.querySelector('.comment-form');
    
    if (commentForm) {
        commentForm.addEventListener('submit', function(event) {
            const commentContent = this.querySelector('textarea').value.trim();
            
            if (!commentContent) {
                // 阻止空评论提交
                event.preventDefault();
                alert('评论内容不能为空');
            }
        });
    }
    
    // 评论字数限制和计数
    const commentTextarea = document.querySelector('.comment-textarea');
    const charCounter = document.querySelector('.char-counter');
    
    if (commentTextarea && charCounter) {
        const maxLength = parseInt(commentTextarea.getAttribute('maxlength') || 500);
        
        commentTextarea.addEventListener('input', function() {
            const remainingChars = maxLength - this.value.length;
            charCounter.textContent = `${remainingChars} 字符剩余`;
            
            // 如果剩余字符较少，给出视觉警告
            if (remainingChars < 20) {
                charCounter.classList.add('text-danger');
            } else {
                charCounter.classList.remove('text-danger');
            }
        });
    }
}

/**
 * 初始化社区帖子分享功能
 */
function initPostSharing() {
    // 分享按钮
    const shareButtons = document.querySelectorAll('.share-btn');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function() {
            const platform = this.getAttribute('data-platform');
            sharePost(platform);
        });
    });
    
    // 特殊处理复制链接按钮
    const copyPostLinkButton = document.getElementById('copyPostLink');
    if (copyPostLinkButton) {
        copyPostLinkButton.addEventListener('click', function() {
            const currentUrl = window.location.href;
            copyToClipboard(currentUrl).then(success => {
                if (success) {
                    // 显示成功提示
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check"></i> 已复制';
                    
                    // 3秒后恢复原始图标
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 3000);
                }
            });
        });
    }
}

/**
 * 分享帖子到不同平台
 * @param {string} platform - 分享平台
 */
function sharePost(platform) {
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
 * 预览帖子内容（编辑时使用）
 */
function previewPostContent() {
    const contentTextarea = document.getElementById('content');
    const previewContainer = document.getElementById('contentPreview');
    
    if (contentTextarea && previewContainer) {
        // 获取内容并转换换行符为<br>
        const content = contentTextarea.value;
        const formattedContent = content.replace(/\n/g, '<br>');
        
        // 显示预览内容
        previewContainer.innerHTML = formattedContent;
        
        // 显示预览区域
        const previewSection = document.querySelector('.preview-section');
        if (previewSection) {
            previewSection.classList.remove('d-none');
        }
    }
}

/**
 * 切换帖子列表的显示模式（列表/卡片）
 * @param {string} mode - 显示模式：'list'或'card'
 */
function togglePostsViewMode(mode) {
    const postsContainer = document.querySelector('.posts-container');
    const listModeBtn = document.getElementById('listModeBtn');
    const cardModeBtn = document.getElementById('cardModeBtn');
    
    if (postsContainer && listModeBtn && cardModeBtn) {
        if (mode === 'list') {
            postsContainer.classList.remove('posts-card-view');
            postsContainer.classList.add('posts-list-view');
            listModeBtn.classList.add('active');
            cardModeBtn.classList.remove('active');
        } else if (mode === 'card') {
            postsContainer.classList.remove('posts-list-view');
            postsContainer.classList.add('posts-card-view');
            cardModeBtn.classList.add('active');
            listModeBtn.classList.remove('active');
        }
        
        // 保存用户偏好到localStorage
        localStorage.setItem('postsViewMode', mode);
    }
}
