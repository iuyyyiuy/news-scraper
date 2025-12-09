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
        
        // Export CSV
        document.getElementById('export-csv').addEventListener('click', () => {
            this.exportToCSV();
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
        console.log('🔄 Loading keywords...');
        try {
            const response = await fetch('/api/database/keywords');
            console.log('📥 Keywords response status:', response.status);
            const result = await response.json();
            console.log('✅ Keywords loaded:', result.data ? result.data.length : 0);
            
            if (result.success) {
                this.renderKeywordOptions(result.data);
            }
        } catch (error) {
            console.error('❌ Error loading keywords:', error);
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
        console.log('🔄 Loading articles...');
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
            
            const url = `/api/database/articles?${params}`;
            console.log('📡 Fetching:', url);
            
            const response = await fetch(url);
            console.log('📥 Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('✅ API Response:', result);
            console.log('📊 Articles count:', result.data ? result.data.length : 0);
            
            if (result.success && result.data) {
                this.totalArticles = result.total;
                console.log('📈 Total articles:', this.totalArticles);
                this.renderArticles(result.data);
                this.updatePagination();
                this.updateArticleCount();
            } else {
                console.error('❌ Invalid response format:', result);
                this.showError();
            }
        } catch (error) {
            console.error('❌ Error loading articles:', error);
            console.error('Error details:', error.message, error.stack);
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
        
        tbody.innerHTML = articles.map(article => {
            // Parse keywords if they're a string
            let keywords = article.matched_keywords;
            if (typeof keywords === 'string') {
                try {
                    keywords = JSON.parse(keywords);
                } catch (e) {
                    keywords = [keywords];
                }
            }
            if (!Array.isArray(keywords)) {
                keywords = [keywords];
            }
            
            return `
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
                        ${keywords.slice(0, 3).map(kw => 
                            `<span class="keyword-tag">${this.escapeHtml(kw)}</span>`
                        ).join('')}
                        ${keywords.length > 3 ? 
                            `<span class="keyword-tag">+${keywords.length - 3}</span>` : ''}
                    </div>
                </td>
                <td>
                    <button class="btn-view" onclick="dashboard.showArticleDetail('${article.id}')">查看</button>
                </td>
            </tr>
            `;
        }).join('');
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
                
                // Parse keywords if they're a string
                let keywords = article.matched_keywords;
                if (typeof keywords === 'string') {
                    try {
                        keywords = JSON.parse(keywords);
                    } catch (e) {
                        keywords = [keywords];
                    }
                }
                if (!Array.isArray(keywords)) {
                    keywords = [keywords];
                }
                
                // Keywords
                const keywordsDiv = document.getElementById('modal-keywords');
                keywordsDiv.innerHTML = keywords.map(kw => 
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
        console.log('🔄 Loading stats...');
        try {
            const response = await fetch('/api/database/stats');
            console.log('📥 Stats response status:', response.status);
            const result = await response.json();
            console.log('✅ Stats loaded:', result);
            
            if (result.success) {
                const lastScrape = result.data.last_scrape;
                if (lastScrape) {
                    // Parse the UTC time and add 8 hours for UTC+8
                    const utcDate = new Date(lastScrape);
                    const utc8Date = new Date(utcDate.getTime() + (8 * 60 * 60 * 1000));
                    
                    // Format as YYYY/MM/DD HH:mm:ss using the UTC+8 date
                    const year = utc8Date.getUTCFullYear();
                    const month = String(utc8Date.getUTCMonth() + 1).padStart(2, '0');
                    const day = String(utc8Date.getUTCDate()).padStart(2, '0');
                    const hours = String(utc8Date.getUTCHours()).padStart(2, '0');
                    const minutes = String(utc8Date.getUTCMinutes()).padStart(2, '0');
                    const seconds = String(utc8Date.getUTCSeconds()).padStart(2, '0');
                    
                    const formattedTime = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
                    
                    document.getElementById('last-update').textContent = 
                        `最后更新: ${formattedTime}`;
                }
            }
        } catch (error) {
            console.error('❌ Error loading stats:', error);
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
    
    exportToCSV() {
        // Use server-side export endpoint
        let url = `/api/database/export/csv`;
        const params = [];
        
        if (this.currentKeyword) params.push(`keyword=${this.currentKeyword}`);
        if (this.currentSource) params.push(`source=${this.currentSource}`);
        
        if (params.length > 0) {
            url += '?' + params.join('&');
        }
        
        // Direct download via link
        window.location.href = url;
    }
}

// Initialize dashboard
const dashboard = new DashboardController();
