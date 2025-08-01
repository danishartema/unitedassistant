import os
from typing import List

def load_rag_context(rag_folder: str) -> List[str]:
    """Loads all .txt files in the RAG folder and returns their contents as a list of strings."""
    context_chunks = []
    if not os.path.exists(rag_folder):
        return context_chunks
    for fname in os.listdir(rag_folder):
        if fname.lower().endswith('.txt'):
            with open(os.path.join(rag_folder, fname), encoding='utf-8') as f:
                context_chunks.append(f.read())
    return context_chunks 