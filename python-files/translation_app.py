import streamlit as st
import os
import sys
from io import StringIO

# Ensure the helper functions (extract_text_from_file, compare_texts, format_comparison_report, translate_check)
# are defined or imported before this code block.
# Assuming they are available in the notebook environment from previous steps.

# Define the supported file types
SUPPORTED_FILE_TYPES = ['pdf', 'docx', 'xlsx', 'pptx']

st.title("Translation Check Tool")

# Create file uploaders for original and translated files
original_file = st.file_uploader("Upload Original File", type=SUPPORTED_FILE_TYPES)
translated_file = st.file_uploader("Upload Translated File", type=SUPPORTED_FILE_TYPES)

# The file_uploader handles type selection based on the 'type' parameter.
# We extract the actual file type from the uploaded file's name later.

# Add a button to trigger the translation check
if st.button("Run Translation Check"):
    if original_file is not None and translated_file is not None:
        # Process the uploaded files
        # Streamlit provides the uploaded file as a BytesIO object.
        # We need to save them to a temporary location to use with our existing functions.
        # Using a more robust way to handle temporary files in a script context
        # In a real Streamlit app, you might use tempfile module or st.session_state
        original_file_path = os.path.join("/tmp", original_file.name)
        translated_file_path = os.path.join("/tmp", translated_file.name)

        try:
            with open(original_file_path, "wb") as f:
                f.write(original_file.getbuffer())

            with open(translated_file_path, "wb") as f:
                f.write(translated_file.getbuffer())

            # Determine file types from uploaded file names
            original_file_type = original_file.name.split('.')[-1].lower()
            translated_file_type = translated_file.name.split('.')[-1].lower()

            # Ensure extracted types are supported
            if original_file_type not in SUPPORTED_FILE_TYPES or translated_file_type not in SUPPORTED_FILE_TYPES:
                 st.error("Unsupported file type uploaded. Please upload PDF, DOCX, XLSX, or PPTX files.")
            else:
                # Call the main translation check function
                # Redirect stdout to capture the output of format_comparison_report
                old_stdout = sys.stdout
                redirected_output = StringIO()
                sys.stdout = redirected_output

                try:
                    # Assuming translate_check, extract_text_from_file, compare_texts, format_comparison_report
                    # are defined in the notebook scope.
                    translate_check(original_file_path, original_file_type, translated_file_path, translated_file_type)
                    comparison_report = redirected_output.getvalue()
                    st.text_area("Comparison Report", comparison_report, height=400)
                except Exception as e:
                    st.error(f"An error occurred during the translation check: {e}")
                finally:
                    sys.stdout = old_stdout # Restore stdout

        except Exception as e:
            st.error(f"An error occurred while saving files: {e}")
        finally:
            # Clean up temporary files safely
            if os.path.exists(original_file_path):
                os.remove(original_file_path)
            if os.path.exists(translated_file_path):
                os.remove(translated_file_path)

    else:
        st.warning("Please upload both original and translated files.")
