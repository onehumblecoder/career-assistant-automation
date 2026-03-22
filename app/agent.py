import os, json, requests
from dotenv import load_dotenv
import asyncio
import boto3
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import SystemMessage, HumanMessage
from fastmcp import Client
load_dotenv()
REGION = os.getenv("AWS_REGION", "us-east-1")
CHAT_MODEL_ID = os.getenv("CHAT_MODEL_ID", "amazon.nova-lite-v1:0")
MCP_BASE = "http://127.0.0.1:8000/mcp/" # streamable-http mount path
SYSTEM = """You are a Student Career Assistant.

Rules:
1) Always retrieve context by calling tool search_career_kb before giving guidance.
2) Ground recommendations in retrieved content cite source + chunk_id.
3) Provide: Answer, Citations, Next Actions (3 bullets).
"""
client = Client(MCP_BASE)
async def call_tool():
    async with client:
        bedrock_runtime = boto3.client("bedrock-runtime", region_name=REGION)
        llm = ChatBedrockConverse(client=bedrock_runtime, model_id=CHAT_MODEL_ID,
                                  temperature=0.2)
        question = input("Ask a career question: ").strip()
        tool_res = await client.call_tool("search_career_kb", {"query": question, "top_k": 5})
        context = tool_res.data
        msgs = [
            SystemMessage(content=SYSTEM),
            HumanMessage(content=f"Question:\n{question}\n\nRetrieved context (JSON):\n{context}")]
        resp = llm.invoke(msgs)
        print("\n=== Assistant ===\n")
        print(resp.content)


asyncio.run(call_tool())

