#!/usr/bin/env python3
"""
Test Control-M style direct script calls pattern detection
"""

import sys
import os
sys.path.append('.')

from ksh_analyzer import KSHAnalyzer

def test_control_m_patterns():
    """Test Control-M style direct script calls"""
    print("Testing Control-M Style Direct Script Calls")
    print("=" * 60)
    
    # Create analyzer
    analyzer = KSHAnalyzer("test_control_m.db")
    
    # Test with sample data
    ksh_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ksh_scripts"
    ctl_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ctl_files"
    
    # Analyze directories
    print("Analyzing KSH scripts...")
    ksh_results = analyzer.analyze_ksh_directory(ksh_dir)
    print("Analyzing CTL files...")
    ctl_results = analyzer.analyze_ctl_directory(ctl_dir)
    
    print(f"Processed {ksh_results['total_files']} KSH files and {ctl_results['total_files']} CTL files")
    
    # Test Control-M style files
    control_m_files = [
        "control_orchestrator.ksh",
        "batch_scheduler.ksh", 
        "job_controller.ksh"
    ]
    
    for script_name in control_m_files:
        print(f"\n--- Testing {script_name} ---")
        
        forward_deps = analyzer.get_forward_dependencies(script_name)
        
        print(f"Forward dependencies: {len(forward_deps)}")
        script_deps = [dep for dep in forward_deps if dep['type'] == 'script']
        ctl_deps = [dep for dep in forward_deps if dep['type'] == 'ctl']
        plsql_deps = [dep for dep in forward_deps if dep['type'] == 'plsql']
        
        print(f"  Script dependencies: {len(script_deps)}")
        for dep in script_deps:
            print(f"    → {dep['target']} (line {dep['line']})")
        
        print(f"  CTL dependencies: {len(ctl_deps)}")
        for dep in ctl_deps:
            print(f"    → {dep['target']} (line {dep['line']})")
        
        print(f"  PL/SQL dependencies: {len(plsql_deps)}")
        for dep in plsql_deps:
            print(f"    → {dep['target']} (line {dep['line']})")
    
    # Test backward dependencies for common scripts
    print(f"\n--- Testing Backward Dependencies ---")
    
    # Test common scripts that should be called by Control-M files
    common_scripts = [
        "data_extractor.ksh",
        "process_customers.ksh",
        "generate_reports.ksh",
        "status_check.ksh",
        "cleanup.ksh"
    ]
    
    for script_name in common_scripts:
        backward_deps = analyzer.get_backward_dependencies(script_name)
        if backward_deps:
            print(f"{script_name} is called by:")
            for dep in backward_deps:
                print(f"    ← {dep['source']} (line {dep['line']})")
    
    # Clean up
    if os.path.exists("test_control_m.db"):
        os.remove("test_control_m.db")
    
    print("\n✅ Control-M pattern testing complete")

if __name__ == "__main__":
    test_control_m_patterns()