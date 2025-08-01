from docx import Document
import os
from typing import Optional

def extract_output_template_from_docx(docx_path: str) -> str:
    """Extracts the output template text from a .docx file (all paragraphs concatenated)."""
    doc = Document(docx_path)
    output = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            output.append(text)
    return '\n'.join(output)

def find_output_docx_file_in_folder(folder_path: str) -> Optional[str]:
    """Finds the first .docx file in a folder and returns its path, or None if not found."""
    for fname in os.listdir(folder_path):
        if fname.lower().endswith('.docx'):
            return os.path.join(folder_path, fname)
    return None 