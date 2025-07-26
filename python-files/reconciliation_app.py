import sys
import pandas as pd
import numpy as np
import re
from datetime import datetime
from fuzzywuzzy import fuzz
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QPushButton, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QLabel, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt

# Function to clean invoice numbers
def clean_invoice_number(invoice):
    if pd.isna(invoice):
        return invoice
    invoice = str(invoice).upper().strip()
    invoice = re.sub(r'[A-Za-z]', '', invoice)
    invoice = re.sub(r'\d{2}-\d{2}|\d{4}-\d{2}|\d{2}\d{2}|\d{4}\d{2}', '', invoice)
    invoice = re.sub(r'[-_/]', '', invoice)
    return invoice.strip()

# Function for fuzzy matching vendor names
def is_similar_name(name1, name2, threshold=80):
    if pd.isna(name1) or pd.isna(name2):
        return False
    return fuzz.ratio(str(name1).upper(), str(name2).upper()) >= threshold

class ReconciliationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GSTR-2B and SAP Reconciliation")
        self.setGeometry(100, 100, 1200, 600)

        # Initialize variables
        self.gstr2b_file = None
        self.sap_file = None
        self.threshold = 80
        self.tolerance = 2
        self.merged_df = None

        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Create tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Data Upload Tab
        self.upload_tab = QWidget()
        self.upload_layout = QVBoxLayout(self.upload_tab)
        self.gstr2b_button = QPushButton("Select GSTR-2B File")
        self.gstr2b_button.clicked.connect(self.load_gstr2b_file)
        self.sap_button = QPushButton("Select SAP File")
        self.sap_button.clicked.connect(self.load_sap_file)
        self.reconcile_button = QPushButton("Run Reconciliation")
        self.reconcile_button.clicked.connect(self.run_reconciliation)
        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.export_results)
        self.upload_layout.addWidget(self.gstr2b_button)
        self.upload_layout.addWidget(self.sap_button)
        self.upload_layout.addWidget(self.reconcile_button)
        self.upload_layout.addWidget(self.export_button)
        self.upload_layout.addStretch()
        self.tabs.addTab(self.upload_tab, "Data Upload")

        # Results Tab
        self.results_tab = QWidget()
        self.results_layout = QVBoxLayout(self.results_tab)
        self.table = QTableWidget()
        self.results_layout.addWidget(self.table)
        self.summary_label = QLabel("Reconciliation Summary: Not yet run")
        self.results_layout.addWidget(self.summary_label)
        self.tabs.addTab(self.results_tab, "Reconciliation Results")

        # Features Tab
        self.features_tab = QWidget()
        self.features_layout = QVBoxLayout(self.features_tab)
        self.threshold_label = QLabel("Fuzzy Matching Threshold (0-100):")
        self.threshold_input = QLineEdit(str(self.threshold))
        self.tolerance_label = QLabel("Tax Difference Tolerance (Rupees):")
        self.tolerance_input = QLineEdit(str(self.tolerance))
        self.apply_button = QPushButton("Apply Settings")
        self.apply_button.clicked.connect(self.apply_settings)
        self.features_layout.addWidget(self.threshold_label)
        self.features_layout.addWidget(self.threshold_input)
        self.features_layout.addWidget(self.tolerance_label)
        self.features_layout.addWidget(self.tolerance_input)
        self.features_layout.addWidget(self.apply_button)
        self.features_layout.addStretch()
        self.tabs.addTab(self.features_tab, "Features")

    def load_gstr2b_file(self):
        self.gstr2b_file, _ = QFileDialog.getOpenFileName(self, "Select GSTR-2B File", "", "Excel Files (*.xlsx)")
        if self.gstr2b_file:
            self.gstr2b_button.setText(f"GSTR-2B: {self.gstr2b_file.split('/')[-1]}")

    def load_sap_file(self):
        self.sap_file, _ = QFileDialog.getOpenFileName(self, "Select SAP File", "", "Excel Files (*.xlsx)")
        if self.sap_file:
            self.sap_button.setText(f"SAP: {self.sap_file.split('/')[-1]}")

    def apply_settings(self):
        try:
            self.threshold = int(self.threshold_input.text())
            if not 0 <= self.threshold <= 100:
                raise ValueError("Threshold must be between 0 and 100")
            self.tolerance = float(self.tolerance_input.text())
            if self.tolerance < 0:
                raise ValueError("Tolerance must be non-negative")
            QMessageBox.information(self, "Success", "Settings applied successfully")
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def run_reconciliation(self):
        if not self.gstr2b_file or not self.sap_file:
            QMessageBox.critical(self, "Error", "Please select both GSTR-2B and SAP files")
            return

        try:
            # Load data
            gstr2b_df = pd.read_excel(self.gstr2b_file)
            sap_df = pd.read_excel(self.sap_file)

            # Validate Document_Number
            sap_df['Document_Number'] = pd.to_numeric(sap_df['Document_Number'], errors='coerce')
            if sap_df['Document_Number'].isna().any():
                QMessageBox.warning(self, "Warning", "Some Document_Number values are non-numeric and have been set to NaN.")

            # Standardize data
            gstr2b_df['Invoice_Date'] = pd.to_datetime(gstr2b_df['Invoice_Date'], errors='coerce')
            sap_df['Invoice_Date'] = pd.to_datetime(sap_df['Invoice_Date'], errors='coerce')
            gstr2b_df['GSTIN'] = gstr2b_df['GSTIN'].str.upper().str.strip()
            sap_df['Vendor_GSTIN'] = sap_df['Vendor_GSTIN'].str.upper().str.strip()
            gstr2b_df['Vendor_Name'] = gstr2b_df['Vendor_Name'].str.upper().str.strip()
            sap_df['Vendor_Name'] = sap_df['Vendor_Name'].str.upper().str.strip()
            gstr2b_df['Clean_Invoice_No'] = gstr2b_df['Invoice_No'].apply(clean_invoice_number)
            sap_df['Clean_Invoice_No'] = sap_df['Invoice_No'].apply(clean_invoice_number)

            # Initial merge
            self.merged_df = pd.merge(
                gstr2b_df,
                sap_df,
                how='outer',
                left_on=['GSTIN', 'Clean_Invoice_No', 'Invoice_Date'],
                right_on=['Vendor_GSTIN', 'Clean_Invoice_No', 'Invoice_Date'],
                suffixes=('_GSTR2B', '_SAP'),
                indicator=True
            )

            # Fuzzy matching for vendor names
            self.merged_df['Vendor_Name_Similar'] = self.merged_df.apply(
                lambda x: is_similar_name(x['Vendor_Name_GSTR2B'], x['Vendor_Name_SAP'], self.threshold)
                if x['_merge'] == 'both' else True, axis=1
            )

            # Update status
            self.merged_df['Recon_Status'] = np.where(
                (self.merged_df['_merge'] == 'both') & (self.merged_df['Vendor_Name_Similar']),
                'Matched',
                np.where(self.merged_df['_merge'] == 'left_only', 'In GSTR-2B Only',
                         np.where(self.merged_df['_merge'] == 'right_only', 'In SAP Only', 'Vendor Name Mismatch'))
            )

            # Secondary merge
            unmatched_gstr2b = self.merged_df[self.merged_df['Recon_Status'].isin(['In GSTR-2B Only', 'Vendor Name Mismatch'])][[
                'GSTIN', 'Vendor_Name_GSTR2B', 'Clean_Invoice_No', 'Invoice_Date',
                'Taxable_Value_GSTR2B', 'IGST_GSTR2B', 'CGST_GSTR2B', 'SGST_GSTR2B'
            ]].copy()
            unmatched_sap = self.merged_df[self.merged_df['Recon_Status'].isin(['In SAP Only', 'Vendor Name Mismatch'])][[
                'Vendor_GSTIN', 'Vendor_Name_SAP', 'Clean_Invoice_No', 'Invoice_Date',
                'Taxable_Value_SAP', 'IGST_SAP', 'CGST_SAP', 'SGST_SAP', 'Document_Number'
            ]].copy()

            secondary_matches = []
            for idx1, row1 in unmatched_gstr2b.iterrows():
                for idx2, row2 in unmatched_sap.iterrows():
                    if (row1['Clean_Invoice_No'] == row2['Clean_Invoice_No'] and
                            row1['Invoice_Date'] == row2['Invoice_Date'] and
                            is_similar_name(row1['Vendor_Name_GSTR2B'], row2['Vendor_Name_SAP'], self.threshold)):
                        match = {
                            'GSTIN': row1['GSTIN'],
                            'Vendor_GSTIN': row2['Vendor_GSTIN'],
                            'Vendor_Name_GSTR2B': row1['Vendor_Name_GSTR2B'],
                            'Vendor_Name_SAP': row2['Vendor_Name_SAP'],
                            'Clean_Invoice_No': row1['Clean_Invoice_No'],
                            'Invoice_Date': row1['Invoice_Date'],
                            'Taxable_Value_GSTR2B': row1['Taxable_Value_GSTR2B'],
                            'Taxable_Value_SAP': row2['Taxable_Value_SAP'],
                            'IGST_GSTR2B': row1['IGST_GSTR2B'],
                            'IGST_SAP': row2['IGST_SAP'],
                            'CGST_GSTR2B': row1['CGST_GSTR2B'],
                            'CGST_SAP': row2['CGST_SAP'],
                            'SGST_GSTR2B': row1['SGST_GSTR2B'],
                            'SGST_SAP': row2['SGST_SAP'],
                            'Document_Number': row2['Document_Number'],
                            'Recon_Status': 'Matched (No GSTIN or Fuzzy Name)'
                        }
                        secondary_matches.append(match)

            secondary_df = pd.DataFrame(secondary_matches)
            unmatched_gstr2b = unmatched_gstr2b[~unmatched_gstr2b['Clean_Invoice_No'].isin(secondary_df['Clean_Invoice_No'])]
            unmatched_sap = unmatched_sap[~unmatched_sap['Clean_Invoice_No'].isin(secondary_df['Clean_Invoice_No'])]
            self.merged_df = pd.concat([
                self.merged_df[~self.merged_df['Recon_Status'].isin(['In GSTR-2B Only', 'In SAP Only', 'Vendor Name Mismatch'])],
                secondary_df,
                unmatched_gstr2b.assign(Recon_Status='In GSTR-2B Only'),
                unmatched_sap.assign(Recon_Status='In SAP Only')
            ], ignore_index=True)

            # Check tax mismatches
            matched_df = self.merged_df[self.merged_df['Recon_Status'].str.contains('Matched|Vendor Name Mismatch')].copy()
            matched_df['IGST_Diff'] = matched_df['IGST_GSTR2B'] - matched_df['IGST_SAP']
            matched_df['CGST_Diff'] = matched_df['CGST_GSTR2B'] - matched_df['CGST_SAP']
            matched_df['SGST_Diff'] = matched_df['SGST_GSTR2B'] - matched_df['SGST_SAP']
            matched_df['Tax_Mismatch'] = (
                (abs(matched_df['IGST_Diff']) > self.tolerance) |
                (abs(matched_df['CGST_Diff']) > self.tolerance) |
                (abs(matched_df['SGST_Diff']) > self.tolerance)
            )
            matched_df['Need_Informed'] = (
                (matched_df['Recon_Status'].str.contains('Matched')) &
                (matched_df['Tax_Mismatch'])
            )
            matched_df.loc[matched_df['Need_Informed'], 'Recon_Status'] = 'Need Informed to Vendor'
            matched_df['Document_Number'] = matched_df.apply(
                lambda x: x['Document_Number']
                if x['Recon_Status'] in ['Matched', 'Matched (No GSTIN or Fuzzy Name)', 'Need Informed to Vendor', 'Vendor Name Mismatch']
                else np.nan, axis=1
            )
            self.merged_df.update(matched_df)

            # Update table
            self.update_table()

            # Update summary
            summary = self.merged_df.groupby('Recon_Status').size().reset_index(name='Count')
            summary_text = "Reconciliation Summary:\n" + summary.to_string(index=False)
            self.summary_label.setText(summary_text)

            QMessageBox.information(self, "Success", "Reconciliation completed successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Reconciliation failed: {str(e)}")

    def update_table(self):
        columns = [
            'GSTIN', 'Vendor_GSTIN', 'Vendor_Name_GSTR2B', 'Vendor_Name_SAP',
            'Invoice_No_GSTR2B', 'Invoice_No_SAP', 'Clean_Invoice_No', 'Invoice_Date',
            'Taxable_Value_GSTR2B', 'Taxable_Value_SAP', 'IGST_GSTR2B', 'IGST_SAP',
            'CGST_GSTR2B', 'CGST_SAP', 'SGST_GSTR2B', 'SGST_SAP', 'Recon_Status',
            'IGST_Diff', 'CGST_Diff', 'SGST_Diff', 'Document_Number'
        ]
        self.table.setRowCount(len(self.merged_df))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        for i, row in self.merged_df.iterrows():
            for j, col in enumerate(columns):
                value = row[col]
                item = QTableWidgetItem(str(value) if pd.notna(value) else "")
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.table.setItem(i, j, item)

    def export_results(self):
        if self.merged_df is None:
            QMessageBox.critical(self, "Error", "No reconciliation data to export")
            return

        # Update DataFrame with table edits
        for i in range(self.table.rowCount()):
            for j, col in enumerate([
                'GSTIN', 'Vendor_GSTIN', 'Vendor_Name_GSTR2B', 'Vendor_Name_SAP',
                'Invoice_No_GSTR2B', 'Invoice_No_SAP', 'Clean_Invoice_No', 'Invoice_Date',
                'Taxable_Value_GSTR2B', 'Taxable_Value_SAP', 'IGST_GSTR2B', 'IGST_SAP',
                'CGST_GSTR2B', 'CGST_SAP', 'SGST_GSTR2B', 'SGST_SAP', 'Recon_Status',
                'IGST_Diff', 'CGST_Diff', 'SGST_Diff', 'Document_Number'
            ]):
                item = self.table.item(i, j)
                if item:
                    try:
                        if col in ['Taxable_Value_GSTR2B', 'Taxable_Value_SAP', 'IGST_GSTR2B', 'IGST_SAP',
                                   'CGST_GSTR2B', 'CGST_SAP', 'SGST_GSTR2B', 'SGST_SAP', 'IGST_Diff', 'CGST_Diff', 'SGST_Diff']:
                            self.merged_df.at[i, col] = float(item.text()) if item.text() else np.nan
                        elif col == 'Invoice_Date':
                            self.merged_df.at[i, col] = pd.to_datetime(item.text(), errors='coerce')
                        else:
                            self.merged_df.at[i, col] = item.text() if item.text() else np.nan
                    except:
                        self.merged_df.at[i, col] = np.nan

        output_file, _ = QFileDialog.getSaveFileName(self, "Save Reconciliation Output", "", "Excel Files (*.xlsx)")
        if output_file:
            self.merged_df[[
                'GSTIN', 'Vendor_GSTIN', 'Vendor_Name_GSTR2B', 'Vendor_Name_SAP',
                'Invoice_No_GSTR2B', 'Invoice_No_SAP', 'Clean_Invoice_No', 'Invoice_Date',
                'Taxable_Value_GSTR2B', 'Taxable_Value_SAP', 'IGST_GSTR2B', 'IGST_SAP',
                'CGST_GSTR2B', 'CGST_SAP', 'SGST_GSTR2B', 'SGST_SAP', 'Recon_Status',
                'IGST_Diff', 'CGST_Diff', 'SGST_Diff', 'Document_Number'
            ]].to_excel(output_file, index=False)
            QMessageBox.information(self, "Success", f"Results saved to {output_file}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ReconciliationApp()
    window.show()
    sys.exit(app.exec_())