#!/usr/bin/env python3
"""
Comprehensive regression test for KSH Analyzer
Tests all functionality to ensure no regressions after fixes
"""

import sys
import os
sys.path.append('.')

from ksh_analyzer import KSHAnalyzer

def test_comprehensive_regression():
    """Run comprehensive regression tests"""
    print("Comprehensive Regression Test Suite")
    print("=" * 60)
    
    # Create analyzer
    analyzer = KSHAnalyzer("test_regression.db")
    
    # Test directories
    ksh_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ksh_scripts"
    ctl_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ctl_files"
    
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "failures": []
    }
    
    def run_test(test_name, test_func):
        test_results["total_tests"] += 1
        try:
            test_func()
            test_results["passed_tests"] += 1
            print(f"✅ {test_name}")
        except Exception as e:
            test_results["failed_tests"] += 1
            test_results["failures"].append(f"{test_name}: {str(e)}")
            print(f"❌ {test_name}: {str(e)}")
    
    # Test 1: Basic Directory Analysis
    def test_directory_analysis():
        ksh_results = analyzer.analyze_ksh_directory(ksh_dir)
        ctl_results = analyzer.analyze_ctl_directory(ctl_dir)
        
        assert ksh_results['total_files'] >= 28, f"Expected at least 28 KSH files, got {ksh_results['total_files']}"
        assert ctl_results['total_files'] >= 10, f"Expected at least 10 CTL files, got {ctl_results['total_files']}"
        assert len(ksh_results['errors']) == 0, f"KSH analysis errors: {ksh_results['errors']}"
    
    run_test("Directory Analysis", test_directory_analysis)
    
    # Test 2: Forward Dependencies
    def test_forward_dependencies():
        forward_deps = analyzer.get_forward_dependencies("step3_processor.ksh")
        assert len(forward_deps) > 0, "step3_processor.ksh should have forward dependencies"
        
        # Should include step4_transformer.ksh
        transformer_deps = [dep for dep in forward_deps if "step4_transformer" in dep['target']]
        assert len(transformer_deps) > 0, "step3_processor.ksh should call step4_transformer.ksh"
    
    run_test("Forward Dependencies", test_forward_dependencies)
    
    # Test 3: Backward Dependencies
    def test_backward_dependencies():
        backward_deps = analyzer.get_backward_dependencies("step4_transformer.ksh")
        assert len(backward_deps) > 0, "step4_transformer.ksh should have backward dependencies"
        
        # Should be called by step3_processor.ksh
        processor_deps = [dep for dep in backward_deps if "step3_processor" in dep['source']]
        assert len(processor_deps) > 0, "step4_transformer.ksh should be called by step3_processor.ksh"
    
    run_test("Backward Dependencies", test_backward_dependencies)
    
    # Test 4: Nested Path Detection
    def test_nested_path_detection():
        level2_deps = analyzer.get_forward_dependencies("level2_script.ksh")
        level3_deps = [dep for dep in level2_deps if "level3_script" in dep['target']]
        level4_deps = [dep for dep in level2_deps if "level4_script" in dep['target']]
        
        assert len(level3_deps) > 0, "level2_script.ksh should call level3_script.ksh"
        assert len(level4_deps) > 0, "level2_script.ksh should call level4_script.ksh"
    
    run_test("Nested Path Detection", test_nested_path_detection)
    
    # Test 5: Duplicate Prevention
    def test_duplicate_prevention():
        level3_deps = analyzer.get_forward_dependencies("level3_script.ksh")
        level4_calls = [dep for dep in level3_deps if 'level4_script' in dep['target']]
        
        # Should have 2 legitimate calls from different lines
        assert len(level4_calls) == 2, f"Expected 2 level4_script calls, got {len(level4_calls)}"
        
        # Should be from different lines
        lines = [dep['line'] for dep in level4_calls]
        assert len(set(lines)) == 2, f"Expected calls from different lines, got {lines}"
    
    run_test("Duplicate Prevention", test_duplicate_prevention)
    
    # Test 6: Control-M Style Direct Calls
    def test_control_m_direct_calls():
        control_deps = analyzer.get_forward_dependencies("control_orchestrator.ksh")
        script_deps = [dep for dep in control_deps if dep['type'] == 'script']
        
        assert len(script_deps) > 5, f"control_orchestrator.ksh should have many script dependencies, got {len(script_deps)}"
        
        # Should include direct calls like data_extractor.ksh
        extractor_deps = [dep for dep in script_deps if 'data_extractor' in dep['target']]
        assert len(extractor_deps) > 0, "Should have data_extractor.ksh dependency"
    
    run_test("Control-M Direct Calls", test_control_m_direct_calls)
    
    # Test 7: CTL File Detection
    def test_ctl_file_detection():
        ctl_deps = analyzer.get_forward_dependencies("step3_processor.ksh")
        ctl_files = [dep for dep in ctl_deps if dep['type'] == 'ctl']
        
        assert len(ctl_files) > 0, "step3_processor.ksh should have CTL dependencies"
        
        # Should include transaction_log.ctl (not transaction.log.ctl)
        transaction_ctl = [dep for dep in ctl_files if 'transaction_log' in dep['target']]
        assert len(transaction_ctl) > 0, "Should have transaction_log.ctl dependency"
    
    run_test("CTL File Detection", test_ctl_file_detection)
    
    # Test 8: PL/SQL Detection
    def test_plsql_detection():
        plsql_deps = analyzer.get_forward_dependencies("step3_processor.ksh")
        plsql_calls = [dep for dep in plsql_deps if dep['type'] == 'plsql']
        
        assert len(plsql_calls) > 0, "step3_processor.ksh should have PL/SQL dependencies"
        
        # Should include some procedure calls (use actual procedures from the file)
        procedure_names = [dep['target'] for dep in plsql_calls]
        assert any('process_transaction_data' in name for name in procedure_names), "Should have process_transaction_data procedure"
    
    run_test("PL/SQL Detection", test_plsql_detection)
    
    # Test 9: Path Normalization
    def test_path_normalization():
        # Test that ./script.ksh and script.ksh are normalized to same name
        normalized1 = analyzer.normalize_script_name("./script.ksh")
        normalized2 = analyzer.normalize_script_name("script.ksh")
        normalized3 = analyzer.normalize_script_name("deep/nested/script.ksh")
        
        assert normalized1 == normalized2, f"Path normalization failed: {normalized1} != {normalized2}"
        assert normalized3 == "script.ksh", f"Deep path normalization failed: {normalized3}"
    
    run_test("Path Normalization", test_path_normalization)
    
    # Test 10: Script List Functions
    def test_script_lists():
        all_scripts = analyzer.get_all_scripts()
        all_ctl_files = analyzer.get_all_ctl_files()
        
        assert len(all_scripts) >= 28, f"Should have at least 28 scripts, got {len(all_scripts)}"
        assert len(all_ctl_files) >= 10, f"Should have at least 10 CTL files, got {len(all_ctl_files)}"
        
        # Check some expected scripts exist
        expected_scripts = ["step1_initiator.ksh", "step3_processor.ksh", "control_orchestrator.ksh"]
        for script in expected_scripts:
            assert script in all_scripts, f"Expected script {script} not found in {all_scripts}"
    
    run_test("Script Lists", test_script_lists)
    
    # Test 11: Batch Scheduler ETL Dependencies
    def test_batch_scheduler_etl():
        batch_deps = analyzer.get_forward_dependencies("batch_scheduler.ksh")
        script_deps = [dep for dep in batch_deps if dep['type'] == 'script']
        
        # Should have ETL pipeline scripts
        etl_scripts = ['data_extractor.ksh', 'intermediate_processor.ksh', 'main_loader.ksh']
        for etl_script in etl_scripts:
            found = any(etl_script in dep['target'] for dep in script_deps)
            assert found, f"batch_scheduler.ksh should call {etl_script}"
    
    run_test("Batch Scheduler ETL", test_batch_scheduler_etl)
    
    # Test 12: Job Controller Dependencies
    def test_job_controller():
        job_deps = analyzer.get_forward_dependencies("job_controller.ksh")
        plsql_deps = [dep for dep in job_deps if dep['type'] == 'plsql']
        
        # Should have job management PL/SQL calls
        job_mgmt_calls = [dep for dep in plsql_deps if 'job_mgmt' in dep['target']]
        assert len(job_mgmt_calls) > 0, "job_controller.ksh should have job_mgmt PL/SQL calls"
    
    run_test("Job Controller", test_job_controller)
    
    # Print results
    print(f"\n{'='*60}")
    print(f"REGRESSION TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed_tests']}")
    print(f"Failed: {test_results['failed_tests']}")
    
    if test_results['failed_tests'] > 0:
        print(f"\nFAILURES:")
        for failure in test_results['failures']:
            print(f"  ❌ {failure}")
    else:
        print(f"\n🎉 ALL TESTS PASSED! 🎉")
    
    # Clean up
    if os.path.exists("test_regression.db"):
        os.remove("test_regression.db")
    
    return test_results['failed_tests'] == 0

if __name__ == "__main__":
    success = test_comprehensive_regression()
    sys.exit(0 if success else 1)