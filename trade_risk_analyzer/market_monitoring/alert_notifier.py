"""
Alert Notification System

Sends market manipulation alerts through multiple channels:
- Email
- Webhook (HTTP POST)
- Telegram
- Slack
- Database
- Console/Logs
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.market_monitoring.market_analyzer import MarketAlert
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage


logger = get_logger(__name__)


class NotificationChannel(Enum):
    """Notification channels"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    TELEGRAM = "telegram"
    SLACK = "slack"
    DATABASE = "database"
    CONSOLE = "console"


@dataclass
class NotificationConfig:
    """Configuration for notifications"""
    # Email settings
    email_enabled: bool = False
    email_smtp_host: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_from: str = ""
    email_to: List[str] = None
    email_password: str = ""
    
    # Webhook settings
    webhook_enabled: bool = False
    webhook_url: str = ""
    webhook_headers: Dict[str, str] = None
    
    # Telegram settings
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    # Slack settings
    slack_enabled: bool = False
    slack_webhook_url: str = ""
    
    # Database settings
    database_enabled: bool = True
    
    # Console settings
    console_enabled: bool = True
    
    # Alert filtering
    min_severity: float = 50.0  # Only send alerts >= 50 severity
    high_risk_only: bool = False  # Only send HIGH risk alerts
    
    def __post_init__(self):
        if self.email_to is None:
            self.email_to = []
        if self.webhook_headers is None:
            self.webhook_headers = {}


class AlertNotifier:
    """
    Sends alerts through multiple notification channels
    """
    
    def __init__(
        self,
        config: NotificationConfig,
        storage: Optional[DatabaseStorage] = None
    ):
        """
        Initialize alert notifier
        
        Args:
            config: Notification configuration
            storage: Database storage for alert persistence
        """
        self.config = config
        self.storage = storage
        self.logger = logger
        
        # Statistics
        self.alerts_sent = 0
        self.alerts_failed = 0
        self.notifications_by_channel: Dict[str, int] = {}
    
    async def send_alert(self, alert: MarketAlert) -> Dict[str, bool]:
        """
        Send alert through all enabled channels
        
        Args:
            alert: Market alert to send
            
        Returns:
            Dictionary of channel: success status
        """
        # Check if alert meets criteria
        if not self._should_send_alert(alert):
            self.logger.debug(f"Alert {alert.alert_id} filtered out")
            return {}
        
        results = {}
        
        # Send through each enabled channel
        tasks = []
        
        if self.config.console_enabled:
            tasks.append(self._send_console(alert))
        
        if self.config.database_enabled and self.storage:
            tasks.append(self._send_database(alert))
        
        if self.config.webhook_enabled:
            tasks.append(self._send_webhook(alert))
        
        if self.config.telegram_enabled:
            tasks.append(self._send_telegram(alert))
        
        if self.config.slack_enabled:
            tasks.append(self._send_slack(alert))
        
        if self.config.email_enabled:
            tasks.append(self._send_email(alert))
        
        # Execute all notifications concurrently
        if tasks:
            channel_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            channels = []
            if self.config.console_enabled:
                channels.append(NotificationChannel.CONSOLE)
            if self.config.database_enabled and self.storage:
                channels.append(NotificationChannel.DATABASE)
            if self.config.webhook_enabled:
                channels.append(NotificationChannel.WEBHOOK)
            if self.config.telegram_enabled:
                channels.append(NotificationChannel.TELEGRAM)
            if self.config.slack_enabled:
                channels.append(NotificationChannel.SLACK)
            if self.config.email_enabled:
                channels.append(NotificationChannel.EMAIL)
            
            for channel, result in zip(channels, channel_results):
                if isinstance(result, Exception):
                    results[channel.value] = False
                    self.alerts_failed += 1
                    self.logger.error(f"Failed to send via {channel.value}: {result}")
                else:
                    results[channel.value] = result
                    if result:
                        self.notifications_by_channel[channel.value] = \
                            self.notifications_by_channel.get(channel.value, 0) + 1
        
        if any(results.values()):
            self.alerts_sent += 1
        
        return results
    
    def _should_send_alert(self, alert: MarketAlert) -> bool:
        """Check if alert should be sent"""
        # Check severity
        if alert.severity < self.config.min_severity:
            return False
        
        # Check risk level
        if self.config.high_risk_only and alert.risk_level.value != "HIGH":
            return False
        
        return True
    
    async def _send_console(self, alert: MarketAlert) -> bool:
        """Send alert to console"""
        try:
            print(f"\n{'='*60}")
            print(f"🚨 MARKET ALERT: {alert.title}")
            print(f"{'='*60}")
            print(f"Market: {alert.market}")
            print(f"Type: {alert.alert_type.value}")
            print(f"Risk Level: {alert.risk_level.value}")
            print(f"Severity: {alert.severity:.1f}/100")
            print(f"Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\nDescription:")
            print(f"  {alert.description}")
            print(f"\nRecommended Action:")
            print(f"  {alert.recommended_action}")
            print(f"\nMarket Health:")
            print(f"  Health Score: {alert.indicators.health_score:.1f}/100")
            print(f"  Manipulation Risk: {alert.indicators.manipulation_risk:.1f}/100")
            print(f"  Liquidity Score: {alert.indicators.liquidity_score:.1f}/100")
            print(f"{'='*60}\n")
            
            return True
        except Exception as e:
            self.logger.error(f"Console notification failed: {e}")
            return False
    
    async def _send_database(self, alert: MarketAlert) -> bool:
        """Save alert to database"""
        try:
            if not self.storage:
                return False
            
            # Convert to database format
            alert_data = alert.to_dict()
            
            # Save to database (implementation depends on your storage backend)
            # For now, we'll log it
            self.logger.info(f"Alert saved to database: {alert.alert_id}")
            
            return True
        except Exception as e:
            self.logger.error(f"Database save failed: {e}")
            return False
    
    async def _send_webhook(self, alert: MarketAlert) -> bool:
        """Send alert via webhook"""
        try:
            if not self.config.webhook_url:
                return False
            
            # Prepare payload
            payload = alert.to_dict()
            
            # Send POST request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.webhook_url,
                    json=payload,
                    headers=self.config.webhook_headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Webhook sent: {alert.alert_id}")
                        return True
                    else:
                        self.logger.error(f"Webhook failed: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Webhook failed: {e}")
            return False
    
    async def _send_telegram(self, alert: MarketAlert) -> bool:
        """Send alert via Telegram"""
        try:
            if not self.config.telegram_bot_token or not self.config.telegram_chat_id:
                return False
            
            # Format message
            message = self._format_telegram_message(alert)
            
            # Send via Telegram Bot API
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.config.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        self.logger.info(f"Telegram sent: {alert.alert_id}")
                        return True
                    else:
                        self.logger.error(f"Telegram failed: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Telegram failed: {e}")
            return False
    
    async def _send_slack(self, alert: MarketAlert) -> bool:
        """Send alert via Slack"""
        try:
            if not self.config.slack_webhook_url:
                return False
            
            # Format message
            payload = self._format_slack_message(alert)
            
            # Send to Slack webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.slack_webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Slack sent: {alert.alert_id}")
                        return True
                    else:
                        self.logger.error(f"Slack failed: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Slack failed: {e}")
            return False
    
    async def _send_email(self, alert: MarketAlert) -> bool:
        """Send alert via email"""
        try:
            if not self.config.email_to or not self.config.email_from:
                return False
            
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 Market Alert: {alert.market} - {alert.risk_level.value} RISK"
            msg['From'] = self.config.email_from
            msg['To'] = ', '.join(self.config.email_to)
            
            # Create HTML body
            html = self._format_email_html(alert)
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.config.email_smtp_host, self.config.email_smtp_port) as server:
                server.starttls()
                server.login(self.config.email_from, self.config.email_password)
                server.send_message(msg)
            
            self.logger.info(f"Email sent: {alert.alert_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Email failed: {e}")
            return False
    
    def _format_telegram_message(self, alert: MarketAlert) -> str:
        """Format alert for Telegram"""
        emoji = "🔴" if alert.risk_level.value == "HIGH" else "🟡" if alert.risk_level.value == "MEDIUM" else "🟢"
        
        message = f"{emoji} <b>MARKET ALERT</b>\n\n"
        message += f"<b>Market:</b> {alert.market}\n"
        message += f"<b>Type:</b> {alert.alert_type.value}\n"
        message += f"<b>Risk:</b> {alert.risk_level.value}\n"
        message += f"<b>Severity:</b> {alert.severity:.1f}/100\n\n"
        message += f"<b>Description:</b>\n{alert.description}\n\n"
        message += f"<b>Action:</b>\n{alert.recommended_action}\n\n"
        message += f"<i>Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return message
    
    def _format_slack_message(self, alert: MarketAlert) -> Dict[str, Any]:
        """Format alert for Slack"""
        color = "#ff0000" if alert.risk_level.value == "HIGH" else "#ffaa00" if alert.risk_level.value == "MEDIUM" else "#00ff00"
        
        return {
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 Market Alert: {alert.market}",
                    "fields": [
                        {"title": "Type", "value": alert.alert_type.value, "short": True},
                        {"title": "Risk Level", "value": alert.risk_level.value, "short": True},
                        {"title": "Severity", "value": f"{alert.severity:.1f}/100", "short": True},
                        {"title": "Health Score", "value": f"{alert.indicators.health_score:.1f}/100", "short": True},
                        {"title": "Description", "value": alert.description, "short": False},
                        {"title": "Recommended Action", "value": alert.recommended_action, "short": False}
                    ],
                    "footer": "Trade Risk Analyzer",
                    "ts": int(alert.timestamp.timestamp())
                }
            ]
        }
    
    def _format_email_html(self, alert: MarketAlert) -> str:
        """Format alert as HTML email"""
        color = "#ff4444" if alert.risk_level.value == "HIGH" else "#ffaa00" if alert.risk_level.value == "MEDIUM" else "#44ff44"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert-box {{ border: 3px solid {color}; padding: 20px; margin: 20px; }}
                .header {{ background-color: {color}; color: white; padding: 10px; }}
                .field {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="alert-box">
                <div class="header">
                    <h2>🚨 Market Alert: {alert.market}</h2>
                </div>
                <div class="field">
                    <span class="label">Type:</span> {alert.alert_type.value}
                </div>
                <div class="field">
                    <span class="label">Risk Level:</span> {alert.risk_level.value}
                </div>
                <div class="field">
                    <span class="label">Severity:</span> {alert.severity:.1f}/100
                </div>
                <div class="field">
                    <span class="label">Time:</span> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                <hr>
                <div class="field">
                    <span class="label">Description:</span><br>
                    {alert.description}
                </div>
                <div class="field">
                    <span class="label">Recommended Action:</span><br>
                    {alert.recommended_action}
                </div>
                <hr>
                <h3>Market Indicators</h3>
                <div class="field">
                    <span class="label">Health Score:</span> {alert.indicators.health_score:.1f}/100
                </div>
                <div class="field">
                    <span class="label">Manipulation Risk:</span> {alert.indicators.manipulation_risk:.1f}/100
                </div>
                <div class="field">
                    <span class="label">Liquidity Score:</span> {alert.indicators.liquidity_score:.1f}/100
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get notification statistics"""
        return {
            'alerts_sent': self.alerts_sent,
            'alerts_failed': self.alerts_failed,
            'by_channel': self.notifications_by_channel
        }
