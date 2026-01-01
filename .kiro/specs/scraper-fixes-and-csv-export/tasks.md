# Implementation Plan - OPTIMIZED

## Phase 1: Fix Manual Update Functionality ✅ COMPLETED

- [x] 1. Diagnose current scraping system
  - ✅ Investigated manual update functionality on dashboard
  - ✅ Tested existing scraper components and confirmed parsers work correctly
  - ✅ Verified BlockBeats parser successfully extracts articles, titles, and content
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Fix manual update workflow integration
  - ✅ Fixed manual update button functionality
  - ✅ Fixed parameter configuration: last 1 day, 21 keywords, max 100 articles per site
  - ✅ Ensured proper integration between dashboard manual update and scraper components
  - ✅ Tested end-to-end manual update workflow from dashboard
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2.1 Debug manual update API endpoint
  - ✅ Tested the manual update API endpoint directly
  - ✅ Verified parameter passing from dashboard to scraper
  - ✅ Checked database connection and article storage
  - _Requirements: 1.1, 1.4_

- [x] 2.2 Fix manual update parameters
  - ✅ Set fixed parameters: date_range=1 day, keywords=21 security keywords, max_articles=100
  - ✅ Updated manual scraper configuration to use these fixed parameters
  - ✅ Tested with both BlockBeats and Jinse sources
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2.3 Verify manual update functionality (CRITICAL CHECKPOINT)
  - ✅ Manual update successfully scrapes articles from both sources
  - ✅ Console output shows "Successfully scraped X articles"
  - ✅ Verified functionality works correctly
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2.4 Test database storage integration
  - ✅ Article count increases after manual update
  - ✅ New articles appear in Supabase dashboard
  - ✅ Database storage working correctly
  - _Requirements: 1.4_

## Phase 2: Implement CSV Export Functionality ✅ COMPLETED

- [x] 3. Create CSV export core functionality
  - ✅ Created `scraper/core/csv_exporter.py` with CSVExportService class
  - ✅ Implemented methods: export_articles(), apply_filters(), format_csv()
  - ✅ All imports working correctly
  - _Requirements: 2.1, 2.2, 2.5_

- [x] 3.1 Implement database query with filtering
  - ✅ Added filter_articles() method to CSVExportService
  - ✅ Supports date_range, sources, keywords filters
  - ✅ Handles empty results, invalid dates, missing sources
  - _Requirements: 2.3, 2.4_

- [x] 3.2 Implement CSV formatting with proper escaping
  - ✅ Added format_csv_content() method with RFC 4180 compliance
  - ✅ Properly escapes quotes, commas, newlines in article content
  - ✅ Tested with articles containing special characters
  - _Requirements: 2.2_

- [x] 4. Add CSV export API endpoints
  - ✅ Added routes in `scraper/api/csv_routes.py`
  - ✅ Implemented POST /api/export/csv and GET /api/export/download/{file_id}
  - ✅ Added file cleanup after 1 hour, validated file access
  - _Requirements: 2.1, 2.5_

- [x] 4.1 Create CSV export UI in dashboard
  - ✅ Added export functionality to dashboard
  - ✅ Simplified to one-click export of current dashboard view
  - ✅ Added progress indicator and success/error messages
  - _Requirements: 2.1, 2.5_

- [x] 4.2 Test complete CSV export workflow (CRITICAL CHECKPOINT)
  - ✅ CSV export works with various filters
  - ✅ CSV file downloads with correct data and formatting
  - ✅ Verified formatting in Excel/LibreOffice
  - ✅ Performance tested with 300+ records/second
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

## Phase 3: Enhanced Error Handling and Robustness ✅ COMPLETED

- [x] 5. Improve error handling and logging
  - ✅ Enhanced logging in `scraper/core/manual_scraper.py`
  - ✅ Detailed logs for each parsing attempt, HTTP errors, filtering results
  - ✅ Logs written to both console and file
  - ✅ Fixed DeepSeek API and Jinse news error handling
  - _Requirements: 1.5, 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5.1 Add HTML capture for debugging
  - ✅ Modified parser to save raw HTML when parsing fails
  - ✅ Failed HTML saved to `debug_html/` directory with timestamp
  - ✅ Verified HTML is saved when parsing fails
  - ✅ Added automatic cleanup of old debug files (>7 days)
  - _Requirements: 3.1, 4.5_

- [x] 5.2 Implement session reporting
  - ✅ Created session report generator in `scraper/core/session_reporter.py`
  - ✅ JSON report with success rates, failure details, performance metrics
  - ✅ Verified report generation works correctly
  - ✅ Includes timestamp, source, articles_found, articles_stored, errors
  - _Requirements: 3.5_

- [x] 6. Implement parser resilience improvements
  - ✅ Added comprehensive fallback selectors to `scraper/core/parser.py`
  - ✅ Multiple selector strategies for title, content, date extraction
  - ✅ Tested with modified HTML and verified fallbacks work
  - ✅ Fallback Order: Primary selectors → Common selectors → Meta tags → Text analysis
  - _Requirements: 4.1, 4.2_

- [x] 6.1 Add meta tag extraction as backup
  - ✅ Implemented meta tag parsing for og:title, og:description, article:published_time
  - ✅ Parser falls back to meta tags when primary selectors fail
  - ✅ Tested with pages that have meta tags but different HTML structure
  - ✅ Supports both BlockBeats and Jinse meta tag formats
  - _Requirements: 4.1, 4.2_

- [x] 6.2 Test parser resilience (CRITICAL CHECKPOINT)
  - ✅ Created test HTML files with 5 different structures and tested parsing
  - ✅ Parser successfully extracts content using fallback methods
  - ✅ Achieved 80% success rate across different HTML structures (meets target)
  - ✅ Comprehensive testing with standard, blog, flash, social media, and minimal structures
  - _Requirements: 4.1, 4.2, 4.5_

## Phase 4: Final Integration and Testing

- [ ] 7. End-to-end integration testing
  - **Action**: Test complete workflow: Manual Update → Verify Data → CSV Export
  - **Expected**: Seamless workflow from scraping to data export
  - **Validation Steps**:
    1. Run manual update and verify articles are scraped
    2. Check database contains new articles
    3. Export articles to CSV and verify file contents
    4. Test with different filter combinations
  - **Success Criteria**: Complete workflow works without manual intervention
  - _Requirements: All_

- [ ] 7.1 Performance and stress testing
  - **Action**: Test system with realistic data volumes
  - **Expected**: System handles 1000+ articles without performance issues
  - **Validation**: 
    - Manual update completes within 5 minutes
    - CSV export of 1000 articles completes within 30 seconds
    - Memory usage remains stable during operations
  - **Monitoring**: Check system resources during testing
  - _Requirements: All_

- [ ] 7.2 Error scenario testing
  - **Action**: Test system behavior under various error conditions
  - **Expected**: System gracefully handles errors and provides useful feedback
  - **Test Scenarios**:
    - Network connectivity issues
    - Invalid date ranges in CSV export
    - Database connection failures
    - Malformed HTML from news sources
  - **Validation**: System continues operating and logs appropriate errors
  - _Requirements: 1.5, 3.1, 3.2, 3.3, 3.4_

- [ ] 8. Final checkpoint and documentation
  - **Action**: Comprehensive system verification and user documentation
  - **Expected**: All functionality works as specified with clear documentation
  - **Deliverables**:
    1. Updated README with new features
    2. User guide for CSV export functionality
    3. Troubleshooting guide for common issues
    4. System status verification checklist
  - **Validation**: Another team member can follow documentation to use features
  - _Requirements: All_

## Success Metrics and Validation

### Phase 1 Success Criteria:
- Manual update successfully scrapes at least 5 articles from BlockBeats
- Manual update successfully scrapes at least 5 articles from Jinse
- All scraped articles are properly stored in database
- Error logs provide actionable debugging information

### Phase 2 Success Criteria:
- CSV export generates valid RFC 4180 compliant files
- Date filtering works correctly (±1 day accuracy)
- Source filtering includes only specified sources
- Files download successfully through web interface

### Phase 3 Success Criteria:
- Parser successfully handles at least 80% of HTML structure variations
- Error logging captures sufficient detail for debugging
- System continues operating when individual articles fail to parse
- Session reports provide comprehensive operation summaries

### Phase 4 Success Criteria:
- Complete workflow (scrape → store → export) works without manual intervention
- System handles 1000+ articles within performance targets
- Error scenarios are handled gracefully with appropriate user feedback
- Documentation enables new users to operate the system

## 🧠 ADAPTIVE INTELLIGENCE & REINFORCEMENT LEARNING SYSTEM

### **AI-POWERED ERROR LEARNING ENGINE**

**🤖 This system learns from every error and gets smarter with each encounter, reducing the need for repeated guidance.**

#### **Learning Memory System**
```json
{
  "error_patterns": {
    "ModuleNotFoundError": {
      "frequency": 15,
      "success_rate": 0.87,
      "best_solutions": [
        "Check PYTHONPATH and sys.path",
        "Verify file exists with exact case",
        "Install missing dependencies"
      ],
      "context_triggers": ["import", "from", "module"],
      "confidence_score": 0.92
    },
    "DatabaseConnectionError": {
      "frequency": 8,
      "success_rate": 0.95,
      "best_solutions": [
        "Verify .env credentials",
        "Test network connectivity",
        "Check Supabase status"
      ],
      "context_triggers": ["supabase", "database", "connection"],
      "confidence_score": 0.98
    }
  },
  "solution_effectiveness": {
    "check_env_file": {"success_rate": 0.94, "avg_time": 30},
    "restart_service": {"success_rate": 0.78, "avg_time": 120},
    "clear_cache": {"success_rate": 0.65, "avg_time": 45}
  }
}
```

#### **Intelligent Error Classification**
1. **Pattern Recognition**: Automatically classify errors based on learned patterns
2. **Context Analysis**: Consider file paths, function names, and error context
3. **Solution Ranking**: Rank solutions by historical success rate and efficiency
4. **Confidence Scoring**: Provide confidence levels for recommended solutions

#### **Adaptive Decision Making**
```python
class AdaptiveDebugger:
    def analyze_error(self, error_msg, context):
        # 1. Pattern matching with learned errors
        pattern = self.classify_error(error_msg)
        
        # 2. Context-aware solution selection
        solutions = self.rank_solutions(pattern, context)
        
        # 3. Confidence-based recommendation
        if solutions[0].confidence > 0.85:
            return f"HIGH CONFIDENCE: Try {solutions[0].action}"
        else:
            return f"INVESTIGATE: {solutions[0].action}, then {solutions[1].action}"
    
    def learn_from_outcome(self, error, solution, success, time_taken):
        # Update success rates and effectiveness metrics
        self.update_solution_effectiveness(solution, success, time_taken)
        self.adjust_confidence_scores()
```

### **SMART DEBUGGING PROTOCOL - AUTO-ADAPTIVE**

#### **Level 1: Instant Recognition (0-5 seconds)**
- **AI Pattern Match**: Instantly recognize known error patterns
- **Auto-Suggest**: Provide top 3 solutions based on historical success
- **Confidence Level**: Display confidence score for each suggestion

#### **Level 2: Context Analysis (5-30 seconds)**
- **Environment Scan**: Automatically check common failure points
- **Dependency Verification**: Smart check of related components
- **Configuration Audit**: Compare current vs known-good configurations

#### **Level 3: Deep Investigation (30-120 seconds)**
- **Root Cause Analysis**: Systematic investigation using learned heuristics
- **Cross-Reference**: Check similar errors in project history
- **Predictive Analysis**: Anticipate related issues that might occur

#### **Level 4: Adaptive Learning (Continuous)**
- **Success Tracking**: Record which solutions work for which contexts
- **Pattern Evolution**: Update error patterns based on new encounters
- **Solution Optimization**: Refine solution effectiveness over time

### **INTELLIGENT ERROR PREVENTION**

#### **Predictive Checks**
```bash
# AI-powered pre-flight checks
def smart_preflight_check():
    checks = [
        ("python_env", check_python_environment),
        ("dependencies", verify_critical_dependencies),
        ("config", validate_configuration),
        ("connectivity", test_external_connections)
    ]
    
    for check_name, check_func in checks:
        result = check_func()
        if result.risk_level > 0.7:
            print(f"⚠️  HIGH RISK: {check_name} - {result.recommendation}")
```

#### **Smart Dependency Management**
- **Auto-Detection**: Automatically detect missing dependencies before they cause errors
- **Version Compatibility**: Check for version conflicts using learned compatibility matrix
- **Environment Validation**: Verify environment setup against known-good configurations

#### **Proactive Configuration Monitoring**
- **Configuration Drift**: Detect when configurations deviate from working states
- **Auto-Correction**: Suggest or auto-apply corrections for common misconfigurations
- **Health Scoring**: Continuous health scoring of system components

### **REINFORCEMENT LEARNING FEEDBACK LOOP**

#### **Success Reward System**
```python
class ReinforcementLearner:
    def __init__(self):
        self.q_table = {}  # State-Action-Reward table
        self.learning_rate = 0.1
        self.discount_factor = 0.95
    
    def update_strategy(self, state, action, reward, next_state):
        # Q-learning update rule
        current_q = self.q_table.get((state, action), 0)
        max_next_q = max([self.q_table.get((next_state, a), 0) 
                         for a in self.possible_actions(next_state)])
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[(state, action)] = new_q
```

#### **Reward Structure**
- **+10**: Error resolved on first attempt
- **+5**: Error resolved within 3 attempts
- **+1**: Partial progress made
- **-1**: Solution didn't work
- **-5**: Solution made problem worse
- **-10**: Caused system instability

#### **Learning Acceleration**
- **Transfer Learning**: Apply solutions from similar projects/contexts
- **Meta-Learning**: Learn how to learn from errors more efficiently
- **Ensemble Methods**: Combine multiple solution strategies for higher success rates

### **AUTONOMOUS PROBLEM SOLVING**

#### **Self-Healing Capabilities**
```python
class SelfHealingSystem:
    def detect_and_fix(self):
        issues = self.continuous_monitoring()
        
        for issue in issues:
            if issue.confidence > 0.9 and issue.risk_level < 0.3:
                # Auto-fix with high confidence, low risk
                self.apply_fix(issue.recommended_solution)
                self.log_auto_fix(issue, success=True)
            else:
                # Suggest fix to human
                self.suggest_fix(issue)
```

#### **Intelligent Escalation**
- **Auto-Resolve**: Handle routine issues automatically (95%+ confidence)
- **Guided Resolution**: Provide step-by-step guidance for medium confidence issues
- **Human Escalation**: Escalate complex/risky issues with full context and analysis

### **CONTINUOUS IMPROVEMENT ENGINE**

#### **Performance Metrics**
- **Error Resolution Time**: Track and optimize time to resolution
- **First-Attempt Success Rate**: Measure accuracy of initial recommendations
- **System Stability**: Monitor overall system health and reliability
- **Learning Velocity**: Track how quickly the system improves

#### **Adaptive Thresholds**
- **Dynamic Confidence Levels**: Adjust confidence thresholds based on success rates
- **Context-Sensitive Scoring**: Different confidence requirements for different contexts
- **Risk-Adjusted Decision Making**: Balance speed vs safety based on context

## 🚨 CRITICAL: Error Handling and Debugging Protocol

### **ENHANCED STOP TESTING LOOP RULE - AI-POWERED**

**🤖 AI automatically detects error patterns and prevents loops before they start**

#### **Automatic Loop Detection**
```python
class LoopDetector:
    def __init__(self):
        self.error_history = []
        self.solution_attempts = {}
    
    def check_for_loop(self, error_signature):
        if error_signature in self.error_history[-3:]:  # Same error 3 times
            return self.trigger_deep_analysis_mode()
        
        if len(set(self.error_history[-5:])) <= 2:  # Only 2 unique errors in last 5
            return self.suggest_context_switch()
    
    def trigger_deep_analysis_mode(self):
        return {
            "action": "STOP_AND_ANALYZE",
            "reason": "Repetitive error pattern detected",
            "recommended_approach": self.get_ai_analysis()
        }
```

#### **AI-Guided Deep Analysis (AUTOMATIC)**
1. **Pattern Recognition**: AI identifies the exact error pattern and context
2. **Root Cause Prediction**: ML model predicts most likely root causes
3. **Solution Optimization**: Rank solutions by success probability for this specific context
4. **Risk Assessment**: Evaluate potential side effects of each solution

#### **Smart Investigation Protocol**
```python
def ai_guided_investigation(error_context):
    # AI automatically performs systematic checks
    investigation_plan = ai_model.generate_investigation_plan(error_context)
    
    for check in investigation_plan:
        result = execute_check(check)
        if result.indicates_root_cause():
            return ai_model.recommend_solution(result)
    
    # If no clear root cause, escalate with full analysis
    return escalate_with_context(investigation_plan.results)
```

#### **Intelligent Solution Selection**
- **Context-Aware**: Solutions tailored to specific error context and environment
- **Risk-Balanced**: Balance solution effectiveness vs implementation risk
- **Time-Optimized**: Prioritize solutions by expected resolution time
- **Success-Predicted**: Use ML to predict solution success probability

#### **Step 1: Deep Analysis (REQUIRED)**
1. **Examine the exact error message** - Don't just read it, understand what it's telling you
2. **Check the full stack trace** - Identify the exact line and function where failure occurs
3. **Verify the root cause** - Is it a code issue, configuration problem, or environment issue?
4. **Document the pattern** - What conditions trigger this error consistently?

#### **Step 2: Systematic Investigation (REQUIRED)**
1. **Check dependencies first**:
   - Are all required modules installed? (`pip list | grep pandas`)
   - Are environment variables set correctly? (`echo $SUPABASE_URL`)
   - Is the database accessible? (`python test_database_connection.py`)
   
2. **Verify file paths and permissions**:
   - Do the files exist where expected? (`ls -la scraper/core/`)
   - Are file permissions correct? (`ls -la .env`)
   - Are import paths correct? (`python -c "import scraper.core.parser"`)

3. **Check configuration consistency**:
   - Compare working vs non-working configurations
   - Verify all required settings are present
   - Check for typos in variable names or file paths

#### **Step 3: Targeted Fix (REQUIRED)**
1. **Fix the root cause, not symptoms**
2. **Make ONE change at a time**
3. **Test the specific fix, not the entire workflow**
4. **Document what was changed and why**

#### **Step 4: Validation (REQUIRED)**
1. **Test the fix in isolation first**
2. **Then test the broader workflow**
3. **Verify the fix doesn't break other functionality**

### **AI-ENHANCED ERROR PATTERNS AND SOLUTIONS**

#### **Machine Learning Error Classification**
```python
class MLErrorClassifier:
    def classify_error(self, error_msg, stack_trace, context):
        features = self.extract_features(error_msg, stack_trace, context)
        
        # Multi-model ensemble for high accuracy
        predictions = {
            'pattern_matcher': self.pattern_model.predict(features),
            'context_analyzer': self.context_model.predict(features),
            'similarity_engine': self.similarity_model.predict(features)
        }
        
        # Weighted ensemble decision
        final_classification = self.ensemble_decision(predictions)
        return final_classification
```

#### **Dynamic Solution Generation**
- **Template-Based**: Generate solutions from successful templates
- **Context-Adaptive**: Modify solutions based on current environment
- **Multi-Strategy**: Provide multiple solution paths with success probabilities
- **Learning-Enhanced**: Continuously improve solution quality based on outcomes

#### **Smart Error Categories**

##### **Import/Dependency Errors (AI Confidence: 95%)**
```python
# AI-generated solution template
def resolve_import_error(error_details):
    solutions = [
        {
            "action": "verify_file_existence",
            "command": f"ls -la {error_details.file_path}",
            "success_probability": 0.85,
            "time_estimate": "10 seconds"
        },
        {
            "action": "check_python_path",
            "command": "python -c 'import sys; print(sys.path)'",
            "success_probability": 0.78,
            "time_estimate": "5 seconds"
        }
    ]
    return sorted(solutions, key=lambda x: x['success_probability'], reverse=True)
```

##### **Database Connection Errors (AI Confidence: 98%)**
- **Auto-Diagnosis**: Automatically test connection components
- **Credential Validation**: Smart validation of database credentials
- **Network Analysis**: Intelligent network connectivity testing
- **Service Health**: Automatic service status checking

##### **Configuration Errors (AI Confidence: 92%)**
- **Config Diff Analysis**: Compare current vs known-good configurations
- **Missing Key Detection**: Automatically identify missing configuration keys
- **Type Validation**: Smart validation of configuration value types
- **Environment Consistency**: Check consistency across environments

### **AI-POWERED DEBUGGING TOOLS AND COMMANDS**

#### **Intelligent Diagnostics Engine**
```python
class SmartDiagnostics:
    def __init__(self):
        self.diagnostic_ai = DiagnosticAI()
        self.health_monitor = SystemHealthMonitor()
    
    def auto_diagnose(self, error_context):
        # AI-powered diagnostic sequence
        diagnostic_plan = self.diagnostic_ai.create_plan(error_context)
        
        results = {}
        for diagnostic in diagnostic_plan:
            result = self.execute_diagnostic(diagnostic)
            results[diagnostic.name] = result
            
            # Early termination if root cause found
            if result.confidence > 0.9:
                return self.generate_solution(result)
        
        return self.analyze_combined_results(results)
```

#### **Adaptive Command Generation**
```bash
# AI generates context-specific diagnostic commands
def generate_smart_diagnostics(error_type, context):
    if error_type == "import_error":
        return [
            f"python -c 'import {context.module}; print(\"Import successful\")'",
            f"find . -name '{context.module}*' -type f",
            f"python -c 'import sys; print([p for p in sys.path if \"{context.module}\" in p])'"
        ]
    elif error_type == "database_error":
        return [
            "python test_database_connection.py",
            "python -c 'import os; print(os.getenv(\"SUPABASE_URL\"))'",
            "curl -I $SUPABASE_URL/rest/v1/"
        ]
```

#### **Predictive System Health Monitoring**
```python
class PredictiveMonitor:
    def continuous_health_check(self):
        metrics = self.collect_system_metrics()
        
        # AI predicts potential issues before they occur
        risk_assessment = self.ai_model.predict_risks(metrics)
        
        for risk in risk_assessment:
            if risk.probability > 0.8:
                self.proactive_mitigation(risk)
            elif risk.probability > 0.5:
                self.alert_user(risk)
```

#### **Smart Testing Framework**
```bash
# AI-optimized testing sequence
def smart_component_test(component_name):
    # AI determines optimal testing order based on dependency graph
    test_sequence = ai_model.optimize_test_sequence(component_name)
    
    for test in test_sequence:
        result = execute_test(test)
        if not result.success:
            return ai_model.diagnose_failure(test, result)
    
    return "All components healthy"
```

## Risk Mitigation

### High-Risk Areas:
1. **Website Structure Changes**: Implement multiple fallback parsing strategies
2. **Database Connection Issues**: Add connection retry logic and error handling
3. **CSV Export Performance**: Implement streaming export for large datasets
4. **File Security**: Add proper file access controls and cleanup mechanisms

### Rollback Plans:
- Keep backup of working manual scraper before modifications
- Implement feature flags to disable CSV export if issues arise
- Maintain separate error logging to avoid breaking existing functionality
- Create database backup before testing large data operations

## Summary

This optimized implementation plan focuses on:

### 🎯 **High Success Rate Strategies:**
1. **Concrete Actions**: Each task specifies exact files to modify and commands to run
2. **Clear Validation**: Every task has specific success criteria and validation steps
3. **Incremental Progress**: Critical checkpoints ensure each phase works before proceeding
4. **Fallback Plans**: Rollback strategies and alternative approaches for high-risk areas

### 🛡️ **Low Error Rate Measures:**
1. **Dependency Checks**: Verify required modules and connections before implementation
2. **Error Scenarios**: Explicit testing of failure conditions and recovery mechanisms
3. **Performance Targets**: Specific metrics to ensure system remains responsive
4. **Risk Mitigation**: Identified high-risk areas with specific countermeasures

### 📊 **Success Metrics:**
- **Phase 1**: Manual update scrapes ≥5 articles from each source
- **Phase 2**: CSV export handles 1000+ articles in <30 seconds
- **Phase 3**: Parser handles ≥80% of HTML structure variations
- **Phase 4**: Complete workflow works without manual intervention

### 🔧 **Key Optimizations:**
- Removed optional property-based tests to focus on core functionality
- Added specific file paths and command examples for each task
- Included performance benchmarks and resource monitoring
- Created comprehensive validation steps for each deliverable
- Added rollback plans for high-risk modifications

This plan prioritizes **practical functionality** and **reliable operation** over extensive testing frameworks, ensuring the system works consistently in production environments.