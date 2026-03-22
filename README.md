# career-assistant-automation# Student Career Assistant (Agentic AI Prototype)
**AWS Bedrock + RAG (ChromaDB) + MCP (FastMCP, stdio) + Async Tool Calls**

career-assistant-prototype/
  README.md
  .env.example
  requirements.txt
  data/
    kb/                       # PDFs/markdown/csv career content
    student_profiles/         # optional: json student profiles
  index/
    faiss_index/              # persisted vector index
  app/
    ingest.py                 # chunk + embed + build FAISS
    mcp_server.py             # MCP tools/resources/prompts
    agent_langchain.py        # single-agent orchestration
    agent_autogen.py          # optional multi-agent
    schemas.py                # pydantic schemas for tool I/O

  AWS Account
 ├─ Amazon Bedrock
 │   ├─ Chat Model (Nova Lite / Claude / Llama)
 │   └─ Titan Text Embeddings v2
 │
 ├─ EC2 OR AWS CloudShell (prototype runtime)
 │   ├─ Python app (LangChain orchestrator)
 │   ├─ MCP Server (career tools)
 │   └─ FAISS vector index (local)
 │
 └─ IAM
     └─ Minimal role for Bedrock Runtime

This repo contains a working prototype of an **agentic Student Career Assistant** that:
- Grounds responses using **RAG** over a curated career knowledge base
- Stores and queries embeddings using **ChromaDB**
- Exposes retrieval + helper actions as **MCP tools** using **FastMCP**
- Runs locally using a **Python virtual environment**
- Uses **async calls** to connect the agent to MCP tools
- Uses **Amazon Bedrock** as the LLM + embeddings provider

---

## ✅ What’s Working (Prototype Capabilities)

- Career exploration Q&A grounded in KB (RAG)
- Resume bullet generation (STAR-style prompts)
- Outreach/networking email drafting
- Tool-based retrieval via MCP (no fragile HTTP negotiation)
- Async orchestration (agent calls MCP tool → uses retrieved context → calls Bedrock)

---

## Architecture Overview

1. ChromaDB locally for vector storage (avoids FAISS issues)
2. MCP locally to expose “career tools” (search KB, outreach templates, etc.) using standard MCP primitives: tools/resources/prompts [pypi.org]
3. LangChain to call Bedrock via ChatBedrockConverse (Converse API integration) [docs.aws.amazon.com]

**Agent (Orchestrator)**
1. Receives the student’s question
2. Calls MCP tool `search_career_kb` (async) to retrieve relevant KB chunks (RAG)
3. Sends question + retrieved context to a Bedrock chat model
4. Returns: **Answer + Citations + Next Actions**

**MCP Server (FastMCP)**
- Exposes tools/resources/prompts (e.g., `search_career_kb`, prompt templates)
- Runs via **stdio transport**
- Is started from the command line
- Uses ChromaDB to perform similarity search

---

## Prerequisites

### Local (Mac)
- Python **3.10+** (3.11 recommended)
- Git

### AWS
- AWS account with **Amazon Bedrock** enabled
- Model access enabled for:
  - A **chat model** (e.g., `amazon.nova-lite-v1:0` or whichever you enabled)
  - **Embeddings**: `amazon.titan-embed-text-v2:0`

> If model access isn’t granted, Bedrock calls will fail.

## Setup (Mac Command Line)
aws configure get region
### 1) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip

**Install Dependencies**
pip install boto3 langchain langchain-core langchain-aws mcp[cli] chromadb python-dotenv
