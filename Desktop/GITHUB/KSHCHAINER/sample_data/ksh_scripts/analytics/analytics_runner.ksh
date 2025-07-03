#!/bin/ksh

# Analytics runner script with specific analytics procedures
# Tests procedure search in nested directories

# Load configuration from parent directory
. ../config.ksh

log_message "Starting analytics processing"

# Core analytics procedures
run_core_analytics() {
    log_message "Running core analytics"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select analytics_core.calculate_daily_metrics() from dual;
        select analytics_core.process_customer_analytics() from dual;
        select analytics_core.generate_trend_analysis() from dual;
        select analytics_core.update_dashboard_metrics() from dual;
EOF
}

# Advanced analytics
run_advanced_analytics() {
    log_message "Running advanced analytics"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select advanced_analytics.predictive_modeling() from dual;
        select advanced_analytics.customer_segmentation() from dual;
        select advanced_analytics.churn_analysis() from dual;
        select advanced_analytics.revenue_forecasting() from dual;
EOF
}

# Business intelligence procedures
run_business_intelligence() {
    log_message "Running business intelligence"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select bi_engine.refresh_data_warehouse() from dual;
        select bi_engine.update_olap_cubes() from dual;
        select bi_engine.generate_executive_dashboard() from dual;
EOF
}

# Performance analytics
analyze_performance() {
    log_message "Analyzing performance metrics"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select performance_analytics.analyze_query_performance() from dual;
        select performance_analytics.monitor_system_health() from dual;
        select performance_analytics.optimize_indexes() from dual;
EOF
}

# Machine learning procedures
run_ml_analytics() {
    log_message "Running ML analytics"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select ml_engine.train_recommendation_model() from dual;
        select ml_engine.score_customer_propensity() from dual;
        select ml_engine.detect_anomalies() from dual;
EOF
}

# Execute analytics workflow
run_core_analytics
run_advanced_analytics
run_business_intelligence
analyze_performance
run_ml_analytics

# Archive analytics results
sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
    select analytics_archive.archive_results('DAILY') from dual;
    select analytics_archive.cleanup_temp_data() from dual;
EOF

log_message "Analytics processing completed"