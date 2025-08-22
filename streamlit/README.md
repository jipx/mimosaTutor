# Streamlit Client (for API Gateway + Lambda Backend)

## Run locally
```bash
pip install -r requirements.txt
export MIMOSA_API_BASE="https://<api-id>.execute-api.<region>.amazonaws.com"
streamlit run streamlit_app.py
```

## Docker
```bash
docker build -t mimosa-streamlit .
docker run -p 8501:8501 -e MIMOSA_API_BASE="https://<your-api>" mimosa-streamlit
```
