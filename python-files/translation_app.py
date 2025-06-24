import streamlit as st
import os # Import os for handling file paths

# Define the supported file types
SUPPORTED_FILE_TYPES = ['pdf', 'docx', 'xlsx', 'pptx']

st.title("Translation Check Tool")

# Create file uploaders for original and translated files
original_file = st.file_uploader("Upload Original File", type=SUPPORTED_FILE_TYPES)
translated_file = st.file_uploader("Upload Translated File", type=SUPPORTED_FILE_TYPES)

# Allow users to specify file types (though st.file_uploader's type parameter handles this for upload)
# We can still add dropdowns for clarity or future manual path input features if needed.
# For now, the file_uploader handles the type selection during upload based on the allowed types.
# original_file_type = st.selectbox("Select Original File Type", SUPPORTED_FILE_TYPES, index=0)
# translated_file_type = st.selectbox("Select Translated File Type", SUPPORTED_FILE_TYPES, index=0)

# Add a button to trigger the translation check
if st.button("Run Translation Check"):
    if original_file is not None and translated_file is not None:
        # Process the uploaded files
        # Streamlit provides the uploaded file as a BytesIO object.
        # We need to save them to a temporary location to use with our existing functions.
        original_file_path = os.path.join("/tmp", original_file.name)
        translated_file_path = os.path.join("/tmp", translated_file.name)

        with open(original_file_path, "wb") as f:
            f.write(original_file.getbuffer())

        with open(translated_file_path, "wb") as f:
            f.write(translated_file.getbuffer())

        # Determine file types from uploaded file names
        original_file_type = original_file.name.split('.')[-1].lower()
        translated_file_type = translated_file.name.split('.')[-1].lower()

        # Ensure selected types match uploaded file extensions (optional but good practice)
        if original_file_type not in SUPPORTED_FILE_TYPES or translated_file_type not in SUPPORTED_FILE_TYPES:
             st.error("Unsupported file type uploaded. Please upload PDF, DOCX, XLSX, or PPTX files.")
        else:
            # Call the main translation check function
            # Redirect stdout to capture the output of format_comparison_report
            import sys
            from io import StringIO

            old_stdout = sys.stdout
            redirected_output = StringIO()
            sys.stdout = redirected_output

            try:
                translate_check(original_file_path, original_file_type, translated_file_path, translated_file_type)
                comparison_report = redirected_output.getvalue()
                st.text_area("Comparison Report", comparison_report, height=400)
            except Exception as e:
                st.error(f"An error occurred during the translation check: {e}")
            finally:
                sys.stdout = old_stdout # Restore stdout

            # Clean up temporary files
            os.remove(original_file_path)
            os.remove(translated_file_path)

    else:
        st.warning("Please upload both original and translated files.")
