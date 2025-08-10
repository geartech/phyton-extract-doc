# Base estável com Python 3.12
FROM python:3.12-bookworm

# Diretório de trabalho dentro do container
WORKDIR /app

# Configs: não gerar .pyc e logs saírem direto no stdout
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Instala dependências do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY app ./app

# Expõe a porta da API
EXPOSE 8000

# Comando para subir a API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
