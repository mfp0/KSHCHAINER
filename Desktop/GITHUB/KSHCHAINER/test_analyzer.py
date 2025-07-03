#!/usr/bin/env python3
"""
Test script for KSH Analyzer
Tests the analyzer functionality and displays results
"""

import sqlite3
from ksh_analyzer import KSHAnalyzer

def test_analyzer():
    """Test the KSH analyzer functionality"""
    print("=" * 60)
    print("KSH SCRIPT DEPENDENCY ANALYZER TEST")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = KSHAnalyzer()
    
    # Test directories
    ksh_dir = "sample_data/ksh_scripts"
    ctl_dir = "sample_data/ctl_files"
    
    print(f"\n1. Testing KSH directory analysis: {ksh_dir}")
    ksh_results = analyzer.analyze_ksh_directory(ksh_dir)
    print(f"   - Files processed: {ksh_results['total_files']}")
    print(f"   - Errors: {len(ksh_results['errors'])}")
    
    print(f"\n2. Testing CTL directory analysis: {ctl_dir}")
    ctl_results = analyzer.analyze_ctl_directory(ctl_dir)
    print(f"   - CTL files found: {ctl_results['total_files']}")
    
    print("\n3. Testing database queries")
    
    # Test script listing
    scripts = analyzer.get_all_scripts()
    print(f"   - Total scripts in database: {len(scripts)}")
    
    # Test CTL files
    ctl_files = analyzer.get_all_ctl_files()
    print(f"   - Total CTL files in database: {len(ctl_files)}")
    
    print("\n4. Testing dependency analysis for each script:")
    print("-" * 50)
    
    for script in scripts:
        print(f"\n   Script: {script}")
        
        # Forward dependencies
        forward_deps = analyzer.get_forward_dependencies(script)
        print(f"   Forward dependencies: {len(forward_deps)}")
        
        for dep in forward_deps:
            status = "COMMENTED" if dep.get('commented', False) else "ACTIVE"
            if dep['type'] == 'plsql':
                target = f"{dep.get('schema', '')}.{dep.get('package', '')}.{dep['target']}"
            else:
                target = dep['target']
            print(f"     → {target} ({dep['type']}, line {dep['line']}) [{status}]")
        
        # Backward dependencies
        backward_deps = analyzer.get_backward_dependencies(script)
        print(f"   Backward dependencies: {len(backward_deps)}")
        
        for dep in backward_deps:
            status = "COMMENTED" if dep.get('commented', False) else "ACTIVE"
            print(f"     ← {dep['source']} ({dep['type']}, line {dep['line']}) [{status}]")
    
    print("\n5. Testing database direct access")
    print("-" * 50)
    
    conn = sqlite3.connect(analyzer.db_path)
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM scripts")
    script_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM dependencies")
    dep_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ctl_files")
    ctl_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM plsql_calls")
    plsql_count = cursor.fetchone()[0]
    
    print(f"   Database statistics:")
    print(f"     - Scripts: {script_count}")
    print(f"     - Dependencies: {dep_count}")
    print(f"     - CTL files: {ctl_count}")
    print(f"     - PL/SQL calls: {plsql_count}")
    
    # Show some sample dependencies
    print(f"\n   Sample dependencies:")
    cursor.execute("SELECT source_script, target_script, dependency_type, line_number, is_commented FROM dependencies LIMIT 10")
    
    for row in cursor.fetchall():
        source, target, dep_type, line, commented = row
        status = "COMMENTED" if commented else "ACTIVE"
        print(f"     {source} → {target} ({dep_type}, line {line}) [{status}]")
    
    # Show some sample PL/SQL calls
    print(f"\n   Sample PL/SQL calls:")
    cursor.execute("SELECT source_script, procedure_name, schema_name, package_name, line_number, is_commented FROM plsql_calls LIMIT 10")
    
    for row in cursor.fetchall():
        source, procedure, schema, package, line, commented = row
        status = "COMMENTED" if commented else "ACTIVE"
        print(f"     {source} → {schema}.{package}.{procedure} (line {line}) [{status}]")
    
    conn.close()
    
    print("\n6. Testing export functionality")
    print("-" * 50)
    
    try:
        analyzer.export_dependencies("test_export.json")
        print("   ✓ Export successful: test_export.json")
    except Exception as e:
        print(f"   ✗ Export failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_analyzer()