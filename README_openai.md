# Mimosa Tutor — OpenAI Studio Setup

This guide explains how to use **Mimosa Tutor Agent** with **OpenAI Studio**, including optional **RAG (Retrieval-Augmented Generation)**.

---

## 1. Sign In to OpenAI Studio
- Go to [OpenAI Studio](https://platform.openai.com/).
- Log in with your OpenAI account.

---

## 2. Create an API Key
1. Navigate to **Dashboard → API Keys**.  
2. Click **Create new secret key**.  
3. Copy the key (`sk-...`).  
   - ⚠️ Store it securely (you won’t see it again).  

---

## 3. Create the Mimosa Tutor Agent
1. In Studio, go to **Assistants** → **Create Assistant**.  
2. Configure:
   - **Name**: `Mimosa Tutor Agent`  
   - **Model**: `gpt-4o-mini` (fast) or `gpt-4` (high accuracy)  
   - **Instructions**:  
     ```
     You are the Mimosa Tutor Agent. 
     - Help students with secure coding labs.
     - Answer based on OWASP Top 10 and Mimosa challenges.
     - Encourage step-by-step reasoning, but never give away full solutions immediately.
     - When RAG documents are available, ground answers using that context first.
     ```
   - **Tools**: Enable **Code Interpreter** if available.  

---

## 4. Add RAG (Retrieval-Augmented Generation)
- In the **Files** tab of the Assistant, upload:
  - **Lab notes** (`.md`, `.txt`, or `.pdf`)  
  - **OWASP/Mimosa challenge docs**  
- These files become the retrieval knowledge base.  
- In **Settings**, enable **File Search** for retrieval.  

---

## 5. Test in Playground
- Open **Playground → Assistants**.  
- Select **Mimosa Tutor Agent**.  
- Try a query:
  ```
  Explain the SQLi Basics Two challenge. 
  Use RAG documents if available.
  ```
- The agent should combine model knowledge + RAG files.  

---

## 6. Manage & Secure
- Rotate API keys periodically.  
- Keep **separate keys** for development and production.  
- Monitor token usage in **Billing → Usage Dashboard**.  

---

✅ With this setup, you now have a **Mimosa Tutor Agent** in OpenAI Studio that supports **RAG-enhanced answers** for secure coding education.
