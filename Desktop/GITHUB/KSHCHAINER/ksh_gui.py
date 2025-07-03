#!/usr/bin/env python3
"""
KSH Script Dependency Analyzer GUI
Tkinter-based GUI for analyzing KSH script dependencies
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import json
from typing import Dict, List
import sqlite3
from ksh_analyzer import KSHAnalyzer

class KSHAnalyzerGUI:
    """Main GUI class for KSH Script Dependency Analyzer"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("KSH Script Dependency Analyzer")
        self.root.geometry("1200x800")
        
        # Initialize analyzer
        self.analyzer = KSHAnalyzer()
        
        # Variables
        self.ksh_dir = tk.StringVar()
        self.ctl_dir = tk.StringVar()
        self.current_script = tk.StringVar()
        
        # Data storage
        self.scripts_data = {}
        self.dependencies_data = {}
        
        self.create_widgets()
        self.create_menu()
        
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Dependencies...", command=self.export_dependencies)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self.refresh_view)
        view_menu.add_command(label="Clear Results", command=self.clear_results)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Database Info", command=self.show_db_info)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_widgets(self):
        """Create main GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Top panel - Directory selection and controls
        self.create_top_panel(main_frame)
        
        # Middle panel - Script explorer and dependency view
        self.create_middle_panel(main_frame)
        
        # Bottom panel - Visualization
        self.create_bottom_panel(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_top_panel(self, parent):
        """Create top panel with directory selection and controls"""
        top_frame = ttk.Frame(parent)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure(3, weight=1)
        
        # KSH Directory selection
        ttk.Label(top_frame, text="KSH Scripts:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(top_frame, textvariable=self.ksh_dir, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(top_frame, text="📁 Browse", command=self.browse_ksh_dir).grid(row=0, column=2, padx=(0, 15))
        
        # CTL Directory selection
        ttk.Label(top_frame, text="CTL Files:").grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        ttk.Entry(top_frame, textvariable=self.ctl_dir, width=50).grid(row=0, column=4, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(top_frame, text="📁 Browse", command=self.browse_ctl_dir).grid(row=0, column=5, padx=(0, 15))
        
        # Control buttons
        button_frame = ttk.Frame(top_frame)
        button_frame.grid(row=1, column=0, columnspan=6, pady=(10, 0))
        
        ttk.Button(button_frame, text="🔍 Scan Dependencies", command=self.scan_dependencies).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📊 Export Results", command=self.export_dependencies).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_view).pack(side=tk.LEFT, padx=(0, 10))
        
    def create_middle_panel(self, parent):
        """Create middle panel with script explorer and dependency view"""
        middle_frame = ttk.Frame(parent)
        middle_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        middle_frame.grid_rowconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_columnconfigure(1, weight=2)
        
        # Left panel - Script Explorer
        left_frame = ttk.LabelFrame(middle_frame, text="Script Explorer", padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Script tree
        self.script_tree = ttk.Treeview(left_frame, columns=('type', 'count'), show='tree headings')
        self.script_tree.heading('#0', text='File')
        self.script_tree.heading('type', text='Type')
        self.script_tree.heading('count', text='Dependencies')
        self.script_tree.column('#0', width=200)
        self.script_tree.column('type', width=60)
        self.script_tree.column('count', width=80)
        
        # Scrollbars for script tree
        script_scrollbar_v = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.script_tree.yview)
        script_scrollbar_h = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.script_tree.xview)
        self.script_tree.configure(yscrollcommand=script_scrollbar_v.set, xscrollcommand=script_scrollbar_h.set)
        
        self.script_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        script_scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        script_scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind selection event
        self.script_tree.bind('<<TreeviewSelect>>', self.on_script_select)
        
        # Search box
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        search_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="🔍").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        # Right panel - Dependency View
        right_frame = ttk.LabelFrame(middle_frame, text="Dependency View", padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Selected script label
        self.selected_label = ttk.Label(right_frame, text="Selected: None", font=('Arial', 10, 'bold'))
        self.selected_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Dependency notebook
        self.dep_notebook = ttk.Notebook(right_frame)
        self.dep_notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Forward dependencies tab
        self.forward_frame = ttk.Frame(self.dep_notebook)
        self.dep_notebook.add(self.forward_frame, text="Calls (Forward)")
        
        self.forward_tree = ttk.Treeview(self.forward_frame, columns=('type', 'line', 'commented'), show='tree headings')
        self.forward_tree.heading('#0', text='Target')
        self.forward_tree.heading('type', text='Type')
        self.forward_tree.heading('line', text='Line')
        self.forward_tree.heading('commented', text='Status')
        
        forward_scrollbar = ttk.Scrollbar(self.forward_frame, orient=tk.VERTICAL, command=self.forward_tree.yview)
        self.forward_tree.configure(yscrollcommand=forward_scrollbar.set)
        
        self.forward_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        forward_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.forward_frame.grid_rowconfigure(0, weight=1)
        self.forward_frame.grid_columnconfigure(0, weight=1)
        
        # Backward dependencies tab
        self.backward_frame = ttk.Frame(self.dep_notebook)
        self.dep_notebook.add(self.backward_frame, text="Called By (Backward)")
        
        self.backward_tree = ttk.Treeview(self.backward_frame, columns=('type', 'line', 'commented'), show='tree headings')
        self.backward_tree.heading('#0', text='Source')
        self.backward_tree.heading('type', text='Type')
        self.backward_tree.heading('line', text='Line')
        self.backward_tree.heading('commented', text='Status')
        
        backward_scrollbar = ttk.Scrollbar(self.backward_frame, orient=tk.VERTICAL, command=self.backward_tree.yview)
        self.backward_tree.configure(yscrollcommand=backward_scrollbar.set)
        
        self.backward_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        backward_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.backward_frame.grid_rowconfigure(0, weight=1)
        self.backward_frame.grid_columnconfigure(0, weight=1)
        
        # PL/SQL Search tab
        self.plsql_search_frame = ttk.Frame(self.dep_notebook)
        self.dep_notebook.add(self.plsql_search_frame, text="PL/SQL Search")
        
        # Search controls
        search_controls = ttk.Frame(self.plsql_search_frame)
        search_controls.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        search_controls.grid_columnconfigure(1, weight=1)
        
        ttk.Label(search_controls, text="Search PL/SQL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.plsql_search_var = tk.StringVar()
        self.plsql_search_entry = ttk.Entry(search_controls, textvariable=self.plsql_search_var, width=30)
        self.plsql_search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.plsql_search_entry.bind('<KeyRelease>', self.on_plsql_search)
        self.plsql_search_entry.bind('<Return>', self.on_plsql_search)
        
        ttk.Button(search_controls, text="🔍 Search", command=self.on_plsql_search).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(search_controls, text="Clear", command=self.clear_plsql_search).grid(row=0, column=3)
        
        # Results display
        self.plsql_results_tree = ttk.Treeview(self.plsql_search_frame, 
                                              columns=('procedure', 'schema', 'package', 'line', 'commented'), 
                                              show='tree headings')
        self.plsql_results_tree.heading('#0', text='Calling Script')
        self.plsql_results_tree.heading('procedure', text='Procedure')
        self.plsql_results_tree.heading('schema', text='Schema')
        self.plsql_results_tree.heading('package', text='Package')
        self.plsql_results_tree.heading('line', text='Line')
        self.plsql_results_tree.heading('commented', text='Status')
        
        self.plsql_results_tree.column('#0', width=150)
        self.plsql_results_tree.column('procedure', width=150)
        self.plsql_results_tree.column('schema', width=100)
        self.plsql_results_tree.column('package', width=100)
        self.plsql_results_tree.column('line', width=60)
        self.plsql_results_tree.column('commented', width=80)
        
        plsql_scrollbar = ttk.Scrollbar(self.plsql_search_frame, orient=tk.VERTICAL, command=self.plsql_results_tree.yview)
        self.plsql_results_tree.configure(yscrollcommand=plsql_scrollbar.set)
        
        self.plsql_results_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        plsql_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        self.plsql_search_frame.grid_rowconfigure(1, weight=1)
        self.plsql_search_frame.grid_columnconfigure(0, weight=1)
        
        # Status label for search results
        self.plsql_status_label = ttk.Label(self.plsql_search_frame, text="Enter search term to find PL/SQL procedures")
        self.plsql_status_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
    def create_bottom_panel(self, parent):
        """Create bottom panel for visualization"""
        vis_frame = ttk.LabelFrame(parent, text="Dependency Graph Visualization", padding="5")
        vis_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        vis_frame.grid_rowconfigure(0, weight=1)
        vis_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas for visualization
        self.canvas = tk.Canvas(vis_frame, bg='white', height=200)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Canvas scrollbars
        canvas_scrollbar_v = ttk.Scrollbar(vis_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        canvas_scrollbar_h = ttk.Scrollbar(vis_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=canvas_scrollbar_v.set, xscrollcommand=canvas_scrollbar_h.set)
        
        canvas_scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        canvas_scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Visualization controls
        vis_controls = ttk.Frame(vis_frame)
        vis_controls.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(vis_controls, text="🔍+ Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(vis_controls, text="🔍- Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(vis_controls, text="📐 Fit All", command=self.fit_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(vis_controls, text="💾 Save Image", command=self.save_visualization).pack(side=tk.LEFT, padx=(0, 5))
        
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN, padding="5")
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Progress bar
        self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
    def browse_ksh_dir(self):
        """Browse for KSH scripts directory"""
        directory = filedialog.askdirectory(title="Select KSH Scripts Directory")
        if directory:
            self.ksh_dir.set(directory)
            
    def browse_ctl_dir(self):
        """Browse for CTL files directory"""
        directory = filedialog.askdirectory(title="Select CTL Files Directory")
        if directory:
            self.ctl_dir.set(directory)
            
    def scan_dependencies(self):
        """Scan for dependencies in background thread"""
        if not self.ksh_dir.get():
            messagebox.showerror("Error", "Please select KSH scripts directory")
            return
            
        if not self.ctl_dir.get():
            messagebox.showerror("Error", "Please select CTL files directory")
            return
            
        # Start scanning in background thread
        self.progress.start()
        self.status_label.config(text="Scanning dependencies...")
        
        thread = threading.Thread(target=self._scan_thread)
        thread.daemon = True
        thread.start()
        
    def _scan_thread(self):
        """Background thread for scanning dependencies"""
        try:
            # Analyze KSH directory
            ksh_results = self.analyzer.analyze_ksh_directory(self.ksh_dir.get())
            
            # Analyze CTL directory
            ctl_results = self.analyzer.analyze_ctl_directory(self.ctl_dir.get())
            
            # Update GUI in main thread
            self.root.after(0, self._update_results, ksh_results, ctl_results)
            
        except Exception as e:
            self.root.after(0, self._scan_error, str(e))
            
    def _update_results(self, ksh_results, ctl_results):
        """Update GUI with scan results"""
        self.progress.stop()
        
        # Update script tree
        self.update_script_tree(ksh_results, ctl_results)
        
        # Update status
        total_scripts = ksh_results['total_files']
        total_ctl = ctl_results['total_files']
        self.status_label.config(text=f"Ready | Scripts: {total_scripts} | CTL Files: {total_ctl}")
        
        messagebox.showinfo("Success", f"Scan completed!\nScripts: {total_scripts}\nCTL Files: {total_ctl}")
        
    def _scan_error(self, error_msg):
        """Handle scan errors"""
        self.progress.stop()
        self.status_label.config(text="Error occurred during scan")
        messagebox.showerror("Scan Error", f"Error during scan: {error_msg}")
        
    def update_script_tree(self, ksh_results, ctl_results):
        """Update the script tree with results"""
        # Clear existing items
        for item in self.script_tree.get_children():
            self.script_tree.delete(item)
            
        # Add KSH Scripts folder
        ksh_node = self.script_tree.insert('', 'end', text=f"📁 KSH Scripts ({ksh_results['total_files']})", 
                                          values=('folder', ''))
        
        # Add scripts
        scripts = self.analyzer.get_all_scripts()
        for script in scripts:
            forward_deps = self.analyzer.get_forward_dependencies(script)
            dep_count = len(forward_deps)
            self.script_tree.insert(ksh_node, 'end', text=script, values=('ksh', dep_count))
            
        # Add CTL Files folder
        ctl_node = self.script_tree.insert('', 'end', text=f"📁 CTL Files ({ctl_results['total_files']})", 
                                          values=('folder', ''))
        
        # Add CTL files
        ctl_files = self.analyzer.get_all_ctl_files()
        for ctl_file in ctl_files:
            self.script_tree.insert(ctl_node, 'end', text=ctl_file, values=('ctl', ''))
            
        # Expand folders
        self.script_tree.item(ksh_node, open=True)
        self.script_tree.item(ctl_node, open=True)
        
    def on_script_select(self, event):
        """Handle script selection in tree"""
        selection = self.script_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        script_name = self.script_tree.item(item, 'text')
        
        # Skip folder items
        if script_name.startswith('📁'):
            return
            
        self.current_script.set(script_name)
        self.selected_label.config(text=f"Selected: {script_name}")
        
        # Update dependency views
        self.update_dependency_views(script_name)
        
        # Update visualization
        self.update_visualization(script_name)
        
    def update_dependency_views(self, script_name):
        """Update forward and backward dependency views"""
        # Clear existing items
        for item in self.forward_tree.get_children():
            self.forward_tree.delete(item)
        for item in self.backward_tree.get_children():
            self.backward_tree.delete(item)
            
        # Update forward dependencies
        forward_deps = self.analyzer.get_forward_dependencies(script_name)
        for dep in forward_deps:
            status = "Commented" if dep.get('commented', False) else "Active"
            if dep['type'] == 'plsql':
                target = f"{dep['schema']}.{dep['package']}.{dep['target']}"
            else:
                target = dep['target']
            self.forward_tree.insert('', 'end', text=target, 
                                   values=(dep['type'], dep['line'], status))
            
        # Update backward dependencies
        backward_deps = self.analyzer.get_backward_dependencies(script_name)
        for dep in backward_deps:
            status = "Commented" if dep.get('commented', False) else "Active"
            self.backward_tree.insert('', 'end', text=dep['source'], 
                                    values=(dep['type'], dep['line'], status))
                                    
    def update_visualization(self, script_name):
        """Update dependency visualization"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Get dependencies
        forward_deps = self.analyzer.get_forward_dependencies(script_name)
        backward_deps = self.analyzer.get_backward_dependencies(script_name)
        
        # Simple visualization - boxes and arrows
        center_x, center_y = 400, 100
        
        # Draw current script in center
        self.canvas.create_rectangle(center_x-50, center_y-15, center_x+50, center_y+15, 
                                   fill='lightblue', outline='blue', width=2)
        self.canvas.create_text(center_x, center_y, text=script_name, font=('Arial', 8, 'bold'))
        
        # Draw forward dependencies (to the right)
        for i, dep in enumerate(forward_deps[:5]):  # Limit to 5 for visibility
            x = center_x + 200
            y = center_y + (i - 2) * 40
            
            # Color based on type
            if dep['type'] == 'script':
                color = 'lightgreen'
            elif dep['type'] == 'ctl':
                color = 'lightyellow'
            else:  # plsql
                color = 'lightcoral'
                
            # Draw box
            self.canvas.create_rectangle(x-60, y-15, x+60, y+15, 
                                       fill=color, outline='black')
            
            # Draw text
            target = dep['target']
            if len(target) > 15:
                target = target[:12] + "..."
            self.canvas.create_text(x, y, text=target, font=('Arial', 7))
            
            # Draw arrow
            self.canvas.create_line(center_x+50, center_y, x-60, y, 
                                  arrow=tk.LAST, fill='blue', width=2)
        
        # Draw backward dependencies (to the left)
        for i, dep in enumerate(backward_deps[:5]):  # Limit to 5 for visibility
            x = center_x - 200
            y = center_y + (i - 2) * 40
            
            # Draw box
            self.canvas.create_rectangle(x-60, y-15, x+60, y+15, 
                                       fill='lightgray', outline='black')
            
            # Draw text
            source = dep['source']
            if len(source) > 15:
                source = source[:12] + "..."
            self.canvas.create_text(x, y, text=source, font=('Arial', 7))
            
            # Draw arrow
            self.canvas.create_line(x+60, y, center_x-50, center_y, 
                                  arrow=tk.LAST, fill='red', width=2)
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_search(self, event):
        """Handle search functionality"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            # Show all items
            for item in self.script_tree.get_children():
                self._show_tree_item(item)
            return
            
        # Filter items
        for item in self.script_tree.get_children():
            self._filter_tree_item(item, search_term)
            
    def _show_tree_item(self, item):
        """Show tree item and its children"""
        self.script_tree.item(item, tags=())
        for child in self.script_tree.get_children(item):
            self._show_tree_item(child)
            
    def _filter_tree_item(self, item, search_term):
        """Filter tree items based on search term"""
        text = self.script_tree.item(item, 'text').lower()
        
        if search_term in text:
            self.script_tree.item(item, tags=())
            # Show parent if child matches
            parent = self.script_tree.parent(item)
            if parent:
                self.script_tree.item(parent, tags=())
        else:
            self.script_tree.item(item, tags=('hidden',))
            
        # Check children
        for child in self.script_tree.get_children(item):
            self._filter_tree_item(child, search_term)
            
    def zoom_in(self):
        """Zoom in visualization"""
        self.canvas.scale("all", 0, 0, 1.2, 1.2)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def zoom_out(self):
        """Zoom out visualization"""
        self.canvas.scale("all", 0, 0, 0.8, 0.8)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def fit_all(self):
        """Fit all items in visualization"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def save_visualization(self):
        """Save visualization as image"""
        messagebox.showinfo("Save Visualization", "Visualization save functionality will be implemented")
        
    def export_dependencies(self):
        """Export dependencies to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Dependencies",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.analyzer.export_dependencies(filename)
                messagebox.showinfo("Success", f"Dependencies exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
                
    def refresh_view(self):
        """Refresh the current view"""
        if self.ksh_dir.get() and self.ctl_dir.get():
            self.scan_dependencies()
            
    def clear_results(self):
        """Clear all results"""
        # Clear tree
        for item in self.script_tree.get_children():
            self.script_tree.delete(item)
            
        # Clear dependency views
        for item in self.forward_tree.get_children():
            self.forward_tree.delete(item)
        for item in self.backward_tree.get_children():
            self.backward_tree.delete(item)
            
        # Clear canvas
        self.canvas.delete("all")
        
        # Reset status
        self.status_label.config(text="Ready")
        self.selected_label.config(text="Selected: None")
        
    def show_db_info(self):
        """Show database information"""
        try:
            conn = sqlite3.connect(self.analyzer.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM scripts")
            script_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM dependencies")
            dep_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ctl_files")
            ctl_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM plsql_calls")
            plsql_count = cursor.fetchone()[0]
            
            conn.close()
            
            info_text = f"""Database Information:
            
Scripts: {script_count}
Dependencies: {dep_count}
CTL Files: {ctl_count}
PL/SQL Calls: {plsql_count}

Database File: {self.analyzer.db_path}"""
            
            messagebox.showinfo("Database Info", info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get database info: {e}")
            
    def on_plsql_search(self, event=None):
        """Handle PL/SQL procedure search"""
        search_term = self.plsql_search_var.get().strip()
        
        # Clear existing results
        for item in self.plsql_results_tree.get_children():
            self.plsql_results_tree.delete(item)
            
        if not search_term:
            self.plsql_status_label.config(text="Enter search term to find PL/SQL procedures")
            return
            
        if len(search_term) < 2:
            self.plsql_status_label.config(text="Search term must be at least 2 characters")
            return
            
        try:
            # Search for procedures
            results = self.analyzer.search_plsql_procedure(search_term)
            
            if not results:
                self.plsql_status_label.config(text=f"No PL/SQL procedures found matching '{search_term}'")
                return
                
            # Display results
            for result in results:
                status = "Commented" if result['is_commented'] else "Active"
                schema = result['schema_name'] or ""
                package = result['package_name'] or ""
                
                self.plsql_results_tree.insert('', 'end', 
                                             text=result['source_script'],
                                             values=(result['procedure_name'], schema, package, 
                                                   result['line_number'], status))
            
            self.plsql_status_label.config(text=f"Found {len(results)} matches for '{search_term}'")
            
        except Exception as e:
            self.plsql_status_label.config(text=f"Search error: {e}")
            
    def clear_plsql_search(self):
        """Clear PL/SQL search results"""
        self.plsql_search_var.set("")
        
        # Clear results
        for item in self.plsql_results_tree.get_children():
            self.plsql_results_tree.delete(item)
            
        self.plsql_status_label.config(text="Enter search term to find PL/SQL procedures")

    def show_about(self):
        """Show about dialog"""
        about_text = """KSH Script Dependency Analyzer
        
Version: 1.1
Author: Assistant
        
This application analyzes KSH/SH scripts to identify:
- Script-to-script dependencies
- CTL file references
- PL/SQL procedure calls

Features:
- Bidirectional dependency mapping
- Visual dependency graphs
- PL/SQL procedure search
- Export functionality
- Search and filter capabilities"""
        
        messagebox.showinfo("About", about_text)


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = KSHAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()