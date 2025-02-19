import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import pymupdf  # PyMuPDF
import torch
import tkinter as tk
from tkinter import filedialog
from transformers import AutoModel, AutoTokenizer, pipeline, AutoModelForCausalLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
import docx
from PIL import Image
import pytesseract

# Function to Open File Dialog
def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a Document",
        filetypes=[
            ("PDF Files", "*.pdf"),
            ("Text Files", "*.txt"),
            ("Word Documents", "*.doc;*.docx"),
            ("Image Files", "*.jpg;*.jpeg;*.png")
        ]
    )
    return file_path

# Step 1: Load and Chunk Document
def load_and_chunk_document(file_path, chunk_size=500, overlap=100):
    try:
        if file_path.endswith(".pdf"):
            with pymupdf.open(file_path) as doc:
                text = "\n".join([page.get_text("text") for page in doc])  # Extract text from all pages
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif file_path.endswith(".doc") or file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif file_path.endswith((".jpg", ".jpeg", ".png")):
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
        else:
            raise ValueError("Unsupported file format. Please upload a .txt, .pdf, .doc, .docx, .jpg, .jpeg, or .png file.")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap
        )
        chunks = text_splitter.split_text(text)
        return chunks
    except Exception as e:
        print(f"Error loading document: {e}")
        return []

# Step 2: Convert Chunks to Embeddings
def create_vector_store(chunks):
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embedding_model)
    return vector_store

# Step 3: Load Fine-Tuned Model (if applicable)
def load_fine_tuned_model():
    model_name = "mistralai/Mistral-7B-Instruct-v0.3"  # Ch`ange if fine-tuned model is available
    hf_token = "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"  # Replace with your actual token

    tokenizer = AutoTokenizer.from_pretrained(
        model_name, 
        # use_auth_token=hf_token,
        trust_remote_code= True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = AutoModel.from_pretrained(
        model_name, 
        use_auth_token=hf_token,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    ).to(device)
    
    return tokenizer, model, device


# Step 4: Query Processing with RAG
def query_rag(vector_store, query, model, tokenizer):
    retriever = vector_store.as_retriever()
    rag_pipeline = RetrievalQA.from_chain_type(llm=model, chain_type="stuff", retriever=retriever)
    response = rag_pipeline.run(query)
    return response

# Example Usage
if __name__ == "__main__":
    document_path = "output_table.pdf"
    # document_path = select_file()
    if not document_path:
        print("No file selected.")
    else:
        chunks = load_and_chunk_document(document_path)
        if chunks:
            vector_store = create_vector_store(chunks)
            tokenizer, model = load_fine_tuned_model()
            
            query = input("Enter your query: ")
            response = query_rag(vector_store, query, model, tokenizer)
            print("Response:", response)
