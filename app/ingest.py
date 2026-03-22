import os, glob
from dotenv import load_dotenv
import boto3

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_core.documents import Document
import chromadb


load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
EMBED_MODEL_ID = os.getenv("EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
KB_DIR = os.getenv("KB_DIR", "data/kb")
CHROMA_DIR = os.getenv("CHROMA_DIR", "index/chroma")

def load_markdown_docs(folder: str):
    docs = []
    for path in glob.glob(os.path.join(folder, "**/*.md"), recursive=True):
        with open(path, "r", encoding="utf-8") as f:
            docs.append(Document(page_content=f.read(), metadata={"source": path}))
    return docs

def main():
    bedrock_runtime1 = boto3.client("bedrock-runtime", region_name=REGION)
    # Titan embeddings v2 model ID and characteristics are documented by AWS. [1](https://deepwiki.com/langchain-ai/langchain-aws/5.1-amazonknowledgebasesretriever)
    embeddings = BedrockEmbeddings(
        client=bedrock_runtime1,
        model_id=EMBED_MODEL_ID,
    )

    docs = load_markdown_docs(KB_DIR)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_or_create_collection("career_kb")

    texts = [c.page_content for c in chunks]
    metas = [c.metadata | {"chunk_id": i} for i, c in enumerate(chunks)]
    ids = [f"chunk-{i}" for i in range(len(chunks))]

    vectors = embeddings.embed_documents(texts)
    col.add(documents=texts, metadatas=metas, ids=ids, embeddings=vectors)

    print(f"✅ Ingested {len(chunks)} chunks into Chroma at {CHROMA_DIR}")

if __name__ == "__main__":
 main()
