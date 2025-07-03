import json
import os
import xlsxwriter
import csv
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import win32print

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data_dict = json.loads(post_data)
            serial_no_data = data_dict.get("data")
            data_location = data_dict.get("data_location", "")
            directory, filename = os.path.split(data_dict.get("data_location"))
            headers = data_dict.get("header_values")
            lab_path = data_dict.get("lab_path")

            if not all([serial_no_data, data_location, headers, lab_path]):
                self._send_error(400, "Missing required fields in the request.")
                return

            data_file_exist = os.path.exists(data_location)
            msg = "Default message"

            mismatch_count = 0
            # for serial_no in serial_no_data:
            #     if list(serial_no.keys()) != headers:
            #         mismatch_count += 1

            if data_file_exist:
                object_to_be_passed = {
                    "header_values": headers,
                    "dict_data_keys": serial_no_data,
                    "mismatch_count": mismatch_count
                }
                msg = json.dumps(object_to_be_passed)

                if mismatch_count == 0:
                    logging.info("Mismatch_count is 0")

                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    file_path = os.path.join(directory, filename)

                    if filename.lower().endswith('.csv'):
                        self._write_to_csv(file_path, headers, serial_no_data)
                    elif filename.lower().endswith('.txt'):
                        prn_data = self._write_to_txt(file_path, headers, serial_no_data)
                    else:
                        self._write_to_xlsx(file_path, headers, serial_no_data)

                    if not filename.lower().endswith('.txt'):
                        lab_file_exist = os.path.exists(lab_path)

                        if lab_file_exist:
                            logging.info(f"Lab file exists at {lab_path}")                            
                            # Uncomment to enable actual printing if necessary
                            os.startfile(lab_path, "print")
                        else:
                            logging.warning("Lab file does not exist")
                            self._send_error(404, "Lab file does not exist")
                            return
                    else:
                        if prn_data:
                            self._print_prn(prn_data)
                        else:
                            logging.warning("Print Failed")
                            self._send_error(500, "Print Failed")
                else:
                    logging.warning("Pack type and header data mismatch")
                    self._send_error(400, "Pack type and header data mismatch")
                    return
            else:
                logging.error("Data file does not exist")
                self._send_error(404, "Data file does not exist")
                return
                   
            response = {
                "message": "Data received successfully",
                "received_data": data_dict,
                "message": msg
            }

            self._send_response(200, response)

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
            logging.error("Invalid JSON in request")

    def _write_to_xlsx(self, file_path, headers, data):
        try:
            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet()

            for col_num, header in enumerate(headers):
                worksheet.write(0, col_num, header)

            for row_num, row_data in enumerate(data, start=1):
                for col_num, key in enumerate(headers):
                    worksheet.write(row_num, col_num, row_data.get(key, ""))
            logging.info("Print with XLSX")
            workbook.close()
            logging.info(f"Data successfully written to {file_path}")

        except xlsxwriter.exceptions.FileCreateError as e:
            logging.error(f"Error creating Excel file: {e}")
            self._send_error(500, "File creation failed")

    def _write_to_csv(self, file_path, headers, data):
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            logging.info("Print with CSV")    
            logging.info(f"Data successfully written to {file_path}")
        except Exception as e:
            logging.error(f"Error creating CSV file: {e}")
            self._send_error(500, "File creation failed")

    def _write_to_txt(self, file_path: str, headers: list, data: list) -> bytes | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                template = file.read()

            result = ""
            for item in data:
                missing_headers = [key for key in headers if f"{{{key}}}" not in template]
                if missing_headers:
                    raise KeyError(f"Missing keys in PRN template: {missing_headers}. Ensure they match the server data.")

                result += template.format(**item) + "\n"

            logging.info("✅ PRN data generated successfully")
            return result.encode('utf-8')

        except KeyError as ke:
            logging.error(f"❌ KeyError generating PRN: {ke}")
            self._send_error(500, "Error generating PRN")

        except Exception as e:
            logging.error(f"❌ Unexpected error generating PRN: {e}")
            self._send_error(500, "Error generating PRN")
        
        return None

    
    def _print_prn(self, prn_data: bytes):
        hPrinter = None
        try:
            printer_name = win32print.GetDefaultPrinter()
            hPrinter = win32print.OpenPrinter(printer_name)

            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Label Job", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, prn_data)
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)

            logging.info("✅ Data printed successfully")

        except Exception as e:
            logging.error(f"❌ Printing failed: {e}")
            self._send_error(500, f"Printing failed: {e}")

        finally:
            if hPrinter:
                try:
                    win32print.ClosePrinter(hPrinter)
                except Exception as e:
                    logging.warning(f"⚠️ Failed to close printer handle: {e}")

    def _send_response(self, code, response):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def _send_error(self, code, message):
        self._send_response(code, {"error": message})

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Starting server on port {port}...")

    while True:  # Keep the server running indefinitely
        try:
            httpd.serve_forever()
        except Exception as e:
            logging.error(f"Server error: {e}. Restarting server...")

if __name__ == '__main__':
    run(port=8080)