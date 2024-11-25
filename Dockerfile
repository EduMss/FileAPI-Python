# Usando uma imagem base do Python
FROM python:3.11-slim

# Definindo o diretório de trabalho no container
WORKDIR /app

# Copiando o arquivo de dependências para o container
COPY requirements.txt .

# Instalando as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiando o restante dos arquivos do projeto
COPY ./app /app

# Expondo a porta 8000 (padrão do FastAPI)
EXPOSE 8082

# Comando para rodar a aplicação com uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]