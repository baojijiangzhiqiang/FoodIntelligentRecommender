/**
 * 美食智能管理系统 - 推荐系统相关JavaScript功能
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化个性化推荐展示
    initPersonalizedRecommendations();
    
    // 初始化相似菜谱展示
    initSimilarRecipes();
    
    // 初始化推荐分类切换
    initRecommendationTabs();
});

/**
 * 初始化个性化推荐展示
 */
function initPersonalizedRecommendations() {
    // 这部分主要是展示效果，实际推荐逻辑在后端完成
    const recommendationContainer = document.querySelector('.recommendation-container');
    
    if (recommendationContainer) {
        // 添加鼠标悬停效果
        const recipeCards = recommendationContainer.querySelectorAll('.recipe-card');
        
        recipeCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                // 添加突出显示效果
                this.classList.add('recipe-card-highlight');
            });
            
            card.addEventListener('mouseleave', function() {
                // 移除突出显示效果
                this.classList.remove('recipe-card-highlight');
            });
        });
    }
}

/**
 * 初始化相似菜谱展示
 */
function initSimilarRecipes() {
    // 相似菜谱轮播效果（如果有多个）
    const similarRecipesContainer = document.querySelector('.similar-recipes-container');
    
    if (similarRecipesContainer) {
        // 如果需要，这里可以添加轮播逻辑
        // 目前使用的是Bootstrap的内置轮播组件，通常不需要额外JavaScript
    }
}

/**
 * 初始化推荐分类切换
 */
function initRecommendationTabs() {
    // 首页推荐标签页切换
    const recommendationTabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    if (recommendationTabs.length > 0) {
        recommendationTabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', function(event) {
                // 当标签页显示时的处理，如果需要可以添加
                const targetId = event.target.getAttribute('href');
                const targetPane = document.querySelector(targetId);
                
                if (targetPane) {
                    // 可以在这里添加标签页显示时的动画或其他效果
                    targetPane.classList.add('tab-pane-active');
                }
            });
        });
    }
}

/**
 * 获取更多推荐菜谱（用于"加载更多"按钮）
 * @param {string} recommendationType - 推荐类型，如'popular', 'latest', 'personalized'
 * @param {number} page - 页码
 */
function loadMoreRecommendations(recommendationType, page) {
    const loadMoreBtn = document.querySelector(`.load-more-${recommendationType}`);
    const recipesContainer = document.querySelector(`.${recommendationType}-recipes-container`);
    
    if (loadMoreBtn && recipesContainer) {
        // 显示加载中动画
        loadMoreBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 加载中...';
        loadMoreBtn.disabled = true;
        
        // 模拟加载更多数据（实际项目中应该是AJAX请求）
        setTimeout(() => {
            // 恢复按钮状态
            loadMoreBtn.innerHTML = '加载更多';
            loadMoreBtn.disabled = false;
            
            // 如果是最后一页，可以隐藏按钮
            if (page >= 3) { // 假设共3页
                loadMoreBtn.style.display = 'none';
                
                // 显示全部加载完成提示
                const completeMessage = document.createElement('p');
                completeMessage.className = 'text-center text-muted mt-3';
                completeMessage.textContent = '已加载全部内容';
                recipesContainer.appendChild(completeMessage);
            }
        }, 1000);
    }
}

/**
 * 渲染推荐菜谱卡片
 * @param {Object} recipe - 菜谱对象
 * @returns {HTMLElement} - 菜谱卡片元素
 */
function renderRecipeCard(recipe) {
    // 创建菜谱卡片HTML
    const cardElement = document.createElement('div');
    cardElement.className = 'col';
    
    cardElement.innerHTML = `
        <div class="card h-100 shadow-sm recipe-card">
            <div class="card-img-container">
                <img src="${recipe.image_url}" class="card-img-top" alt="${recipe.name}">
                <div class="card-img-overlay d-flex align-items-start justify-content-between">
                    <span class="badge bg-primary">${recipe.difficulty}</span>
                    <span class="badge bg-warning text-dark">
                        <i class="fas fa-star"></i> ${recipe.avg_rating.toFixed(1)}
                    </span>
                </div>
            </div>
            <div class="card-body">
                <h5 class="card-title">${recipe.name}</h5>
                <p class="card-text small text-truncate">${recipe.description}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div class="small text-muted">
                        <i class="fas fa-clock"></i> ${recipe.prep_time + recipe.cook_time}分钟
                    </div>
                    <a href="/recipes/${recipe.id}" class="btn btn-sm btn-outline-primary">
                        查看详情
                    </a>
                </div>
            </div>
        </div>
    `;
    
    return cardElement;
}

/**
 * 随机化推荐结果的顺序（用于增加多样性）
 * @param {Array} recommendations - 推荐结果数组
 * @returns {Array} - 随机化顺序后的推荐结果
 */
function randomizeRecommendations(recommendations) {
    // 使用Fisher-Yates洗牌算法
    const shuffled = [...recommendations];
    
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    
    return shuffled;
}
