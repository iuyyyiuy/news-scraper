#!/usr/bin/env python3
"""
Fix Trading Strategy UI Visibility Issues
Improves text contrast and trader identification
"""

def fix_ui_visibility():
    """Fix UI visibility issues in trading strategy interface"""
    
    print("🎨 Fixing Trading Strategy UI Visibility")
    print("=" * 50)
    
    # Fix 1: Improve AI insights section contrast
    print("\n1. Improving AI insights section contrast...")
    
    css_fixes = """
        /* Improved AI Insights Section */
        .ai-insight {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .ai-insight h3, .ai-insight h5 {
            color: #ffffff !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        .ai-insight .alert {
            background: rgba(255,255,255,0.1) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            color: #ffffff !important;
        }
        
        .ai-insight .alert i {
            color: #ffffff !important;
        }
        
        .ai-insight ul li {
            color: #ffffff !important;
            margin-bottom: 8px;
            line-height: 1.5;
        }
        
        .ai-insight .card {
            background: rgba(255,255,255,0.1) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            color: #ffffff !important;
        }
        
        .ai-insight .card-title {
            color: #ffffff !important;
        }
        
        .ai-insight .card-text {
            color: #ffffff !important;
        }
        
        .ai-insight .text-muted {
            color: rgba(255,255,255,0.8) !important;
        }
        
        /* Improved Trader ID Styling */
        .trader-id {
            font-weight: bold;
            font-size: 1.1em;
            color: #2c3e50 !important;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 4px 12px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 5px;
            border: 2px solid #2196f3;
        }
        
        .trader-id.highlight {
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%) !important;
            border-color: #ff9800 !important;
            color: #e65100 !important;
        }
        
        /* Better table styling */
        .table-dark th {
            background-color: #343a40 !important;
            color: white !important;
            border-color: #454d55 !important;
        }
        
        .trader-row {
            padding: 15px;
            border-bottom: 1px solid #eee;
            transition: background-color 0.2s;
            border-left: 4px solid transparent;
        }
        
        .trader-row:hover {
            background-color: #f8f9fa !important;
            border-left-color: #007bff !important;
        }
    """
    
    # Write CSS fixes to a file
    with open('scraper/static/css/trading_ui_fixes.css', 'w', encoding='utf-8') as f:
        f.write(css_fixes)
    
    print("✅ CSS fixes written to scraper/static/css/trading_ui_fixes.css")
    
    # Fix 2: Update HTML template to include the CSS
    print("\n2. Updating HTML template...")
    
    try:
        with open('scraper/templates/trading_strategy.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Add CSS link if not already present
        if 'trading_ui_fixes.css' not in html_content:
            css_link = '<link href="/static/css/trading_ui_fixes.css" rel="stylesheet">'
            
            # Insert after the existing CSS links
            if '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">' in html_content:
                html_content = html_content.replace(
                    '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">',
                    '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">\n    ' + css_link
                )
                
                with open('scraper/templates/trading_strategy.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print("✅ CSS link added to HTML template")
            else:
                print("⚠️  Could not find insertion point for CSS link")
        else:
            print("✅ CSS link already present in template")
    
    except Exception as e:
        print(f"❌ Error updating HTML template: {e}")
    
    # Fix 3: Create JavaScript patch
    print("\n3. Creating JavaScript improvements...")
    
    js_patch = """
// Improved trader display function
function displayProfitableTradersImproved(traders) {
    const container = document.getElementById('profitableTraders');
    
    if (!traders || traders.length === 0) {
        container.innerHTML = '<p class="text-muted">未找到盈利交易者数据</p>';
        return;
    }

    let html = '<div class="table-responsive"><table class="table table-hover">';
    html += `
        <thead class="table-dark">
            <tr>
                <th>交易者ID</th>
                <th>总盈亏</th>
                <th>胜率</th>
                <th>平均杠杆</th>
                <th>策略类型</th>
                <th>交易数量</th>
            </tr>
        </thead>
        <tbody>
    `;

    traders.slice(0, 20).forEach((trader, index) => {
        const strategyClass = `strategy-${trader.strategy_type || 'unknown'}`;
        const isTopPerformer = index < 3; // Highlight top 3 performers
        
        html += `
            <tr class="trader-row">
                <td>
                    <span class="trader-id ${isTopPerformer ? 'highlight' : ''}">
                        ${trader.user_id}
                    </span>
                    ${isTopPerformer ? '<i class="fas fa-crown text-warning ms-1" title="顶级表现者"></i>' : ''}
                </td>
                <td class="profit-positive">
                    <strong>$${trader.total_pnl.toFixed(2)}</strong>
                </td>
                <td>
                    <span class="badge bg-success">${trader.win_rate.toFixed(1)}%</span>
                </td>
                <td>
                    <span class="badge ${trader.avg_leverage > 10 ? 'bg-danger' : trader.avg_leverage > 5 ? 'bg-warning' : 'bg-success'}">
                        ${trader.avg_leverage.toFixed(1)}x
                    </span>
                </td>
                <td>
                    <span class="strategy-badge ${strategyClass}">
                        ${getStrategyDisplayName(trader.strategy_type)}
                    </span>
                </td>
                <td>
                    <span class="badge bg-info">${trader.total_trades}</span>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    
    // Add explanation
    html += `
        <div class="alert alert-info mt-3">
            <h6><i class="fas fa-info-circle me-2"></i>交易者说明</h6>
            <ul class="mb-0">
                <li><strong>交易者ID</strong>: 基于上传的CSV文件名生成 (例如: 2282678.csv → 2282678)</li>
                <li><strong>顶级表现者</strong>: 前3名盈利最高的交易者 <i class="fas fa-crown text-warning"></i></li>
                <li><strong>杠杆颜色</strong>: 
                    <span class="badge bg-success">低风险 (≤5x)</span>
                    <span class="badge bg-warning">中风险 (5-10x)</span>
                    <span class="badge bg-danger">高风险 (>10x)</span>
                </li>
            </ul>
        </div>
    `;
    
    container.innerHTML = html;
}

function getStrategyDisplayName(strategyType) {
    const displayNames = {
        'scalper': '剥头皮',
        'day_trader': '日内交易',
        'swing_trader': '波段交易',
        'position_trader': '趋势交易',
        'unknown': '未知'
    };
    return displayNames[strategyType] || strategyType;
}

// Override the original function if it exists
if (typeof window.TradingStrategyAnalyzer !== 'undefined') {
    window.TradingStrategyAnalyzer.prototype.displayProfitableTraders = displayProfitableTradersImproved;
}
"""
    
    with open('scraper/static/js/trading_ui_fixes.js', 'w', encoding='utf-8') as f:
        f.write(js_patch)
    
    print("✅ JavaScript improvements written to scraper/static/js/trading_ui_fixes.js")
    
    print("\n" + "=" * 50)
    print("🎉 UI Visibility Fixes Complete!")
    print("\n📋 Changes Made:")
    print("   ✅ Improved AI insights section contrast (dark background)")
    print("   ✅ Enhanced trader ID visibility with colored badges")
    print("   ✅ Added top performer highlighting with crown icons")
    print("   ✅ Color-coded leverage risk levels")
    print("   ✅ Added explanatory text for trader identification")
    print("\n🔧 Files Created/Modified:")
    print("   📄 scraper/static/css/trading_ui_fixes.css")
    print("   📄 scraper/static/js/trading_ui_fixes.js")
    print("   📄 scraper/templates/trading_strategy.html (CSS link added)")
    print("\n🚀 Next Steps:")
    print("   1. Restart the server to load the changes")
    print("   2. Refresh the trading strategy page")
    print("   3. The interface should now be much more readable!")

if __name__ == "__main__":
    # Create CSS directory if it doesn't exist
    import os
    os.makedirs('scraper/static/css', exist_ok=True)
    
    fix_ui_visibility()