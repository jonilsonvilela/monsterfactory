🔥 Monster Factory 🔥
Sua fábrica de assistentes inteligentes para automação de tarefas jurídicas.
📖 Visão Geral
Monster Factory é uma plataforma de automação inteligente construída para o setor jurídico. O seu core consiste numa arquitetura de "fábrica" projetada para criar, gerir e executar "monstros": assistentes de IA altamente especializados, cada um treinado para uma tarefa jurídica específica.

Utilizando um poderoso modelo de linguagem (Google Gemini) e a técnica de Geração Aumentada por Recuperação (RAG), a plataforma analisa documentos complexos, como decisões judiciais em .pdf, e automatiza processos repetitivos, como o preenchimento de súmulas, a geração de relatórios e, futuramente, a elaboração de pareceres e comunicações.

O projeto foi desenhado com base em dois pilares: modularidade e escalabilidade. A arquitetura de assistentes isolados permite que novos "monstros" sejam desenvolvidos e integrados à fábrica sem qualquer alteração na infraestrutura central.

✨ Funcionalidades Principais
Arquitetura de Fábrica de Monstros: Desenvolva e adicione novos assistentes de IA como módulos independentes. Cada "monstro" tem a sua própria lógica, prompts e schemas, garantindo um isolamento completo.

Análise Inteligente com RAG: Faça o upload de documentos .pdf e o sistema irá contextualizar a análise utilizando uma base de conhecimento vetorial (RAG) construída a partir de documentos internos, como a "Política Recursal".

Preenchimento Automático de Formulários: A IA preenche formulários web complexos com os dados extraídos dos documentos, minimizando o trabalho manual.

Validação Humana e Feedback Loop: Permite que o utilizador revise e corrija os dados extraídos. Cada correção é armazenada numa base de dados SQLite (feedback.db), criando um ciclo de feedback valioso para o re-treino e aprimoramento contínuo dos modelos.

Geração de Documentos: Após a validação humana, o sistema gera automaticamente documentos .docx e .pdf a partir de templates pré-definidos.

🏗️ Arquitetura do Sistema
O projeto opera sobre uma arquitetura de microsserviços orquestrada pelo Docker Compose, garantindo que cada componente funcione de forma isolada e eficiente.

1. Frontend (index.html):
Uma Single-Page Application (SPA) construída com HTML5, TailwindCSS e JavaScript puro. É a interface do utilizador, por onde as tarefas são iniciadas.

2. Orquestrador Principal / API (main.py):
O coração da fábrica. Este serviço FastAPI não contém lógica de negócio dos assistentes. As suas responsabilidades são:

Receber as requisições da API.

Gerir o upload de ficheiros.

Identificar qual "monstro" (assistente) deve ser ativado com base no assistant_type.

Utilizar importlib para carregar dinamicamente o módulo do assistente solicitado.

Executar a lógica do assistente em segundo plano (asyncio).

Gerir o estado dos jobs e responder aos pedidos de status.

Interagir com a base de dados de feedback.

3. Assistentes Modulares (assistants/):
Esta é a "linha de produção" da fábrica. Cada subdiretório é um "monstro" autocontido.

Exemplo: assistants/dispensa_assistant/:

logic.py: Contém todo o fluxo de trabalho: extração de texto do PDF, consulta à base de vetores (RAG) e a chamada à API do LLM.

prompt.py: Define as instruções exatas ("personalidade" e "ordens") que são dadas à IA.

schema.py: Define o formato JSON exato que a IA deve retornar como resposta.

4. Serviço de Geração (generator_service.py):
Um microsserviço FastAPI especializado. Ele recebe uma estrutura de dados JSON e a utiliza para preencher um template .docx (docxtpl) e depois o converte para .pdf (usando LibreOffice), disponibilizando ambos para download.

5. Serviço de Treinamento (training_service.py):
Outro microsserviço FastAPI que serve um propósito único: expor um endpoint que consulta a base de dados feedback.db e retorna os dados formatados em JSONL, prontos para serem usados em processos de fine-tuning de modelos de linguagem.

🛠️ Stack Tecnológica
Backend: Python 3.11, FastAPI

Frontend: HTML5, TailwindCSS, JavaScript (Vanilla)

IA & RAG: LangChain, Google Gemini, HuggingFace Embeddings (rufimelo/Legal-BERTimbau-sts-large), Faiss (Vector Store)

Geração de Documentos: docxtpl, LibreOffice (via Docker)

Base de Dados (Feedback): SQLite

Infraestrutura: Docker, Docker Compose

🚀 Guia de Instalação e Execução
Para pôr a fábrica a funcionar, é necessário ter o Docker e o Docker Compose instalados.

Passo 1: Clonar o Repositório

Bash

git clone https://github.com/seu-usuario/monster-factory.git
cd monster-factory
Passo 2: Configurar a Chave da API
Crie um ficheiro .env na raiz do projeto e adicione a sua chave da API do Google Gemini.

Snippet de código

# .env
GEMINI_API_KEY="SUA_CHAVE_DE_API_AQUI"
Passo 3: Adicionar a Base de Conhecimento
Coloque o documento que servirá de base para o sistema RAG na raiz do projeto, com o nome Política Recursal.pdf.

Passo 4: Construir a Base Vetorial (Passo Crítico)
A IA precisa que o conhecimento do PDF seja convertido para um formato que ela entenda (vetores). Criámos um script para automatizar isto.

Primeiro, inicie os serviços uma vez para construir as imagens Docker com todas as dependências:

Bash

docker-compose up --build -d
Em seguida, execute o script de criação da base de vetores dentro do contentor da api:

Bash

docker-compose exec api python create_vector_store.py
Este comando irá criar o ficheiro vector_store.pkl na raiz do seu projeto.

Passo 5: Iniciar a Fábrica
Agora, com tudo configurado, inicie todos os serviços em modo interativo para poder ver os logs:

Bash

docker-compose up
Dica: Se quiser que os serviços rodem em segundo plano, use docker-compose up -d.

Passo 6: Aceder à Interface
Abra o seu navegador e vá para o endereço do serviço da API:
➡️ http://127.0.0.1:8000/
O index.html deve ser servido automaticamente.

🔬 Como Desenvolver um Novo "Monstro"
A arquitetura foi desenhada para tornar a criação de novos assistentes um processo simples e padronizado.

Crie a Pasta do Assistente:
Dentro da pasta assistants/, crie um novo diretório para o seu monstro. Ex: assistants/email_assistant/.

Crie os Módulos de Lógica:
Dentro da nova pasta, crie os três ficheiros essenciais:

schema.py: Defina a estrutura de dados que a sua nova IA deve preencher.

prompt.py: Escreva as instruções detalhadas (o prompt) para a nova tarefa.

logic.py: Crie a função principal (ex: run_email_generation) que executa o fluxo (pode ou não usar RAG).

Registe o Novo Monstro:
No ficheiro main.py, adicione uma entrada no dicionário assistant_map para que o orquestrador saiba como chamar a sua nova criação.

Python

# main.py
assistant_map = {
    "analise_sumula": "assistants.dispensa_assistant",
    "gerar_email": "assistents.email_assistant" # Novo monstro
}
Ajuste a Interface:
Se necessário, adicione novas opções no index.html para que os utilizadores possam selecionar e interagir com o novo assistente.