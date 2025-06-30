import os
import gradio as gr
from docling.document_converter import DocumentConverter

def convert_multiple_files(input_files):
    output_files = []
    converter = DocumentConverter()
    
    for input_file in input_files:
        try:
            base_name = os.path.splitext(os.path.basename(input_file.name))[0]
            output_file = os.path.join(os.path.dirname(input_file), f"{base_name}.md")
            
            result = converter.convert(input_file.name)
            markdown = result.document.export_to_markdown()
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            output_files.append(output_file)
        
        except Exception as e:
            raise gr.Error(f"Failed to convert {input_file.name}: {str(e)}")
    
    return output_files

# Gradio UI for batch conversion
with gr.Blocks(title="Batch Word to Markdown Converter") as demo:
    gr.HTML("<style>footer.svelte-czcr5b { display: none !important; }</style>")
    gr.Markdown("## 📄 Batch Convert Word Documents (.docx) to Markdown")
    
    file_input = gr.File(
        label="Upload .docx files",
        file_types=[".docx"],
        file_count="multiple"
    )
    file_output = gr.File(
        label="Download converted Markdown files",
        file_types=[".md"],
        interactive=False,
        file_count="multiple"
    )
    
    convert_btn = gr.Button("Convert All", variant="primary")
    
    convert_btn.click(
        fn=convert_multiple_files,
        inputs=file_input,
        outputs=file_output
    )

if __name__ == "__main__":
    demo.launch(share=False, inbrowser=True)