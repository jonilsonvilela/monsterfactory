import os
import pickle
import fitz  # PyMuPDF
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --- Configurações ---
POLICY_DOC_PATH = "Política Recursal.pdf"
VECTOR_STORE_PATH = "vector_store.pkl"
EMBEDDING_MODEL = "rufimelo/Legal-BERTimbau-sts-large"

def create_and_save_vector_store():
    """
    Lê o PDF da política, cria os embeddings e salva a base de vetores em um ficheiro .pkl.
    """
    print(f"A ler o documento: {POLICY_DOC_PATH}")
    if not os.path.exists(POLICY_DOC_PATH):
        print(f"ERRO: Ficheiro '{POLICY_DOC_PATH}' não encontrado.")
        return

    # Extrai o texto do PDF
    with fitz.open(POLICY_DOC_PATH) as doc:
        policy_text = "".join(page.get_text() for page in doc)
    
    docs = [Document(page_content=policy_text)]

    # Divide o texto em pedaços (chunks)
    print("A dividir o texto em chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    print(f"Texto dividido em {len(chunks)} chunks.")

    # Carrega o modelo de embeddings (pode demorar um pouco na primeira vez)
    print(f"A carregar o modelo de embeddings: {EMBEDDING_MODEL}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    print("Modelo carregado.")

    # Cria a base de vetores FAISS
    print("A criar a base de dados vetorial (FAISS)...")
    vector_store = FAISS.from_documents(chunks, embedding=embeddings)
    print("Base de dados criada com sucesso.")

    # Salva a base de vetores no ficheiro
    with open(VECTOR_STORE_PATH, "wb") as f:
        pickle.dump(vector_store, f)
    
    print(f"✅ Base de dados vetorial salva com sucesso em: {VECTOR_STORE_PATH}")

if __name__ == "__main__":
    create_and_save_vector_store()