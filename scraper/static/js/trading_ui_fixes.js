
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
