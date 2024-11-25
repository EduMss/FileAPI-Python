from fastapi import FastAPI, Request, Response, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import HTTPException
from fastapi import Form
import os


app = FastAPI()

# Configurações
UPLOAD_FOLDER = '/app/files'  # Altere para o diretório onde você quer armazenar os arquivos
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Garantir que o diretório exista
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Baixar arquivo:
# curl -H "Accept: application/octet-stream" http://localhost:8082/nome_do_arquivo -O

# Visualizar arquivo:
#curl -H "Accept: image/*" http://localhost:8082/nome_do_arquivo

# Rota para acessar e fazer o download ou visualizar arquivos
@app.get("/{filename}")
async def serve_file(filename: str, request: Request):
    file_location = os.path.join(UPLOAD_FOLDER, filename)

    # Verifica se o arquivo existe
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="File not found")

    # Verifica o cabeçalho 'Accept' para decidir se o arquivo deve ser exibido ou baixado
    accept_header = request.headers.get('Accept', '')

    # Se o cabeçalho Accept for diferente de 'application/octet-stream' (que indica que deve forçar o download)
    if 'application/octet-stream' in accept_header:
        # Forçar o download do arquivo
        return FileResponse(file_location, headers={'Content-Disposition': 'attachment; filename=' + filename})

    # Caso contrário, exibe o arquivo (ideal para tipos de imagem, pdf, etc.)
    return FileResponse(file_location)

# Rota para listar todos os arquivos do diretório
@app.get("/", response_class=HTMLResponse)
async def list_files(request: Request):
    # Verifica se o diretório existe
    if not os.path.exists(UPLOAD_FOLDER):
        raise HTTPException(status_code=404, detail="Directory not found")
    
    # Lista os arquivos no diretório
    files = os.listdir(UPLOAD_FOLDER)
    
    # Cria uma página HTML simples para mostrar a lista de arquivos
    html_content = "<h1>Arquivos Disponíveis</h1><ul>"
    for file in files:
        file_url = f"/{file}"  # Cria a URL para acessar cada arquivo
        html_content += f'<li><a href="{file_url}">{file}</a></li>'
    html_content += "</ul>"
    
    return HTMLResponse(content=html_content)

# Rota para mostrar o formulário de upload
@app.get("/Send", response_class=HTMLResponse)
async def upload_form():
    return '''
    <html>
        <body>
            <h1>Upload de Arquivo</h1>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="file"><br>
                <input type="submit" value="Enviar">
            </form>
        </body>
    </html>
    '''

# Rota para processar o upload do arquivo
@app.post("/")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    file_location = os.path.join(UPLOAD_FOLDER, filename)

    # Verifica se o tipo de arquivo é permitido
    if not filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS:
        return {"error": "Tipo de arquivo não permitido"}

    with open(file_location, "wb") as f:
        f.write(file.file.read())

    return {"filename": filename, "file_location": file_location}

@app.delete("/{filename}")
def delete_file(filename: str):
    # Caminho completo do arquivo
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Verifica se o arquivo existe
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Apaga o arquivo
    try:
        file_path.unlink()
        return {"message": f"File '{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")