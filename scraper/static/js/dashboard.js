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
        
        // Manual Update
        document.getElementById('manual-update').addEventListener('click', () => {
            this.showManualUpdateModal();
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
                        ${keywords.map(kw => 
                            `<span class="keyword-tag">${this.escapeHtml(kw)}</span>`
                        ).join('')}
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
    
    showManualUpdateModal() {
        document.getElementById('manual-update-modal').classList.add('active');
    }
    
    closeManualUpdateModal() {
        document.getElementById('manual-update-modal').classList.remove('active');
    }
    
    confirmManualUpdate() {
        // Close the modal first
        this.closeManualUpdateModal();
        
        // Get selected article count
        const articleCountSelect = document.getElementById('article-count-select');
        const maxArticles = parseInt(articleCountSelect.value);
        
        // Start the manual update with selected count
        this.startManualUpdate(maxArticles);
    }
    
    async startManualUpdate(maxArticles = 500) {
        const button = document.getElementById('manual-update');
        const originalText = button.textContent;
        
        try {
            // Disable button and show loading state
            button.disabled = true;
            button.textContent = '更新中...';
            button.style.opacity = '0.6';
            
            // Show persistent running notification (doesn't auto-disappear)
            this.progressNotification = this.showPersistentNotification(`🔄 正在运行... (${maxArticles}篇/源)`, 'info');
            
            // Start manual update with selected article count
            const response = await fetch('/api/manual-update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    max_articles: maxArticles
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Start checking for completion
                this.checkUpdateCompletion();
                
                // Refresh data after a delay
                setTimeout(() => {
                    this.loadArticles();
                    this.loadStats();
                }, 10000);
            } else {
                throw new Error(result.message || '启动失败');
            }
            
        } catch (error) {
            console.error('Manual update error:', error);
            // Remove progress notification and show error
            this.removePersistentNotification();
            this.showNotification(`❌ 手动更新失败: ${error.message}`, 'error');
        } finally {
            // Re-enable button after delay
            setTimeout(() => {
                button.disabled = false;
                button.textContent = originalText;
                button.style.opacity = '1';
            }, 5000);
        }
    }
    
    async checkUpdateCompletion() {
        // Get current article count before update
        const initialCount = this.totalArticles;
        console.log(`🔍 Starting completion check. Initial count: ${initialCount}`);
        
        // Check update status every 5 seconds for 3 minutes (more responsive)
        let checks = 0;
        const maxChecks = 36; // 3 minutes with 5-second intervals
        let lastArticleCount = initialCount;
        let stableCountChecks = 0;
        
        const checkInterval = setInterval(async () => {
            checks++;
            console.log(`📊 Completion check ${checks}/${maxChecks}`);
            
            try {
                // Refresh data to get updated count
                await this.loadArticles();
                await this.loadStats();
                
                // Calculate new articles added
                const newArticlesCount = this.totalArticles - initialCount;
                console.log(`📈 Current total: ${this.totalArticles}, New articles: ${newArticlesCount}`);
                
                // Check if article count has stabilized (no change for 3 consecutive checks)
                if (this.totalArticles === lastArticleCount) {
                    stableCountChecks++;
                    console.log(`⏸️ Article count stable for ${stableCountChecks} checks`);
                } else {
                    stableCountChecks = 0;
                    lastArticleCount = this.totalArticles;
                    console.log(`🔄 Article count changed, resetting stability counter`);
                }
                
                // Show completion if:
                // 1. Article count has been stable for 3 checks (15 seconds) AND we've waited at least 30 seconds
                // 2. OR we've reached the maximum wait time
                const minChecksBeforeCompletion = 6; // 30 seconds minimum
                const stableChecksNeeded = 3; // 15 seconds of stability
                
                if ((stableCountChecks >= stableChecksNeeded && checks >= minChecksBeforeCompletion) || checks >= maxChecks) {
                    clearInterval(checkInterval);
                    console.log(`✅ Scraping completed. Final count: ${this.totalArticles}, New articles: ${newArticlesCount}`);
                    
                    // Update the persistent progress notification to show completion (don't remove it yet)
                    this.updateProgressNotificationToCompletion(newArticlesCount);
                    
                    // Remove the notification after 10 seconds (longer than before)
                    setTimeout(() => {
                        this.removePersistentNotification();
                    }, 10000);
                }
                
            } catch (error) {
                console.error('Status check error:', error);
                if (checks >= maxChecks) {
                    clearInterval(checkInterval);
                    console.log('❌ Completion check failed, showing timeout message');
                    // Update the persistent progress notification to show timeout (don't remove it yet)
                    this.updateProgressNotificationToCompletion(0, true);
                    
                    // Remove the notification after 10 seconds
                    setTimeout(() => {
                        this.removePersistentNotification();
                    }, 10000);
                }
            }
        }, 5000); // Check every 5 seconds instead of 10
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification - centered on screen
        notification.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 16px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            max-width: 400px;
            min-width: 200px;
            text-align: center;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            font-size: 16px;
        `;
        
        // Set background color based on type
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#28a745';
                break;
            case 'error':
                notification.style.backgroundColor = '#dc3545';
                break;
            case 'info':
            default:
                notification.style.backgroundColor = '#17a2b8';
                break;
        }
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translate(-50%, -50%) scale(0.9)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
    
    showPersistentNotification(message, type = 'info') {
        // Create persistent notification element (doesn't auto-disappear)
        const notification = document.createElement('div');
        notification.className = `persistent-notification notification-${type}`;
        
        // Create animated content for progress notifications
        if (message.includes('正在运行')) {
            // Create animated progress indicator
            const progressContainer = document.createElement('div');
            progressContainer.style.cssText = `
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
            `;
            
            // Create spinning loader
            const spinner = document.createElement('div');
            spinner.className = 'progress-spinner';
            spinner.style.cssText = `
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255,255,255,0.3);
                border-top: 2px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            `;
            
            // Create dynamic text element
            const textElement = document.createElement('span');
            textElement.className = 'progress-text';
            textElement.textContent = '正在运行';
            
            // Create dots animation element
            const dotsElement = document.createElement('span');
            dotsElement.className = 'progress-dots';
            dotsElement.style.cssText = `
                display: inline-block;
                width: 20px;
                text-align: left;
            `;
            
            progressContainer.appendChild(spinner);
            progressContainer.appendChild(textElement);
            progressContainer.appendChild(dotsElement);
            notification.appendChild(progressContainer);
            
            // Start animations
            this.startProgressAnimations(dotsElement, textElement);
            
        } else {
            // Regular static message
            notification.textContent = message;
        }
        
        // Style the notification - centered on screen
        notification.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 16px 24px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10001;
            max-width: 400px;
            min-width: 200px;
            text-align: center;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            font-size: 16px;
        `;
        
        // Add CSS animations to document if not already added
        this.addProgressAnimationCSS();
        
        // Set background color based on type
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#28a745';
                break;
            case 'error':
                notification.style.backgroundColor = '#dc3545';
                break;
            case 'info':
            default:
                notification.style.backgroundColor = '#17a2b8';
                break;
        }
        
        // Add to page
        document.body.appendChild(notification);
        
        // Return the notification element so it can be removed later
        return notification;
    }
    
    removePersistentNotification() {
        // Stop any running animations
        if (this.progressAnimationInterval) {
            clearInterval(this.progressAnimationInterval);
            this.progressAnimationInterval = null;
        }
        
        // Remove any existing persistent notifications
        if (this.progressNotification && this.progressNotification.parentNode) {
            this.progressNotification.style.opacity = '0';
            this.progressNotification.style.transform = 'translate(-50%, -50%) scale(0.9)';
            setTimeout(() => {
                if (this.progressNotification && this.progressNotification.parentNode) {
                    this.progressNotification.parentNode.removeChild(this.progressNotification);
                }
                this.progressNotification = null;
            }, 300);
        }
    }
    
    startProgressAnimations(dotsElement, textElement) {
        // Animate dots (. .. ...)
        let dotCount = 0;
        this.progressAnimationInterval = setInterval(() => {
            dotCount = (dotCount + 1) % 4;
            dotsElement.textContent = '.'.repeat(dotCount);
        }, 500);
        
        // Optional: Cycle through different status messages
        const statusMessages = [
            '正在运行',
            '抓取中',
            '处理中',
            '分析中'
        ];
        let messageIndex = 0;
        
        setInterval(() => {
            messageIndex = (messageIndex + 1) % statusMessages.length;
            if (textElement && textElement.parentNode) {
                textElement.textContent = statusMessages[messageIndex];
            }
        }, 3000);
    }
    
    addProgressAnimationCSS() {
        // Check if CSS is already added
        if (document.getElementById('progress-animation-css')) {
            return;
        }
        
        // Add CSS animation for spinner
        const style = document.createElement('style');
        style.id = 'progress-animation-css';
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.6; }
            }
            
            .progress-spinner {
                animation: spin 1s linear infinite;
            }
            
            .progress-text {
                animation: pulse 2s ease-in-out infinite;
            }
        `;
        document.head.appendChild(style);
    }
    
    updateProgressNotificationToCompletion(newArticlesCount, isTimeout = false) {
        // Stop any running animations first
        if (this.progressAnimationInterval) {
            clearInterval(this.progressAnimationInterval);
            this.progressAnimationInterval = null;
        }
        
        // Update the existing progress notification to show completion
        if (this.progressNotification && this.progressNotification.parentNode) {
            // Clear the existing content
            this.progressNotification.innerHTML = '';
            
            // Create completion message
            let completionMessage;
            let messageType;
            
            if (isTimeout) {
                completionMessage = '⚠️ 更新完成检查超时';
                messageType = 'warning';
                this.progressNotification.style.backgroundColor = '#ffc107';
                this.progressNotification.style.color = '#212529';
            } else if (newArticlesCount > 0) {
                completionMessage = `✅ 完成！新增 ${newArticlesCount} 篇文章`;
                messageType = 'success';
                this.progressNotification.style.backgroundColor = '#28a745';
            } else {
                completionMessage = '✅ 完成！没有新增新闻';
                messageType = 'info';
                this.progressNotification.style.backgroundColor = '#17a2b8';
            }
            
            // Create completion content with icon and message
            const completionContainer = document.createElement('div');
            completionContainer.style.cssText = `
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
            `;
            
            // Create completion icon (checkmark or warning)
            const icon = document.createElement('div');
            icon.style.cssText = `
                font-size: 20px;
                animation: completionPulse 2s ease-in-out infinite;
            `;
            icon.textContent = isTimeout ? '⚠️' : '✅';
            
            // Create completion text
            const textElement = document.createElement('span');
            textElement.style.cssText = `
                font-weight: 600;
                animation: completionPulse 2s ease-in-out infinite;
            `;
            textElement.textContent = completionMessage.replace(/^[✅⚠️]\s*/, ''); // Remove emoji from text since we have it in icon
            
            completionContainer.appendChild(icon);
            completionContainer.appendChild(textElement);
            this.progressNotification.appendChild(completionContainer);
            
            // Add completion animation CSS if not already added
            this.addCompletionAnimationCSS();
            
            console.log(`📢 Updated progress notification to show completion: ${completionMessage}`);
        }
    }
    
    addCompletionAnimationCSS() {
        // Check if CSS is already added
        if (document.getElementById('completion-animation-css')) {
            return;
        }
        
        // Add CSS animation for completion
        const style = document.createElement('style');
        style.id = 'completion-animation-css';
        style.textContent = `
            @keyframes completionPulse {
                0%, 100% { 
                    opacity: 1; 
                    transform: scale(1);
                }
                50% { 
                    opacity: 0.8; 
                    transform: scale(1.05);
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    async exportToCSV() {
        // Export all articles in the database
        const statusDiv = this.showSimpleStatus('⏳ 正在导出所有文章...');
        
        try {
            // Export all articles (no filters, high limit)
            const params = {
                include_content: true,
                max_records: 1000  // Export up to 1000 articles
            };
            
            console.log('📤 Exporting all articles:', params);
            
            // Call export API
            const response = await fetch('/api/export/csv', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });
            
            const result = await response.json();
            console.log('📥 Export result:', result);
            
            if (result.success) {
                this.updateStatus(statusDiv, 'success', `✅ 导出成功! 共 ${result.articles_count} 条记录`);
                
                // Auto download
                setTimeout(() => {
                    window.location.href = result.download_url;
                    setTimeout(() => {
                        statusDiv.remove();
                    }, 2000);
                }, 500);
            } else {
                this.updateStatus(statusDiv, 'error', `❌ 导出失败: ${result.message}`);
            }
            
        } catch (error) {
            console.error('❌ Export error:', error);
            this.updateStatus(statusDiv, 'error', `❌ 导出失败: ${error.message}`);
        }
    }
    
    showSimpleStatus(message) {
        // Create simple status notification - centered
        const statusDiv = document.createElement('div');
        statusDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #e8f8fa;
            color: #17a2b8;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            z-index: 1001;
            font-size: 16px;
            font-weight: 500;
            max-width: 350px;
            min-width: 200px;
            text-align: center;
        `;
        statusDiv.innerHTML = message;
        document.body.appendChild(statusDiv);
        return statusDiv;
    }
    
    updateStatus(statusDiv, type, message) {
        const colors = {
            success: { bg: '#d4edda', color: '#155724' },
            error: { bg: '#f8d7da', color: '#721c24' },
            info: { bg: '#e8f8fa', color: '#17a2b8' }
        };
        
        const style = colors[type] || colors.info;
        statusDiv.style.background = style.bg;
        statusDiv.style.color = style.color;
        statusDiv.innerHTML = message;
    }
    
    showExportModal() {
        // Removed - using simple export instead
    }
    
    createExportModal() {
        // Removed - using simple export instead
    }
    
    async performExport() {
        // Removed - using simple export instead
    }
}

// Initialize dashboard
const dashboard = new DashboardController();
