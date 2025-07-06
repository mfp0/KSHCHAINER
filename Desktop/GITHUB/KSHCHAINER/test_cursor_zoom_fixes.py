#!/usr/bin/env python3
"""
Test script for cursor positioning and zoom functionality fixes
"""

import sys
import os
sys.path.append('.')

from ksh_analyzer import KSHAnalyzer

def test_analyzer_setup():
    """Test that the analyzer works correctly for GUI testing"""
    print("Testing KSH Analyzer Setup for GUI")
    print("=" * 50)
    
    # Create analyzer
    analyzer = KSHAnalyzer("test_gui_fixes.db")
    
    # Test with sample data
    ksh_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ksh_scripts"
    ctl_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ctl_files"
    
    # Analyze directories
    print("Analyzing KSH scripts...")
    ksh_results = analyzer.analyze_ksh_directory(ksh_dir)
    print("Analyzing CTL files...")
    ctl_results = analyzer.analyze_ctl_directory(ctl_dir)
    
    print(f"Processed {ksh_results['total_files']} KSH files and {ctl_results['total_files']} CTL files")
    
    # Get some test scripts for GUI testing
    scripts = analyzer.get_all_scripts()
    print(f"\nAvailable scripts for testing: {len(scripts)}")
    
    # Test specific scripts that should work well for cursor/zoom testing
    test_scripts = [
        "step3_processor.ksh",
        "control_orchestrator.ksh", 
        "level2_script.ksh",
        "batch_scheduler.ksh"
    ]
    
    for script_name in test_scripts:
        if script_name in scripts:
            forward_deps = analyzer.get_forward_dependencies(script_name)
            backward_deps = analyzer.get_backward_dependencies(script_name)
            
            print(f"\n{script_name}:")
            print(f"  Forward dependencies: {len(forward_deps)}")
            print(f"  Backward dependencies: {len(backward_deps)}")
            
            # Count different types
            script_deps = [dep for dep in forward_deps if dep['type'] == 'script']
            ctl_deps = [dep for dep in forward_deps if dep['type'] == 'ctl']
            plsql_deps = [dep for dep in forward_deps if dep['type'] == 'plsql']
            
            print(f"    Scripts: {len(script_deps)}, CTL: {len(ctl_deps)}, PL/SQL: {len(plsql_deps)}")
    
    # Clean up
    if os.path.exists("test_gui_fixes.db"):
        os.remove("test_gui_fixes.db")
    
    print(f"\n✅ Analyzer setup complete - ready for GUI testing")
    print(f"\nRECOMMENDED TESTING PROCEDURE:")
    print(f"1. Run: python3 ksh_gui.py")
    print(f"2. Set KSH directory to: {ksh_dir}")
    print(f"3. Set CTL directory to: {ctl_dir}")
    print(f"4. Click 'Scan Dependencies'")
    print(f"5. Test the following improvements:")
    print(f"   ✓ Click directly on rectangles (not slightly to the left)")
    print(f"   ✓ Drag rectangles smoothly")
    print(f"   ✓ Mouse wheel zoom at cursor position")
    print(f"   ✓ Zoom controls work properly")
    print(f"   ✓ Reset zoom returns to 100%")
    print(f"   ✓ Fit All button works")
    print(f"6. Test with scripts: {', '.join(test_scripts)}")

if __name__ == "__main__":
    test_analyzer_setup()