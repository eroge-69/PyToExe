"""
Main entry point for the data validation application
Zadanie rekrutacyjne - Data Validation and Error Reporting

This application:
1. Loads data from multiple sources (MPK, Grafana, Signio, Installations)
2. Validates data integrity and identifies errors
3. Generates comprehensive device listing with error information in CSV format
4. Logs all operations and errors
5. Skips columns containing 'tag' in their names
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Import from modules package
try:
    from modules.dataloader import DataLoader
except ImportError as e:
    # Fallback - add modules to path
    sys.path.insert(0, str(Path(__file__).parent / "modules"))
    try:
        from dataloader import DataLoader
    except ImportError as e2:
        print(f"Error importing DataLoader: {e2}")
        print("Make sure dataloader.py is in the modules/ folder")
        print("Expected structure:")
        print("  modules/")
        print("    __init__.py")
        print("    dataloader.py")
        sys.exit(1)


class DataValidationApp:
    """Main application class for data validation"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.loader = None
        self.validation_results = {}
        self.device_data = []
        
    def _setup_logger(self):
        """Setup application logger"""
        logs_folder = Path("logs")
        logs_folder.mkdir(exist_ok=True)
        
        log_file = logs_folder / f"{datetime.now().strftime('%Y%m%d')}.logs"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('DataValidationApp')
    
    def _filter_tag_columns(self, df, source_name=""):
        """Filter out columns containing 'tag' in their names"""
        if df is None or df.empty:
            return df
        
        original_columns = list(df.columns)
        # Filter out columns containing 'tag' (case insensitive)
        filtered_columns = [col for col in df.columns if 'tag' not in col.lower()]
        
        if len(filtered_columns) < len(original_columns):
            skipped_columns = [col for col in original_columns if col not in filtered_columns]
            self.logger.info(f"Skipping tag columns in {source_name}: {skipped_columns}")
        
        return df[filtered_columns] if filtered_columns else df
    
    def initialize(self):
        """Initialize the application"""
        self.logger.info("="*60)
        self.logger.info("STARTING DATA VALIDATION APPLICATION")
        self.logger.info("="*60)
        
        # Check if data folder exists
        data_folder = Path("data")
        if not data_folder.exists():
            self.logger.error(f"Data folder not found: {data_folder}")
            self.logger.error("Please ensure the data folder exists with required files:")
            self.logger.error("  - 20250613_0832_baza_kontaktowa.csv")
            self.logger.error("  - 20250613_0832_terminale_grafana.csv")
            self.logger.error("  - 20250613_0832_terminale_instalations.xlsx")
            self.logger.error("  - 20250613_0832_terminale_signio.csv")
            return False
        
        # Create output folder
        out_folder = Path("out")
        out_folder.mkdir(exist_ok=True)
        
        self.logger.info("Application initialized successfully")
        return True
    
    def load_data(self):
        """Load all data sources"""
        self.logger.info("STEP 1: Loading data from all sources...")
        
        self.loader = DataLoader(data_folder="data", logs_folder="logs")
        data = self.loader.load_all_data()
        
        # Filter out tag columns from all loaded data
        if hasattr(self.loader, 'baza_kontaktowa') and self.loader.baza_kontaktowa is not None:
            self.loader.baza_kontaktowa = self._filter_tag_columns(self.loader.baza_kontaktowa, "baza_kontaktowa")
        
        if hasattr(self.loader, 'terminale_grafana') and self.loader.terminale_grafana is not None:
            self.loader.terminale_grafana = self._filter_tag_columns(self.loader.terminale_grafana, "terminale_grafana")
        
        if hasattr(self.loader, 'terminale_instalations') and self.loader.terminale_instalations is not None:
            self.loader.terminale_instalations = self._filter_tag_columns(self.loader.terminale_instalations, "terminale_instalations")
        
        if hasattr(self.loader, 'terminale_signio') and self.loader.terminale_signio is not None:
            self.loader.terminale_signio = self._filter_tag_columns(self.loader.terminale_signio, "terminale_signio")
        
        # Check if any data was loaded
        loaded_sources = [name for name, df in data.items() if not df.empty]
        failed_sources = [name for name, df in data.items() if df.empty]
        
        self.logger.info(f"Successfully loaded: {len(loaded_sources)} sources")
        self.logger.info(f"Failed to load: {len(failed_sources)} sources")
        
        if loaded_sources:
            self.logger.info(f"Loaded sources: {', '.join(loaded_sources)}")
        if failed_sources:
            self.logger.warning(f"Failed sources: {', '.join(failed_sources)}")
        
        return len(loaded_sources) > 0
    
    def validate_individual_sources(self):
        """Validate each data source individually"""
        self.logger.info("STEP 2: Validating individual data sources...")
        
        validation_results = {}
        
        # Validate baza kontaktowa
        if self.loader.baza_kontaktowa is not None and not self.loader.baza_kontaktowa.empty:
            validation_results['baza_kontaktowa'] = self._validate_baza_kontaktowa()
        
        # Validate terminale grafana
        if self.loader.terminale_grafana is not None and not self.loader.terminale_grafana.empty:
            validation_results['terminale_grafana'] = self._validate_terminale_grafana()
        
        # Validate terminale instalations
        if self.loader.terminale_instalations is not None and not self.loader.terminale_instalations.empty:
            validation_results['terminale_instalations'] = self._validate_terminale_instalations()
        
        # Validate terminale signio
        if self.loader.terminale_signio is not None and not self.loader.terminale_signio.empty:
            validation_results['terminale_signio'] = self._validate_terminale_signio()
        
        self.validation_results = validation_results
        return validation_results
    
    def _validate_baza_kontaktowa(self):
        """Validate baza kontaktowa data - REFERENCE DATA (correct addresses)"""
        self.logger.info("Validating baza kontaktowa (REFERENCE - correct addresses)...")
        df = self.loader.baza_kontaktowa
        errors = []
        
        # Check for missing required columns in reference data
        required_columns = ['Nr sklepu', 'Miasto', 'Kod pocztowy', 'Ulica', 'Status sklepu']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns in reference data: {missing_columns}")
        
        # Validate Nr sklepu (should be numeric and unique in reference)
        if 'Nr sklepu' in df.columns:
            invalid_nr_sklepu = df[df['Nr sklepu'].isna() | (df['Nr sklepu'] == '')].index.tolist()
            if invalid_nr_sklepu:
                errors.append(f"Empty or invalid Nr sklepu in reference data: {len(invalid_nr_sklepu)} rows")
            
            # Check for duplicates in reference data
            duplicates = df[df.duplicated(subset=['Nr sklepu'], keep=False)]
            if not duplicates.empty:
                errors.append(f"Duplicate Nr sklepu in reference data: {len(duplicates)} rows")
        
        # Validate postal codes format in reference data
        if 'Kod pocztowy' in df.columns:
            import re
            postal_pattern = re.compile(r'^\d{2}-\d{3}$')
            invalid_postal = df[~df['Kod pocztowy'].astype(str).str.match(postal_pattern, na=False)].index.tolist()
            if invalid_postal:
                errors.append(f"Invalid postal code format in reference data: {len(invalid_postal)} rows")
        
        # Check completeness of reference address data
        address_fields = ['Miasto', 'Ulica']
        for field in address_fields:
            if field in df.columns:
                empty_values = df[df[field].isna() | (df[field] == '')].index.tolist()
                if empty_values:
                    errors.append(f"Missing {field} in reference data: {len(empty_values)} rows")
        
        # Info: This is reference data
        if len(errors) == 0:
            self.logger.info("✅ Reference address data (Baza Kontaktowa) appears complete and valid")
        else:
            self.logger.warning("⚠️  Issues in reference address data - this may affect Signio validation")
        
        self.logger.info(f"Baza kontaktowa validation: {len(errors)} issues found")
        return {
            'total_rows': len(df),
            'errors': errors,
            'error_count': len(errors)
        }
    
    def _validate_terminale_grafana(self):
        """Validate terminale grafana data"""
        self.logger.info("Validating terminale grafana...")
        df = self.loader.terminale_grafana
        errors = []
        
        # Check for required columns
        required_columns = ['ID', 'NAME', 'MPK', 'STATUS SKLEPU']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Validate IDs
        if 'ID' in df.columns:
            empty_ids = df[df['ID'].isna() | (df['ID'] == '')].index.tolist()
            if empty_ids:
                errors.append(f"Empty IDs in rows: {len(empty_ids)}")
        
        # Validate MPK codes
        if 'MPK' in df.columns:
            empty_mpk = df[df['MPK'].isna() | (df['MPK'] == '')].index.tolist()
            if empty_mpk:
                errors.append(f"Empty MPK codes in rows: {len(empty_mpk)}")
        
        # Check data consistency
        if 'DATA INSTALACJI' in df.columns:
            invalid_dates = []
            for idx, date_val in df['DATA INSTALACJI'].items():
                if pd.notna(date_val) and date_val != '':
                    try:
                        pd.to_datetime(date_val)
                    except:
                        invalid_dates.append(idx)
            if invalid_dates:
                errors.append(f"Invalid installation dates in rows: {len(invalid_dates)}")
        
        self.logger.info(f"Terminale grafana validation: {len(errors)} issues found")
        return {
            'total_rows': len(df),
            'errors': errors,
            'error_count': len(errors)
        }
    
    def _validate_terminale_instalations(self):
        """Validate terminale instalations data - REFERENCE DATA (correct device info)"""
        self.logger.info("Validating terminale instalations (REFERENCE - correct device data)...")
        df = self.loader.terminale_instalations
        errors = []
        
        # Basic structure validation for reference data
        expected_columns = ['MPK', 'Format', 'Liczba monitorw', 'Typ monitora', 'Rozmiar', 'Producent', 'Data instalacji']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns in reference data: {missing_columns}")
        
        # Check for empty critical reference fields
        if 'MPK' in df.columns:
            empty_mpk = df[df['MPK'].isna() | (df['MPK'] == '')].index.tolist()
            if empty_mpk:
                errors.append(f"Empty MPK codes in reference data: {len(empty_mpk)} rows")
        
        # Validate reference device data completeness
        critical_fields = ['Format', 'Typ monitora', 'Rozmiar', 'Producent']
        for field in critical_fields:
            if field in df.columns:
                empty_values = df[df[field].isna() | (df[field] == '')].index.tolist()
                if empty_values:
                    errors.append(f"Missing {field} in reference data: {len(empty_values)} rows")
        
        # Check for date format in installation dates
        if 'Data instalacji' in df.columns:
            invalid_dates = []
            for idx, date_val in df['Data instalacji'].items():
                if pd.notna(date_val) and str(date_val).strip() != '':
                    try:
                        pd.to_datetime(str(date_val))
                    except:
                        invalid_dates.append(idx)
            if invalid_dates:
                errors.append(f"Invalid installation dates in reference data: {len(invalid_dates)} rows")
        
        # Info: This is reference data
        if len(errors) == 0:
            self.logger.info("✅ Reference device data (Instalations) appears complete and valid")
        else:
            self.logger.warning("⚠️  Issues in reference device data - this may affect Signio validation")
        
        self.logger.info(f"Terminale instalations validation: {len(errors)} issues found")
        return {
            'total_rows': len(df),
            'errors': errors,
            'error_count': len(errors)
        }
    
    def _validate_terminale_signio(self):
        """Validate terminale signio data"""
        self.logger.info("Validating terminale signio...")
        df = self.loader.terminale_signio
        errors = []
        
        # Similar validation to grafana
        required_columns = ['ID', 'NAME', 'MPK']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Validate IDs
        if 'ID' in df.columns:
            empty_ids = df[df['ID'].isna() | (df['ID'] == '')].index.tolist()
            if empty_ids:
                errors.append(f"Empty IDs in rows: {len(empty_ids)}")
        
        # Validate MPK codes
        if 'MPK' in df.columns:
            empty_mpk = df[df['MPK'].isna() | (df['MPK'] == '')].index.tolist()
            if empty_mpk:
                errors.append(f"Empty MPK codes in rows: {len(empty_mpk)}")
        
        self.logger.info(f"Terminale signio validation: {len(errors)} issues found")
        return {
            'total_rows': len(df),
            'errors': errors,
            'error_count': len(errors)
        }
    
    def validate_cross_source_consistency(self):
        """Validate consistency across different data sources - FOCUS ON SIGNIO COVERAGE"""
        self.logger.info("STEP 3: Validating Signio data coverage against reference sources...")
        
        # This is the MAIN validation - checking if Signio matches reference data
        consistency_errors = self.loader.validate_data_consistency()
        
        if consistency_errors:
            self.logger.warning("CRITICAL: Signio data coverage issues detected!")
            for error in consistency_errors:
                self.logger.warning(f"  ❌ {error}")
        else:
            self.logger.info("✅ Signio data coverage validation passed!")
        
        self.logger.info(f"Cross-source validation: {len(consistency_errors)} issues found")
        return consistency_errors
    
    def _validate_field(self, value, field_name, validation_type='not_empty'):
        """Validate individual field value and return error description"""
        errors = []
        
        if validation_type == 'not_empty':
            if pd.isna(value) or str(value).strip() == '':
                errors.append(f"Empty {field_name}")
        
        elif validation_type == 'postal_code':
            import re
            if pd.notna(value):
                postal_pattern = re.compile(r'^\d{2}-\d{3}$')
                if not postal_pattern.match(str(value)):
                    errors.append(f"Invalid postal code format")
        
        elif validation_type == 'date':
            if pd.notna(value) and str(value).strip() != '':
                try:
                    pd.to_datetime(str(value))
                except:
                    errors.append(f"Invalid date format")
        
        elif validation_type == 'numeric':
            if pd.notna(value) and str(value).strip() != '':
                try:
                    float(value)
                except:
                    errors.append(f"Invalid numeric value")
        
        return '; '.join(errors) if errors else ''
    
    def _get_reference_data(self, mpk_code):
        """Get reference data for given MPK code from baza_kontaktowa and instalations"""
        reference = {}
        
        # Get address data from baza_kontaktowa
        if (self.loader.baza_kontaktowa is not None and 
            not self.loader.baza_kontaktowa.empty and 
            'Nr sklepu' in self.loader.baza_kontaktowa.columns):
            
            baza_row = self.loader.baza_kontaktowa[
                self.loader.baza_kontaktowa['Nr sklepu'].astype(str) == str(mpk_code)
            ]
            
            if not baza_row.empty:
                baza_row = baza_row.iloc[0]
                reference.update({
                    'ref_miasto': baza_row.get('Miasto', ''),
                    'ref_kod_pocztowy': baza_row.get('Kod pocztowy', ''),
                    'ref_ulica': baza_row.get('Ulica', ''),
                    'ref_status_sklepu': baza_row.get('Status sklepu', ''),
                    'ref_kontakt': baza_row.get('Kontakt', '')
                })
        
        # Get installation data from terminale_instalations
        if (self.loader.terminale_instalations is not None and 
            not self.loader.terminale_instalations.empty and 
            'MPK' in self.loader.terminale_instalations.columns):
            
            inst_row = self.loader.terminale_instalations[
                self.loader.terminale_instalations['MPK'].astype(str) == str(mpk_code)
            ]
            
            if not inst_row.empty:
                inst_row = inst_row.iloc[0]
                reference.update({
                    'ref_format': inst_row.get('Format', ''),
                    'ref_liczba_monitorow': inst_row.get('Liczba monitorw', ''),
                    'ref_typ_monitora': inst_row.get('Typ monitora', ''),
                    'ref_rozmiar': inst_row.get('Rozmiar', ''),
                    'ref_producent': inst_row.get('Producent', ''),
                    'ref_data_instalacji': inst_row.get('Data instalacji', '')
                })
        
        return reference
    
    def create_device_listing(self):
        """Create comprehensive device listing with error information"""
        self.logger.info("STEP 4: Creating comprehensive device listing...")
        
        device_records = []
        
        # Process Signio data as primary source
        if (self.loader.terminale_signio is not None and 
            not self.loader.terminale_signio.empty):
            
            self.logger.info("Processing Signio devices...")
            
            for idx, row in self.loader.terminale_signio.iterrows():
                device_record = {}
                
                # Basic device data from Signio
                device_record['source'] = 'Signio'
                device_record['id'] = row.get('ID', '')
                device_record['name'] = row.get('NAME', '')
                device_record['mpk'] = row.get('MPK', '')
                device_record['fingerprint'] = row.get('FINGERPRINT', '')
                
                # Add other available columns from Signio (excluding tag columns)
                for col in self.loader.terminale_signio.columns:
                    if col not in ['ID', 'NAME', 'MPK', 'FINGERPRINT'] and 'tag' not in col.lower():
                        device_record[f'signio_{col.lower()}'] = row.get(col, '')
                
                # Get reference data
                mpk_code = row.get('MPK', '')
                reference_data = self._get_reference_data(mpk_code)
                device_record.update(reference_data)
                
                # Validate fields and add error columns
                device_record['error_id'] = self._validate_field(row.get('ID'), 'ID')
                device_record['error_name'] = self._validate_field(row.get('NAME'), 'NAME')
                device_record['error_mpk'] = self._validate_field(row.get('MPK'), 'MPK')
                
                # Check against reference data
                device_record['error_address_mismatch'] = ''
                device_record['error_installation_mismatch'] = ''
                
                # Address validation against reference
                if reference_data.get('ref_miasto'):
                    signio_city = row.get('MIASTO', '') or row.get('City', '')
                    if signio_city and signio_city.strip().lower() != reference_data['ref_miasto'].strip().lower():
                        device_record['error_address_mismatch'] += 'City mismatch; '
                
                # Installation data validation
                installation_errors = []
                if not reference_data.get('ref_format'):
                    installation_errors.append('Missing format in reference')
                if not reference_data.get('ref_typ_monitora'):
                    installation_errors.append('Missing monitor type in reference')
                if not reference_data.get('ref_producent'):
                    installation_errors.append('Missing producer in reference')
                
                device_record['error_installation_mismatch'] = '; '.join(installation_errors)
                
                # Calculate completeness score
                total_fields = len([k for k in device_record.keys() if not k.startswith('error_')])
                empty_fields = len([v for v in device_record.values() if str(v).strip() == ''])
                device_record['completeness_score'] = round((total_fields - empty_fields) / total_fields * 100, 1)
                
                device_records.append(device_record)
        
        # Process Grafana data for devices not in Signio
        if (self.loader.terminale_grafana is not None and 
            not self.loader.terminale_grafana.empty):
            
            self.logger.info("Processing Grafana devices not in Signio...")
            
            signio_mpks = set()
            if device_records:
                signio_mpks = {str(record['mpk']) for record in device_records}
            
            for idx, row in self.loader.terminale_grafana.iterrows():
                mpk_code = str(row.get('MPK', ''))
                
                if mpk_code not in signio_mpks:
                    device_record = {}
                    
                    # Basic device data from Grafana
                    device_record['source'] = 'Grafana'
                    device_record['id'] = row.get('ID', '')
                    device_record['name'] = row.get('NAME', '')
                    device_record['mpk'] = row.get('MPK', '')
                    device_record['fingerprint'] = row.get('FINGERPRINT', '')
                    
                    # Add other available columns from Grafana (excluding tag columns)
                    for col in self.loader.terminale_grafana.columns:
                        if col not in ['ID', 'NAME', 'MPK', 'FINGERPRINT'] and 'tag' not in col.lower():
                            device_record[f'grafana_{col.lower()}'] = row.get(col, '')
                    
                    # Get reference data
                    reference_data = self._get_reference_data(mpk_code)
                    device_record.update(reference_data)
                    
                    # Validate fields
                    device_record['error_id'] = self._validate_field(row.get('ID'), 'ID')
                    device_record['error_name'] = self._validate_field(row.get('NAME'), 'NAME')
                    device_record['error_mpk'] = self._validate_field(row.get('MPK'), 'MPK')
                    device_record['error_address_mismatch'] = 'Not in Signio system'
                    device_record['error_installation_mismatch'] = ''
                    
                    # Calculate completeness score
                    total_fields = len([k for k in device_record.keys() if not k.startswith('error_')])
                    empty_fields = len([v for v in device_record.values() if str(v).strip() == ''])
                    device_record['completeness_score'] = round((total_fields - empty_fields) / total_fields * 100, 1)
                    
                    device_records.append(device_record)
        
        self.device_data = device_records
        self.logger.info(f"Created device listing with {len(device_records)} devices")
        return device_records
    def generate_comprehensive_report(self):
        """Generate comprehensive device report CSV"""
        self.logger.info("STEP 5: Generating comprehensive device report...")

        # Create device listing
        self.create_device_listing()

        if not self.device_data:
            self.logger.warning("No device data to report")
            # Create empty report
            empty_df = pd.DataFrame(columns=[
                'source', 'id', 'name', 'mpk', 'all_errors', 'completeness_score'
            ])
            output_file = Path("out") / "result.csv"
            empty_df.to_csv(output_file, index=False, encoding='utf-8')
            return output_file

        # Convert to DataFrame
        device_df = pd.DataFrame(self.device_data)

        # Combine all error_* columns into one 'all_errors' column
        error_columns = [col for col in device_df.columns if col.startswith('error_')]
        device_df['all_errors'] = device_df[error_columns].apply(
            lambda row: '; '.join([str(e) for e in row if str(e).strip() != '']),
            axis=1
        )

        # (Optional) remove original error_* columns
        device_df.drop(columns=error_columns, inplace=True)

        # Add summary statistics
        self.logger.info("Device listing summary:")
        self.logger.info(f"  Total devices: {len(device_df)}")
        self.logger.info(f"  Signio devices: {len(device_df[device_df['source'] == 'Signio'])}")
        self.logger.info(f"  Grafana-only devices: {len(device_df[device_df['source'] == 'Grafana'])}")

        # Count total error instances (rows with non-empty 'all_errors')
        error_rows = device_df[device_df['all_errors'].str.strip() != '']
        self.logger.info(f"  Devices with errors: {len(error_rows)}")

        # Calculate average completeness
        if 'completeness_score' in device_df.columns:
            avg_completeness = device_df['completeness_score'].mean()
            self.logger.info(f"  Average completeness: {avg_completeness:.1f}%")

        # Save comprehensive report
        output_file = Path("out") / "result.csv"
        device_df.to_csv(output_file, index=False, encoding='utf-8')

        self.logger.info(f"Comprehensive device report saved to: {output_file}")
        self.logger.info(f"Report contains {len(device_df)} devices with {len(device_df.columns)} columns")

        return output_file


    def run(self):
        """Run the complete data validation process"""
        try:
            # Initialize
            if not self.initialize():
                return False
            
            # Load data
            if not self.load_data():
                self.logger.error("Failed to load any data - aborting")
                return False
            
            # Validate individual sources
            self.validate_individual_sources()
            
            # Validate cross-source consistency
            self.validate_cross_source_consistency()
            
            # Generate comprehensive report
            report_file = self.generate_comprehensive_report()
            
            # Summary
            self.logger.info("="*60)
            self.logger.info("DATA VALIDATION COMPLETED SUCCESSFULLY")
            self.logger.info("="*60)
            self.logger.info(f"Comprehensive device report generated: {report_file}")
            
            # Print summary statistics
            total_errors = sum(result['error_count'] for result in self.validation_results.values())
            self.logger.info(f"Total validation errors: {total_errors}")
            
            for source, result in self.validation_results.items():
                self.logger.info(f"  {source}: {result['error_count']} errors in {result['total_rows']} rows")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Application failed with error: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

def main():
    """Main entry point"""
    app = DataValidationApp()
    success = app.run()
    
    if success:
        print("\n✓ Data validation completed successfully!")
        print("✓ Check logs/ folder for detailed logs")
        print("✓ Check out/result.csv for comprehensive device report")
        return 0
    else:
        print("\n✗ Data validation failed!")
        print("✗ Check logs for detailed error information")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)