#!/usr/bin/env python3
"""Test the scheduler manually"""
import sys
sys.path.insert(0, '.')

from scraper.core.scheduler import SchedulerService

print("Testing scheduler service...")
scheduler = SchedulerService()

print("\nTriggering manual scrape...")
scheduler.trigger_scrape_now()

print("\nDone!")
