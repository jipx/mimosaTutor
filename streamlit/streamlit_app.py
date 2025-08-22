import os, requests
from typing import Dict, Any
import streamlit as st

st.set_page_config(page_title="Mimosa Tutor (API Gateway)", page_icon="🛡️", layout="wide")
st.title("🛡️ Mimosa Tutor — Streamlit Client")
st.caption("This UI talks to your AWS API Gateway + Lambda backend.")

st.sidebar.header("Backend")
api_base = st.sidebar.text_input("API Base URL", value=os.getenv("MIMOSA_API_BASE","https://YOUR-HTTP-API-ID.execute-api.YOUR-REGION.amazonaws.com"))
vector_store_id = st.sidebar.text_input("Vector Store ID (optional for RAG)", value=os.getenv("MIMOSA_VECTOR_STORE_ID",""))
use_rag = st.sidebar.checkbox("Enable RAG (File Search)", value=False)
model = st.sidebar.text_input("Model (optional; server default OK)", value="")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.1)

col1, col2 = st.sidebar.columns(2)
if col1.button("Check health"):
    try:
        r = requests.get(f"{api_base.rstrip('/')}/health", timeout=15)
        st.sidebar.success(f"Health: {r.status_code} {r.json()}")
    except Exception as e:
        st.sidebar.error(f"Health failed: {e}")
if col2.button("Clear chat"):
    st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("### 🔎 Quick Prompts")
cols = st.columns(3)
quick = {
    "Bad Teacher (A01)": "Walk me through Bad Teacher step-by-step. Give hints first, then minimal solution and remediation.",
    "Cookie Muncher (A03)": "Test Cookie Muncher for XSS safely. Give hints first, show a tiny vulnerable vs hardened snippet.",
    "Verbose Login (A07)": "How to detect verbose login messages leaking info? Give hints, then remediation checklist."
}
for i, (k, v) in enumerate(quick.items()):
    with cols[i % 3]:
        if st.button(k):
            st.session_state.messages.append({"role":"user","content": v})

st.markdown("---")
st.markdown("### 💬 Chat")
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_text = st.chat_input("Ask about a challenge or use quick prompts above…")
if user_text:
    st.session_state.messages.append({"role":"user","content": user_text})

def call_backend(text: str) -> str:
    body: Dict[str, Any] = {
        "message": text,
        "use_rag": bool(use_rag),
        "vector_store_id": vector_store_id.strip() or None,
        "temperature": float(temperature),
    }
    if model.strip():
        body["model"] = model.strip()
    try:
        r = requests.post(f"{api_base.rstrip('/')}/chat", json=body, timeout=90)
        if r.status_code == 200:
            data = r.json()
            return data.get("answer") or "_(no text output)_"
        else:
            return f":warning: {r.status_code} — {r.text}"
    except Exception as e:
        return f":warning: Request error: `{e}`"

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            answer = call_backend(st.session_state.messages[-1]["content"])
        st.markdown(answer)
    st.session_state.messages.append({"role":"assistant","content": answer})
