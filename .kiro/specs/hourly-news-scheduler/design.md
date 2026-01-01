# Hourly News Scheduler Dashboard - Design

## Overview

The Hourly News Scheduler Dashboard enhances the existing news scraper web interface to support automated hourly scraping operations. The design focuses on providing real-time monitoring, control capabilities, and comprehensive status reporting for the automated scraping process that sequentially processes BlockBeats and Jinse every hour.

## Architecture

The dashboard extends the existing web interface architecture with new components for scheduler management:

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Dashboard                            │
├─────────────────────────────────────────────────────────────┤
│  Scheduler Control Panel  │  Real-time Status Display      │
│  - Start/Stop Buttons     │  - Current Operation Status    │
│  - Schedule Configuration │  - Progress Indicators         │
│  - Manual Trigger        │  - Article Counters            │
├─────────────────────────────────────────────────────────────┤
│                 WebSocket Connection                        │
├─────────────────────────────────────────────────────────────┤
│              Backend Scheduler Service                      │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │ Scheduler Core  │  │    Session Manager              │  │
│  │ - APScheduler   │  │ - Real-time Updates             │  │
│  │ - Hourly Cron   │  │ - Status Broadcasting           │  │
│  │ - Job Queue     │  │ - Log Management                │  │
│  └─────────────────┘  └─────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│              Sequential Source Processing                   │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │ BlockBeats      │  │ Jinse Scraper                   │  │
│  │ Scraper (1st)   │  │ (2nd)                           │  │
│  └─────────────────┘  └─────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                 AI Content Analyzer                         │
│              & Supabase Database                            │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Scheduler Control Panel Component

**Purpose**: Provides user interface controls for managing the hourly scheduler

**Interface**:
```typescript
interface SchedulerControlPanel {
  // State
  isSchedulerRunning: boolean;
  nextRunTime: Date | null;
  currentOperation: string | null;
  
  // Actions
  startHourlyScheduler(): Promise<void>;
  stopHourlyScheduler(): Promise<void>;
  triggerManualScrape(): Promise<void>;
  getSchedulerStatus(): Promise<SchedulerStatus>;
}

interface SchedulerStatus {
  running: boolean;
  nextRunTime: string | null;
  lastRunTime: string | null;
  totalCycles: number;
  lastCycleResults: CycleResults | null;
}
```

### 2. Real-time Status Display Component

**Purpose**: Shows live updates of scraping progress and results

**Interface**:
```typescript
interface StatusDisplay {
  // Current operation state
  currentSource: 'BlockBeats' | 'Jinse' | null;
  operationStatus: 'idle' | 'processing' | 'complete' | 'error';
  
  // Progress tracking
  articlesChecked: number;
  articlesFound: number;
  articlesSaved: number;
  articlesFiltered: number;
  duplicatesSkipped: number;
  
  // AI analysis status
  aiAnalysisActive: boolean;
  aiFilteredCount: number;
  relevanceScores: number[];
  
  // Database status
  databaseConnected: boolean;
  lastSaveTime: Date | null;
  saveErrors: string[];
}
```

### 3. Enhanced Session Manager

**Purpose**: Manages real-time updates and WebSocket communication

**Interface**:
```typescript
interface EnhancedSessionManager {
  // Scheduler-specific logging
  logSchedulerEvent(event: SchedulerEvent): void;
  logSourceProgress(source: string, progress: SourceProgress): void;
  logCycleComplete(results: CycleResults): void;
  
  // Real-time broadcasting
  broadcastSchedulerStatus(status: SchedulerStatus): void;
  broadcastSourceProgress(progress: SourceProgress): void;
  broadcastError(error: ErrorEvent): void;
}

interface SchedulerEvent {
  type: 'cycle_start' | 'cycle_complete' | 'source_start' | 'source_complete' | 'error';
  timestamp: Date;
  source?: string;
  data?: any;
}

interface SourceProgress {
  source: string;
  articlesChecked: number;
  articlesFound: number;
  articlesSaved: number;
  latestNewsId?: number;
  status: 'processing' | 'complete' | 'error';
}
```

### 4. Hourly Scheduler Service

**Purpose**: Manages the automated hourly scraping schedule

**Interface**:
```typescript
interface HourlySchedulerService {
  // Scheduler management
  startHourlySchedule(): Promise<void>;
  stopHourlySchedule(): Promise<void>;
  getStatus(): SchedulerStatus;
  
  // Manual operations
  triggerImmediateScrape(): Promise<CycleResults>;
  
  // Configuration
  setScheduleInterval(hours: number): void;
  setMaxArticlesPerSource(count: number): void;
}

interface CycleResults {
  cycleId: string;
  startTime: Date;
  endTime: Date;
  duration: number;
  sources: SourceResults[];
  totalArticlesFound: number;
  totalArticlesSaved: number;
  totalErrors: number;
  aiAnalysisUsed: boolean;
}

interface SourceResults {
  source: string;
  articlesChecked: number;
  articlesFound: number;
  articlesSaved: number;
  duplicatesSkipped: number;
  aiFiltered: number;
  errors: string[];
  latestNewsId: number;
  duration: number;
}
```

## Data Models

### Scheduler State Model
```typescript
interface SchedulerState {
  id: string;
  isRunning: boolean;
  intervalHours: number;
  nextRunTime: Date | null;
  lastRunTime: Date | null;
  totalCycles: number;
  createdAt: Date;
  updatedAt: Date;
}
```

### Cycle History Model
```typescript
interface CycleHistory {
  id: string;
  cycleNumber: number;
  startTime: Date;
  endTime: Date;
  duration: number;
  sourcesProcessed: string[];
  totalArticlesFound: number;
  totalArticlesSaved: number;
  totalErrors: number;
  aiAnalysisEnabled: boolean;
  status: 'completed' | 'failed' | 'partial';
  errorDetails?: string;
}
```

### Real-time Progress Model
```typescript
interface ProgressUpdate {
  sessionId: string;
  timestamp: Date;
  source: string;
  eventType: 'start' | 'progress' | 'complete' | 'error';
  data: {
    articlesChecked?: number;
    articlesFound?: number;
    articlesSaved?: number;
    latestNewsId?: number;
    errorMessage?: string;
    aiAnalysisResults?: AIAnalysisResults;
  };
}
```
## 
Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Property 1: Scheduler status display consistency
*For any* scheduler state (running or stopped), the dashboard interface should display the correct corresponding status
**Validates: Requirements 1.1**

Property 2: Next run time display when running
*For any* scheduler in running state, the dashboard interface should display a valid future timestamp as the next run time
**Validates: Requirements 1.2**

Property 3: Real-time status updates
*For any* change in scheduler status, the dashboard interface should update its display to reflect the new status
**Validates: Requirements 1.5**

Property 4: Progress indicators during processing
*For any* source being processed, the dashboard interface should display progress indicators for that source
**Validates: Requirements 2.4**

Property 5: Error display with continuation
*For any* error that occurs during processing, the dashboard interface should display the error status while allowing processing to continue to the next source
**Validates: Requirements 2.5**

Property 6: Progress counter updates
*For any* article checking process, the dashboard interface should show accurate progress counters (e.g., "X/200 articles checked")
**Validates: Requirements 3.3**

Property 7: Article saved counter increments
*For any* article that gets successfully saved, the dashboard interface should increment the "articles saved" counter by exactly one
**Validates: Requirements 3.4**

Property 8: Duplicate detection counter display
*For any* article processing operation, the dashboard interface should display current duplicate detection counts
**Validates: Requirements 4.1**

Property 9: AI analysis status indication
*For any* active AI analysis process, the dashboard interface should show "AI Analysis" status indicator
**Validates: Requirements 4.2**

Property 10: AI filtering counter updates
*For any* article filtered out by AI analysis, the dashboard interface should increment the "filtered by AI" counter
**Validates: Requirements 4.3**

Property 11: AI analysis results display
*For any* completed AI analysis, the dashboard interface should display relevance scores and filtering statistics
**Validates: Requirements 4.4**

Property 12: Real-time article save updates
*For any* article saved to the database, the dashboard interface should show real-time updates of the saved article count
**Validates: Requirements 5.1**

Property 13: Database success indicators
*For any* successful database operation, the dashboard interface should display green status indicators
**Validates: Requirements 5.2**

Property 14: Database error indicators
*For any* failed database operation, the dashboard interface should display red error indicators with retry status
**Validates: Requirements 5.3**

Property 15: Completion timestamp updates
*For any* processing operation that completes, the dashboard interface should display the updated last scrape timestamp
**Validates: Requirements 5.5**

Property 16: Cycle start logging
*For any* hourly cycle that starts, the dashboard interface should display the cycle start time and sources being processed
**Validates: Requirements 6.1**

Property 17: Source completion statistics
*For any* source that completes processing, the dashboard interface should show summary statistics including found, stored, and filtered counts
**Validates: Requirements 6.2**

Property 18: Error message logging
*For any* error that occurs, the dashboard interface should display error messages with timestamps in a dedicated error log section
**Validates: Requirements 6.3**

Property 19: Cycle completion metrics
*For any* cycle that completes, the dashboard interface should show total cycle duration and performance metrics
**Validates: Requirements 6.4**

## Error Handling

### Scheduler Service Errors
- **Connection Failures**: If the scheduler service becomes unavailable, the dashboard should display a clear "Scheduler Offline" status and disable control buttons
- **Job Execution Errors**: If a scheduled job fails, the error should be logged and displayed, but the scheduler should continue with the next scheduled run
- **Configuration Errors**: Invalid scheduler configurations should be validated and rejected with clear error messages

### Source Processing Errors
- **BlockBeats Unavailable**: If BlockBeats cannot be accessed, log the error and proceed to Jinse processing
- **Jinse Unavailable**: If Jinse cannot be accessed, log the error and complete the cycle with BlockBeats results only
- **Parsing Errors**: Individual article parsing failures should be logged but not stop the overall scraping process

### Database Errors
- **Connection Loss**: Display connection status and attempt automatic reconnection
- **Insert Failures**: Retry failed inserts once, then log and continue with next article
- **Query Timeouts**: Implement timeout handling with user-visible status updates

### AI Analysis Errors
- **API Unavailable**: Fall back to keyword-based filtering with clear status indication
- **Analysis Timeout**: Skip AI analysis for timed-out articles and continue processing
- **Invalid Responses**: Log invalid AI responses and treat as "relevant" to avoid false negatives

## Testing Strategy

### Unit Tests
- Test scheduler control panel button functionality
- Test status display component state management
- Test WebSocket connection handling
- Test error boundary components
- Test progress counter calculations
- Test timestamp formatting and display

### Property-Based Tests
- Property tests will verify that dashboard state updates correctly reflect backend state changes
- Property tests will ensure counters increment correctly for all article processing operations
- Property tests will validate that error states are properly displayed and handled
- Property tests will verify real-time updates work consistently across different scenarios

### Integration Tests
- Test complete hourly cycle execution with dashboard monitoring
- Test scheduler start/stop functionality through dashboard controls
- Test error recovery scenarios (network failures, database issues)
- Test WebSocket reconnection and state synchronization
- Test AI analysis integration with dashboard updates

### Manual Testing
- Verify dashboard responsiveness during high-volume scraping
- Test user experience during error conditions
- Validate real-time update performance
- Test historical data access functionality

The testing approach combines unit tests for individual components, property-based tests for universal behaviors, and integration tests for end-to-end workflows. This ensures both component reliability and system-wide correctness.