import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import sqlparse
import re
from collections import defaultdict

class SQLExtractorInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Table Extractor")
        self.root.geometry("1000x700")
        self.info_text = (
            "Made By Talha Müderrisoğlu for Aras Kargo. 08.2025"
        )
        self.last_results = None  # (read_only, write_only, read_and_write, dependencies)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        # Smaller info button style
        style.configure('Info.TButton', padding=(2, 2), font=("Arial", 9))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="SQL Table Extractor", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))

        # Info 
        info_btn = ttk.Button(main_frame, text="ℹ️", command=self.show_info, style='Info.TButton', width=2)
        info_btn.grid(row=0, column=1, sticky=tk.E, pady=(0, 20))
        
        # Input SQL Label
        input_label = ttk.Label(main_frame, text="Input SQL Query:", font=("Arial", 12, "bold"))
        input_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # Input SQL Text Area
        self.sql_input = scrolledtext.ScrolledText(main_frame, height=10, width=80, font=("Consolas", 10))
        self.sql_input.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # Extract Button
        extract_btn = ttk.Button(button_frame, text="Extract Tables", command=self.extract_tables)
        extract_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear Button
        clear_btn = ttk.Button(button_frame, text="Clear All", command=self.clear_all)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Export to XLSX Button (enabled after extraction)
        self.export_btn = ttk.Button(button_frame, text="Export to XLSX", command=self.export_to_xlsx, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        
        
        # Output Label
        output_label = ttk.Label(main_frame, text="Extraction Results:", font=("Arial", 12, "bold"))
        output_label.grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        
        # Output Text Area
        self.output_text = scrolledtext.ScrolledText(main_frame, height=15, width=80, font=("Consolas", 10), state=tk.DISABLED)
        self.output_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def extract_tables(self):
        """Extract tables from the input SQL"""
        sql_query = self.sql_input.get("1.0", tk.END).strip()
        
        if not sql_query:
            messagebox.showwarning("Warning", "Please enter SQL query first!")
            return
            
        try:
            # Extract raw results
            read_only, write_only, read_and_write, dependencies = self.extract_tables_from_sql(sql_query)

            # Normalize names (remove [DBO]., brackets, etc.)
            read_only_n = self._normalize_table_set(read_only)
            write_only_n = self._normalize_table_set(write_only)
            read_and_write_n = self._normalize_table_set(read_and_write)
            dependencies_n = self._normalize_dependencies(dependencies)

            # Persist normalized results for export
            self.last_results = (read_only_n, write_only_n, read_and_write_n, dependencies_n)
            
            # Format output
            output = ""

            # Show stored procedure name when available
            sp_name = self._extract_stored_procedure_name(sql_query)
            if sp_name:
                output += f"SP: {sp_name}\n\n"
            
            output += "📖 READ-ONLY TABLES:\n"
            if read_only_n:
                for table in sorted(read_only_n):
                    output += f"  • {table}\n"
            else:
                output += "  (None)\n"
            
            output += "\n✏️  WRITE-ONLY TABLES:\n"
            if write_only_n:
                for table in sorted(write_only_n):
                    output += f"  • {table}\n"
            else:
                output += "  (None)\n"
            
            output += "\n🔄 READ & WRITE TABLES:\n"
            if read_and_write_n:
                for table in sorted(read_and_write_n):
                    output += f"  • {table}\n"
            else:
                output += "  (None)\n"
            
            output += "\n📊 TABLE DEPENDENCIES (Source → Target):\n"
            if dependencies_n:
                for target, sources in sorted(dependencies_n.items()):
                    if sources:
                        for source in sorted(sources):
                            output += f"  {source} → {target}\n"
                    else:
                        output += f"  — → {target}\n"
            else:
                output += "  (None)\n"
            
            # Clear previous output and insert new results
            self.output_text.configure(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", output)
            self.output_text.configure(state=tk.DISABLED)
            # Enable export button now that we have results
            self.export_btn.configure(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing SQL: {str(e)}")
    
    def clear_all(self):
        """Clear both input and output areas"""
        self.sql_input.delete("1.0", tk.END)
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state=tk.DISABLED)
    
   
    
    def extract_tables_from_sql(self, sql):
        """Extract tables from SQL query - copied from original file"""
        # Pre-split batches on GO 
        batches = re.split(r'(?im)^\s*GO\s*$', sql)

        source_tables_all = set()
        target_tables_all = set()
        table_dependencies = defaultdict(set)

        for raw_batch in batches:
            if not raw_batch or not raw_batch.strip():
                continue
            sql_batch = sqlparse.format(raw_batch, keyword_case='upper', strip_comments=True)
            statements = sqlparse.parse(sql_batch)

            for statement in statements:
                sql_str = statement.value.upper()

            # Detect target tables (support multiple per statement)
            sql_clean = ' '.join(sql_str.split())
            targets_this_stmt = set()

            # Build alias map from FROM/JOIN clauses to resolve UPDATE aliases
            alias_map = self.extract_alias_map(sql_str)
            # (SELECT ... FROM X) alias
            try:
                derived_alias_map = self.extract_derived_alias_map(sql_str)
                alias_map.update(derived_alias_map)
            except Exception:
                pass

            # INSERT INTO <table>
            for t in re.findall(r'\bINSERT\s+INTO\s+([A-Z0-9_.\[\]#]+)', sql_clean):
                targets_this_stmt.add(t)

            # UPDATE <alias_or_table>
            update_targets_raw = re.findall(r'\bUPDATE\s+([A-Z0-9_.\[\]#]+)', sql_clean)
            update_targets_resolved = []
            for t in update_targets_raw:
                resolved = alias_map.get(t, t)
                update_targets_resolved.append(resolved)
                targets_this_stmt.add(resolved)

            # DELETE FROM <table>
            for t in re.findall(r'\bDELETE\s+FROM\s+([A-Z0-9_.\[\]#]+)', sql_clean):
                targets_this_stmt.add(t)

            # MERGE [INTO] <table>
            for t in re.findall(r'\bMERGE\s+(?:INTO\s+)?([A-Z0-9_.\[\]#]+)', sql_clean):
                targets_this_stmt.add(t)

            # Standalone INTO (e.g., SELECT ... INTO <table>)
            for t in re.findall(r'\bINTO\s+([A-Z0-9_.\[\]#]+)', sql_clean):
                targets_this_stmt.add(t)

            # DROP TABLE [IF EXISTS] <table>[, <table2> ...]
            # Restrict capture to end of statement segment and validate table-like tokens
            for m in re.finditer(r'\bDROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?([^;\n]+)', sql_str, re.IGNORECASE):
                tables_blob = m.group(1)
                for part in re.split(r'\s*,\s*', tables_blob.strip()):
                    table_match = re.match(r'^([A-Z0-9_.\[\]#]+)$', part.strip(), re.IGNORECASE)
                    if table_match:
                        targets_this_stmt.add(table_match.group(1).upper())

            # Collect all targets detected in this statement
            target_tables_all.update(targets_this_stmt)

            # Source tables: FROM, JOIN, subqueries
            from_tables = self.extract_tables_from_clause(sql_str, "FROM")
            join_tables = self.extract_tables_from_clause(sql_str, "JOIN")
            using_tables = self.extract_tables_from_clause(sql_str, "USING")
            subquery_tables = self.extract_tables_from_subqueries(sql_str)
            # Connection-based query sources: OPENQUERY/OPENROWSET/EXEC
            connection_tables = self.extract_tables_from_connection_queries(sql_str)
            
            # Filter out function names and keep only actual table references
            all_sources = set(from_tables + join_tables + subquery_tables + using_tables + connection_tables)
            # Remove common function names 
            function_names = {'OPENQUERY', 'OPENROWSET', 'SELECT', 'CAST', 'AS', 'EXEC'}
            all_sources = all_sources - function_names

            # For UPDATE statements, the target tables are also read from
            for t in update_targets_resolved:
                all_sources.add(t)
            # For MERGE statements, the target tables are also read from
            if any(re.search(r'\bMERGE\b', sql_clean) for _ in [0]):
                for t in re.findall(r'\bMERGE\s+(?:INTO\s+)?([A-Z0-9_.\[\]#]+)', sql_clean):
                    all_sources.add(t)

            # Avoid mapping current targets as their own sources in this statement
            all_sources_for_mapping = all_sources - targets_this_stmt

            # Map sources → target
            for target_table in targets_this_stmt:
                table_dependencies[target_table].update(all_sources_for_mapping)

            source_tables_all.update(all_sources)

        # Classification
        read_only = source_tables_all - target_tables_all
        write_only = target_tables_all - source_tables_all
        read_and_write = source_tables_all & target_tables_all

        return read_only, write_only, read_and_write, table_dependencies

    def extract_derived_alias_map(self, sql_str):
        """Map aliases of derived tables to their base table when detectable.

        Example handled:
        FROM CARGO_FACT c, (SELECT ... FROM SHIPMENT_FACT ...) s
        → {'S': 'SHIPMENT_FACT'}
        """
        alias_map = {}
        pattern = r'\(\s*SELECT[\s\S]*?FROM\s+([A-Z0-9_.\[\]#]+)[\s\S]*?\)\s+(?:AS\s+)?([A-Z0-9_.\[\]]+)'
        for base, alias in re.findall(pattern, sql_str, re.IGNORECASE):
            upper_alias = alias.upper()
            upper_base = base.upper()
            if upper_alias not in {'AS', 'SELECT', 'CAST', 'OPENQUERY', 'OPENROWSET'}:
                alias_map[upper_alias] = upper_base
        return alias_map

    def extract_alias_map(self, sql_str):
        """Extract alias → base table mapping from FROM and JOIN clauses within a statement."""
        alias_map = {}
        for clause in ("FROM", "JOIN"):
            pattern = rf'\b{clause}\s+([A-Z0-9_.\[\]#]+)(?:\s+(?:AS\s+)?([A-Z0-9_.\[\]]+))?'
            for base, alias in re.findall(pattern, sql_str):
                if alias and alias not in {'AS', 'SELECT', 'CAST', 'OPENQUERY', 'OPENROWSET'}:
                    alias_map[alias] = base
        return alias_map

    def extract_tables_from_clause(self, sql_str, clause_type):
        """Extract table names from FROM or JOIN clauses, handling aliases properly"""
        tables = []
        
        # Pattern to match: table_name [alias] or table_name AS alias
        pattern = rf'\b{clause_type}\s+([A-Z0-9_.\[\]#]+)(?:\s+(?:AS\s+)?([A-Z0-9_.\[\]]+))?'
        
        matches = re.findall(pattern, sql_str)
        for match in matches:
            table_name = match[0]
            # Only add the actual table name, not the alias
            if table_name and table_name not in {'AS', 'SELECT', 'CAST', 'OPENQUERY'}:
                tables.append(table_name)
        
        # Also handle comma-separated table lists in FROM clause (but avoid OPENQUERY/OPENROWSET/derived tables)
        if clause_type == "FROM":
            from_span_pattern = r'\bFROM\s+([^;]+?)(?=\s+(?:WHERE|GROUP|ORDER|HAVING|UNION|JOIN|$))'
            comma_matches = re.findall(from_span_pattern, sql_str, re.DOTALL)
            for from_span in comma_matches:
                span_upper = from_span.upper()
                # Skip complex FROM sources like OPENQUERY/OPENROWSET/derived tables to avoid mis-parsing inner commas
                if any(keyword in span_upper for keyword in ("OPENQUERY", "OPENROWSET")):
                    continue
                if "(" in span_upper:  # likely a derived table or function call
                    continue
                # Now safe to split by commas for simple table lists
                table_parts = re.split(r'\s*,\s*', from_span.strip())
                for part in table_parts:
                    table_match = re.match(r'([A-Z0-9_.\[\]#]+)(?:\s+(?:AS\s+)?([A-Z0-9_.\[\]]+))?', part.strip())
                    if table_match:
                        table_name = table_match.group(1)
                        if table_name and table_name not in {'AS', 'SELECT', 'CAST', 'OPENQUERY', 'OPENROWSET'}:
                            tables.append(table_name)
        
        return tables

    def extract_tables_from_subqueries(self, sql_str):
        """Extract table names from subqueries"""
        tables = []
        
        # Find subqueries and extract table names from them
        subquery_pattern = r'\(\s*SELECT.*?FROM\s+([A-Z0-9_.\[\]#]+)(?:\s+(?:AS\s+)?([A-Z0-9_.\[\]]+))?'
        matches = re.findall(subquery_pattern, sql_str, re.DOTALL)
        
        for match in matches:
            table_name = match[0]
            if table_name and table_name not in {'AS', 'SELECT', 'CAST', 'OPENQUERY'}:
                tables.append(table_name)
        
        return tables

    def extract_tables_from_connection_queries(self, sql_str):
        """Extract table names from connection-based constructs like OPENQUERY/OPENROWSET/EXEC AT.

        This scans for:
        - OPENQUERY(SERVER, 'SELECT ... FROM <table> ...')
        - OPENROWSET(..., 'SELECT ... FROM <table> ...')
        - EXEC('SELECT ... FROM <table> ...') AT SERVER
        """
        tables = set()

        # Helper to parse inner SQL and collect tables using existing helpers
        def collect_from_inner_sql(inner_sql: str):
            try:
                inner_formatted = sqlparse.format(inner_sql, keyword_case='upper', strip_comments=True)
            except Exception:
                inner_formatted = inner_sql.upper()
            
            # For inner SQL, avoid comma-splitting heuristics by invoking a minimal matcher
            inner_from = self._extract_simple_from_tables(inner_formatted)
            inner_join = self.extract_tables_from_clause(inner_formatted, "JOIN")
            inner_using = self.extract_tables_from_clause(inner_formatted, "USING")
            inner_sub = self.extract_tables_from_subqueries(inner_formatted)
            for t in inner_from + inner_join + inner_using + inner_sub:
                if t and t not in {"AS", "SELECT", "CAST", "OPENQUERY", "OPENROWSET", "EXEC"}:
                    tables.add(t)

        # OPENQUERY(SERVER, ...
        for m in re.finditer(r"OPENQUERY\s*\(\s*[A-Z0-9_\[\]\.]+\s*,\s*'([\s\S]*?)'\s*\)", sql_str, re.DOTALL):
            inner_sql = m.group(1)
            collect_from_inner_sql(inner_sql)

        # OPENROWSET(..., '...')
        for m in re.finditer(r"OPENROWSET\s*\(\s*[\s\S]*?,\s*[\s\S]*?,\s*'([\s\S]*?)'\s*\)", sql_str, re.DOTALL):
            inner_sql = m.group(1)
            collect_from_inner_sql(inner_sql)

        # EXEC
        #  server
        for m in re.finditer(r"EXEC\s*\(\s*'([\s\S]*?)'\s*\)\s*AT\s+[A-Z0-9_\[\]\.]+", sql_str, re.DOTALL):
            inner_sql = m.group(1)
            collect_from_inner_sql(inner_sql)

        return list(tables)

    def _extract_simple_from_tables(self, sql_str):
        """Extract tables from FROM clause using a conservative approach.

        This avoids splitting by commas and only captures the first table-like token
        after FROM, which suits inner queries inside OPENQUERY where the FROM is simple.
        """
        tables = []
        pattern = r'\bFROM\s+([A-Z0-9_.\[\]#]+)(?:\s+(?:AS\s+)?[A-Z0-9_.\[\]]+)?'
        for m in re.finditer(pattern, sql_str):
            table_name = m.group(1)
            if table_name and table_name not in {'AS', 'SELECT', 'CAST', 'OPENQUERY', 'OPENROWSET'}:
                tables.append(table_name)
        return tables

    def extract_table_after_keyword(self, sql_str, keyword):
        # Clean up the SQL string and make it a single line
        sql_clean = ' '.join(sql_str.split())
        # Handle both regular table names and bracketed table names
        if keyword == "MERGE":
            match = re.search(r'\bMERGE\s+(?:INTO\s+)?([A-Z0-9_.\[\]#]+)', sql_clean)
        elif keyword == "MERGE INTO":
            # Backward compatibility
            match = re.search(r'\bMERGE\s+INTO\s+([A-Z0-9_.\[\]#]+)', sql_clean)
        else:
            match = re.search(fr'\b{keyword}\s+([A-Z0-9_.\[\]#]+)', sql_clean)
        return match.group(1) if match else None

    def _normalize_single_name(self, name):
        if not name:
            return name
        # Remove brackets
        no_brackets = re.sub(r'[\[\]]', '', name)
        parts = [p for p in no_brackets.split('.') if p]
        if not parts:
            return no_brackets
        # Remove leading DBO 
        if parts[0].strip().upper() == 'DBO':
            parts = parts[1:]
        return '.'.join(parts)

    def _normalize_table_set(self, names_set):
        return {self._normalize_single_name(n) for n in names_set}

    def _normalize_dependencies(self, deps_dict):
        normalized = defaultdict(set)
        for target, sources in deps_dict.items():
            norm_target = self._normalize_single_name(target)
            for s in sources:
                norm_source = self._normalize_single_name(s)
                normalized[norm_target].add(norm_source)
        return normalized

    def _extract_stored_procedure_name(self, sql_text):
        if not sql_text:
            return None
        match = re.search(r'\bALTER\s+PROCEDURE\s+([A-Za-z0-9_\.\[\]]+)', sql_text, re.IGNORECASE)
        if not match:
            match = re.search(r'\bALTER\s+PROC\s+([A-Za-z0-9_\.\[\]]+)', sql_text, re.IGNORECASE)
        if not match:
            match = re.search(r'\bCREATE\s+PROCEDURE\s+([A-Za-z0-9_\.\[\]]+)', sql_text, re.IGNORECASE)
        if not match:
            match = re.search(r'\bCREATE\s+PROC\s+([A-Za-z0-9_\.\[\]]+)', sql_text, re.IGNORECASE)
        if not match:
            return None
        sp_raw = match.group(1)
        sp_norm = self._normalize_single_name(sp_raw)
        if '.' in sp_norm:
            return sp_norm.split('.')[-1]
        return sp_norm

    def show_info(self):
        messagebox.showinfo("Information", self.info_text)

    def export_to_xlsx(self):
        if not self.last_results:
            messagebox.showwarning("Warning", "Please extract tables before exporting.")
            return
        read_only, write_only, read_and_write, dependencies = self.last_results

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            title="Save Extraction Results"
        )
        if not file_path:
            return

        try:
            try:
                import importlib
                wb_module = importlib.import_module("openpyxl.workbook.workbook")
                Workbook = getattr(wb_module, "Workbook")
            except Exception:
                messagebox.showerror(
                    "Missing Dependency",
                    "openpyxl is required for exporting to .xlsx.\nInstall it with:\n\npip install openpyxl"
                )
                return

            wb = Workbook()
            ws_ro = wb.active
            ws_ro.title = "Read Only"
            ws_ro.append(["Table"])
            for table in sorted(read_only):
                ws_ro.append([table])

            ws_wo = wb.create_sheet("Write Only")
            ws_wo.append(["Table"])
            for table in sorted(write_only):
                ws_wo.append([table])

            ws_rw = wb.create_sheet("Read & Write")
            ws_rw.append(["Table"])
            for table in sorted(read_and_write):
                ws_rw.append([table])

            ws_dep = wb.create_sheet("Dependencies")
            ws_dep.append(["Target", "Sources"])
            for target, sources in sorted(dependencies.items()):
                sources_list = ", ".join(sorted(sources)) if sources else ""
                ws_dep.append([target, sources_list])

            wb.save(file_path)
            messagebox.showinfo("Success", f"Results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")

def main():
    root = tk.Tk()
    app = SQLExtractorInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()
