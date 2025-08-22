import os
import boto3
from fastapi import FastAPI
from pydantic import BaseModel
from mangum import Mangum
from openai import OpenAI

# Fetch OpenAI API key from Secrets Manager at cold start
SECRET_NAME = os.getenv("OPENAI_SECRET_NAME", "OPENAI_API_KEY")
OPENAI_API_KEY = None
try:
    sm = boto3.client("secretsmanager")
    val = sm.get_secret_value(SecretId=SECRET_NAME)
    OPENAI_API_KEY = val.get("SecretString")
except Exception as e:
    OPENAI_API_KEY = None

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = os.getenv("MODEL", "gpt-5")

app = FastAPI(title="Mimosa Backend")

class ChatIn(BaseModel):
    message: str
    use_rag: bool = False
    vector_store_id: str | None = None
    temperature: float = 0.2
    model: str | None = None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat")
def chat(body: ChatIn):
    tools = []
    if body.use_rag and body.vector_store_id:
        tools.append({"type": "file_search", "vector_store_ids": [body.vector_store_id]})
    system = (
        "You are a Mimosa security tutor. Give hints first, then minimal solution "
        "and remediation. Ground answers in attached notes when file_search is enabled."
    )
    try:
        resp = client.responses.create(
            model=body.model or MODEL,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": body.message},
            ],
            tools=tools or None,
            temperature=body.temperature,
        )
        out = []
        for item in getattr(resp, "output", []) or []:
            if item.type == "message":
                for c in item.content:
                    if c.type == "output_text":
                        out.append(c.text)
        return {"answer": "\n".join(out) if out else "(no text output)",
                "model": body.model or MODEL,
                "tool_used": bool(tools)}
    except Exception as e:
        return {"error": str(e)}

handler = Mangum(app)
