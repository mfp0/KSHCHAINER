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
import datetime
import tempfile
import subprocess
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
        
        # Initialize drag tracking
        self.dragging = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.canvas_objects = {}
        self.element_connections = {}
        
        # Zoom tracking
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        self.create_widgets()
        self.create_menu()
        
        # Bind keyboard shortcuts
        self.root.bind('<F3>', lambda e: self.open_selected_script())
        self.root.bind('<Control-o>', lambda e: self.open_current_in_external_editor())
        
        # Load saved directory paths on startup
        self.load_saved_paths()
        
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="📂 Open Selected Script", command=self.open_selected_script, accelerator="F3")
        file_menu.add_command(label="🖥️ Open in External Editor", command=self.open_current_in_external_editor, accelerator="Ctrl+O")
        file_menu.add_separator()
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
        
        # Script tree with enhanced search support
        self.script_tree = ttk.Treeview(left_frame, columns=('type', 'count'), show='tree headings')
        self.script_tree.heading('#0', text='File')
        self.script_tree.heading('type', text='Type')
        self.script_tree.heading('count', text='Dependencies')
        self.script_tree.column('#0', width=200)
        self.script_tree.column('type', width=60)
        self.script_tree.column('count', width=80)
        
        # Configure treeview tags for search highlighting
        self.script_tree.tag_configure('matched', background='lightyellow', foreground='black')
        self.script_tree.tag_configure('normal', background='white', foreground='black')
        
        # Scrollbars for script tree
        script_scrollbar_v = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.script_tree.yview)
        script_scrollbar_h = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.script_tree.xview)
        self.script_tree.configure(yscrollcommand=script_scrollbar_v.set, xscrollcommand=script_scrollbar_h.set)
        
        self.script_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        script_scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        script_scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind selection event
        self.script_tree.bind('<<TreeviewSelect>>', self.on_script_select)
        
        # Bind right-click context menu
        self.script_tree.bind('<Button-3>', self.show_script_context_menu)
        self.script_tree.bind('<Double-1>', self.open_selected_script)
        
        # Search box for scripts
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        search_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="🔍 Scripts:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        self.search_entry.bind('<Return>', self.on_search)
        
        # Add clear button for script search
        ttk.Button(search_frame, text="✗", command=self.clear_script_search).grid(row=0, column=2, padx=(2, 0))
        
        # Global PL/SQL search box
        plsql_search_frame = ttk.Frame(left_frame)
        plsql_search_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        plsql_search_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(plsql_search_frame, text="🔍 PL/SQL:").grid(row=0, column=0, padx=(0, 5))
        self.global_plsql_search_var = tk.StringVar()
        self.global_plsql_search_entry = ttk.Entry(plsql_search_frame, textvariable=self.global_plsql_search_var)
        self.global_plsql_search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        # Make PL/SQL search truly dynamic with delayed execution
        self.global_plsql_search_entry.bind('<KeyRelease>', self._delayed_plsql_search)
        self.global_plsql_search_entry.bind('<Return>', self.on_global_plsql_search)
        
        # Add timer for delayed search
        self._plsql_search_timer = None

        ttk.Button(plsql_search_frame, text="🔍", command=self.on_global_plsql_search).grid(row=0, column=2)
        
        # Add clear button for PL/SQL search
        ttk.Button(plsql_search_frame, text="✗", command=self.clear_global_plsql_search).grid(row=0, column=3, padx=(2, 0))
        
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
        
    def create_bottom_panel(self, parent):
        """Create bottom panel with PL/SQL results and visualization"""
        # Create notebook for bottom panel
        bottom_notebook = ttk.Notebook(parent)
        bottom_notebook.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # PL/SQL Search Results tab
        plsql_results_frame = ttk.Frame(bottom_notebook)
        bottom_notebook.add(plsql_results_frame, text="Global PL/SQL Search Results")
        
        # PL/SQL Results display with enhanced columns
        self.global_plsql_results_tree = ttk.Treeview(plsql_results_frame, 
                                              columns=('full_procedure', 'procedure', 'schema', 'package', 'line', 'commented', 'match_quality'), 
                                              show='tree headings')
        self.global_plsql_results_tree.heading('#0', text='Calling Script')
        self.global_plsql_results_tree.heading('full_procedure', text='Full Procedure Name')
        self.global_plsql_results_tree.heading('procedure', text='Procedure')
        self.global_plsql_results_tree.heading('schema', text='Schema')
        self.global_plsql_results_tree.heading('package', text='Package')
        self.global_plsql_results_tree.heading('line', text='Line')
        self.global_plsql_results_tree.heading('commented', text='Status')
        self.global_plsql_results_tree.heading('match_quality', text='Match Quality')
        
        self.global_plsql_results_tree.column('#0', width=180)
        self.global_plsql_results_tree.column('full_procedure', width=250)
        self.global_plsql_results_tree.column('procedure', width=150)
        self.global_plsql_results_tree.column('schema', width=100)
        self.global_plsql_results_tree.column('package', width=130)
        self.global_plsql_results_tree.column('line', width=60)
        self.global_plsql_results_tree.column('commented', width=80)
        self.global_plsql_results_tree.column('match_quality', width=120)
        
        global_plsql_scrollbar = ttk.Scrollbar(plsql_results_frame, orient=tk.VERTICAL, command=self.global_plsql_results_tree.yview)
        self.global_plsql_results_tree.configure(yscrollcommand=global_plsql_scrollbar.set)
        
        self.global_plsql_results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        global_plsql_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        plsql_results_frame.grid_rowconfigure(0, weight=1)
        plsql_results_frame.grid_columnconfigure(0, weight=1)
        
        # Status label for global search results
        self.global_plsql_status_label = ttk.Label(plsql_results_frame, text="Use PL/SQL search box above to find procedures across all scripts")
        self.global_plsql_status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Visualization tab
        vis_frame = ttk.Frame(bottom_notebook)
        bottom_notebook.add(vis_frame, text="Dependency Graph Visualization")
        vis_frame.grid_rowconfigure(0, weight=1)
        vis_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas for visualization with drag support
        self.canvas = tk.Canvas(vis_frame, bg='white', height=200)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Canvas scrollbars
        canvas_scrollbar_v = ttk.Scrollbar(vis_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        canvas_scrollbar_h = ttk.Scrollbar(vis_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=canvas_scrollbar_v.set, xscrollcommand=canvas_scrollbar_h.set)
        
        canvas_scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        canvas_scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Drag support variables
        self.dragging = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.canvas_objects = {}  # Store canvas objects with their IDs
        self.element_connections = {}  # Store connections between elements
        
        # Store current zoom factor
        self.zoom_factor = 1.0
        
        # Bind drag events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Mouse wheel zoom support with cursor position
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows/Mac
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux scroll down
        
        # Key bindings for zoom
        self.canvas.bind("<Control-plus>", lambda e: self.zoom_in())
        self.canvas.bind("<Control-minus>", lambda e: self.zoom_out())
        self.canvas.bind("<Control-0>", lambda e: self.reset_zoom())
        
        # Focus the canvas to receive key events
        self.canvas.focus_set()
        
        # Visualization controls
        vis_controls = ttk.Frame(vis_frame)
        vis_controls.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(vis_controls, text="🔍+ Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(vis_controls, text="🔍- Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(vis_controls, text="🔄 Reset Zoom", command=self.reset_zoom).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(vis_controls, text="📐 Fit All", command=self.fit_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(vis_controls, text="💾 Save Image", command=self.save_visualization).pack(side=tk.LEFT, padx=(0, 5))
        
        # Add zoom level indicator
        self.zoom_label = ttk.Label(vis_controls, text="Zoom: 100%")
        self.zoom_label.pack(side=tk.LEFT, padx=(10, 0))
        
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
        
        # Save directory paths for future use
        self.analyzer.save_directory_paths(self.ksh_dir.get(), self.ctl_dir.get())
        
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
            
        # Update forward dependencies (commented dependencies are now excluded by analyzer)
        forward_deps = self.analyzer.get_forward_dependencies(script_name)
        for dep in forward_deps:
            status = "Active"  # All dependencies are active since commented ones are excluded
            if dep['type'] == 'plsql':
                # Build proper PL/SQL name format
                schema = dep.get('schema', '')
                package = dep.get('package', '')
                procedure = dep['target']
                
                if schema and package:
                    target = f"{schema}.{package}.{procedure}"
                elif package:
                    target = f"{package}.{procedure}"
                else:
                    target = procedure
            else:
                target = dep['target']
            self.forward_tree.insert('', 'end', text=target, 
                                   values=(dep['type'], dep['line'], status))
            
        # Update backward dependencies (commented dependencies are now excluded by analyzer)
        backward_deps = self.analyzer.get_backward_dependencies(script_name)
        for dep in backward_deps:
            status = "Active"  # All dependencies are active since commented ones are excluded
            self.backward_tree.insert('', 'end', text=dep['source'], 
                                    values=(dep['type'], dep['line'], status))
                                    
    def update_visualization(self, script_name):
        """Update dependency visualization with draggable elements"""
        # Clear canvas and tracking variables
        self.canvas.delete("all")
        self.canvas_objects = {}
        self.element_connections = {}
        
        # Get dependencies
        forward_deps = self.analyzer.get_forward_dependencies(script_name)
        backward_deps = self.analyzer.get_backward_dependencies(script_name)
        
        # Build dependency chain if script is part of one
        chain = self.build_dependency_chain(script_name)
        
        if len(chain) > 2:  # If we have a chain
            # Draw the main chain AND additional dependencies for complete cartography
            self.draw_comprehensive_chain_view(chain, script_name, forward_deps, backward_deps)
        else:
            # Draw star diagram with all dependency types
            self.draw_star_diagram(script_name, forward_deps, backward_deps)
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def build_dependency_chain(self, script_name):
        """Build dependency chain starting from the given script"""
        chain = [script_name]
        visited = {script_name}
        
        # Build forward chain
        current = script_name
        while True:
            forward_deps = self.analyzer.get_forward_dependencies(current)
            script_deps = [dep for dep in forward_deps if dep['type'] in ['script', 'ctl']]
            
            if not script_deps:
                break
                
            # Prioritize script files to continue the chain, then CTL files
            next_script = None
            
            # First, look for script dependencies to continue the chain
            # Avoid common utility scripts in favor of more specific ones
            common_scripts = ['config.ksh', 'utils.ksh', 'notify.ksh', 'common.ksh']
            
            # First try non-common scripts
            for dep in script_deps:
                if (dep['target'] not in visited and 
                    dep['type'] == 'script' and 
                    dep['target'] not in common_scripts):
                    next_script = dep['target']
                    break
            
            # If no specific scripts, take any script dependency
            if not next_script:
                for dep in script_deps:
                    if dep['target'] not in visited and dep['type'] == 'script':
                        next_script = dep['target']
                        break
            
            # Only if no scripts found, look for CTL files (but these usually end the chain)
            if not next_script:
                for dep in script_deps:
                    if dep['target'] not in visited and dep['type'] == 'ctl':
                        next_script = dep['target']
                        break
            
            if not next_script:
                break
                
            chain.append(next_script)
            visited.add(next_script)
            current = next_script
            
            # Prevent infinite loops
            if len(chain) > 10:
                break
        
        # Build backward chain
        current = script_name
        backward_chain = []
        while True:
            backward_deps = self.analyzer.get_backward_dependencies(current)
            script_deps = [dep for dep in backward_deps if dep['type'] in ['script', 'ctl']]
            
            if not script_deps:
                break
                
            # Prioritize script files in backward chain (CTL files don't call other files)
            prev_script = None
            
            # Look for script dependencies first (CTL files are typically endpoints)
            for dep in script_deps:
                if dep['source'] not in visited and dep['type'] == 'script':
                    prev_script = dep['source']
                    break
            
            # If no scripts, check CTL files (though this is rare)
            if not prev_script:
                for dep in script_deps:
                    if dep['source'] not in visited and dep['type'] == 'ctl':
                        prev_script = dep['source']
                        break
            
            if not prev_script:
                break
                
            backward_chain.insert(0, prev_script)
            visited.add(prev_script)
            current = prev_script
            
            # Prevent infinite loops
            if len(backward_chain) > 10:
                break
        
        return backward_chain + chain
    
    def draw_dependency_chain(self, chain, selected_script):
        """Draw dependency chain visualization with auto-sized rectangles and connected arrows"""
        if not chain:
            return
            
        start_x = 50
        start_y = 100
        min_box_height = 40
        min_spacing = 200  # Minimum spacing between elements
        
        # Store element positions and connections
        elements = {}
        
        # First pass: calculate text dimensions and positions for all elements
        text_dimensions = {}
        box_widths = {}
        positions = []
        
        for script in chain:
            text_width, text_height = self.calculate_text_dimensions(script, ('Arial', 9, 'bold'))
            text_dimensions[script] = (text_width, text_height)
            box_width = max(text_width + 20, 100)
            box_widths[script] = box_width
        
        # Calculate positions with dynamic spacing to avoid overlaps
        current_x = start_x
        for i, script in enumerate(chain):
            if i == 0:
                x = current_x
            else:
                # Calculate spacing based on previous and current box widths
                prev_script = chain[i-1]
                prev_box_width = box_widths[prev_script]
                current_box_width = box_widths[script]
                
                # Minimum gap between boxes
                min_gap = 30
                required_spacing = prev_box_width//2 + current_box_width//2 + min_gap
                actual_spacing = max(min_spacing, required_spacing)
                
                x = positions[i-1] + actual_spacing
            
            positions.append(x)
            current_x = x
        
        for i, script in enumerate(chain):
            x = positions[i]
            y = start_y
            
            # Calculate box dimensions based on text size
            text_width, text_height = text_dimensions[script]
            box_width = box_widths[script]  # Use pre-calculated width
            box_height = max(text_height + 10, min_box_height)  # Minimum height, padding of 10
            
            # Determine color based on file type
            if script == selected_script:
                color = 'lightblue'
                outline = 'blue'
                width = 3
            elif script.endswith('.ctl'):
                color = 'lightyellow'
                outline = 'orange'
                width = 2
            else:
                color = 'lightgreen'
                outline = 'darkgreen'
                width = 2
            
            # Create draggable rectangle with calculated dimensions
            group_tag = f"group_{i}"
            rect = self.canvas.create_rectangle(
                x - box_width//2, y - box_height//2,
                x + box_width//2, y + box_height//2,
                fill=color, outline=outline, width=width,
                tags=('draggable', 'rect', group_tag)
            )
            
            # Create draggable text (no truncation)
            text = self.canvas.create_text(
                x, y, text=script, font=('Arial', 9, 'bold'),
                tags=('draggable', 'text', group_tag)
            )
            
            # Store element info with actual dimensions
            elements[group_tag] = {
                'rect': rect,
                'text': text,
                'center_x': x,
                'center_y': y,
                'box_width': box_width,
                'box_height': box_height,
                'arrows_out': [],
                'arrows_in': []
            }
            
            # Create step label
            step_label = self.canvas.create_text(
                x, y - box_height//2 - 20, text=f"Step {i+1}", font=('Arial', 8),
                fill='darkred', tags=('step_label', group_tag)
            )
            elements[group_tag]['step_label'] = step_label
        
        # Create arrows between elements
        for i in range(len(chain) - 1):
            source_tag = f"group_{i}"
            target_tag = f"group_{i+1}"
            
            source_elem = elements[source_tag]
            target_elem = elements[target_tag]
            
            # Create arrow
            arrow = self.canvas.create_line(
                source_elem['center_x'] + source_elem['box_width']//2, source_elem['center_y'],
                target_elem['center_x'] - target_elem['box_width']//2, target_elem['center_y'],
                arrow=tk.LAST, fill='darkblue', width=2,
                tags=('arrow', f'arrow_{i}')
            )
            
            # Store arrow connections
            elements[source_tag]['arrows_out'].append(arrow)
            elements[target_tag]['arrows_in'].append(arrow)
            
            # Store arrow connection info for updating during drag
            self.element_connections[arrow] = {
                'source': source_tag,
                'target': target_tag,
                'type': 'chain'
            }
        
        # Store all elements for drag operations
        self.canvas_objects.update(elements)
    
    def draw_comprehensive_chain_view(self, chain, selected_script, forward_deps, backward_deps):
        """Draw comprehensive view showing both chain and additional dependencies"""
        # First draw the main chain
        self.draw_dependency_chain(chain, selected_script)
        
        # Then add additional dependencies that aren't part of the main chain
        self.add_additional_dependencies_to_chain(selected_script, forward_deps, backward_deps, chain)
    
    def add_additional_dependencies_to_chain(self, script_name, forward_deps, backward_deps, chain):
        """Add CTL files and PL/SQL procedures to the chain visualization"""
        # Find the script in the chain to get its position
        script_index = chain.index(script_name) if script_name in chain else -1
        if script_index == -1:
            return
        
        # Get the position of the selected script from existing chain visualization
        script_tag = f"group_{script_index}"
        if script_tag not in self.canvas_objects:
            return
        
        script_elem = self.canvas_objects[script_tag]
        center_x = script_elem['center_x']
        center_y = script_elem['center_y']
        
        additional_elements = {}
        
        # Add forward dependencies (CTL and PL/SQL) below the chain
        forward_non_script_deps = [dep for dep in forward_deps if dep['type'] in ['ctl', 'plsql'] or 
                                  (dep['type'] == 'script' and dep['target'] not in chain)]
        
        for i, dep in enumerate(forward_non_script_deps[:8]):  # Limit for visibility
            x = center_x + (i - len(forward_non_script_deps)//2) * 120  # Spread horizontally
            y = center_y + 120  # Below the main chain
            
            # Determine color and display text based on type
            if dep['type'] == 'ctl':
                color = 'lightyellow'
                outline = 'orange'
                display_text = dep['target']
                icon = '📄'
            elif dep['type'] == 'plsql':
                color = 'lightcoral'
                outline = 'darkred'
                # Format PL/SQL procedure name
                schema = dep.get('schema', '')
                package = dep.get('package', '')
                procedure = dep['target']
                if schema and package:
                    display_text = f"{schema}.{package}.{procedure}"
                elif package:
                    display_text = f"{package}.{procedure}"
                else:
                    display_text = procedure
                # Truncate if too long
                if len(display_text) > 25:
                    display_text = display_text[:22] + "..."
                icon = '⚡'
            else:  # script not in chain
                color = 'lightgreen'
                outline = 'darkgreen'
                display_text = dep['target']
                icon = '📜'
            
            # Calculate text dimensions
            full_text = f"{icon} {display_text}"
            text_width, text_height = self.calculate_text_dimensions(full_text, ('Arial', 8))
            box_width = max(text_width + 20, 100)
            box_height = max(text_height + 10, 30)
            
            # Create draggable box
            group_tag = f"group_additional_forward_{i}"
            rect = self.canvas.create_rectangle(
                x - box_width//2, y - box_height//2,
                x + box_width//2, y + box_height//2,
                fill=color, outline=outline, width=2,
                tags=('draggable', 'rect', group_tag)
            )
            
            text = self.canvas.create_text(
                x, y, text=full_text, font=('Arial', 8),
                tags=('draggable', 'text', group_tag)
            )
            
            # Store element info
            additional_elements[group_tag] = {
                'rect': rect,
                'text': text,
                'center_x': x,
                'center_y': y,
                'box_width': box_width,
                'box_height': box_height,
                'arrows_out': [],
                'arrows_in': []
            }
            
            # Create arrow from main script to this dependency
            arrow = self.canvas.create_line(
                center_x, center_y + script_elem['box_height']//2,
                x, y - box_height//2,
                arrow=tk.LAST, fill=outline, width=2,
                tags=('arrow', f'additional_forward_arrow_{i}')
            )
            
            # Store arrow connection
            self.canvas_objects[script_tag]['arrows_out'].append(arrow)
            additional_elements[group_tag]['arrows_in'].append(arrow)
            
            self.element_connections[arrow] = {
                'source': script_tag,
                'target': group_tag,
                'type': 'additional_forward'
            }
        
        # Add backward dependencies (scripts not in chain) above the chain
        backward_non_script_deps = [dep for dep in backward_deps if dep['type'] == 'script' and dep['source'] not in chain]
        
        for i, dep in enumerate(backward_non_script_deps[:5]):  # Limit for visibility
            x = center_x + (i - len(backward_non_script_deps)//2) * 120  # Spread horizontally
            y = center_y - 120  # Above the main chain
            
            color = 'lightgray'
            outline = 'black'
            display_text = f"📜 {dep['source']}"
            
            # Calculate text dimensions
            text_width, text_height = self.calculate_text_dimensions(display_text, ('Arial', 8))
            box_width = max(text_width + 20, 100)
            box_height = max(text_height + 10, 30)
            
            # Create draggable box
            group_tag = f"group_additional_backward_{i}"
            rect = self.canvas.create_rectangle(
                x - box_width//2, y - box_height//2,
                x + box_width//2, y + box_height//2,
                fill=color, outline=outline, width=2,
                tags=('draggable', 'rect', group_tag)
            )
            
            text = self.canvas.create_text(
                x, y, text=display_text, font=('Arial', 8),
                tags=('draggable', 'text', group_tag)
            )
            
            # Store element info
            additional_elements[group_tag] = {
                'rect': rect,
                'text': text,
                'center_x': x,
                'center_y': y,
                'box_width': box_width,
                'box_height': box_height,
                'arrows_out': [],
                'arrows_in': []
            }
            
            # Create arrow from this dependency to main script
            arrow = self.canvas.create_line(
                x, y + box_height//2,
                center_x, center_y - script_elem['box_height']//2,
                arrow=tk.LAST, fill=outline, width=2,
                tags=('arrow', f'additional_backward_arrow_{i}')
            )
            
            # Store arrow connection
            additional_elements[group_tag]['arrows_out'].append(arrow)
            self.canvas_objects[script_tag]['arrows_in'].append(arrow)
            
            self.element_connections[arrow] = {
                'source': group_tag,
                'target': script_tag,
                'type': 'additional_backward'
            }
        
        # Update the canvas objects with additional elements
        self.canvas_objects.update(additional_elements)
    
    def calculate_text_dimensions(self, text, font):
        """Calculate text dimensions for proper rectangle sizing"""
        try:
            # Create a temporary text item to measure dimensions
            temp_text = self.canvas.create_text(0, 0, text=text, font=font)
            bbox = self.canvas.bbox(temp_text)
            
            if bbox:
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
            else:
                # Fallback to estimated dimensions
                width = len(text) * 8  # Rough estimate: 8 pixels per character
                height = 16  # Standard text height
            
            # Clean up temporary text
            self.canvas.delete(temp_text)
            
            return width, height
        except:
            # Fallback dimensions if measurement fails
            return len(text) * 8, 16
    
    def draw_star_diagram(self, script_name, forward_deps, backward_deps):
        """Draw star-style dependency diagram with auto-sized rectangles and connected arrows"""
        center_x, center_y = 400, 150
        elements = {}
        
        # Calculate center script dimensions
        center_text_width, center_text_height = self.calculate_text_dimensions(script_name, ('Arial', 10, 'bold'))
        center_box_width = max(center_text_width + 20, 120)
        center_box_height = max(center_text_height + 10, 40)
        
        # Draw current script in center (draggable) with auto-sizing
        center_tag = "group_center"
        center_rect = self.canvas.create_rectangle(
            center_x - center_box_width//2, center_y - center_box_height//2,
            center_x + center_box_width//2, center_y + center_box_height//2,
            fill='lightblue', outline='blue', width=3,
            tags=('draggable', 'rect', center_tag)
        )
        center_text = self.canvas.create_text(
            center_x, center_y, text=script_name, font=('Arial', 10, 'bold'),
            tags=('draggable', 'text', center_tag)
        )
        
        # Store center element with actual dimensions
        elements[center_tag] = {
            'rect': center_rect,
            'text': center_text,
            'center_x': center_x,
            'center_y': center_y,
            'box_width': center_box_width,
            'box_height': center_box_height,
            'arrows_out': [],
            'arrows_in': []
        }
        
        # Draw forward dependencies (to the right) - include ALL types for complete cartography
        for i, dep in enumerate(forward_deps[:8]):  # Increased limit for more comprehensive view
            x = center_x + 350  # Increased distance to accommodate larger boxes
            y = center_y + (i - 2) * 80  # Increased vertical spacing
            
            # Color and formatting based on type
            if dep['type'] == 'script':
                color = 'lightgreen'
                outline = 'darkgreen'
                display_text = f"📜 {dep['target']}"
            elif dep['type'] == 'ctl':
                color = 'lightyellow'
                outline = 'orange'
                display_text = f"📄 {dep['target']}"
            else:  # plsql
                color = 'lightcoral'
                outline = 'darkred'
                # Format PL/SQL procedure name
                schema = dep.get('schema', '')
                package = dep.get('package', '')
                procedure = dep['target']
                if schema and package:
                    proc_name = f"{schema}.{package}.{procedure}"
                elif package:
                    proc_name = f"{package}.{procedure}"
                else:
                    proc_name = procedure
                # Truncate if too long
                if len(proc_name) > 30:
                    proc_name = proc_name[:27] + "..."
                display_text = f"⚡ {proc_name}"
            
            # Calculate text dimensions for auto-sizing
            target_text_width, target_text_height = self.calculate_text_dimensions(display_text, ('Arial', 8))
            target_box_width = max(target_text_width + 20, 100)
            target_box_height = max(target_text_height + 10, 30)
            
            # Create draggable box with auto-sizing
            group_tag = f"group_forward_{i}"
            rect = self.canvas.create_rectangle(
                x - target_box_width//2, y - target_box_height//2,
                x + target_box_width//2, y + target_box_height//2,
                fill=color, outline=outline, width=2,
                tags=('draggable', 'rect', group_tag)
            )
            
            # Create draggable text with icon and formatting
            text = self.canvas.create_text(
                x, y, text=display_text, font=('Arial', 8),
                tags=('draggable', 'text', group_tag)
            )
            
            # Store element info with actual dimensions
            elements[group_tag] = {
                'rect': rect,
                'text': text,
                'center_x': x,
                'center_y': y,
                'box_width': target_box_width,
                'box_height': target_box_height,
                'arrows_out': [],
                'arrows_in': []
            }
            
            # Create arrow using actual box dimensions
            arrow = self.canvas.create_line(
                center_x + center_box_width//2, center_y, 
                x - target_box_width//2, y,
                arrow=tk.LAST, fill='blue', width=2,
                tags=('arrow', f'forward_arrow_{i}')
            )
            
            # Store arrow connections
            elements[center_tag]['arrows_out'].append(arrow)
            elements[group_tag]['arrows_in'].append(arrow)
            
            self.element_connections[arrow] = {
                'source': center_tag,
                'target': group_tag,
                'type': 'forward'
            }
        
        # Draw backward dependencies (to the left)
        for i, dep in enumerate(backward_deps[:8]):  # Increased limit for more comprehensive view
            x = center_x - 350  # Increased distance to accommodate larger boxes
            y = center_y + (i - 2) * 80  # Increased vertical spacing
            
            # Format source with icon
            source = dep['source']
            display_text = f"📜 {source}"
            
            # Calculate text dimensions for auto-sizing
            source_text_width, source_text_height = self.calculate_text_dimensions(display_text, ('Arial', 8))
            source_box_width = max(source_text_width + 20, 100)
            source_box_height = max(source_text_height + 10, 30)
            
            # Create draggable box with auto-sizing
            group_tag = f"group_backward_{i}"
            rect = self.canvas.create_rectangle(
                x - source_box_width//2, y - source_box_height//2,
                x + source_box_width//2, y + source_box_height//2,
                fill='lightgray', outline='black', width=2,
                tags=('draggable', 'rect', group_tag)
            )
            
            # Create draggable text with icon
            text = self.canvas.create_text(
                x, y, text=display_text, font=('Arial', 8),
                tags=('draggable', 'text', group_tag)
            )
            
            # Store element info with actual dimensions
            elements[group_tag] = {
                'rect': rect,
                'text': text,
                'center_x': x,
                'center_y': y,
                'box_width': source_box_width,
                'box_height': source_box_height,
                'arrows_out': [],
                'arrows_in': []
            }
            
            # Create arrow using actual box dimensions
            arrow = self.canvas.create_line(
                x + source_box_width//2, y, 
                center_x - center_box_width//2, center_y,
                arrow=tk.LAST, fill='red', width=2,
                tags=('arrow', f'backward_arrow_{i}')
            )
            
            # Store arrow connections
            elements[group_tag]['arrows_out'].append(arrow)
            elements[center_tag]['arrows_in'].append(arrow)
            
            self.element_connections[arrow] = {
                'source': group_tag,
                'target': center_tag,
                'type': 'backward'
            }
        
        # Store all elements for drag operations
        self.canvas_objects.update(elements)
        
    def on_search(self, event=None):
        """Handle dynamic KSH script search functionality"""
        search_term = self.search_var.get().strip().lower()
        
        if not search_term:
            # Show all items and clear highlights
            self._restore_all_items()
            return
        
        # Dynamic filtering with highlighting
        matched_count = 0
        all_items = self._get_all_tree_items()
        
        # Store original structure for restoration
        if not hasattr(self, '_original_tree_structure'):
            self._store_original_tree_structure()
        
        # Clear current tree
        for item in self.script_tree.get_children():
            self.script_tree.delete(item)
        
        # Rebuild tree with only matching items
        for item_data in all_items:
            if self._item_matches_search(item_data, search_term):
                self._add_matching_item(item_data, search_term)
                matched_count += 1
        
        # Auto-select if single match
        if matched_count == 1:
            items = self.script_tree.get_children()
            if items:
                self.script_tree.selection_set(items[0])
                self.script_tree.focus(items[0])
            
    def _show_tree_item(self, item):
        """Show tree item and its children"""
        self.script_tree.item(item, tags=())
        for child in self.script_tree.get_children(item):
            self._show_tree_item(child)
            
    def _get_all_tree_items(self):
        """Get all tree items with their data"""
        if not hasattr(self, '_all_tree_items'):
            self._all_tree_items = []
            
        # If we have stored items, return them
        if self._all_tree_items:
            return self._all_tree_items
            
        # Otherwise, collect from current tree
        items = []
        for item in self.script_tree.get_children():
            items.extend(self._collect_item_data(item))
        return items
    
    def _collect_item_data(self, item):
        """Recursively collect item data"""
        items = []
        text = self.script_tree.item(item, 'text')
        values = self.script_tree.item(item, 'values')
        
        items.append({
            'text': text,
            'values': values,
            'parent': None,
            'children': []
        })
        
        # Collect children
        for child in self.script_tree.get_children(item):
            child_items = self._collect_item_data(child)
            items.extend(child_items)
        
        return items
    
    def _store_original_tree_structure(self):
        """Store the original tree structure for restoration"""
        self._original_tree_structure = []
        for item in self.script_tree.get_children():
            self._original_tree_structure.extend(self._collect_item_data(item))
    
    def _item_matches_search(self, item_data, search_term):
        """Check if item matches search term"""
        text = item_data['text'].lower()
        values_text = ' '.join(str(v).lower() for v in item_data['values'])
        all_text = f"{text} {values_text}"
        return search_term in all_text
    
    def _add_matching_item(self, item_data, search_term):
        """Add matching item to tree with highlighting"""
        text = item_data['text']
        values = item_data['values']
        
        # Add item with highlighting if it contains search term
        if search_term in text.lower():
            tag = 'matched'
        else:
            tag = 'normal'
            
        self.script_tree.insert('', 'end', text=text, values=values, tags=(tag,))
    
    def _restore_all_items(self):
        """Restore all original items"""
        # Clear current tree
        for item in self.script_tree.get_children():
            self.script_tree.delete(item)
        
        # Restore from original structure if available
        if hasattr(self, '_original_tree_structure'):
            for item_data in self._original_tree_structure:
                self.script_tree.insert('', 'end', 
                                      text=item_data['text'], 
                                      values=item_data['values'], 
                                      tags=('normal',))
        else:
            # Fallback: refresh the data
            if hasattr(self, 'analyzer') and self.ksh_dir.get():
                self.scan_dependencies()
    
    def clear_script_search(self):
        """Clear script search and restore all items"""
        self.search_var.set("")
        self._restore_all_items()
            
    def zoom_in(self):
        """Zoom in visualization"""
        if self.zoom_factor < self.max_zoom:
            self._zoom_canvas(1.2)
        
    def zoom_out(self):
        """Zoom out visualization"""
        if self.zoom_factor > self.min_zoom:
            self._zoom_canvas(0.8)
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        if self.zoom_factor != 1.0:
            self._zoom_canvas(1.0 / self.zoom_factor)
        
    def _zoom_canvas(self, scale_factor):
        """Zoom canvas and update arrow connections"""
        # Update zoom factor
        self.zoom_factor *= scale_factor
        
        # Get canvas center for zoom origin
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        
        # Scale all canvas items from center
        self.canvas.scale("all", center_x, center_y, scale_factor, scale_factor)
        
        # Update canvas object positions after scaling
        for group_tag, obj_info in self.canvas_objects.items():
            if 'center_x' in obj_info and 'center_y' in obj_info:
                # Scale positions relative to center
                obj_info['center_x'] = center_x + (obj_info['center_x'] - center_x) * scale_factor
                obj_info['center_y'] = center_y + (obj_info['center_y'] - center_y) * scale_factor
                if 'box_width' in obj_info and 'box_height' in obj_info:
                    obj_info['box_width'] *= scale_factor
                    obj_info['box_height'] *= scale_factor
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Update zoom label
        zoom_percent = int(self.zoom_factor * 100)
        self.zoom_label.config(text=f"Zoom: {zoom_percent}%")
        
        # Force arrow updates by updating all connections
        self._update_all_arrows()
    
    def _update_all_arrows(self):
        """Update all arrow connections after zoom or other transformations"""
        for arrow_id, connection_info in self.element_connections.items():
            if connection_info['source'] in self.canvas_objects and connection_info['target'] in self.canvas_objects:
                source_elem = self.canvas_objects[connection_info['source']]
                target_elem = self.canvas_objects[connection_info['target']]
                
                # Calculate new arrow coordinates
                if connection_info['type'] == 'chain':
                    x1 = source_elem['center_x'] + source_elem['box_width']//2
                    y1 = source_elem['center_y']
                    x2 = target_elem['center_x'] - target_elem['box_width']//2
                    y2 = target_elem['center_y']
                else:  # star diagram arrows
                    x1 = source_elem['center_x'] + source_elem['box_width']//2
                    y1 = source_elem['center_y']
                    x2 = target_elem['center_x'] - target_elem['box_width']//2
                    y2 = target_elem['center_y']
                
                # Update arrow coordinates
                self.canvas.coords(arrow_id, x1, y1, x2, y2)
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel zoom centered on cursor position"""
        # Check zoom limits
        if event.delta > 0 or event.num == 4:  # Zoom in
            if self.zoom_factor >= self.max_zoom:
                return
            scale_factor = 1.1
        else:  # Zoom out
            if self.zoom_factor <= self.min_zoom:
                return
            scale_factor = 0.9
        
        # Get mouse position in canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Update zoom factor
        self.zoom_factor *= scale_factor
        
        # Scale all canvas items from mouse position
        self.canvas.scale("all", canvas_x, canvas_y, scale_factor, scale_factor)
        
        # Update canvas object positions after scaling
        for group_tag, obj_info in self.canvas_objects.items():
            if 'center_x' in obj_info and 'center_y' in obj_info:
                # Scale positions relative to mouse position
                obj_info['center_x'] = canvas_x + (obj_info['center_x'] - canvas_x) * scale_factor
                obj_info['center_y'] = canvas_y + (obj_info['center_y'] - canvas_y) * scale_factor
                if 'box_width' in obj_info and 'box_height' in obj_info:
                    obj_info['box_width'] *= scale_factor
                    obj_info['box_height'] *= scale_factor
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Update zoom label
        zoom_percent = int(self.zoom_factor * 100)
        self.zoom_label.config(text=f"Zoom: {zoom_percent}%")
        
        # Force arrow updates
        self._update_all_arrows()
        
    def fit_all(self):
        """Fit all items in visualization"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def save_visualization(self):
        """Save visualization as image using built-in Python libraries"""
        # Check if there's anything to save
        if not self.canvas_objects:
            messagebox.showwarning("No Visualization", "No visualization to save. Please select a script first.")
            return
        
        # Get save location and format
        filename = filedialog.asksaveasfilename(
            title="Save Visualization",
            defaultextension=".ps",
            filetypes=[
                ("PostScript files", "*.ps"),
                ("Text representation", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return
        
        try:
            # Determine format from extension
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.ps':
                self._save_as_postscript(filename)
            elif file_ext == '.txt':
                self._save_as_text(filename)
            else:
                # Default to PostScript
                self._save_as_postscript(filename)
            
            messagebox.showinfo("Success", f"Visualization saved to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save visualization: {e}")
    
    def _save_as_postscript(self, filename):
        """Save canvas as PostScript file with enhanced formatting"""
        # Get the bounding box of all items
        bbox = self.canvas.bbox("all")
        if not bbox:
            raise ValueError("No items to save")
        
        # Add some padding
        padding = 30
        x1, y1, x2, y2 = bbox
        x1 -= padding
        y1 -= padding
        x2 += padding
        y2 += padding
        
        # Calculate page size (limit to reasonable dimensions)
        width = x2 - x1
        height = y2 - y1
        max_size = 800  # Maximum dimension
        
        if width > max_size or height > max_size:
            scale = max_size / max(width, height)
            width *= scale
            height *= scale
        
        # Save as PostScript with enhanced settings
        self.canvas.postscript(
            file=filename,
            x=x1, y=y1,
            width=x2-x1, height=y2-y1,
            pagewidth=width, pageheight=height,
            colormode='color',
            pageanchor='nw'
        )
        
        # Add metadata comment to the PostScript file
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            # Add custom header with metadata
            header = f"""%%!PS-Adobe-3.0 EPSF-3.0
%%Creator: KSH Script Dependency Analyzer v1.2
%%Title: Dependency Visualization
%%CreationDate: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
%%DocumentData: Clean7Bit
%%LanguageLevel: 2
%%Pages: 1
%%BoundingBox: 0 0 {int(width)} {int(height)}
%%EndComments

"""
            
            # Find the original PS header and replace it
            if content.startswith('%!PS-Adobe'):
                # Find end of original header
                end_header = content.find('%%EndComments')
                if end_header > 0:
                    content = header + content[end_header + len('%%EndComments'):]
                else:
                    content = header + content[content.find('\n') + 1:]
            else:
                content = header + content
            
            with open(filename, 'w') as f:
                f.write(content)
                
        except Exception:
            # If metadata addition fails, the basic PostScript file is still valid
            pass
    
    def _save_as_text(self, filename):
        """Save visualization as text representation"""
        # Create text representation of the dependency diagram
        text_content = []
        text_content.append("KSH Script Dependency Visualization")
        text_content.append("=" * 50)
        text_content.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        text_content.append(f"Total elements: {len(self.canvas_objects)}")
        text_content.append("")
        
        # Add current script info if available
        if hasattr(self, 'current_script') and self.current_script.get():
            text_content.append(f"Selected Script: {self.current_script.get()}")
            text_content.append("")
        
        # Group elements by type
        elements_by_type = {
            'scripts': [],
            'ctl_files': [],
            'plsql': [],
            'other': []
        }
        
        for group_tag, element in self.canvas_objects.items():
            # Get the text content of the element
            if 'text' in element:
                text_items = self.canvas.find_withtag(group_tag)
                element_text = ""
                for item in text_items:
                    item_type = self.canvas.type(item)
                    if item_type == "text":
                        element_text = self.canvas.itemcget(item, "text")
                        break
                
                # Categorize based on content or group tag
                if 'script' in group_tag.lower() or element_text.endswith('.ksh') or element_text.endswith('.sh'):
                    elements_by_type['scripts'].append(element_text)
                elif 'ctl' in group_tag.lower() or element_text.endswith('.ctl'):
                    elements_by_type['ctl_files'].append(element_text)
                elif '⚡' in element_text or 'plsql' in group_tag.lower():
                    elements_by_type['plsql'].append(element_text)
                else:
                    elements_by_type['other'].append(element_text)
        
        # Add categorized elements to text
        if elements_by_type['scripts']:
            text_content.append("SCRIPTS:")
            text_content.append("-" * 20)
            for script in sorted(elements_by_type['scripts']):
                text_content.append(f"  📜 {script}")
            text_content.append("")
        
        if elements_by_type['ctl_files']:
            text_content.append("CTL FILES:")
            text_content.append("-" * 20)
            for ctl in sorted(elements_by_type['ctl_files']):
                text_content.append(f"  📄 {ctl}")
            text_content.append("")
        
        if elements_by_type['plsql']:
            text_content.append("PL/SQL PROCEDURES:")
            text_content.append("-" * 20)
            for plsql in sorted(elements_by_type['plsql']):
                text_content.append(f"  ⚡ {plsql}")
            text_content.append("")
        
        if elements_by_type['other']:
            text_content.append("OTHER ELEMENTS:")
            text_content.append("-" * 20)
            for other in sorted(elements_by_type['other']):
                text_content.append(f"  🔹 {other}")
            text_content.append("")
        
        # Add connection information
        if self.element_connections:
            text_content.append("CONNECTIONS:")
            text_content.append("-" * 20)
            
            connections_by_type = {}
            for arrow_id, conn_info in self.element_connections.items():
                conn_type = conn_info.get('type', 'unknown')
                if conn_type not in connections_by_type:
                    connections_by_type[conn_type] = []
                
                source_tag = conn_info.get('source', 'unknown')
                target_tag = conn_info.get('target', 'unknown')
                
                # Get readable names from canvas objects
                source_name = self._get_element_name(source_tag)
                target_name = self._get_element_name(target_tag)
                
                connections_by_type[conn_type].append(f"{source_name} → {target_name}")
            
            for conn_type, connections in connections_by_type.items():
                if connections:
                    text_content.append(f"  {conn_type.upper()} connections:")
                    for conn in sorted(connections):
                        text_content.append(f"    {conn}")
                    text_content.append("")
        
        # Add zoom and view information
        text_content.append("VIEW INFORMATION:")
        text_content.append("-" * 20)
        text_content.append(f"Current zoom: {int(self.zoom_factor * 100)}%")
        if bbox := self.canvas.bbox("all"):
            text_content.append(f"Canvas bounds: {bbox[0]},{bbox[1]} to {bbox[2]},{bbox[3]}")
        text_content.append("")
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_content))
    
    def _get_element_name(self, group_tag):
        """Get readable name for an element from its group tag"""
        if group_tag in self.canvas_objects:
            element = self.canvas_objects[group_tag]
            if 'text' in element:
                text_items = self.canvas.find_withtag(group_tag)
                for item in text_items:
                    if self.canvas.type(item) == "text":
                        return self.canvas.itemcget(item, "text")
        return group_tag
        
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
            
        # Clear canvas and reset zoom
        self.canvas.delete("all")
        self.canvas_objects.clear()
        self.element_connections.clear()
        self.zoom_factor = 1.0
        if hasattr(self, 'zoom_label'):
            self.zoom_label.config(text="Zoom: 100%")
        
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
            
    def _delayed_plsql_search(self, event=None):
        """Handle delayed PL/SQL search for dynamic filtering"""
        # Cancel previous timer
        if self._plsql_search_timer:
            self.root.after_cancel(self._plsql_search_timer)
        
        # Set new timer for 300ms delay
        self._plsql_search_timer = self.root.after(300, self.on_global_plsql_search)
    
    def on_global_plsql_search(self, event=None):
        """Handle enhanced global PL/SQL procedure search with function-name-only capability"""
        search_term = self.global_plsql_search_var.get().strip()
        
        # Clear existing results
        for item in self.global_plsql_results_tree.get_children():
            self.global_plsql_results_tree.delete(item)
            
        if not search_term:
            self.global_plsql_status_label.config(text="Use PL/SQL search box above to find procedures across all scripts")
            return
        
        # Allow single character searches for more dynamic experience
        if len(search_term) < 1:
            return
            
        try:
            # Enhanced search with function-name-only capability
            results = self.analyzer.search_plsql_procedure_enhanced(search_term)
            
            if not results:
                self.global_plsql_status_label.config(text=f"No PL/SQL procedures found matching '{search_term}' across all scripts")
                return
                
            # Display enhanced results
            for result in results:
                status = "Commented" if result['is_commented'] else "Active"
                schema = result['schema_name'] or ""
                package = result['package_name'] or ""
                full_procedure = result['full_procedure']
                match_quality = result.get('match_quality', 'unknown')
                
                # Enhanced format match quality for display including function-name matches
                quality_display = {
                    'exact_procedure': '🎯 Exact Procedure',
                    'exact_function_name': '🎯 Exact Function',
                    'partial_procedure': '📝 Partial Procedure',
                    'partial_function_name': '📝 Partial Function',
                    'package_match': '📦 Package',
                    'schema_match': '🏢 Schema',
                    'context_match': '📄 Context',
                    'unknown': '❓ Unknown'
                }.get(match_quality, match_quality)
                
                self.global_plsql_results_tree.insert('', 'end', 
                                             text=result['source_script'],
                                             values=(full_procedure, result['procedure_name'], schema, package, 
                                                   result['line_number'], status, quality_display))
            
            # Group results by script for summary
            scripts = set(result['source_script'] for result in results)
            procedures = set(result['full_procedure'] for result in results)
            
            self.global_plsql_status_label.config(text=f"Found {len(results)} calls to {len(procedures)} procedures across {len(scripts)} scripts")
            
        except Exception as e:
            self.global_plsql_status_label.config(text=f"Search error: {e}")
    
    def clear_global_plsql_search(self):
        """Clear global PL/SQL search results"""
        self.global_plsql_search_var.set("")
        
        # Clear results
        for item in self.global_plsql_results_tree.get_children():
            self.global_plsql_results_tree.delete(item)
            
        self.global_plsql_status_label.config(text="Use PL/SQL search box above to find procedures across all scripts")
    
    def on_canvas_click(self, event):
        """Handle canvas click for dragging with improved hit detection"""
        # Convert screen coordinates to canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Find all items under the cursor (not just the closest)
        items = self.canvas.find_overlapping(canvas_x - 5, canvas_y - 5, canvas_x + 5, canvas_y + 5)
        
        # Find the topmost draggable item
        draggable_item = None
        for item in reversed(items):  # Check topmost items first
            tags = self.canvas.gettags(item)
            if 'draggable' in tags:
                draggable_item = item
                break
        
        if draggable_item:
            self.dragging = draggable_item
            self.drag_start_x = canvas_x
            self.drag_start_y = canvas_y
            
            # Change cursor to indicate dragging
            self.canvas.config(cursor="hand2")
        else:
            # Reset cursor if clicking empty space
            self.canvas.config(cursor="")
    
    def on_canvas_drag(self, event):
        """Handle canvas dragging with arrow updates"""
        if self.dragging:
            # Convert screen coordinates to canvas coordinates
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            
            # Calculate movement
            dx = canvas_x - self.drag_start_x
            dy = canvas_y - self.drag_start_y
            
            # Move the item
            self.canvas.move(self.dragging, dx, dy)
            
            # Find the group tag for this item
            tags = self.canvas.gettags(self.dragging)
            group_tag = None
            for tag in tags:
                if tag.startswith('group_'):
                    group_tag = tag
                    break
            
            if group_tag:
                # Move all items in the same group
                for item in self.canvas.find_withtag(group_tag):
                    if item != self.dragging:
                        self.canvas.move(item, dx, dy)
                
                # Update element position in our tracking
                if group_tag in self.canvas_objects:
                    element = self.canvas_objects[group_tag]
                    element['center_x'] += dx
                    element['center_y'] += dy
                    
                    # Update all connected arrows
                    self.update_connected_arrows(group_tag)
            
            # Update start position for next drag
            self.drag_start_x = canvas_x
            self.drag_start_y = canvas_y
            
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def update_connected_arrows(self, group_tag):
        """Update arrows connected to the moved element"""
        if group_tag not in self.canvas_objects:
            return
            
        element = self.canvas_objects[group_tag]
        
        # Update outgoing arrows
        for arrow in element['arrows_out']:
            if arrow in self.element_connections:
                conn = self.element_connections[arrow]
                source_elem = self.canvas_objects[conn['source']]
                target_elem = self.canvas_objects[conn['target']]
                
                # Calculate new arrow positions using actual box dimensions
                if conn['type'] == 'chain':
                    # For chain arrows (horizontal)
                    x1 = source_elem['center_x'] + source_elem['box_width']//2
                    y1 = source_elem['center_y']
                    x2 = target_elem['center_x'] - target_elem['box_width']//2
                    y2 = target_elem['center_y']
                elif conn['type'] == 'additional_forward':
                    # For additional forward arrows (vertical down)
                    x1 = source_elem['center_x']
                    y1 = source_elem['center_y'] + source_elem['box_height']//2
                    x2 = target_elem['center_x']
                    y2 = target_elem['center_y'] - target_elem['box_height']//2
                elif conn['type'] == 'additional_backward':
                    # For additional backward arrows (vertical up)
                    x1 = source_elem['center_x']
                    y1 = source_elem['center_y'] + source_elem['box_height']//2
                    x2 = target_elem['center_x']
                    y2 = target_elem['center_y'] - target_elem['box_height']//2
                else:
                    # For star diagram arrows using actual box dimensions
                    if conn['type'] == 'forward':
                        x1 = source_elem['center_x'] + source_elem['box_width']//2
                        y1 = source_elem['center_y']
                        x2 = target_elem['center_x'] - target_elem['box_width']//2
                        y2 = target_elem['center_y']
                    else:  # backward
                        x1 = source_elem['center_x'] + source_elem['box_width']//2
                        y1 = source_elem['center_y']
                        x2 = target_elem['center_x'] - target_elem['box_width']//2
                        y2 = target_elem['center_y']
                
                # Update arrow coordinates
                self.canvas.coords(arrow, x1, y1, x2, y2)
        
        # Update incoming arrows
        for arrow in element['arrows_in']:
            if arrow in self.element_connections:
                conn = self.element_connections[arrow]
                source_elem = self.canvas_objects[conn['source']]
                target_elem = self.canvas_objects[conn['target']]
                
                # Calculate new arrow positions using actual box dimensions
                if conn['type'] == 'chain':
                    # For chain arrows (horizontal)
                    x1 = source_elem['center_x'] + source_elem['box_width']//2
                    y1 = source_elem['center_y']
                    x2 = target_elem['center_x'] - target_elem['box_width']//2
                    y2 = target_elem['center_y']
                elif conn['type'] == 'additional_forward':
                    # For additional forward arrows (vertical down)
                    x1 = source_elem['center_x']
                    y1 = source_elem['center_y'] + source_elem['box_height']//2
                    x2 = target_elem['center_x']
                    y2 = target_elem['center_y'] - target_elem['box_height']//2
                elif conn['type'] == 'additional_backward':
                    # For additional backward arrows (vertical up)
                    x1 = source_elem['center_x']
                    y1 = source_elem['center_y'] + source_elem['box_height']//2
                    x2 = target_elem['center_x']
                    y2 = target_elem['center_y'] - target_elem['box_height']//2
                else:
                    # For star diagram arrows using actual box dimensions
                    if conn['type'] == 'forward':
                        x1 = source_elem['center_x'] + source_elem['box_width']//2
                        y1 = source_elem['center_y']
                        x2 = target_elem['center_x'] - target_elem['box_width']//2
                        y2 = target_elem['center_y']
                    else:  # backward
                        x1 = source_elem['center_x'] + source_elem['box_width']//2
                        y1 = source_elem['center_y']
                        x2 = target_elem['center_x'] - target_elem['box_width']//2
                        y2 = target_elem['center_y']
                
                # Update arrow coordinates
                self.canvas.coords(arrow, x1, y1, x2, y2)
    
    def on_canvas_release(self, event):
        """Handle canvas release after dragging"""
        if self.dragging:
            self.dragging = None
            self.canvas.config(cursor="")  # Reset cursor

    def show_about(self):
        """Show about dialog"""
        about_text = """KSH Script Dependency Analyzer
        
Version: 1.2
Author: Assistant
        
This application analyzes KSH/SH scripts to identify:
- Script-to-script dependencies
- CTL file references
- PL/SQL procedure calls

Features:
- Bidirectional dependency mapping
- Visual dependency graphs with improved dragging
- Mouse wheel zoom and cursor-centered zooming
- Image export (PostScript and text formats)
- PL/SQL procedure search
- Export functionality
- Search and filter capabilities

Controls:
- Mouse wheel: Zoom in/out at cursor position
- Drag: Move visualization elements
- Ctrl+Plus/Minus: Zoom in/out
- Ctrl+0: Reset zoom
- Save Image: Export visualization to PostScript or text"""
        
        messagebox.showinfo("About", about_text)
    
    def load_saved_paths(self):
        """Load saved directory paths on startup"""
        try:
            ksh_dir, ctl_dir = self.analyzer.load_directory_paths()
            if ksh_dir:
                self.ksh_dir.set(ksh_dir)
            if ctl_dir:
                self.ctl_dir.set(ctl_dir)
        except Exception as e:
            # Silently ignore errors on startup
            pass
    
    def show_script_context_menu(self, event):
        """Show context menu for script tree items"""
        # Get the item under the cursor
        item = self.script_tree.identify_row(event.y)
        if not item:
            return
            
        # Select the item
        self.script_tree.selection_set(item)
        
        # Get item details
        script_name = self.script_tree.item(item, 'text')
        item_values = self.script_tree.item(item, 'values')
        
        # Skip folder items
        if script_name.startswith('📁') or not item_values:
            return
            
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label=f"📂 Open {script_name}", command=self.open_selected_script)
        context_menu.add_command(label=f"🖥️ Open in External Editor", command=lambda: self.open_in_external_editor(script_name))
        context_menu.add_separator()
        context_menu.add_command(label="📋 Copy Path", command=lambda: self.copy_script_path(script_name))
        context_menu.add_command(label="📊 Show Dependencies", command=lambda: self.show_script_dependencies(script_name))
        
        # Show menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def open_selected_script(self, event=None):
        """Open the selected script in default editor or text viewer"""
        selection = self.script_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a script to open")
            return
            
        item = selection[0]
        script_name = self.script_tree.item(item, 'text')
        item_values = self.script_tree.item(item, 'values')
        
        # Skip folder items
        if script_name.startswith('📁') or not item_values:
            messagebox.showwarning("Invalid Selection", "Please select a script file, not a folder")
            return
            
        # Get script type
        script_type = item_values[0] if item_values else 'unknown'
        
        # Find the full path of the script
        script_path = self.get_script_full_path(script_name, script_type)
        
        if not script_path:
            messagebox.showerror("File Not Found", f"Could not find path for {script_name}")
            return
            
        if not os.path.exists(script_path):
            messagebox.showerror("File Not Found", f"File does not exist: {script_path}")
            return
            
        # Open file in built-in viewer
        self.show_file_viewer(script_name, script_path)
    
    def get_script_full_path(self, script_name, script_type):
        """Get the full path for a script"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.analyzer.db_path)
            cursor = conn.cursor()
            
            if script_type == 'ksh' or script_type == 'sh':
                cursor.execute('SELECT filepath FROM scripts WHERE filename = ?', (script_name,))
            elif script_type == 'ctl':
                cursor.execute('SELECT filepath FROM ctl_files WHERE filename = ?', (script_name,))
            else:
                conn.close()
                return None
                
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error retrieving file path: {e}")
            return None
    
    def show_file_viewer(self, filename, filepath):
        """Show file content in a built-in viewer window with line numbering"""
        try:
            # Create new window
            viewer_window = tk.Toplevel(self.root)
            viewer_window.title(f"File Viewer - {filename}")
            viewer_window.geometry("1000x700")
            
            # Create main frame for editor layout
            editor_frame = ttk.Frame(viewer_window)
            editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create frame for text area and line numbers
            text_frame = ttk.Frame(editor_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create line number text widget
            line_numbers = tk.Text(text_frame, width=6, padx=3, takefocus=0,
                                 border=0, state='disabled', wrap='none',
                                 font=('Courier', 10), bg='#f0f0f0', fg='#666666')
            
            # Create main text widget
            text_widget = tk.Text(text_frame, wrap=tk.NONE, font=('Courier', 10),
                                undo=True, maxundo=20, state='normal')
            
            # Synchronize scrolling between line numbers and text
            def on_text_scroll(*args):
                line_numbers.yview_moveto(args[0])
                v_scrollbar.set(*args)
            
            def on_line_scroll(*args):
                text_widget.yview_moveto(args[0])
                v_scrollbar.set(*args)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
            h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
            
            # Configure scrollbar commands
            v_scrollbar.config(command=lambda *args: [text_widget.yview(*args), line_numbers.yview(*args)])
            text_widget.configure(yscrollcommand=on_text_scroll, xscrollcommand=h_scrollbar.set)
            line_numbers.configure(yscrollcommand=on_line_scroll)
            
            # Grid layout for editor components
            line_numbers.grid(row=0, column=0, sticky=(tk.N, tk.S))
            text_widget.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
            v_scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
            h_scrollbar.grid(row=1, column=1, sticky=(tk.W, tk.E))
            
            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(1, weight=1)
            
            # Read and display file content
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # Insert content into text widget
                text_widget.insert('1.0', content)
                
                # Generate and insert line numbers
                self.update_line_numbers(line_numbers, text_widget)
                
                # Make text widget read-only
                text_widget.config(state=tk.DISABLED)
                
                # Add syntax highlighting for known file types
                self.apply_basic_syntax_highlighting(text_widget, filename)
                
            except Exception as e:
                text_widget.insert('1.0', f"Error reading file: {e}")
                text_widget.config(state=tk.DISABLED)
                self.update_line_numbers(line_numbers, text_widget)
            
            # Add control buttons
            button_frame = ttk.Frame(editor_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Label(button_frame, text=f"Path: {filepath}").pack(side=tk.LEFT)
            ttk.Button(button_frame, text="🔄 Refresh", 
                      command=lambda: self.refresh_file_viewer_with_lines(text_widget, line_numbers, filepath)).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="📋 Copy Path", 
                      command=lambda: self.copy_to_clipboard(filepath)).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="🔍 Find", 
                      command=lambda: self.show_find_dialog(text_widget)).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="📊 Go to Line", 
                      command=lambda: self.show_goto_line_dialog(text_widget, line_numbers)).pack(side=tk.RIGHT, padx=(5, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file viewer: {e}")
    
    def update_line_numbers(self, line_numbers, text_widget):
        """Update line numbers in the line number widget"""
        line_numbers.config(state='normal')
        line_numbers.delete('1.0', tk.END)
        
        # Get total number of lines
        line_count = int(text_widget.index('end-1c').split('.')[0])
        
        # Calculate width needed for line numbers
        max_digits = len(str(line_count))
        line_numbers.config(width=max_digits + 2)
        
        # Generate line numbers
        line_number_string = '\n'.join(str(i).rjust(max_digits) for i in range(1, line_count + 1))
        line_numbers.insert('1.0', line_number_string)
        line_numbers.config(state='disabled')
    
    def refresh_file_viewer_with_lines(self, text_widget, line_numbers, filepath):
        """Refresh file viewer content with line numbers"""
        try:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            text_widget.insert('1.0', content)
            text_widget.config(state=tk.DISABLED)
            
            # Update line numbers
            self.update_line_numbers(line_numbers, text_widget)
            
            # Reapply syntax highlighting
            filename = filepath.split('/')[-1]  # Get filename from path
            self.apply_basic_syntax_highlighting(text_widget, filename)
            
        except Exception as e:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', f"Error refreshing file: {e}")
            text_widget.config(state=tk.DISABLED)
            self.update_line_numbers(line_numbers, text_widget)
    
    def show_goto_line_dialog(self, text_widget, line_numbers):
        """Show go to line dialog"""
        goto_window = tk.Toplevel(self.root)
        goto_window.title("Go to Line")
        goto_window.geometry("250x100")
        goto_window.transient(self.root)
        
        ttk.Label(goto_window, text="Line number:").pack(pady=5)
        
        line_var = tk.StringVar()
        line_entry = ttk.Entry(goto_window, textvariable=line_var, width=20)
        line_entry.pack(pady=5)
        line_entry.focus()
        
        def go_to_line():
            try:
                line_num = int(line_var.get())
                # Get total lines
                total_lines = int(text_widget.index('end-1c').split('.')[0])
                
                if 1 <= line_num <= total_lines:
                    # Move to the specified line
                    text_widget.see(f"{line_num}.0")
                    text_widget.mark_set(tk.INSERT, f"{line_num}.0")
                    
                    # Highlight the line temporarily
                    text_widget.tag_configure("current_line", background="yellow")
                    text_widget.tag_add("current_line", f"{line_num}.0", f"{line_num}.end")
                    
                    # Remove highlight after 2 seconds
                    goto_window.after(2000, lambda: text_widget.tag_remove("current_line", "1.0", tk.END))
                    
                    goto_window.destroy()
                else:
                    messagebox.showerror("Invalid Line", f"Line number must be between 1 and {total_lines}")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid line number")
        
        ttk.Button(goto_window, text="Go", command=go_to_line).pack(pady=5)
        
        # Bind Enter key
        line_entry.bind('<Return>', lambda e: go_to_line())
    
    def apply_basic_syntax_highlighting(self, text_widget, filename):
        """Apply basic syntax highlighting based on file type"""
        # Configure tags for different syntax elements
        text_widget.tag_configure("comment", foreground="green")
        text_widget.tag_configure("string", foreground="blue")
        text_widget.tag_configure("keyword", foreground="purple", font=('Courier', 10, 'bold'))
        text_widget.tag_configure("variable", foreground="orange")
        
        content = text_widget.get('1.0', tk.END)
        lines = content.split('\n')
        
        if filename.endswith(('.ksh', '.sh')):
            # Shell script highlighting
            keywords = ['if', 'then', 'else', 'elif', 'fi', 'for', 'do', 'done', 'while', 'case', 'esac', 'function']
            
            for line_num, line in enumerate(lines, 1):
                line_start = f"{line_num}.0"
                
                # Comments
                comment_pos = line.find('#')
                if comment_pos != -1:
                    start_pos = f"{line_num}.{comment_pos}"
                    end_pos = f"{line_num}.{len(line)}"
                    text_widget.tag_add("comment", start_pos, end_pos)
                
                # Keywords
                for keyword in keywords:
                    start = 0
                    while True:
                        pos = line.find(keyword, start)
                        if pos == -1:
                            break
                        # Check if it's a whole word
                        if (pos == 0 or not line[pos-1].isalnum()) and \
                           (pos + len(keyword) >= len(line) or not line[pos + len(keyword)].isalnum()):
                            start_pos = f"{line_num}.{pos}"
                            end_pos = f"{line_num}.{pos + len(keyword)}"
                            text_widget.tag_add("keyword", start_pos, end_pos)
                        start = pos + 1
                
                # Variables
                import re
                var_matches = re.finditer(r'\$\{?[A-Za-z_][A-Za-z0-9_]*\}?', line)
                for match in var_matches:
                    start_pos = f"{line_num}.{match.start()}"
                    end_pos = f"{line_num}.{match.end()}"
                    text_widget.tag_add("variable", start_pos, end_pos)
        
        elif filename.endswith('.ctl'):
            # CTL file highlighting
            for line_num, line in enumerate(lines, 1):
                # Comments
                if line.strip().startswith('--'):
                    start_pos = f"{line_num}.0"
                    end_pos = f"{line_num}.{len(line)}"
                    text_widget.tag_add("comment", start_pos, end_pos)
    
    def refresh_file_viewer(self, text_widget, filepath):
        """Refresh file viewer content"""
        try:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            text_widget.insert('1.0', content)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', f"Error refreshing file: {e}")
            text_widget.config(state=tk.DISABLED)
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", f"Copied to clipboard:\n{text}")
    
    def show_find_dialog(self, text_widget):
        """Show find dialog for text widget"""
        find_window = tk.Toplevel(self.root)
        find_window.title("Find")
        find_window.geometry("300x100")
        find_window.transient(self.root)
        
        ttk.Label(find_window, text="Find:").pack(pady=5)
        
        find_var = tk.StringVar()
        find_entry = ttk.Entry(find_window, textvariable=find_var, width=30)
        find_entry.pack(pady=5)
        find_entry.focus()
        
        def do_find():
            search_text = find_var.get()
            if search_text:
                # Clear previous highlights
                text_widget.tag_remove("found", "1.0", tk.END)
                
                # Configure found tag
                text_widget.tag_configure("found", background="yellow")
                
                # Search and highlight
                start_pos = "1.0"
                count = 0
                while True:
                    pos = text_widget.search(search_text, start_pos, tk.END)
                    if not pos:
                        break
                    end_pos = f"{pos}+{len(search_text)}c"
                    text_widget.tag_add("found", pos, end_pos)
                    start_pos = end_pos
                    count += 1
                
                if count > 0:
                    # Scroll to first match
                    first_pos = text_widget.search(search_text, "1.0", tk.END)
                    text_widget.see(first_pos)
                    messagebox.showinfo("Find Results", f"Found {count} matches")
                else:
                    messagebox.showinfo("Find Results", "No matches found")
        
        ttk.Button(find_window, text="Find", command=do_find).pack(pady=5)
        
        # Bind Enter key
        find_entry.bind('<Return>', lambda e: do_find())
    
    def copy_script_path(self, script_name):
        """Copy script full path to clipboard"""
        item_values = None
        for item in self.script_tree.get_children():
            for child in self.script_tree.get_children(item):
                if self.script_tree.item(child, 'text') == script_name:
                    item_values = self.script_tree.item(child, 'values')
                    break
        
        if not item_values:
            messagebox.showerror("Error", "Could not find script details")
            return
            
        script_type = item_values[0]
        script_path = self.get_script_full_path(script_name, script_type)
        
        if script_path:
            self.copy_to_clipboard(script_path)
        else:
            messagebox.showerror("Error", "Could not find script path")
    
    def show_script_dependencies(self, script_name):
        """Show script dependencies (same as clicking on the script)"""
        # Find and select the script in the tree
        for item in self.script_tree.get_children():
            for child in self.script_tree.get_children(item):
                if self.script_tree.item(child, 'text') == script_name:
                    self.script_tree.selection_set(child)
                    self.current_script.set(script_name)
                    self.selected_label.config(text=f"Selected: {script_name}")
                    self.update_dependency_views(script_name)
                    self.update_visualization(script_name)
                    break
    
    def open_in_external_editor(self, script_name):
        """Open script in external editor"""
        # Get script details
        item_values = None
        for item in self.script_tree.get_children():
            for child in self.script_tree.get_children(item):
                if self.script_tree.item(child, 'text') == script_name:
                    item_values = self.script_tree.item(child, 'values')
                    break
        
        if not item_values:
            messagebox.showerror("Error", "Could not find script details")
            return
            
        script_type = item_values[0]
        script_path = self.get_script_full_path(script_name, script_type)
        
        if not script_path:
            messagebox.showerror("File Not Found", f"Could not find path for {script_name}")
            return
            
        if not os.path.exists(script_path):
            messagebox.showerror("File Not Found", f"File does not exist: {script_path}")
            return
        
        # Try to open with system default editor
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                # Windows
                os.startfile(script_path)
            elif system == "Darwin":
                # macOS
                subprocess.run(["open", script_path])
            else:
                # Linux and others
                # Try common editors in order
                editors = ["code", "gedit", "nano", "vim", "emacs", "xdg-open"]
                opened = False
                
                for editor in editors:
                    try:
                        subprocess.run([editor, script_path], check=True)
                        opened = True
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                
                if not opened:
                    # Fallback: try xdg-open
                    try:
                        subprocess.run(["xdg-open", script_path])
                    except:
                        messagebox.showerror("Error", 
                                           f"Could not open file in external editor.\n"
                                           f"Please install a text editor or open manually:\n{script_path}")
                        return
            
            messagebox.showinfo("Opened", f"Opened {script_name} in external editor")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open in external editor: {e}")
    
    def open_current_in_external_editor(self):
        """Open currently selected script in external editor"""
        if not self.current_script.get():
            messagebox.showwarning("No Selection", "Please select a script first")
            return
            
        self.open_in_external_editor(self.current_script.get())


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = KSHAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()