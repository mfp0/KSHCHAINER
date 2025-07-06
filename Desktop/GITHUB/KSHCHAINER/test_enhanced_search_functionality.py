#!/usr/bin/env python3
"""
Comprehensive test script for enhanced search functionality
Tests both KSH script search and PL/SQL procedure search
"""

import sys
import os
sys.path.append('.')

from ksh_analyzer import KSHAnalyzer

def test_enhanced_search_functionality():
    """Test all enhanced search functionality"""
    print("Testing Enhanced Search Functionality")
    print("=" * 60)
    
    # Create analyzer
    analyzer = KSHAnalyzer("test_search.db")
    
    # Test with sample data
    ksh_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ksh_scripts"
    ctl_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ctl_files"
    
    # Analyze directories
    print("Analyzing sample data...")
    ksh_results = analyzer.analyze_ksh_directory(ksh_dir)
    ctl_results = analyzer.analyze_ctl_directory(ctl_dir)
    
    print(f"Processed {ksh_results['total_files']} KSH files and {ctl_results['total_files']} CTL files")
    
    # Test 1: KSH Script Search
    print(f"\n1. TESTING KSH SCRIPT SEARCH")
    print("-" * 40)
    
    scripts = analyzer.get_all_scripts()
    print(f"Total scripts available: {len(scripts)}")
    
    # Test various search patterns
    search_tests = [
        ("level", "Partial match search"),
        ("step3", "Specific script search"),
        ("processor", "Functional name search"),
        ("control", "Control-M script search"),
        ("batch", "Batch processing search"),
        ("level4_script.ksh", "Full filename search"),
        ("ut", "Short pattern search (as requested)")
    ]
    
    for search_term, description in search_tests:
        print(f"\nSearching for '{search_term}' ({description}):")
        
        # Simulate what the GUI search would find
        matching_scripts = []
        for script in scripts:
            if search_term.lower() in script.lower():
                matching_scripts.append(script)
        
        if matching_scripts:
            print(f"  Found {len(matching_scripts)} matches:")
            for script in matching_scripts[:5]:  # Show first 5 matches
                print(f"    - {script}")
            if len(matching_scripts) > 5:
                print(f"    ... and {len(matching_scripts) - 5} more")
        else:
            print(f"  No matches found")
    
    # Test 2: Enhanced PL/SQL Search
    print(f"\n\n2. TESTING ENHANCED PL/SQL SEARCH")
    print("-" * 40)
    
    # Test function-name-only searches
    plsql_search_tests = [
        ("process_data", "Function name only"),
        ("log_job_success", "Exact function name"),
        ("update", "Partial function name"),
        ("emergency", "Function containing word"),
        ("core_processor", "Package name"),
        ("deep_schema", "Schema name"),
        ("apply_business_rules", "Full function name"),
        ("finalize", "Partial function search"),
        ("check", "Common function pattern")
    ]
    
    for search_term, description in plsql_search_tests:
        print(f"\nSearching for PL/SQL '{search_term}' ({description}):")
        
        try:
            # Test enhanced search
            results = analyzer.search_plsql_procedure_enhanced(search_term)
            
            if results:
                print(f"  Found {len(results)} matches:")
                
                # Group by match quality
                quality_groups = {}
                for result in results:
                    quality = result.get('match_quality', 'unknown')
                    if quality not in quality_groups:
                        quality_groups[quality] = []
                    quality_groups[quality].append(result)
                
                for quality, group in quality_groups.items():
                    print(f"    {quality.replace('_', ' ').title()}: {len(group)} matches")
                    for result in group[:3]:  # Show first 3 in each group
                        print(f"      → {result['source_script']}: {result['full_procedure']}")
                    if len(group) > 3:
                        print(f"      ... and {len(group) - 3} more")
            else:
                print(f"  No matches found")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    # Test 3: Compare old vs new PL/SQL search
    print(f"\n\n3. COMPARING OLD VS NEW PLSQL SEARCH")
    print("-" * 40)
    
    comparison_terms = ["process", "log", "update"]
    
    for term in comparison_terms:
        print(f"\nTesting '{term}':")
        
        try:
            # Old search
            old_results = analyzer.search_plsql_procedure(term)
            print(f"  Old search: {len(old_results)} results")
            
            # New enhanced search
            new_results = analyzer.search_plsql_procedure_enhanced(term)
            print(f"  Enhanced search: {len(new_results)} results")
            
            # Show quality distribution for new search
            if new_results:
                qualities = {}
                for result in new_results:
                    quality = result.get('match_quality', 'unknown')
                    qualities[quality] = qualities.get(quality, 0) + 1
                
                print("    Quality distribution:")
                for quality, count in sorted(qualities.items()):
                    print(f"      {quality.replace('_', ' ').title()}: {count}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # Test 4: Edge Cases
    print(f"\n\n4. TESTING EDGE CASES")
    print("-" * 40)
    
    edge_cases = [
        ("", "Empty search"),
        ("x", "Single character"),
        ("nonexistent", "Non-existent term"),
        ("LEVEL", "Uppercase search"),
        ("level.ksh", "File extension included"),
        ("step3_processor.ksh", "Full exact filename")
    ]
    
    for search_term, description in edge_cases:
        print(f"\nTesting '{search_term}' ({description}):")
        
        # KSH search
        ksh_matches = [s for s in scripts if search_term.lower() in s.lower()]
        print(f"  KSH matches: {len(ksh_matches)}")
        
        # PL/SQL search
        try:
            plsql_matches = analyzer.search_plsql_procedure_enhanced(search_term)
            print(f"  PL/SQL matches: {len(plsql_matches)}")
        except Exception as e:
            print(f"  PL/SQL error: {e}")
    
    # Test 5: Performance Test
    print(f"\n\n5. PERFORMANCE TESTING")
    print("-" * 40)
    
    import time
    
    # Test search performance
    test_terms = ["level", "process", "core", "update", "schema"]
    
    for term in test_terms:
        start_time = time.time()
        
        try:
            results = analyzer.search_plsql_procedure_enhanced(term)
            end_time = time.time()
            
            print(f"Search '{term}': {len(results)} results in {(end_time - start_time)*1000:.2f}ms")
            
        except Exception as e:
            print(f"Search '{term}': Error - {e}")
    
    # Clean up
    if os.path.exists("test_search.db"):
        os.remove("test_search.db")
    
    print(f"\n\n{'='*60}")
    print("SEARCH FUNCTIONALITY TESTING COMPLETE")
    print("="*60)
    print("\nRECOMMENDED GUI TESTING:")
    print("1. Run: python3 ksh_gui.py")
    print("2. Load sample data directories")
    print("3. Click 'Scan Dependencies'")
    print("4. Test KSH Script Search:")
    print("   - Type 'ut' → should show utilities and other matches")
    print("   - Type 'level' → should show level scripts dynamically")
    print("   - Type 'step3_processor.ksh' → should find exact match")
    print("5. Test PL/SQL Search:")
    print("   - Type 'process' → should show function name matches")
    print("   - Type 'log_job_success' → should find exact function")
    print("   - Type 'update' → should show all update functions")
    print("6. Verify dynamic filtering works as you type")
    print("7. Test clear buttons (✗) work properly")

if __name__ == "__main__":
    test_enhanced_search_functionality()