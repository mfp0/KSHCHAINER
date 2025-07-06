#!/usr/bin/env python3
"""
KSH Script Dependency Analyzer
Analyzes KSH/SH scripts to identify dependencies including:
- Script-to-script calls
- CTL file references
- PL/SQL procedure calls
"""

import re
import os
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

class KSHAnalyzer:
    """Main analyzer class for KSH script dependencies"""
    
    def __init__(self, db_path: str = "ksh_dependencies.db"):
        self.db_path = db_path
        self.setup_database()
        self.setup_logging()
        
        # Regex patterns for different dependency types
        self.patterns = {
            'script_call': [
                r'(?:^|\s)(\w+\.(?:ksh|sh))(?:\s|$)',  # Direct script calls
                r'(?:^|\s)\.\/(\w+\.(?:ksh|sh))(?:\s|$)',  # Relative path calls
                r'(?:^|\s)ksh\s+(\w+\.(?:ksh|sh))(?:\s|$)',  # ksh command calls
                r'(?:^|\s)\.\s+(\w+\.(?:ksh|sh))(?:\s|$)',  # Source with dot
                r'(?:^|\s)source\s+(\w+\.(?:ksh|sh))(?:\s|$)',  # Source command
            ],
            'ctl_file': [
                r'control\s*=\s*(\w+\.ctl)',  # SQL*Loader control file
                r'(\w+\.ctl)',  # General CTL file reference
            ],
            'plsql_call': [
                r'select\s+(\w+\.\w+(?:\.\w+)*)\s*\([^)]*\)\s+from\s+dual',  # PL/SQL function call from dual
                r'(\w+\.\w+(?:\.\w+)*)\s*\([^)]*\)',  # General PL/SQL procedure/function call (2+ parts)
            ]
        }
        
    def setup_database(self):
        """Initialize SQLite database for storing dependencies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY,
                filename TEXT UNIQUE,
                filepath TEXT,
                file_type TEXT,
                line_count INTEGER,
                last_modified TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY,
                source_script TEXT,
                target_script TEXT,
                dependency_type TEXT,
                line_number INTEGER,
                context TEXT,
                is_commented INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ctl_files (
                id INTEGER PRIMARY KEY,
                filename TEXT UNIQUE,
                filepath TEXT,
                referenced_by TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plsql_calls (
                id INTEGER PRIMARY KEY,
                source_script TEXT,
                procedure_name TEXT,
                schema_name TEXT,
                package_name TEXT,
                line_number INTEGER,
                context TEXT,
                is_commented INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY,
                setting_name TEXT UNIQUE,
                setting_value TEXT,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ksh_analyzer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def is_line_commented(self, line: str) -> bool:
        """Check if a line is commented out"""
        stripped = line.strip()
        return stripped.startswith('#') or stripped.startswith('//')
        
    def extract_dependencies_from_file(self, filepath: str) -> Dict[str, List[Tuple]]:
        """Extract all dependencies from a single KSH/SH file"""
        dependencies = {
            'scripts': [],
            'ctl_files': [],
            'plsql_calls': []
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            filename = os.path.basename(filepath)
            
            for line_num, line in enumerate(lines, 1):
                is_commented = self.is_line_commented(line)
                line_clean = line.strip()
                
                # Skip empty lines
                if not line_clean:
                    continue
                    
                # Extract script calls - use set to prevent duplicates per line
                found_scripts = set()
                for pattern in self.patterns['script_call']:
                    matches = re.findall(pattern, line_clean, re.IGNORECASE)
                    for match in matches:
                        if match not in found_scripts:
                            found_scripts.add(match)
                            dependencies['scripts'].append((
                                filename, match, line_num, line_clean, is_commented
                            ))
                
                # Extract CTL file references - use set to prevent duplicates per line
                found_ctl_files = set()
                for pattern in self.patterns['ctl_file']:
                    matches = re.findall(pattern, line_clean, re.IGNORECASE)
                    for match in matches:
                        if match not in found_ctl_files:
                            found_ctl_files.add(match)
                            dependencies['ctl_files'].append((
                                filename, match, line_num, line_clean, is_commented
                            ))
                
                # Extract PL/SQL calls - use set to prevent duplicates per line
                found_plsql_calls = set()
                for pattern in self.patterns['plsql_call']:
                    matches = re.findall(pattern, line_clean, re.IGNORECASE)
                    for match in matches:
                        if '.' in match and match not in found_plsql_calls:
                            found_plsql_calls.add(match)
                            parts = match.split('.')
                            if len(parts) >= 2:
                                if len(parts) == 2:
                                    # Format: package.procedure
                                    schema = ''
                                    package = parts[0]
                                    procedure = parts[1]
                                else:
                                    # Format: schema.package.procedure (or longer)
                                    schema = parts[0]
                                    package = parts[1]
                                    procedure = '.'.join(parts[2:])
                                dependencies['plsql_calls'].append((
                                    filename, match, schema, package, procedure, 
                                    line_num, line_clean, is_commented
                                ))
                        
        except Exception as e:
            self.logger.error(f"Error processing file {filepath}: {e}")
            
        return dependencies
    
    def scan_directory(self, directory: str, extensions: List[str]) -> List[str]:
        """Scan directory for files with specified extensions"""
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))
        return files
    
    def analyze_ksh_directory(self, ksh_dir: str) -> Dict[str, any]:
        """Analyze all KSH/SH files in directory"""
        self.logger.info(f"Analyzing KSH directory: {ksh_dir}")
        
        # Find all KSH/SH files
        ksh_files = self.scan_directory(ksh_dir, ['.ksh', '.sh'])
        
        results = {
            'total_files': len(ksh_files),
            'dependencies': {},
            'errors': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM scripts')
        cursor.execute('DELETE FROM dependencies')
        cursor.execute('DELETE FROM plsql_calls')
        
        for filepath in ksh_files:
            try:
                # Store script info
                stat = os.stat(filepath)
                cursor.execute('''
                    INSERT OR REPLACE INTO scripts 
                    (filename, filepath, file_type, line_count, last_modified)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    os.path.basename(filepath),
                    filepath,
                    'ksh' if filepath.endswith('.ksh') else 'sh',
                    sum(1 for line in open(filepath, 'r', encoding='utf-8', errors='ignore')),
                    str(stat.st_mtime)
                ))
                
                # Extract dependencies
                deps = self.extract_dependencies_from_file(filepath)
                results['dependencies'][os.path.basename(filepath)] = deps
                
                # Store script dependencies
                for dep in deps['scripts']:
                    cursor.execute('''
                        INSERT INTO dependencies 
                        (source_script, target_script, dependency_type, line_number, context, is_commented)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (dep[0], dep[1], 'script', dep[2], dep[3], dep[4]))
                
                # Store CTL file dependencies
                for dep in deps['ctl_files']:
                    cursor.execute('''
                        INSERT INTO dependencies 
                        (source_script, target_script, dependency_type, line_number, context, is_commented)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (dep[0], dep[1], 'ctl', dep[2], dep[3], dep[4]))
                
                # Store PL/SQL calls
                for dep in deps['plsql_calls']:
                    cursor.execute('''
                        INSERT INTO plsql_calls 
                        (source_script, procedure_name, schema_name, package_name, line_number, context, is_commented)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (dep[0], dep[1], dep[2], dep[3], dep[5], dep[6], dep[7]))
                
            except Exception as e:
                error_msg = f"Error processing {filepath}: {e}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Analysis complete. Processed {len(ksh_files)} files")
        return results
    
    def analyze_ctl_directory(self, ctl_dir: str) -> Dict[str, any]:
        """Analyze all CTL files in directory"""
        self.logger.info(f"Analyzing CTL directory: {ctl_dir}")
        
        # Find all CTL files
        ctl_files = self.scan_directory(ctl_dir, ['.ctl'])
        
        results = {
            'total_files': len(ctl_files),
            'ctl_files': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing CTL data
        cursor.execute('DELETE FROM ctl_files')
        
        for filepath in ctl_files:
            try:
                filename = os.path.basename(filepath)
                results['ctl_files'].append(filename)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO ctl_files 
                    (filename, filepath, referenced_by)
                    VALUES (?, ?, ?)
                ''', (filename, filepath, ''))
                
            except Exception as e:
                error_msg = f"Error processing CTL file {filepath}: {e}"
                self.logger.error(error_msg)
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"CTL analysis complete. Found {len(ctl_files)} files")
        return results
    
    def get_forward_dependencies(self, script_name: str) -> List[Dict]:
        """Get what the script calls (forward dependencies)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT target_script, dependency_type, line_number, context, is_commented
            FROM dependencies
            WHERE source_script = ? AND is_commented = 0
            ORDER BY line_number
        ''', (script_name,))
        
        deps = []
        for row in cursor.fetchall():
            deps.append({
                'target': row[0],
                'type': row[1],
                'line': row[2],
                'context': row[3],
                'commented': bool(row[4])
            })
        
        # Add PL/SQL calls
        cursor.execute('''
            SELECT procedure_name, schema_name, package_name, line_number, context, is_commented
            FROM plsql_calls
            WHERE source_script = ? AND is_commented = 0
            ORDER BY line_number
        ''', (script_name,))
        
        for row in cursor.fetchall():
            deps.append({
                'target': row[0],
                'type': 'plsql',
                'schema': row[1],
                'package': row[2],
                'line': row[3],
                'context': row[4],
                'commented': bool(row[5])
            })
        
        conn.close()
        return deps
    
    def get_backward_dependencies(self, script_name: str) -> List[Dict]:
        """Get what calls the script (backward dependencies)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT source_script, dependency_type, line_number, context, is_commented
            FROM dependencies
            WHERE target_script = ? AND is_commented = 0
            ORDER BY source_script, line_number
        ''', (script_name,))
        
        deps = []
        for row in cursor.fetchall():
            deps.append({
                'source': row[0],
                'type': row[1],
                'line': row[2],
                'context': row[3],
                'commented': bool(row[4])
            })
        
        conn.close()
        return deps
    
    def get_all_scripts(self) -> List[str]:
        """Get list of all analyzed scripts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT filename FROM scripts ORDER BY filename')
        scripts = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return scripts
    
    def get_all_ctl_files(self) -> List[str]:
        """Get list of all CTL files"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT filename FROM ctl_files ORDER BY filename')
        ctl_files = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return ctl_files
    
    def search_plsql_procedure(self, search_term: str) -> List[Dict]:
        """Enhanced search for scripts that call PL/SQL procedures
        
        Args:
            search_term: The procedure name to search for (can be partial, like 'attempt_recovery')
            
        Returns:
            List of dictionaries containing calling scripts and details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced search patterns for better partial matching
        search_pattern = f"%{search_term}%"
        exact_pattern = search_term.lower()
        
        # Multiple search strategies for better results
        cursor.execute('''
            SELECT source_script, procedure_name, schema_name, package_name, 
                   line_number, context, is_commented
            FROM plsql_calls
            WHERE 
                -- Exact procedure name match (highest priority)
                LOWER(procedure_name) = ?
                OR LOWER(procedure_name) LIKE ?
                -- Schema name match
                OR LOWER(schema_name) LIKE ?
                -- Package name match
                OR LOWER(package_name) LIKE ?
                -- Full qualified name match (schema.package.procedure)
                OR LOWER(COALESCE(schema_name, '') || '.' || COALESCE(package_name, '') || '.' || procedure_name) LIKE ?
                -- Context search (for procedures mentioned in comments or strings)
                OR LOWER(context) LIKE ?
            ORDER BY 
                -- Prioritize exact matches first
                CASE WHEN LOWER(procedure_name) = ? THEN 1
                     WHEN LOWER(procedure_name) LIKE ? THEN 2
                     WHEN LOWER(package_name) LIKE ? THEN 3
                     WHEN LOWER(schema_name) LIKE ? THEN 4
                     ELSE 5 END,
                source_script, line_number
        ''', (exact_pattern, search_pattern, search_pattern, search_pattern, 
              search_pattern, search_pattern, exact_pattern, search_pattern, 
              search_pattern, search_pattern))
        
        results = []
        for row in cursor.fetchall():
            # Build proper full procedure name with null handling
            schema = row[2] or ''
            package = row[3] or ''
            procedure = row[1] or ''
            
            # Create full procedure name based on available components
            if schema and package:
                full_procedure = f"{schema}.{package}.{procedure}"
            elif package:
                full_procedure = f"{package}.{procedure}"
            else:
                full_procedure = procedure
            
            results.append({
                'source_script': row[0],
                'procedure_name': procedure,
                'schema_name': schema,
                'package_name': package,
                'full_procedure': full_procedure,
                'line_number': row[4],
                'context': row[5],
                'is_commented': bool(row[6]),
                'match_quality': self._get_match_quality(search_term, procedure, package, schema)
            })
        
        conn.close()
        
        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for result in results:
            key = (result['source_script'], result['line_number'], result['full_procedure'])
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results
    
    def _get_match_quality(self, search_term: str, procedure: str, package: str, schema: str) -> str:
        """Determine the quality of the match for sorting purposes"""
        search_lower = search_term.lower()
        
        if procedure.lower() == search_lower:
            return "exact_procedure"
        elif procedure.lower().find(search_lower) != -1:
            return "partial_procedure"
        elif package and package.lower().find(search_lower) != -1:
            return "package_match"
        elif schema and schema.lower().find(search_lower) != -1:
            return "schema_match"
        else:
            return "context_match"
    
    def get_all_plsql_procedures(self) -> List[Dict]:
        """Get list of all unique PL/SQL procedures found in scripts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT schema_name, package_name, procedure_name,
                   COUNT(*) as call_count
            FROM plsql_calls
            GROUP BY schema_name, package_name, procedure_name
            ORDER BY schema_name, package_name, procedure_name
        ''')
        
        procedures = []
        for row in cursor.fetchall():
            procedures.append({
                'schema': row[0],
                'package': row[1],
                'procedure': row[2],
                'full_name': f"{row[0]}.{row[1]}.{row[2]}",
                'call_count': row[3]
            })
        
        conn.close()
        return procedures
    
    def cleanup_duplicate_plsql_calls(self):
        """Remove duplicate PL/SQL calls from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Remove duplicates by keeping only the first occurrence of each unique combination
        cursor.execute('''
            DELETE FROM plsql_calls 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM plsql_calls 
                GROUP BY source_script, procedure_name, schema_name, package_name, line_number
            )
        ''')
        
        duplicates_removed = cursor.rowcount
        conn.commit()
        conn.close()
        
        if duplicates_removed > 0:
            self.logger.info(f"Removed {duplicates_removed} duplicate PL/SQL call entries")
        
        return duplicates_removed
    
    def get_plsql_procedure_callers(self, procedure_name: str) -> List[Dict]:
        """Get all scripts that call a specific PL/SQL procedure (exact match)
        
        Args:
            procedure_name: Full procedure name (schema.package.procedure) or partial
            
        Returns:
            List of calling scripts with details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if '.' in procedure_name:
            # Exact match for full procedure name
            cursor.execute('''
                SELECT source_script, procedure_name, schema_name, package_name, 
                       line_number, context, is_commented
                FROM plsql_calls
                WHERE LOWER(schema_name || '.' || package_name || '.' || procedure_name) = LOWER(?)
                ORDER BY source_script, line_number
            ''', (procedure_name,))
        else:
            # Match just the procedure name
            cursor.execute('''
                SELECT source_script, procedure_name, schema_name, package_name, 
                       line_number, context, is_commented
                FROM plsql_calls
                WHERE LOWER(procedure_name) = LOWER(?)
                ORDER BY source_script, line_number
            ''', (procedure_name,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'source_script': row[0],
                'procedure_name': row[1],
                'schema_name': row[2],
                'package_name': row[3],
                'full_procedure': f"{row[2]}.{row[3]}.{row[1]}",
                'line_number': row[4],
                'context': row[5],
                'is_commented': bool(row[6])
            })
        
        conn.close()
        return results
    
    def save_directory_paths(self, ksh_dir: str, ctl_dir: str):
        """Save directory paths to database for persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        
        # Save KSH directory
        cursor.execute('''
            INSERT OR REPLACE INTO user_settings 
            (setting_name, setting_value, last_updated)
            VALUES (?, ?, ?)
        ''', ('ksh_directory', ksh_dir, timestamp))
        
        # Save CTL directory
        cursor.execute('''
            INSERT OR REPLACE INTO user_settings 
            (setting_name, setting_value, last_updated)
            VALUES (?, ?, ?)
        ''', ('ctl_directory', ctl_dir, timestamp))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Saved directory paths: KSH={ksh_dir}, CTL={ctl_dir}")
    
    def load_directory_paths(self) -> tuple:
        """Load saved directory paths from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT setting_value FROM user_settings 
                WHERE setting_name = ?
            ''', ('ksh_directory',))
            ksh_result = cursor.fetchone()
            ksh_dir = ksh_result[0] if ksh_result else ""
            
            cursor.execute('''
                SELECT setting_value FROM user_settings 
                WHERE setting_name = ?
            ''', ('ctl_directory',))
            ctl_result = cursor.fetchone()
            ctl_dir = ctl_result[0] if ctl_result else ""
            
            conn.close()
            
            self.logger.info(f"Loaded directory paths: KSH={ksh_dir}, CTL={ctl_dir}")
            return ksh_dir, ctl_dir
            
        except Exception as e:
            self.logger.error(f"Error loading directory paths: {e}")
            conn.close()
            return "", ""
    
    def export_dependencies(self, output_file: str, format: str = 'json'):
        """Export dependencies to various formats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all dependencies
        cursor.execute('''
            SELECT source_script, target_script, dependency_type, line_number, context, is_commented
            FROM dependencies
            ORDER BY source_script, line_number
        ''')
        
        dependencies = []
        for row in cursor.fetchall():
            dependencies.append({
                'source': row[0],
                'target': row[1],
                'type': row[2],
                'line': row[3],
                'context': row[4],
                'commented': bool(row[5])
            })
        
        # Get PL/SQL calls
        cursor.execute('''
            SELECT source_script, procedure_name, schema_name, package_name, line_number, context, is_commented
            FROM plsql_calls
            ORDER BY source_script, line_number
        ''')
        
        plsql_calls = []
        for row in cursor.fetchall():
            plsql_calls.append({
                'source': row[0],
                'procedure': row[1],
                'schema': row[2],
                'package': row[3],
                'line': row[4],
                'context': row[5],
                'commented': bool(row[6])
            })
        
        conn.close()
        
        export_data = {
            'dependencies': dependencies,
            'plsql_calls': plsql_calls,
            'export_timestamp': str(os.path.getmtime(self.db_path)) if os.path.exists(self.db_path) else 'N/A'
        }
        
        if format.lower() == 'json':
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Dependencies exported to {output_file}")


if __name__ == "__main__":
    # Test the analyzer
    analyzer = KSHAnalyzer()
    
    # Test with sample data
    ksh_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ksh_scripts"
    ctl_dir = "/mnt/c/Users/mpolo/Desktop/GITHUB/KSHCHAINER/sample_data/ctl_files"
    
    if os.path.exists(ksh_dir):
        ksh_results = analyzer.analyze_ksh_directory(ksh_dir)
        print(f"KSH Analysis Results: {ksh_results['total_files']} files processed")
        
    if os.path.exists(ctl_dir):
        ctl_results = analyzer.analyze_ctl_directory(ctl_dir)
        print(f"CTL Analysis Results: {ctl_results['total_files']} files found")
        
    # Test dependency queries
    scripts = analyzer.get_all_scripts()
    if scripts:
        test_script = scripts[0]
        print(f"\nTesting dependencies for: {test_script}")
        
        forward_deps = analyzer.get_forward_dependencies(test_script)
        print(f"Forward dependencies: {len(forward_deps)}")
        
        backward_deps = analyzer.get_backward_dependencies(test_script)
        print(f"Backward dependencies: {len(backward_deps)}")