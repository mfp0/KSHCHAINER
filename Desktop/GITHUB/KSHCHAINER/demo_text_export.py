#!/usr/bin/env python3
"""
Demo script to show text export format
"""

import sys
import os
import datetime
sys.path.append('.')

from ksh_analyzer import KSHAnalyzer

def create_demo_text_export():
    """Create a demo text export to show the format"""
    print("Creating Demo Text Export")
    print("=" * 40)
    
    # Create analyzer
    analyzer = KSHAnalyzer("demo_export.db")
    
    # Test with sample data
    ksh_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ksh_scripts"
    ctl_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ctl_files"
    
    # Analyze directories
    print("Analyzing sample data...")
    analyzer.analyze_ksh_directory(ksh_dir)
    analyzer.analyze_ctl_directory(ctl_dir)
    
    # Get dependencies for a sample script
    script_name = "step3_processor.ksh"
    forward_deps = analyzer.get_forward_dependencies(script_name)
    backward_deps = analyzer.get_backward_dependencies(script_name)
    
    print(f"Creating text export demo for: {script_name}")
    
    # Create sample text content (simulating what the GUI would generate)
    text_content = []
    text_content.append("KSH Script Dependency Visualization")
    text_content.append("=" * 50)
    text_content.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    text_content.append(f"Selected Script: {script_name}")
    text_content.append("")
    
    # Group dependencies by type
    script_deps = [dep for dep in forward_deps if dep['type'] == 'script']
    ctl_deps = [dep for dep in forward_deps if dep['type'] == 'ctl']
    plsql_deps = [dep for dep in forward_deps if dep['type'] == 'plsql']
    
    # Add script dependencies
    if script_deps:
        text_content.append("SCRIPTS:")
        text_content.append("-" * 20)
        text_content.append(f"  📜 {script_name} (center)")
        for dep in script_deps:
            text_content.append(f"  📜 {dep['target']}")
        text_content.append("")
    
    # Add CTL dependencies
    if ctl_deps:
        text_content.append("CTL FILES:")
        text_content.append("-" * 20)
        for dep in ctl_deps:
            text_content.append(f"  📄 {dep['target']}")
        text_content.append("")
    
    # Add PL/SQL dependencies
    if plsql_deps:
        text_content.append("PL/SQL PROCEDURES:")
        text_content.append("-" * 20)
        for dep in plsql_deps:
            text_content.append(f"  ⚡ {dep['target']}")
        text_content.append("")
    
    # Add connections
    text_content.append("CONNECTIONS:")
    text_content.append("-" * 20)
    text_content.append("  FORWARD connections:")
    for dep in forward_deps:
        text_content.append(f"    {script_name} → {dep['target']} ({dep['type']})")
    
    if backward_deps:
        text_content.append("  BACKWARD connections:")
        for dep in backward_deps:
            text_content.append(f"    {dep['source']} → {script_name} ({dep['type']})")
    
    text_content.append("")
    text_content.append("VIEW INFORMATION:")
    text_content.append("-" * 20)
    text_content.append("Current zoom: 100%")
    text_content.append("Export format: Text representation")
    
    # Write demo file
    demo_file = "demo_visualization_export.txt"
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text_content))
    
    print(f"✅ Demo text export created: {demo_file}")
    print(f"\nSample content:")
    print("-" * 30)
    for i, line in enumerate(text_content):
        if i < 15:  # Show first 15 lines
            print(line)
        elif i == 15:
            print("... (truncated)")
            break
    
    print(f"\n📄 Full content available in: {demo_file}")
    
    # Show statistics
    print(f"\nEXPORT STATISTICS:")
    print(f"- Total lines: {len(text_content)}")
    print(f"- File size: {os.path.getsize(demo_file)} bytes")
    print(f"- Scripts: {len(script_deps) + 1}")  # +1 for center script
    print(f"- CTL files: {len(ctl_deps)}")
    print(f"- PL/SQL procedures: {len(plsql_deps)}")
    print(f"- Total dependencies: {len(forward_deps)}")
    
    # Clean up
    if os.path.exists("demo_export.db"):
        os.remove("demo_export.db")

if __name__ == "__main__":
    create_demo_text_export()