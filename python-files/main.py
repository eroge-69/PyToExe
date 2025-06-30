from pptx import Presentation

def extract_notes(pptx_path, output_txt_path):
    prs = Presentation(pptx_path)
    with open(output_txt_path, "w", encoding="utf-8") as f:
        for i, slide in enumerate(prs.slides, 1):
            notes_slide = slide.notes_slide
            text = ""
            if notes_slide and notes_slide.notes_text_frame:
                text = notes_slide.notes_text_frame.text.strip()
            f.write(f"Slide {i} Notes:\n{text}\n\n")

if __name__ == "__main__":
    filename = input("Entrez le nom du fichier PPTX (par exemple, test) : ")
    extract_notes(f"{filename}.pptx", "notes.txt")
