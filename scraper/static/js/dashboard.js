/**
 * Dashboard Controller for News Database
 */

class DashboardController {
    constructor() {
        this.currentPage = 1;
        this.limit = 50;
        this.currentKeyword = null;
        this.currentSource = null;
        this.totalArticles = 0;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadKeywords();
        this.loadArticles();
        this.loadStats();
    }
    
    setupEventListeners() {
        // Filter changes
        document.getElementById('keyword-filter').addEventListener('change', (e) => {
            this.currentKeyword = e.target.value || null;
            this.currentPage = 1;
            this.loadArticles();
        });
        
        document.getElementById('source-filter').addEventListener('change', (e) => {
            this.currentSource = e.target.value || null;
            this.currentPage = 1;
            this.loadArticles();
        });
        
        // Clear filters
        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });
        
        // Pagination
        document.getElementById('prev-page').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadArticles();
            }
        });
        
        document.getElementById('next-page').addEventListener('click', () => {
            this.currentPage++;
            this.loadArticles();
        });
        
        // Modal close
        document.querySelector('.close').addEventListener('click', () => {
            this.closeModal();
        });
        
        document.getElementById('article-modal').addEventListener('click', (e) => {
            if (e.target.id === 'article-modal') {
                this.closeModal();
            }
        });
    }
    
    async loadKeywords() {
        try {
            const response = await fetch('/api/database/keywords');
            const result = await response.json();
            
            if (result.success) {
                this.renderKeywordOptions(result.data);
            }
        } catch (error) {
            console.error('Error loading keywords:', error);
        }
    }
    
    renderKeywordOptions(keywords) {
        const select = document.getElementById('keyword-filter');
        const currentValue = select.value;
        
        // Keep "全部关键词" option
        select.innerHTML = '<option value="">全部关键词</option>';
        
        keywords.forEach(item => {
            const option = document.createElement('option');
            option.value = item.keyword;
            option.textContent = `${item.keyword} (${item.count})`;
            select.appendChild(option);
        });
        
        // Restore selection
        select.value = currentValue;
    }
    
    async loadArticles() {
        try {
            const offset = (this.currentPage - 1) * this.limit;
            const params = new URLSearchParams({
                limit: this.limit,
                offset: offset
            });
            
            if (this.currentKeyword) {
                params.append('keyword', this.currentKeyword);
            }
            
            if (this.currentSource) {
                params.append('source', this.currentSource);
            }
            
            const response = await fetch(`/api/database/articles?${params}`);
            const result = await response.json();
            
            if (result.success) {
                this.totalArticles = result.total;
                this.renderArticles(result.data);
                this.updatePagination();
                this.updateArticleCount();
            }
        } catch (error) {
            console.error('Error loading articles:', error);
            this.showError();
        }
    }
    
    renderArticles(articles) {
        const tbody = document.getElementById('articles-tbody');
        
        if (articles.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5">
                        <div class="empty-state">
                            <div class="empty-state-icon">📭</div>
                            <div>暂无数据</div>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = articles.map(article => `
            <tr>
                <td class="article-date">${this.formatDate(article.date)}</td>
                <td><span class="article-source">${article.source}</span></td>
                <td>
                    <div class="article-title" onclick="dashboard.showArticleDetail('${article.id}')">
                        ${this.escapeHtml(article.title)}
                    </div>
                </td>
                <td>
                    <div class="keywords-cell">
                        ${article.matched_keywords.slice(0, 3).map(kw => 
                            `<span class="keyword-tag">${this.escapeHtml(kw)}</span>`
                        ).join('')}
                        ${article.matched_keywords.length > 3 ? 
                            `<span class="keyword-tag">+${article.matched_keywords.length - 3}</span>` : ''}
                    </div>
                </td>
                <td>
                    <button class="btn-view" onclick="dashboard.showArticleDetail('${article.id}')">
                        查看
                    </button>
                </td>
            </tr>
        `).join('');
    }
    
    async showArticleDetail(articleId) {
        try {
            const response = await fetch(`/api/database/articles/${articleId}`);
            const result = await response.json();
            
            if (result.success) {
                const article = result.data;
                
                document.getElementById('modal-title').textContent = article.title;
                document.getElementById('modal-source').textContent = article.source;
                document.getElementById('modal-date').textContent = this.formatDate(article.date);
                
                // Keywords
                const keywordsDiv = document.getElementById('modal-keywords');
                keywordsDiv.innerHTML = article.matched_keywords.map(kw => 
                    `<span class="keyword-tag">${this.escapeHtml(kw)}</span>`
                ).join('');
                
                // Content
                document.getElementById('modal-content').textContent = article.content;
                
                // Link
                document.getElementById('modal-link').href = article.url;
                
                // Show modal
                document.getElementById('article-modal').classList.add('active');
            }
        } catch (error) {
            console.error('Error loading article detail:', error);
        }
    }
    
    closeModal() {
        document.getElementById('article-modal').classList.remove('active');
    }
    
    updatePagination() {
        const totalPages = Math.ceil(this.totalArticles / this.limit);
        
        document.getElementById('prev-page').disabled = this.currentPage === 1;
        document.getElementById('next-page').disabled = this.currentPage >= totalPages || totalPages === 0;
        
        document.getElementById('page-info').textContent = 
            totalPages > 0 ? `第 ${this.currentPage} / ${totalPages} 页` : '第 1 页';
    }
    
    updateArticleCount() {
        document.getElementById('article-count').textContent = `${this.totalArticles} 条新闻`;
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/database/stats');
            const result = await response.json();
            
            if (result.success) {
                const lastScrape = result.data.last_scrape;
                if (lastScrape) {
                    const date = new Date(lastScrape);
                    document.getElementById('last-update').textContent = 
                        `最后更新: ${date.toLocaleString('zh-CN')}`;
                }
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    clearFilters() {
        this.currentKeyword = null;
        this.currentSource = null;
        this.currentPage = 1;
        
        document.getElementById('keyword-filter').value = '';
        document.getElementById('source-filter').value = '';
        
        this.loadArticles();
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${month}/${day}`;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showError() {
        const tbody = document.getElementById('articles-tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="5">
                    <div class="empty-state">
                        <div class="empty-state-icon">❌</div>
                        <div>加载失败，请刷新页面重试</div>
                    </div>
                </td>
            </tr>
        `;
    }
}

// Initialize dashboard
const dashboard = new DashboardController();
