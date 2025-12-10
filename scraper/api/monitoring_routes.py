"""
API routes for system monitoring and alert logs.
"""

import json
import os
import glob
from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


def read_log_files() -> List[Dict[str, Any]]:
    """Read alert logs from JSON files."""
    logs = []
    
    try:
        # Find all alert log files
        log_files = glob.glob('alert_logs_*.json')
        
        for log_file in sorted(log_files, reverse=True):  # Most recent first
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                log_entry = json.loads(line)
                                logs.append(log_entry)
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                print(f"Error reading log file {log_file}: {e}")
                continue
    
    except Exception as e:
        print(f"Error reading log files: {e}")
    
    # Sort by timestamp (most recent first)
    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return logs


def read_session_files() -> List[Dict[str, Any]]:
    """Read session statistics from JSON files."""
    sessions = []
    
    try:
        # Find all session stats files
        session_files = glob.glob('session_stats_*.json')
        
        for session_file in sorted(session_files, reverse=True):  # Most recent first
            try:
                with open(session_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                session_entry = json.loads(line)
                                sessions.append(session_entry)
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                print(f"Error reading session file {session_file}: {e}")
                continue
    
    except Exception as e:
        print(f"Error reading session files: {e}")
    
    # Sort by start_time (most recent first)
    sessions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
    return sessions


@router.get('/logs')
def get_alert_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    limit: int = Query(50, description="Maximum number of logs to return", le=100)
):
    """Get recent alert logs."""
    try:
        logs = read_log_files()
        
        # Filter by level if specified
        if level and level.upper() in ['INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            logs = [log for log in logs if log.get('level') == level.upper()]
        
        # Limit results
        logs = logs[:limit]
        
        return logs
    
    except Exception as e:
        return {'error': str(e)}


@router.get('/sessions')
def get_scraping_sessions(
    limit: int = Query(20, description="Maximum number of sessions to return", le=50)
):
    """Get recent scraping sessions."""
    try:
        sessions = read_session_files()
        
        # Limit results
        sessions = sessions[:limit]
        
        return sessions
    
    except Exception as e:
        return {'error': str(e)}


@router.get('/health')
def get_system_health():
    """Get overall system health metrics."""
    try:
        logs = read_log_files()
        sessions = read_session_files()
        
        # Calculate health metrics
        recent_sessions = sessions[:5] if sessions else []
        
        if recent_sessions:
            # Calculate average success rate
            success_rates = []
            for session in recent_sessions:
                perf_metrics = session.get('performance_metrics', {})
                success_rate = perf_metrics.get('success_rate_percent', 0)
                success_rates.append(success_rate)
            
            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
            
            # Calculate average duration
            durations = []
            for session in recent_sessions:
                perf_metrics = session.get('performance_metrics', {})
                duration = perf_metrics.get('total_duration_seconds', 0)
                durations.append(duration)
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Count total errors in recent sessions
            total_errors = sum(session.get('errors_encountered', 0) for session in recent_sessions)
        else:
            avg_success_rate = 0
            avg_duration = 0
            total_errors = 0
        
        # Count recent errors and criticals from logs
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_errors = []
        recent_criticals = []
        
        for log in logs:
            try:
                log_time = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                if log_time >= recent_cutoff:
                    if log.get('level') == 'ERROR':
                        recent_errors.append(log)
                    elif log.get('level') == 'CRITICAL':
                        recent_criticals.append(log)
            except (ValueError, TypeError):
                continue
        
        # Determine overall health status
        if avg_success_rate >= 90 and len(recent_criticals) == 0:
            health_status = "HEALTHY"
        elif avg_success_rate >= 70 and len(recent_criticals) <= 1:
            health_status = "WARNING"
        else:
            health_status = "CRITICAL"
        
        # Get last session time
        last_session_time = None
        if recent_sessions:
            last_session_time = recent_sessions[0].get('start_time')
        
        health_data = {
            'health_status': health_status,
            'avg_success_rate_percent': avg_success_rate,
            'avg_session_duration_seconds': avg_duration,
            'recent_errors_count': len(recent_errors),
            'recent_criticals_count': len(recent_criticals),
            'total_recent_errors': total_errors,
            'last_session_time': last_session_time,
            'total_sessions': len(sessions),
            'total_logs': len(logs)
        }
        
        return health_data
    
    except Exception as e:
        return {
            'health_status': 'UNKNOWN',
            'error': str(e)
        }


@router.get('/stats')
def get_monitoring_stats():
    """Get detailed monitoring statistics."""
    try:
        logs = read_log_files()
        sessions = read_session_files()
        
        # Count logs by level
        log_counts = {'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}
        for log in logs:
            level = log.get('level', 'INFO')
            if level in log_counts:
                log_counts[level] += 1
        
        # Count logs by component
        component_counts = {}
        for log in logs:
            component = log.get('component', 'Unknown')
            component_counts[component] = component_counts.get(component, 0) + 1
        
        # Session statistics
        session_stats = {
            'total_sessions': len(sessions),
            'total_articles_found': sum(s.get('articles_found', 0) for s in sessions),
            'total_articles_stored': sum(s.get('articles_stored', 0) for s in sessions),
            'total_duplicates': sum(s.get('articles_duplicate', 0) for s in sessions),
            'total_errors': sum(s.get('errors_encountered', 0) for s in sessions)
        }
        
        stats = {
            'log_counts': log_counts,
            'component_counts': component_counts,
            'session_stats': session_stats,
            'data_freshness': {
                'logs_count': len(logs),
                'sessions_count': len(sessions),
                'last_updated': datetime.now().isoformat()
            }
        }
        
        return stats
    
    except Exception as e:
        return {'error': str(e)}