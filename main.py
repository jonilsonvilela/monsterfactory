# main.py
# Versão 3.0 - Arquitetura de Assistentes Modulares

import asyncio
import uuid
import json
import sqlite3
import datetime
import requests
import os
import importlib

from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# --- Configuração da Aplicação e Banco de Dados ---
DB_FILE = "feedback.db"

def init_db():
    # (código do init_db sem alterações)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        form_type TEXT NOT NULL,
        rag_context TEXT,
        original_response TEXT NOT NULL,
        corrected_response TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

app = FastAPI(
    title="Monster Factory API",
    description="O cérebro por trás da fábrica de assistentes jurídicos.",
    version="3.0.0"
)

@app.on_event("startup")
async def startup_event():
    init_db()

# --- Configurações Gerais (CORS, Constantes, Vector Store) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
GENERATOR_SERVICE_URL = "http://generator:8001"

import pickle
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
VECTOR_STORE_PATH = "vector_store.pkl"
if os.path.exists(VECTOR_STORE_PATH):
    with open(VECTOR_STORE_PATH, "rb") as f:
        vector_store = pickle.load(f)
else:
    print("AVISO: vector_store.pkl não encontrado. O RAG não funcionará.")
    vector_store = None

# --- Banco de Dados em Memória para Jobs ---
jobs: Dict[str, Dict[str, Any]] = {}

# --- Modelos Pydantic ---
class Job(BaseModel):
    job_id: str
    status: str
    data: Dict[str, Any] | None = None
class GenerationRequest(BaseModel):
    job_id: str; form_data: Dict[str, Any]; original_data: Dict[str, Any]; rag_context: str | None = None

# --- LÓGICA DO ORQUESTRADOR ---

async def run_assistant_in_background(job_id: str, assistant_name: str, **kwargs):
    """
    Carrega e executa a lógica de um assistente dinamicamente.
    """
    try:
        # Mapeia o nome do assistente para o caminho do módulo
        # Ex: "analise_sumula" -> "assistants.dispensa_assistant.logic"
        # Adicionaremos outros assistentes aqui no futuro
        assistant_map = {
            "analise_sumula": "assistants.dispensa_assistant"
        }
        
        assistant_path = assistant_map.get(assistant_name)
        if not assistant_path:
            raise ModuleNotFoundError(f"Assistente '{assistant_name}' não encontrado.")

        # Importa dinamicamente a lógica do assistente
        logic_module = importlib.import_module(f"{assistant_path}.logic")
        
        # Chama a função principal do assistente (assumimos que seja 'run_analysis')
        # e passa os argumentos necessários
        result = logic_module.run_analysis(
            form_type=kwargs.get("form_type"),
            file_content=kwargs.get("file_content"),
            vector_store=vector_store,
            gemini_url=GEMINI_API_URL
        )

        # Atualiza o job com o resultado
        jobs[job_id].update({
            "status": "ready",
            "data": result["extracted_data"],
            "rag_context": result["rag_context"],
            "form_type": kwargs.get("form_type")
        })
        print(f"Job {job_id} (Assistente: {assistant_name}) concluído com sucesso.")

    except Exception as e:
        print(f"Job {job_id} falhou: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["data"] = {"error": str(e)}


# --- Endpoints da API ---

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à Fábrica de Monstros v3.0!"}

@app.post("/api/v1/analysis", status_code=202)
async def start_analysis(
    file: UploadFile = File(...),
    assistant_type: str = Form(...), # ex: "analise_sumula"
    form_type: str = Form(None)      # ex: "autodispensa"
):
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido.")
    
    job_id = str(uuid.uuid4())
    file_content = await file.read()
    
    # Inicializa o job
    jobs[job_id] = {"status": "processing", "data": None}
    
    # Cria a tarefa em segundo plano, passando os argumentos para o assistente
    asyncio.create_task(run_assistant_in_background(
        job_id=job_id,
        assistant_name=assistant_type,
        form_type=form_type,
        file_content=file_content
    ))
    
    return {"job_id": job_id}


@app.get("/api/v1/analysis/{job_id}/status", response_model=Job)
def get_analysis_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabalho não encontrado.")
    
    response_data = job.get("data")
    if job["status"] == "ready" and response_data:
        response_data["rag_context"] = job.get("rag_context")

    return Job(job_id=job_id, status=job["status"], data=response_data)


@app.post("/api/v1/generate")
def generate_documents(request: GenerationRequest):
    # (Este endpoint não precisa de alterações)
    job = jobs.get(request.job_id)
    if not job or job["status"] != "ready":
        raise HTTPException(status_code=400, detail="O trabalho não está pronto para geração.")

    if request.original_data != request.form_data:
        # (lógica de salvar feedback sem alterações)
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO feedback (timestamp, form_type, rag_context, original_response, corrected_response) VALUES (?, ?, ?, ?, ?)",
                (
                    datetime.datetime.now().isoformat(),
                    job["form_type"],
                    request.rag_context,
                    json.dumps(request.original_data),
                    json.dumps(request.form_data)
                )
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"ERRO ao guardar feedback: {e}")

    payload = {"form_type": job["form_type"], "form_data": request.form_data}
    internal_generator_url = f"{GENERATOR_SERVICE_URL}/api/v1/generate-document"
    public_download_url = "http://127.0.0.1:8001/download"

    try:
        response = requests.post(internal_generator_url, json=payload, timeout=90.0)
        response.raise_for_status()
        result = response.json()
        return {
            "message": result["message"],
            "docx_url": f"{public_download_url}/{result['docx_filename']}",
            "pdf_url": f"{public_download_url}/{result['pdf_filename']}"
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Não foi possível conectar ao serviço de geração: {e}")