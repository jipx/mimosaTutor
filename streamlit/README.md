Mimosa Mentor — Streamlit Client

A Streamlit frontend for the Mimosa Mentor project.
It talks to your AWS API Gateway → Lambda → OpenAI backend and gives students:

🎯 Challenge selector (search + filters)

💡 Progressive LabHints (Socratic)

🧩 Vulnerable vs Hardened code with side‑by‑side diff

✅ Verification checklists (unit‑test / code‑review style)

💬 Freeform chat

📥 Export to Markdown (optional if you enabled it)

1) Prereqs

Python 3.9+

An API endpoint fronting your Lambda (HTTP API or Function URL)

Your Custom GPT in OpenAI Studio with the multi‑agent routing + JSON knowledge uploaded

2) Quickstart
# In the client directory:
pip install -r requirements.txt

# Point the client at your API Gateway route:
export API_URL="https://<api-id>.execute-api.<region>.amazonaws.com/prod/chat"
# Optional API Gateway usage-plan key:
# export API_KEY="your-api-key"

# Run the app:
streamlit run app.py


Open the URL Streamlit prints (usually http://localhost:8501
).

Using Streamlit Cloud? Put secrets in Settings → Secrets (see “Configuration” below).

3) Configuration

The client reads configuration from Streamlit secrets (preferred) or environment variables:

Option A — Streamlit secrets (recommended)

Create .streamlit/secrets.toml (or use Streamlit Cloud “Secrets”):

API_URL="https://<api-id>.execute-api.<region>.amazonaws.com/prod/chat"
# API_KEY="your-api-key"  # only if you enabled API Gateway usage plans

Option B — Environment variables
export API_URL="https://<api-id>.execute-api.<region>.amazonaws.com/prod/chat"
export API_KEY="your-api-key"  # optional

4) How it works

Sidebar provides a challenge selector and quick actions:

First/Next Hint → [HintGuide] with stage: orientation|surface|context|defense

Code Compare → [CodeTutor] with action: code_compare

Verify → [Verifier] with action: verify

The client sends a structured prompt string (no schema required).
Your Studio GPT Instructions route the request to the right “agent” and retrieve from uploaded JSON.

Code diff:
When the backend returns two fenced code blocks (first=vulnerable, second=hardened), the client shows them side‑by‑side plus an HTML diff (green add / red remove / yellow change).

5) File structure
.
├─ app.py               # Streamlit UI (selector, hints, code+diff, verify, chat)
├─ requirements.txt     # streamlit, requests
└─ README.md            # this file


(If you added images/exports, you may also have an assets/ folder.)

6) Common tasks
Update the lab list

Open app.py and edit the LABS_META list to match your curriculum (topic, OWASP, week, difficulty).

Customize routing phrases

The helper format_router_message() builds the structured prompt.
If you renamed agents or actions in Studio, tweak it here.

Add Markdown export (optional)

If you enabled the export section, it will bundle the latest hint/code/verify from the chat into a .md download for students.

7) Troubleshooting

“Stream/Download error” when grabbing a ZIP here in ChatGPT

Try right‑click → “Save link as…”, or use the mirror filename.

If downloads are blocked, copy files from the “Dump” message and paste locally.

Blank reply / “Backend returned no reply.”

Confirm API_URL is correct and reachable.

Check Lambda logs (CloudWatch) for errors.

If your Lambda is in a VPC, ensure NAT gateway for outbound internet.

HTTP 403

If you enabled API Gateway usage plans, set API_KEY.

CORS issues (when hosting Streamlit elsewhere)

In API Gateway HTTP API → CORS, allow your Streamlit origin (and POST, content-type, x-api-key).

Slow responses

Increase Lambda timeout to 20–30s.

Keep prompts concise.

Consider smaller/faster model (e.g., gpt-4o-mini) in Lambda.

8) Security checklist

🔒 Never embed your OpenAI key in the Streamlit client. The Lambda should fetch it from Secrets Manager.

🛡️ Use API Gateway usage plans or Cognito/JWT if exposing to students publicly.

🧹 Log minimally (redact PII/tokens).

🧭 Principle of least privilege on IAM (Lambda only reads needed secret, no wildcards).

9) Optional: Docker (for ECS/EC2)

Create Dockerfile (optional):

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV PORT=8501
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]


Build & run:

docker build -t mimosa-streamlit .
docker run -p 8501:8501 -e API_URL="https://<api-id>.execute-api.<region>.amazonaws.com/prod/chat" mimosa-streamlit

10) Links you’ll use

Streamlit: https://streamlit.io

AWS API Gateway HTTP APIs: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html

AWS Lambda: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html