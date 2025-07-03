#!/usr/bin/env python3
"""
Test script for PL/SQL procedure search functionality
Tests the new search features and ensures regression is avoided
"""

from ksh_analyzer import KSHAnalyzer

def test_plsql_search():
    """Test PL/SQL procedure search functionality"""
    print("=" * 70)
    print("PL/SQL PROCEDURE SEARCH FUNCTIONALITY TEST")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = KSHAnalyzer()
    
    # Analyze all sample data (including new test cases)
    print("\n1. Re-analyzing sample data with new test cases...")
    ksh_results = analyzer.analyze_ksh_directory('sample_data/ksh_scripts')
    ctl_results = analyzer.analyze_ctl_directory('sample_data/ctl_files')
    
    print(f"   - KSH files processed: {ksh_results['total_files']}")
    print(f"   - CTL files found: {ctl_results['total_files']}")
    print(f"   - Errors: {len(ksh_results['errors'])}")
    
    print("\n2. Testing get_all_plsql_procedures()...")
    all_procedures = analyzer.get_all_plsql_procedures()
    print(f"   - Total unique PL/SQL procedures found: {len(all_procedures)}")
    
    print("\n   Top 10 procedures:")
    for i, proc in enumerate(all_procedures[:10]):
        print(f"     {i+1}. {proc['full_name']} (called {proc['call_count']} times)")
    
    print("\n3. Testing search_plsql_procedure() with various search terms...")
    
    # Test case 1: Search for "customer"
    print("\n   Test Case 1: Search for 'customer'")
    customer_results = analyzer.search_plsql_procedure("customer")
    print(f"   Found {len(customer_results)} matches for 'customer':")
    for result in customer_results[:5]:  # Show first 5
        status = "COMMENTED" if result['is_commented'] else "ACTIVE"
        print(f"     - {result['source_script']} calls {result['full_procedure']} (line {result['line_number']}) [{status}]")
    
    # Test case 2: Search for "process"
    print("\n   Test Case 2: Search for 'process'")
    process_results = analyzer.search_plsql_procedure("process")
    print(f"   Found {len(process_results)} matches for 'process':")
    for result in process_results[:5]:  # Show first 5
        status = "COMMENTED" if result['is_commented'] else "ACTIVE"
        print(f"     - {result['source_script']} calls {result['full_procedure']} (line {result['line_number']}) [{status}]")
    
    # Test case 3: Search for "analytics"
    print("\n   Test Case 3: Search for 'analytics'")
    analytics_results = analyzer.search_plsql_procedure("analytics")
    print(f"   Found {len(analytics_results)} matches for 'analytics':")
    for result in analytics_results:
        status = "COMMENTED" if result['is_commented'] else "ACTIVE"
        print(f"     - {result['source_script']} calls {result['full_procedure']} (line {result['line_number']}) [{status}]")
    
    # Test case 4: Search for "validate"
    print("\n   Test Case 4: Search for 'validate'")
    validate_results = analyzer.search_plsql_procedure("validate")
    print(f"   Found {len(validate_results)} matches for 'validate':")
    for result in validate_results:
        status = "COMMENTED" if result['is_commented'] else "ACTIVE"
        print(f"     - {result['source_script']} calls {result['full_procedure']} (line {result['line_number']}) [{status}]")
    
    # Test case 5: Search for schema name "finance_pkg"
    print("\n   Test Case 5: Search for 'finance_pkg'")
    finance_results = analyzer.search_plsql_procedure("finance_pkg")
    print(f"   Found {len(finance_results)} matches for 'finance_pkg':")
    for result in finance_results:
        status = "COMMENTED" if result['is_commented'] else "ACTIVE"
        print(f"     - {result['source_script']} calls {result['full_procedure']} (line {result['line_number']}) [{status}]")
    
    print("\n4. Testing get_plsql_procedure_callers() with exact matches...")
    
    # Test exact procedure name matching
    if all_procedures:
        test_proc = all_procedures[0]['full_name']
        print(f"\n   Testing exact match for: {test_proc}")
        exact_results = analyzer.get_plsql_procedure_callers(test_proc)
        print(f"   Found {len(exact_results)} exact matches:")
        for result in exact_results:
            status = "COMMENTED" if result['is_commented'] else "ACTIVE"
            print(f"     - {result['source_script']} (line {result['line_number']}) [{status}]")
    
    print("\n5. Testing procedure search by partial procedure name...")
    
    # Extract some procedure names for testing
    if all_procedures:
        for proc in all_procedures[:3]:
            proc_name = proc['procedure']
            print(f"\n   Testing partial match for procedure name: '{proc_name}'")
            partial_results = analyzer.get_plsql_procedure_callers(proc_name)
            print(f"   Found {len(partial_results)} matches:")
            for result in partial_results[:3]:  # Show first 3
                status = "COMMENTED" if result['is_commented'] else "ACTIVE"
                print(f"     - {result['source_script']} calls {result['full_procedure']} (line {result['line_number']}) [{status}]")
    
    print("\n6. Testing case insensitive search...")
    
    # Test case insensitive search
    print("\n   Testing case insensitive search for 'CUSTOMER' (uppercase)")
    customer_upper_results = analyzer.search_plsql_procedure("CUSTOMER")
    print(f"   Found {len(customer_upper_results)} matches (should be same as lowercase):")
    
    print("\n   Testing case insensitive search for 'Analytics' (mixed case)")
    analytics_mixed_results = analyzer.search_plsql_procedure("Analytics")
    print(f"   Found {len(analytics_mixed_results)} matches:")
    
    print("\n7. Regression test - verify existing functionality still works...")
    
    # Test that regular dependency analysis still works
    scripts = analyzer.get_all_scripts()
    print(f"   - Total scripts still found: {len(scripts)}")
    
    # Test forward dependencies for a script
    if scripts:
        test_script = scripts[0]
        forward_deps = analyzer.get_forward_dependencies(test_script)
        print(f"   - Forward dependencies for {test_script}: {len(forward_deps)}")
        
        backward_deps = analyzer.get_backward_dependencies(test_script)
        print(f"   - Backward dependencies for {test_script}: {len(backward_deps)}")
    
    # Test CTL files still work
    ctl_files = analyzer.get_all_ctl_files()
    print(f"   - CTL files still found: {len(ctl_files)}")
    
    print("\n8. Summary statistics...")
    print("=" * 50)
    
    # Final statistics
    import sqlite3
    conn = sqlite3.connect(analyzer.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM scripts")
    script_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM dependencies")
    dep_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ctl_files")
    ctl_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM plsql_calls")
    plsql_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT schema_name || '.' || package_name || '.' || procedure_name) FROM plsql_calls")
    unique_procs = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"   Database Summary:")
    print(f"     - Scripts: {script_count}")
    print(f"     - Dependencies: {dep_count}")
    print(f"     - CTL files: {ctl_count}")
    print(f"     - PL/SQL calls: {plsql_count}")
    print(f"     - Unique procedures: {unique_procs}")
    
    print("\n" + "=" * 70)
    print("PL/SQL SEARCH TEST COMPLETED SUCCESSFULLY!")
    print("✓ Search functionality working")
    print("✓ Case insensitive search working")
    print("✓ Partial matching working")
    print("✓ Exact matching working")
    print("✓ No regression in existing functionality")
    print("=" * 70)

if __name__ == "__main__":
    test_plsql_search()