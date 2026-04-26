import os
from rag import load_manual, chunk_documents, build_vectorstore

PDF_PATH = "VFYmanual.pdf"

if not os.path.exists(PDF_PATH):
    print("ERROR: VFYmanual.pdf not found in the backend folder.")
    print("Please add the manual PDF to the backend folder and name it VFYmanual.pdf")
    exit()

pages = load_manual(PDF_PATH)
chunks = chunk_documents(pages)
vectorstore = build_vectorstore(chunks)

print("Manual successfully loaded into vector store!")