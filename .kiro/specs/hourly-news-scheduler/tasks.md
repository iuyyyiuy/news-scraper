# Implementation Plan

- [x] 1. Enhance Scheduler Service for Hourly Operations
  - Modify existing scheduler service to support hourly intervals instead of daily
  - Add methods for starting/stopping hourly schedule via API
  - Implement sequential source processing (BlockBeats first, then Jinse)
  - Add real-time status broadcasting through WebSocket
  - _Requirements: 1.1, 1.2, 1.5, 2.1, 2.2, 2.3_

- [x] 1.1 Write property test for scheduler status consistency
  - **Property 1: Scheduler status display consistency**
  - **Validates: Requirements 1.1**

- [x] 1.2 Write property test for next run time display
  - **Property 2: Next run time display when running**
  - **Validates: Requirements 1.2**

- [ ] 2. Create Scheduler Control Panel Component
  - Build React/JavaScript component for scheduler controls
  - Implement start/stop scheduler buttons with API integration
  - Add manual trigger functionality for immediate scraping
  - Display current scheduler status and next run time
  - Handle loading states and error conditions
  - _Requirements: 1.3, 1.4, 1.5_

- [ ] 2.1 Write property test for real-time status updates
  - **Property 3: Real-time status updates**
  - **Validates: Requirements 1.5**

- [ ] 3. Implement Real-time Progress Display Component
  - Create component to show current scraping operation status
  - Display source processing order (BlockBeats → Jinse → Complete)
  - Show progress indicators and article counters
  - Implement WebSocket connection for live updates
  - Add error status display with continuation indicators
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 3.1 Write property test for progress indicators
  - **Property 4: Progress indicators during processing**
  - **Validates: Requirements 2.4**

- [ ] 3.2 Write property test for error handling with continuation
  - **Property 5: Error display with continuation**
  - **Validates: Requirements 2.5**

- [ ] 3.3 Write property test for progress counter updates
  - **Property 6: Progress counter updates**
  - **Validates: Requirements 3.3**

- [ ] 3.4 Write property test for article saved counter
  - **Property 7: Article saved counter increments**
  - **Validates: Requirements 3.4**

- [ ] 4. Add AI Analysis Status Monitoring
  - Extend progress display to show AI analysis status
  - Display duplicate detection and filtering counters
  - Show AI relevance scores and filtering statistics
  - Implement fallback status display for AI failures
  - Add real-time updates for AI processing results
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 4.1 Write property test for duplicate detection display
  - **Property 8: Duplicate detection counter display**
  - **Validates: Requirements 4.1**

- [ ] 4.2 Write property test for AI analysis status indication
  - **Property 9: AI analysis status indication**
  - **Validates: Requirements 4.2**

- [ ] 4.3 Write property test for AI filtering counter
  - **Property 10: AI filtering counter updates**
  - **Validates: Requirements 4.3**

- [ ] 4.4 Write property test for AI analysis results display
  - **Property 11: AI analysis results display**
  - **Validates: Requirements 4.4**

- [ ] 5. Implement Database Status Monitoring
  - Add real-time database connection status indicators
  - Display success/error indicators for database operations
  - Show retry status for failed operations
  - Implement connection error warnings
  - Update last scrape timestamp display
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 5.1 Write property test for real-time save updates
  - **Property 12: Real-time article save updates**
  - **Validates: Requirements 5.1**

- [ ] 5.2 Write property test for database success indicators
  - **Property 13: Database success indicators**
  - **Validates: Requirements 5.2**

- [ ] 5.3 Write property test for database error indicators
  - **Property 14: Database error indicators**
  - **Validates: Requirements 5.3**

- [ ] 5.4 Write property test for completion timestamp updates
  - **Property 15: Completion timestamp updates**
  - **Validates: Requirements 5.5**

- [ ] 6. Create Enhanced Logging and History Display
  - Build comprehensive log display component
  - Show cycle start times and source processing information
  - Display summary statistics for completed sources
  - Implement dedicated error log section with timestamps
  - Add cycle completion metrics and performance data
  - Create historical data access functionality
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 6.1 Write property test for cycle start logging
  - **Property 16: Cycle start logging**
  - **Validates: Requirements 6.1**

- [ ] 6.2 Write property test for source completion statistics
  - **Property 17: Source completion statistics**
  - **Validates: Requirements 6.2**

- [ ] 6.3 Write property test for error message logging
  - **Property 18: Error message logging**
  - **Validates: Requirements 6.3**

- [ ] 6.4 Write property test for cycle completion metrics
  - **Property 19: Cycle completion metrics**
  - **Validates: Requirements 6.4**

- [ ] 7. Enhance WebSocket Communication
  - Extend existing WebSocket implementation for scheduler events
  - Add message types for scheduler status, progress updates, and errors
  - Implement automatic reconnection for WebSocket failures
  - Add message queuing for offline periods
  - Handle concurrent user sessions with scheduler updates
  - _Requirements: 1.5, 2.4, 2.5, 5.1, 5.2, 5.3_

- [ ] 8. Update Backend API Routes
  - Add REST endpoints for scheduler control (start/stop/status)
  - Implement manual trigger endpoint for immediate scraping
  - Add endpoints for historical cycle data retrieval
  - Update existing scraper endpoints to support hourly operations
  - Add scheduler configuration endpoints
  - _Requirements: 1.3, 1.4, 6.5_

- [ ] 9. Modify Existing Scraper Components
  - Update MultiSourceScraper to support sequential processing order
  - Modify session manager to handle scheduler-specific logging
  - Enhance progress reporting for real-time dashboard updates
  - Add scheduler-aware error handling and recovery
  - Update database manager for scheduler status persistence
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3_

- [ ] 10. Integrate Dashboard Components
  - Add scheduler control panel to main dashboard page
  - Integrate real-time status display with existing interface
  - Update navigation to include scheduler monitoring section
  - Ensure responsive design for scheduler components
  - Add keyboard shortcuts for scheduler controls
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Add Error Handling and Recovery
  - Implement comprehensive error boundaries for React components
  - Add automatic retry logic for failed scheduler operations
  - Create fallback UI states for offline/error conditions
  - Add user-friendly error messages and recovery suggestions
  - Implement graceful degradation when WebSocket is unavailable
  - _Requirements: 2.5, 4.5, 5.3, 5.4, 6.3_

- [ ] 12.1 Write unit tests for error boundary components
  - Test React error boundaries handle component failures gracefully
  - Test fallback UI displays appropriate error messages
  - Test recovery mechanisms work correctly
  - _Requirements: 2.5, 4.5, 5.4_

- [ ] 13. Performance Optimization
  - Optimize WebSocket message frequency to prevent UI lag
  - Implement efficient state management for real-time updates
  - Add debouncing for rapid counter updates
  - Optimize rendering performance for large log displays
  - Add pagination for historical data access
  - _Requirements: 5.1, 6.1, 6.2, 6.4, 6.5_

- [ ] 14. Final Integration Testing
  - Test complete hourly cycle with dashboard monitoring
  - Verify all real-time updates work correctly
  - Test scheduler controls under various conditions
  - Validate error handling and recovery scenarios
  - Test performance with extended operation periods
  - _Requirements: All requirements_

- [ ] 15. Final Checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.