# Dockerfile para QInvest Risk Score API
# Imagem de produção otimizada para FastAPI

# Usar imagem Python slim oficial
FROM python:3.11-slim

# Definir metadados da imagem
LABEL maintainer="QInvest Team"
LABEL description="QInvest Risk Score API - Sistema de avaliação de risco empresarial"
LABEL version="1.0.0"

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Criar usuário não-root para segurança
RUN groupadd -r qinvest && useradd -r -g qinvest qinvest

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de dependências primeiro (otimização de cache)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn uvicorn[standard]

# Criar diretórios necessários
RUN mkdir -p /app/models/trained_models /app/data /app/logs \
    && chown -R qinvest:qinvest /app

# Copiar código da aplicação
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/

# Dar permissões adequadas
RUN chown -R qinvest:qinvest /app

# Mudar para usuário não-root
USER qinvest

# Expor porta
EXPOSE 8000

# Configurar health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--access-log"]
