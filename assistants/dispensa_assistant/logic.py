# assistants/dispensa_assistant/logic.py
# Contém a lógica de negócio principal para o assistente de dispensa.

import fitz  # PyMuPDF
import httpx
import json
from fastapi import HTTPException
from langchain_community.vectorstores import FAISS

# Importa as peças específicas deste assistente
from .schema import get_schema
from .prompt import get_prompt

def run_analysis(form_type: str, file_content: bytes, vector_store: FAISS, gemini_url: str):
    """
    Executa o fluxo completo de análise para o assistente de dispensa.
    Retorna um dicionário com os dados extraídos e o contexto RAG.
    """
    # 1. Extrair texto do PDF
    with fitz.open(stream=file_content, filetype="pdf") as doc:
        decision_text = "".join(page.get_text() for page in doc)
    if not decision_text.strip():
        raise ValueError("O arquivo PDF está vazio ou não contém texto extraível.")

    # 2. Recuperar contexto da base de vetores (RAG)
    query_text = decision_text[:2000]
    relevant_docs = vector_store.similarity_search(query=query_text, k=3)
    rag_context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])

    # 3. Construir o prompt e obter o schema
    prompt_text = get_prompt(decision_text, rag_context)
    json_schema = get_schema(form_type)

    if not prompt_text or not json_schema:
        raise ValueError(f"Não foi possível encontrar prompt ou schema para o formulário '{form_type}'.")

    # 4. Chamar a API do modelo de linguagem (LLM)
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {"type": "OBJECT", "properties": json_schema}
        }
    }
    
    response = httpx.post(gemini_url, json=payload, timeout=120.0)
    response.raise_for_status()
    
    result = response.json()
    if 'candidates' in result and result['candidates']:
        try:
            extracted_text = result['candidates'][0]['content']['parts'][0]['text']
            extracted_data = json.loads(extracted_text)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Dados inválidos retornados pela API Gemini: {e.msg}"
            )
        return {
            "extracted_data": extracted_data,
            "rag_context": rag_context
        }
    else:
        raise ValueError(f"Resposta inesperada da API Gemini: {result}")
