"""
Visualization Module

Creates charts and visualizations for trade risk analysis reports.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from io import BytesIO
import base64

from trade_risk_analyzer.core.base import Alert, RiskLevel, PatternType
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class Visualizer:
    """
    Main visualization class for creating charts and plots
    """
    
    def __init__(self):
        """Initialize visualizer"""
        self.logger = logger
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if matplotlib and seaborn are available"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            import seaborn as sns
            self.matplotlib_available = True
            self.plt = plt
            self.sns = sns
            
            # Set style
            sns.set_style("whitegrid")
            sns.set_palette("husl")
            
        except ImportError:
            self.logger.warning(
                "matplotlib/seaborn not installed. Visualizations will not be available. "
                "Install with: pip install matplotlib seaborn"
            )
            self.matplotlib_available = False
    
    def create_anomaly_score_distribution(
        self,
        alerts: List[Alert],
        output_path: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 6)
    ) -> Optional[str]:
        """
        Create histogram of anomaly score distribution
        
        Args:
            alerts: List of alerts
            output_path: Optional file path to save figure
            figsize: Figure size (width, height)
            
        Returns:
            Output path or base64 encoded image
        """
        if not self.matplotlib_available:
            raise ImportError("matplotlib is required for visualizations")
        
        if not alerts:
            self.logger.warning("No alerts provided for visualization")
            return None
        
        # Extract scores
        scores = [alert.anomaly_score for alert in alerts]
        
        # Create figure
        fig, ax = self.plt.subplots(figsize=figsize)
        
        # Create histogram
        ax.hist(scores, bins=20, edgecolor='black', alpha=0.7)
        
        # Add vertical lines for risk thresholds
        ax.axvline(x=80, color='red', linestyle='--', label='High Risk (80+)', linewidth=2)
        ax.axvline(x=50, color='orange', linestyle='--', label='Medium Risk (50-80)', linewidth=2)
        
        # Labels and title
        ax.set_xlabel('Anomaly Score', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Anomaly Score Distribution', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save or return
        if output_path:
            self.plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.plt.close()
            self.logger.info(f"Anomaly score distribution saved to {output_path}")
            return output_path
        else:
            # Return base64 encoded image
            buffer = BytesIO()
            self.plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            self.plt.close()
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            return f"data:image/png;base64,{image_base64}"
    
    def create_risk_level_distribution(
        self,
        alerts: List[Alert],
        output_path: Optional[str] = None,
        figsize: Tuple[int, int] = (8, 8)
    ) -> Optional[str]:
        """
        Create pie chart of risk level distribution
        
        Args:
            alerts: List of alerts
            output_path: Optional file path to save figure
            figsize: Figure size (width, height)
            
        Returns:
            Output path or base64 encoded image
        """
        if not self.matplotlib_available:
            raise ImportError("matplotlib is required for visualizations")
        
        if not alerts:
            self.logger.warning("No alerts provided for visualization")
            return None
        
        # Count by risk level
        risk_counts = {
            'HIGH': sum(1 for a in alerts if a.risk_level == RiskLevel.HIGH),
            'MEDIUM': sum(1 for a in alerts if a.risk_level == RiskLevel.MEDIUM),
            'LOW': sum(1 for a in alerts if a.risk_level == RiskLevel.LOW)
        }
        
        # Filter out zero counts
        risk_counts = {k: v for k, v in risk_counts.items() if v > 0}
        
        if not risk_counts:
            self.logger.warning("No risk levels to visualize")
            return None
        
        # Create figure
        fig, ax = self.plt.subplots(figsize=figsize)
        
        # Colors for risk levels
        colors = {
            'HIGH': '#ff4444',
            'MEDIUM': '#ffaa00',
            'LOW': '#44ff44'
        }
        
        pie_colors = [colors[level] for level in risk_counts.keys()]
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            risk_counts.values(),
            labels=risk_counts.keys(),
            autopct='%1.1f%%',
            colors=pie_colors,
            startangle=90,
            textprops={'fontsize': 12}
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Risk Level Distribution', fontsize=14, fontweight='bold')
        
        # Save or return
        if output_path:
            self.plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.plt.close()
            self.logger.info(f"Risk level distribution saved to {output_path}")
            return output_path
        else:
            buffer = BytesIO()
            self.plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            self.plt.close()
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            return f"data:image/png;base64,{image_base64}"
    
    def create_time_series_plot(
        self,
        alerts: List[Alert],
        output_path: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 6),
        resample_freq: str = 'D'
    ) -> Optional[str]:
        """
        Create time series plot of alerts over time
        
        Args:
            alerts: List of alerts
            output_path: Optional file path to save figure
            figsize: Figure size (width, height)
            resample_freq: Resampling frequency ('H'=hourly, 'D'=daily, 'W'=weekly)
            
        Returns:
            Output path or base64 encoded image
        """
        if not self.matplotlib_available:
            raise ImportError("matplotlib is required for visualizations")
        
        if not alerts:
            self.logger.warning("No alerts provided for visualization")
            return None
        
        # Create DataFrame
        df = pd.DataFrame([
            {
                'timestamp': alert.timestamp,
                'anomaly_score': alert.anomaly_score,
                'risk_level': alert.risk_level.value
            }
            for alert in alerts
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Create figure with subplots
        fig, (ax1, ax2) = self.plt.subplots(2, 1, figsize=figsize, sharex=True)
        
        # Plot 1: Alert count over time
        alert_counts = df.resample(resample_freq).size()
        ax1.plot(alert_counts.index, alert_counts.values, marker='o', linewidth=2)
        ax1.fill_between(alert_counts.index, alert_counts.values, alpha=0.3)
        ax1.set_ylabel('Alert Count', fontsize=12)
        ax1.set_title('Alerts Over Time', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Average anomaly score over time
        avg_scores = df['anomaly_score'].resample(resample_freq).mean()
        ax2.plot(avg_scores.index, avg_scores.values, marker='o', color='orange', linewidth=2)
        ax2.fill_between(avg_scores.index, avg_scores.values, alpha=0.3, color='orange')
        
        # Add risk threshold lines
        ax2.axhline(y=80, color='red', linestyle='--', label='High Risk', alpha=0.7)
        ax2.axhline(y=50, color='orange', linestyle='--', label='Medium Risk', alpha=0.7)
        
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Avg Anomaly Score', fontsize=12)
        ax2.set_title('Average Anomaly Score Over Time', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        self.plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        self.plt.tight_layout()
        
        # Save or return
        if output_path:
            self.plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.plt.close()
            self.logger.info(f"Time series plot saved to {output_path}")
            return output_path
        else:
            buffer = BytesIO()
            self.plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            self.plt.close()
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            return f"data:image/png;base64,{image_base64}"
    
    def create_temporal_heatmap(
        self,
        alerts: List[Alert],
        output_path: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 8)
    ) -> Optional[str]:
        """
        Create heatmap showing alert patterns by hour and day of week
        
        Args:
            alerts: List of alerts
            output_path: Optional file path to save figure
            figsize: Figure size (width, height)
            
        Returns:
            Output path or base64 encoded image
        """
        if not self.matplotlib_available:
            raise ImportError("matplotlib is required for visualizations")
        
        if not alerts:
            self.logger.warning("No alerts provided for visualization")
            return None
        
        # Create DataFrame
        df = pd.DataFrame([
            {
                'timestamp': alert.timestamp,
                'hour': alert.timestamp.hour,
                'day_of_week': alert.timestamp.strftime('%A'),
                'anomaly_score': alert.anomaly_score
            }
            for alert in alerts
        ])
        
        # Create pivot table for heatmap
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Count alerts by hour and day
        heatmap_data = df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
        
        # Reorder days
        heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])
        
        # Create figure
        fig, ax = self.plt.subplots(figsize=figsize)
        
        # Create heatmap
        im = self.sns.heatmap(
            heatmap_data,
            cmap='YlOrRd',
            annot=True,
            fmt='d',
            cbar_kws={'label': 'Alert Count'},
            ax=ax
        )
        
        ax.set_xlabel('Hour of Day', fontsize=12)
        ax.set_ylabel('Day of Week', fontsize=12)
        ax.set_title('Alert Temporal Distribution Heatmap', fontsize=14, fontweight='bold')
        
        # Save or return
        if output_path:
            self.plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.plt.close()
            self.logger.info(f"Temporal heatmap saved to {output_path}")
            return output_path
        else:
            buffer = BytesIO()
            self.plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            self.plt.close()
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            return f"data:image/png;base64,{image_base64}"
    
    def create_pattern_distribution(
        self,
        alerts: List[Alert],
        output_path: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 6)
    ) -> Optional[str]:
        """
        Create bar chart of pattern type distribution
        
        Args:
            alerts: List of alerts
            output_path: Optional file path to save figure
            figsize: Figure size (width, height)
            
        Returns:
            Output path or base64 encoded image
        """
        if not self.matplotlib_available:
            raise ImportError("matplotlib is required for visualizations")
        
        if not alerts:
            self.logger.warning("No alerts provided for visualization")
            return None
        
        # Count by pattern type
        pattern_counts = {}
        for pattern_type in PatternType:
            count = sum(1 for a in alerts if a.pattern_type == pattern_type)
            if count > 0:
                pattern_counts[pattern_type.value] = count
        
        if not pattern_counts:
            self.logger.warning("No patterns to visualize")
            return None
        
        # Sort by count
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        patterns, counts = zip(*sorted_patterns)
        
        # Create figure
        fig, ax = self.plt.subplots(figsize=figsize)
        
        # Create bar chart
        bars = ax.bar(range(len(patterns)), counts, edgecolor='black', alpha=0.7)
        
        # Color bars by count (gradient)
        colors = self.plt.cm.viridis(np.linspace(0.3, 0.9, len(bars)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        # Labels and title
        ax.set_xlabel('Pattern Type', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title('Alert Distribution by Pattern Type', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(patterns)))
        ax.set_xticklabels(patterns, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for i, (pattern, count) in enumerate(zip(patterns, counts)):
            ax.text(i, count, str(count), ha='center', va='bottom', fontweight='bold')
        
        self.plt.tight_layout()
        
        # Save or return
        if output_path:
            self.plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.plt.close()
            self.logger.info(f"Pattern distribution saved to {output_path}")
            return output_path
        else:
            buffer = BytesIO()
            self.plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            self.plt.close()
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            return f"data:image/png;base64,{image_base64}"
    
    def create_user_risk_comparison(
        self,
        user_scores: Dict[str, float],
        output_path: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 6),
        top_n: int = 20
    ) -> Optional[str]:
        """
        Create bar chart comparing risk scores across users
        
        Args:
            user_scores: Dictionary mapping user_id to risk score
            output_path: Optional file path to save figure
            figsize: Figure size (width, height)
            top_n: Number of top users to show
            
        Returns:
            Output path or base64 encoded image
        """
        if not self.matplotlib_available:
            raise ImportError("matplotlib is required for visualizations")
        
        if not user_scores:
            self.logger.warning("No user scores provided for visualization")
            return None
        
        # Sort by score and take top N
        sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        users, scores = zip(*sorted_users)
        
        # Create figure
        fig, ax = self.plt.subplots(figsize=figsize)
        
        # Create bar chart
        bars = ax.barh(range(len(users)), scores, edgecolor='black', alpha=0.7)
        
        # Color bars by risk level
        for i, (bar, score) in enumerate(zip(bars, scores)):
            if score >= 80:
                bar.set_color('#ff4444')
            elif score >= 50:
                bar.set_color('#ffaa00')
            else:
                bar.set_color('#44ff44')
        
        # Add risk threshold lines
        ax.axvline(x=80, color='red', linestyle='--', label='High Risk', alpha=0.7)
        ax.axvline(x=50, color='orange', linestyle='--', label='Medium Risk', alpha=0.7)
        
        # Labels and title
        ax.set_xlabel('Risk Score', fontsize=12)
        ax.set_ylabel('User ID', fontsize=12)
        ax.set_title(f'Top {len(users)} Users by Risk Score', fontsize=14, fontweight='bold')
        ax.set_yticks(range(len(users)))
        ax.set_yticklabels(users)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        
        # Invert y-axis so highest score is on top
        ax.invert_yaxis()
        
        self.plt.tight_layout()
        
        # Save or return
        if output_path:
            self.plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.plt.close()
            self.logger.info(f"User risk comparison saved to {output_path}")
            return output_path
        else:
            buffer = BytesIO()
            self.plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            self.plt.close()
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            return f"data:image/png;base64,{image_base64}"
    
    def create_dashboard(
        self,
        alerts: List[Alert],
        output_path: str,
        figsize: Tuple[int, int] = (16, 12)
    ) -> str:
        """
        Create comprehensive dashboard with multiple visualizations
        
        Args:
            alerts: List of alerts
            output_path: File path to save figure
            figsize: Figure size (width, height)
            
        Returns:
            Output path
        """
        if not self.matplotlib_available:
            raise ImportError("matplotlib is required for visualizations")
        
        if not alerts:
            self.logger.warning("No alerts provided for dashboard")
            return None
        
        # Create figure with subplots
        fig = self.plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. Anomaly score distribution
        ax1 = fig.add_subplot(gs[0, 0])
        scores = [alert.anomaly_score for alert in alerts]
        ax1.hist(scores, bins=20, edgecolor='black', alpha=0.7)
        ax1.axvline(x=80, color='red', linestyle='--', linewidth=2)
        ax1.axvline(x=50, color='orange', linestyle='--', linewidth=2)
        ax1.set_xlabel('Anomaly Score')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Anomaly Score Distribution', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 2. Risk level distribution
        ax2 = fig.add_subplot(gs[0, 1])
        risk_counts = {
            'HIGH': sum(1 for a in alerts if a.risk_level == RiskLevel.HIGH),
            'MEDIUM': sum(1 for a in alerts if a.risk_level == RiskLevel.MEDIUM),
            'LOW': sum(1 for a in alerts if a.risk_level == RiskLevel.LOW)
        }
        risk_counts = {k: v for k, v in risk_counts.items() if v > 0}
        colors = {'HIGH': '#ff4444', 'MEDIUM': '#ffaa00', 'LOW': '#44ff44'}
        pie_colors = [colors[level] for level in risk_counts.keys()]
        ax2.pie(risk_counts.values(), labels=risk_counts.keys(), autopct='%1.1f%%',
                colors=pie_colors, startangle=90)
        ax2.set_title('Risk Level Distribution', fontweight='bold')
        
        # 3. Pattern distribution
        ax3 = fig.add_subplot(gs[1, :])
        pattern_counts = {}
        for pattern_type in PatternType:
            count = sum(1 for a in alerts if a.pattern_type == pattern_type)
            if count > 0:
                pattern_counts[pattern_type.value] = count
        
        if pattern_counts:
            sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
            patterns, counts = zip(*sorted_patterns)
            bars = ax3.bar(range(len(patterns)), counts, edgecolor='black', alpha=0.7)
            ax3.set_xlabel('Pattern Type')
            ax3.set_ylabel('Count')
            ax3.set_title('Alert Distribution by Pattern Type', fontweight='bold')
            ax3.set_xticks(range(len(patterns)))
            ax3.set_xticklabels(patterns, rotation=45, ha='right')
            ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Time series
        ax4 = fig.add_subplot(gs[2, :])
        df = pd.DataFrame([
            {'timestamp': alert.timestamp, 'anomaly_score': alert.anomaly_score}
            for alert in alerts
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        alert_counts = df.resample('D').size()
        ax4.plot(alert_counts.index, alert_counts.values, marker='o', linewidth=2)
        ax4.fill_between(alert_counts.index, alert_counts.values, alpha=0.3)
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Alert Count')
        ax4.set_title('Alerts Over Time', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        self.plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Overall title
        fig.suptitle('Trade Risk Analysis Dashboard', fontsize=16, fontweight='bold', y=0.995)
        
        # Save
        self.plt.savefig(output_path, dpi=300, bbox_inches='tight')
        self.plt.close()
        
        self.logger.info(f"Dashboard saved to {output_path}")
        return output_path
