import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import chromadb
import boto3
from langchain_aws.embeddings import BedrockEmbeddings

load_dotenv()
REGION = os.getenv("AWS_REGION", "us-east-1")
#amazon.titan-embed-text-v2:0
EMBED_MODEL_ID = os.getenv("EMBED_MODEL_ID", "amazon.nova-micro-v1:0")
CHROMA_DIR = os.getenv("CHROMA_DIR", "index/chroma")
client = None
col = None
embeddings = None
@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict]:
    global client, col, embeddings
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=REGION)
    embeddings = BedrockEmbeddings(client=bedrock_runtime,model_id=EMBED_MODEL_ID)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_or_create_collection("career_kb")
    try:
        yield {"embeddings": embeddings, "col": col}
    finally:
        pass

mcp = FastMCP(name="Student Career Tools",lifespan=lifespan, json_response=True)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two integer numbers together."""
    return a + b


@mcp.tool()
def search_career_kb(query: str, top_k: int = 5):
    """RAG retrieval: return top chunks with source citations."""
    qvec = embeddings.embed_query(query)
    res = col.query(query_embeddings=[qvec], n_results=top_k,
    include=["documents","metadatas","distances"])
    out = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        out.append({
    "text": doc,
    "source": meta.get("source"),
    "chunk_id": meta.get("chunk_id"),
    "score": float(dist),
    })
    return {"results": out}

@mcp.prompt()
def outreach_email_prompt(student_context: str, target_role: str, company: str):
    return f"""
Write a concise networking email for a student.
Student context: {student_context}
Target role: {target_role}
Company: {company}
Structure:
- Subject line
- 1 line intro
- 1 line why them
- 1 line ask (15 min chat)
- 2 time windows + thanks
""".strip()
@mcp.resource("career://playbook/outreach")
def outreach_playbook():
    return "Use short subject, specific why, clear ask, and gratitude."
#if __name__ == "__main__":
    # MCP SDK supports streamable-http transport.
    #mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
 #   mcp.settings.host = "127.0.0.1"
  #  mcp.settings.port = 8000
   # mcp.run(transport="streamable-http")
