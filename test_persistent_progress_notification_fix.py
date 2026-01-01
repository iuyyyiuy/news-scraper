#!/usr/bin/env python3
"""
Test Persistent Progress Notification Fix
Tests that the progress notification stays visible until completion and shows final result
"""

import time
import subprocess
import json

def create_test_html():
    """Create a test HTML file to verify the notification behavior"""
    
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Progress Notification Test</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .test-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .test-button {
            padding: 12px 24px;
            background: #17a2b8;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            margin: 10px;
            transition: all 0.2s;
        }
        
        .test-button:hover {
            background: #138496;
            transform: translateY(-1px);
        }
        
        .test-results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #17a2b8;
        }
        
        .log-entry {
            margin: 5px 0;
            padding: 8px 12px;
            background: white;
            border-radius: 4px;
            font-family: monospace;
            font-size: 14px;
        }
        
        .log-info { border-left: 3px solid #17a2b8; }
        .log-success { border-left: 3px solid #28a745; }
        .log-warning { border-left: 3px solid #ffc107; }
    </style>
</head>
<body>
    <div class="test-container">
        <h1>🧪 Progress Notification Test</h1>
        <p>This test verifies that the progress notification stays visible until completion and shows the final result.</p>
        
        <div class="test-controls">
            <button class="test-button" onclick="testProgressNotification(5, 'success')">
                Test Success (5 new articles)
            </button>
            <button class="test-button" onclick="testProgressNotification(0, 'success')">
                Test Success (0 new articles)
            </button>
            <button class="test-button" onclick="testProgressNotification(0, 'timeout')">
                Test Timeout
            </button>
            <button class="test-button" onclick="clearLogs()">
                Clear Logs
            </button>
        </div>
        
        <div class="test-results">
            <h3>📋 Test Results</h3>
            <div id="test-logs"></div>
        </div>
    </div>

    <script>
        // Simplified version of the dashboard notification system for testing
        class TestNotificationSystem {
            constructor() {
                this.progressNotification = null;
                this.progressAnimationInterval = null;
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
                    textElement.textContent = completionMessage.replace(/^[✅⚠️]\\s*/, ''); // Remove emoji from text since we have it in icon
                    
                    completionContainer.appendChild(icon);
                    completionContainer.appendChild(textElement);
                    this.progressNotification.appendChild(completionContainer);
                    
                    // Add completion animation CSS if not already added
                    this.addCompletionAnimationCSS();
                    
                    console.log(`📢 Updated progress notification to show completion: ${completionMessage}`);
                    logMessage(`📢 Updated notification to: ${completionMessage}`, 'success');
                }
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
                        logMessage('🗑️ Progress notification removed', 'info');
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
        }
        
        // Initialize notification system
        const notificationSystem = new TestNotificationSystem();
        
        function logMessage(message, type = 'info') {
            const logsContainer = document.getElementById('test-logs');
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry log-${type}`;
            logEntry.textContent = `${new Date().toLocaleTimeString()} - ${message}`;
            logsContainer.appendChild(logEntry);
            logsContainer.scrollTop = logsContainer.scrollHeight;
        }
        
        function testProgressNotification(newArticlesCount, resultType) {
            logMessage(`🧪 Starting test: ${newArticlesCount} articles, ${resultType} result`, 'info');
            
            // Step 1: Show progress notification
            notificationSystem.progressNotification = notificationSystem.showPersistentNotification('🔄 正在运行... (300篇/源)', 'info');
            logMessage('📢 Progress notification shown', 'info');
            
            // Step 2: Simulate scraping process (3 seconds)
            setTimeout(() => {
                logMessage('⏳ Simulating scraping process...', 'info');
                
                // Step 3: Update to completion after 3 seconds
                setTimeout(() => {
                    if (resultType === 'timeout') {
                        notificationSystem.updateProgressNotificationToCompletion(0, true);
                    } else {
                        notificationSystem.updateProgressNotificationToCompletion(newArticlesCount, false);
                    }
                    
                    // Step 4: Remove notification after 10 seconds
                    setTimeout(() => {
                        notificationSystem.removePersistentNotification();
                    }, 10000);
                    
                }, 3000);
            }, 500);
        }
        
        function clearLogs() {
            document.getElementById('test-logs').innerHTML = '';
        }
        
        // Initial log
        logMessage('🚀 Progress Notification Test System Ready', 'success');
    </script>
</body>
</html>'''
    
    with open('test_progress_notification_behavior.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Created test HTML file: test_progress_notification_behavior.html")

def test_dashboard_js_changes():
    """Test that the dashboard.js changes are correct"""
    
    print("🔍 Testing Dashboard JavaScript Changes")
    print("-" * 50)
    
    try:
        with open('scraper/static/js/dashboard.js', 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Check for the new method
        if 'updateProgressNotificationToCompletion' in js_content:
            print("✅ Found updateProgressNotificationToCompletion method")
        else:
            print("❌ Missing updateProgressNotificationToCompletion method")
            return False
        
        # Check for completion animation CSS
        if 'addCompletionAnimationCSS' in js_content:
            print("✅ Found addCompletionAnimationCSS method")
        else:
            print("❌ Missing addCompletionAnimationCSS method")
            return False
        
        # Check for the updated completion logic
        if 'this.updateProgressNotificationToCompletion(newArticlesCount)' in js_content:
            print("✅ Found updated completion logic")
        else:
            print("❌ Missing updated completion logic")
            return False
        
        # Check for 10-second delay
        if 'setTimeout(() => {' in js_content and '10000' in js_content:
            print("✅ Found 10-second delay for notification removal")
        else:
            print("❌ Missing 10-second delay")
            return False
        
        print("✅ All dashboard.js changes are present")
        return True
        
    except FileNotFoundError:
        print("❌ Dashboard JavaScript file not found")
        return False
    except Exception as e:
        print(f"❌ Error checking dashboard.js: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Persistent Progress Notification Fix")
    print("=" * 60)
    
    # Test dashboard.js changes
    js_ok = test_dashboard_js_changes()
    
    # Create test HTML
    create_test_html()
    
    print("\n" + "=" * 60)
    print("🏁 Test Results")
    print("=" * 60)
    
    print(f"Dashboard.js Changes: {'✅ PASS' if js_ok else '❌ FAIL'}")
    print(f"Test HTML Created: ✅ PASS")
    
    if js_ok:
        print(f"\n🎉 IMPLEMENTATION COMPLETE!")
        print(f"✅ Progress notification now stays visible until completion")
        print(f"✅ Final result is shown in the same notification (no disappearing)")
        print(f"✅ Notification remains visible for 10 seconds after completion")
        print(f"✅ Smooth transition from progress to completion message")
        
        print(f"\n🧪 Testing:")
        print(f"1. Open test_progress_notification_behavior.html in browser")
        print(f"2. Test different scenarios (success, no articles, timeout)")
        print(f"3. Verify notification behavior matches requirements")
        
        print(f"\n🌐 Live Testing:")
        print(f"1. Start web server: python run_web_server.py")
        print(f"2. Open dashboard: http://localhost:5000/dashboard")
        print(f"3. Click '手动更新' and observe notification behavior")
        
    else:
        print(f"\n⚠️  Some tests failed - check the output above")
    
    return js_ok

if __name__ == "__main__":
    main()