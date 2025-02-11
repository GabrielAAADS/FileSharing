import socket
import os
import threading
import shutil

from fastapi import FastAPI, HTTPException, status, File, UploadFile
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Permite chamadas apenas do frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Permite todos os headers
)

class DistributedDownloadSource(BaseModel):
    ip: str
    port: int

class DistributedDownloadRequest(BaseModel):
    filename: str
    filesize: int
    sources: List[DistributedDownloadSource]

client_state = {
    "connected": False,
    "client_socket": None,
    "server_ip": None,
    "client_port": None,
    "file_server_thread": None,
    "lock": threading.Lock(),
    "public_folder": "C:\\public"
}

class ConnectRequest(BaseModel):
    server_ip: str
    client_ip: str = "0.0.0.0"
    client_port: int = 1235
    public_folder: str = "C:\\public"

class FileRequest(BaseModel):
    filename: str
    size: int | None = None

class DownloadRequest(BaseModel):
    ip: str
    port: int
    filename: str
    offset_start: int = 0
    offset_end: int | None = None

@app.post("/download/distributed")
async def distributed_download(req: DistributedDownloadRequest):
    n_sources = len(req.sources)
    if n_sources == 0:
        raise HTTPException(status_code=400, detail="Nenhuma fonte selecionada")
    
    total_size = req.filesize
    segment_size = total_size // n_sources
    remainder = total_size % n_sources

    destination = os.path.join(client_state["public_folder"], req.filename)
    results = [None] * n_sources
    threads = []
    current_offset = 0

    for i, source in enumerate(req.sources):
        start = current_offset

        if i == n_sources - 1:
            end = start + segment_size + remainder
        else:
            end = start + segment_size
        current_offset = end

        t = threading.Thread(
            target=download_segment_thread,
            args=(source.ip, source.port, req.filename, start, end, results, i)
        )
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

    if any(segment is None for segment in results):
        raise HTTPException(
            status_code=500,
            detail="Falha ao baixar um ou mais segmentos."
        )
    
    with open(destination, "wb") as f:
        for segment in results:
            f.write(segment)

    return {
        "message": "Download distribuído concluído com sucesso",
        "path": destination,
        "bytes_received": os.path.getsize(destination)
    }

@app.get("/files")
async def get_local_files():
    validate_not_connected()

    try:
        files = []
        public_folder = client_state["public_folder"]
        for filename in os.listdir(public_folder):
            filepath = os.path.join(public_folder, filename)
            files.append({
                "filename": filename,
                "size": os.path.getsize(filepath)
            })
        return {"files": files}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/connect")
async def connect(request: ConnectRequest):

    validate_already_connected()
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((request.server_ip, 1234))

        client_socket.send(f"JOIN {request.client_ip} {request.client_port}\n".encode("utf-8"))
        response = client_socket.recv(1024).decode("utf-8").strip()
        
        if "CONFIRMJOIN" not in response:
            raise Exception("Resposta inválida do servidor")

        with client_state["lock"]:
            client_state.update({
                "connected": True,
                "client_socket": client_socket,
                "server_ip": request.server_ip,
                "client_port": request.client_port,
                "public_folder": request.public_folder
            })

        file_server_thread = threading.Thread(
            target=start_file_server,
            args=(request.public_folder, request.client_port),
            daemon=True
        )
        file_server_thread.start()
        client_state["file_server_thread"] = file_server_thread

        try:
            await refresh_files_sync()
        except Exception as e:
            print(f"Aviso: Falha ao atualizar arquivos - {str(e)}")

        return {"message": "Conexão estabelecida com sucesso"}

    except Exception as e:
        if client_socket:
            client_socket.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
  
# @app.post("/connect")
# async def connect(request: ConnectRequest):

#         validate_already_connected()

#         try:
#             client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             client_socket.settimeout(10)
#             client_socket.connect((request.server_ip, 1234))
            
#             # client_ip = socket.gethostbyname(socket.gethostname())

#             join_command = f"JOIN {request.client_ip}\n"

#             # client_socket.send(join_cmd.encode())

#             client_state.update({
#                 "connected": False,
#                 "client_socket": client_socket,
#                 "server_ip": request.server_ip,
#                 "client_port": request.client_port,
#                 "public_folder": request.public_folder
#             })

#             response_server = send_server_command(join_command)
            
#             # response = client_socket.recv(1024).decode()

#             if "CONFIRMJOIN" not in response_server:
#                 client_state.update({
#                     "connected": False,
#                     "client_socket": None,
#                     "server_ip": None,
#                     "client_port": None,
#                     "lock": threading.Lock(),
#                     "public_folder": "C:\public"
#                 })
#                 raise Exception("Falha ao conectar ao servidor")
            
#             client_state.update({
#                 "connected": True,
#                 "client_socket": client_socket,
#                 "server_ip": request.server_ip,
#                 "client_port": request.client_port,
#                 "public_folder": request.public_folder
#             })

#             client_state["file_server_thread"] = threading.Thread(
#                 target=start_file_server,
#                 args=(request.public_folder, request.client_port),
#                 daemon=True
#             )
#             client_state["file_server_thread"].start()

#             # Retornar também retorno desse método 
#             response_refresh = refresh_files()

#             return {"message": "Conectado ao servidor", 
#                     "response_server": response_server,
#                     "response_refresh": response_refresh}

#         except Exception as e:
#             if client_socket:
#                 client_socket.close()
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=str(e)
#             )
        
@app.get("/search")
async def search(pattern: str = ""):
    validate_not_connected()

    try:
        response = send_server_command(f"SEARCH {pattern}")
        results = []
        
        for line in response.split('\n'):
            if line.startswith("FILE"):
                parts = line.split()
                results.append({
                    "filename": parts[1],
                    "ip": parts[2],
                    "port": int(parts[3]),
                    "size": int(parts[4])
                })
        
        return {"results": results}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@app.post("/download")
async def download_file_endpoint(request: DownloadRequest):

    validate_not_connected()

    try:
        os.makedirs(client_state["public_folder"], exist_ok=True)
        destination = os.path.join(client_state["public_folder"], request.filename)
    
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
            peer_socket.settimeout(10)
            peer_socket.connect((request.ip, request.port))
            
            get_cmd = f"GET {request.filename}"
            if request.offset_start is not None:
                get_cmd += f" {request.offset_start}"
            if request.offset_end is not None:
                get_cmd += f" {request.offset_end}"
            get_cmd += "\n"
            
            response = peer_socket.send(get_cmd.encode("utf-8"))

            data = peer_socket.recv(4096)
            
            if data.startswith(b"ERROR"):
                error_msg = data.decode("utf-8").strip()
                raise HTTPException(
                    status_code=404,
                    detail=f"Erro no download: {error_msg}"
                )

            with open(destination, "wb") as f:
                f.write(data)
                while True:
                    data = peer_socket.recv(4096)
                    if not data:
                        break
                    f.write(data)
                    
        return {
            "message": "Download concluído com sucesso",
            "path": destination,
            "bytes_received": os.path.getsize(destination),
            "response": response
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/leave")
async def leave():
    validate_not_connected()

    try:
        response_server = send_server_command("LEAVE")
        
        if "CONFIRMLEAVE" not in response_server:
            raise Exception("Erro ao desconectar")
    
        client_state["client_socket"].close()
        client_state.update({
            "connected": False,
            "client_socket": None,
            "server_ip": None,
            "client_port": None,
            "public_folder": None,
            "file_server_thread": None
        })
        
        return {"message": "Desconectado do servidor com sucesso", response_server: response_server}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
@app.post("/refresh")
async def refresh_files_sync(override: bool = False) -> list:
    validate_not_connected()

    responses = []
    public_folder = client_state["public_folder"]
    try:
        for filename in os.listdir(public_folder):
            filepath = os.path.join(public_folder, filename)
            size = os.path.getsize(filepath)
            command = "CREATEFILE OVERRIDE" if override else "CREATEFILE"
            command += f" {filename} {size}"
            response_server = send_server_command(command)
            if "ERROR" in response_server:
                responses.append(f"Arquivo {filename}: {response_server}")
            else:
                responses.append(f"Arquivo {filename}: OK")
        return responses
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    validate_not_connected()
    
    public_folder = client_state["public_folder"]
    destination = os.path.join(public_folder, file.filename)

    if os.path.exists(destination):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo com esse nome já existe."
        )
    
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(destination)
        
        command = f"CREATEFILE ADD {file.filename} {file_size}"
        response_server = send_server_command(command)
        
        await refresh_files_sync()
        
        return {
            "message": "Arquivo enviado com sucesso",
            "filename": file.filename,
            "size": file_size,
            "response_server": response_server
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/remove")
async def remove_file(filename: str):
    validate_not_connected()
    
    public_folder = client_state["public_folder"]
    destination = os.path.join(public_folder, filename)
    
    if not os.path.exists(destination):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    try:
        os.remove(destination)
        
        command = f"DELETEFILE {filename}"
        response_server = send_server_command(command)
        
        await refresh_files_sync()
        
        return {
            "message": "Arquivo removido com sucesso",
            "filename": filename,
            "response_server": response_server
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
def download_segment_thread(ip: str, port: int, filename: str, offset_start: int, offset_end: int, results: list, index: int):
    segment_data = b""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
        try:
            peer_socket.settimeout(10)
            peer_socket.connect((ip, port))

            get_cmd = f"GET {filename} {offset_start} {offset_end}\n"
            peer_socket.send(get_cmd.encode("utf-8"))

            while True:
                data = peer_socket.recv(4096)
                if not data:
                    break
                segment_data += data
        except Exception as e:
            segment_data = None
            print(e)
        results[index] = segment_data

def send_server_command(command: str, expect_confirmation: bool = True):
    if command.startswith("JOIN"):
        validate_already_connected()
    else:
        validate_not_connected()

    try:
        client_socket = client_state["client_socket"]
        client_socket.send(f"{command}\n".encode("utf-8"))
        
        if expect_confirmation:
            response = client_socket.recv(1024).decode("utf-8").strip()
            return response
        return None

    except socket.error as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erro de comunicação com o servidor: {str(e)}"
        )

def validate_already_connected():
        with client_state["lock"]:
            if client_state["connected"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já conectado ao servidor"
                )

def validate_not_connected():
        with client_state["lock"]:
            if not client_state["connected"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não conectado ao servidor"
                )

def start_file_server(public_folder, client_port):
    print(f"Servidor de arquivos escutando na porta {client_port}...")

    file_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    file_server_socket.bind(("0.0.0.0", client_port))
    file_server_socket.listen(5)

    print(f"Servidor de arquivos escutando na porta {client_port}...")

    def handle_request(conn, addr):
        try:
            conn.settimeout(10)
            request = conn.recv(1024).decode("utf-8").strip()
            print(f"Conexão de {addr} - Solicitação: {request}")
            
            if request.startswith("GET"):
                parts = request.split()
                filename = parts[1]
                offset_start = int(parts[2]) if len(parts) > 2 else 0
                offset_end = int(parts[3]) if len(parts) > 3 else None

                filepath = os.path.join(public_folder, filename)
                
                if not os.path.exists(filepath):
                    conn.send("ERROR File not found\n".encode())
                    conn.close()
                    return
                
                try:
                    with open(filepath, "rb") as f:
                        # file_size = os.path.getsize(filepath)
                        
                        # # Validar offsets
                        # offset_start = max(0, min(offset_start, file_size))
                        # if offset_end:
                        #     offset_end = max(offset_start, min(offset_end, file_size))
                        # else:
                        #     offset_end = file_size
                        
                        f.seek(offset_start)
                        data = f.read(offset_end - offset_start) if offset_end else f.read()
                        conn.sendall(data)
                except FileNotFoundError:
                    conn.send("ERROR File not found\n".encode())
                except Exception as e:
                    print(f"Erro ao ler o arquivo: {str(e)}")
                    conn.send("ERROR Internal server error\n".encode())

        except Exception as e:
            print(f"Erro: {str(e)}")
        finally:
            conn.close()

    while True:
        client_conn, client_addr = file_server_socket.accept()
        threading.Thread(target=handle_request, args=(client_conn, client_addr)).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)