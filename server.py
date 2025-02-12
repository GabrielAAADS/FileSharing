import socket
import threading

all_files = {}  

def handle_client(client_socket, client_address):

    client_key = None
    print(f"[+] Nova conexão de {client_address}")

    try:
        while True:
            try:
                message = client_socket.recv(1024).decode("utf-8").strip()
                
                if not message:
                    break
                print(f"Mensagem recebida de {client_address}: {message}")

                if message.startswith("JOIN"):
                    tokens = message.split()
                    if len(tokens) < 3:
                        client_socket.send("ERROR Invalid JOIN command\n".encode("utf-8"))
                        continue
                    client_key = f"{tokens[1]}:{tokens[2]}"
                    all_files[client_key] = []
                    client_socket.send("CONFIRMJOIN\n".encode("utf-8"))
                    print("JOIN")
                    print(all_files)

                # if message.startswith("JOIN"):
                #     ip_address = message.split()[1]
                #     all_files[ip_address] = []
                #     client_socket.send("CONFIRMJOIN\n".encode("utf-8"))
                #     print("JOIN")
                #     print(all_files)

                # Melhoria: confirmar envio dos arquivos ao iniciar conexão (FRONT)

                elif message.startswith("CREATEFILE OVERRIDE"):
                    _, _, filename, size = message.split()
                    size = int(size)
                    
                    all_files[client_key] = [f for f in all_files[client_key] if f["filename"] != filename]
                    all_files[client_key].append({"filename": filename, "size": size})
                    client_socket.send(f"CONFIRMCREATEFILE {filename}\n".encode("utf-8"))
                    print("CREATEFILE OVERRIDE")
                    print(all_files)

                elif message.startswith("CREATEFILE ADD"):
                    _, _, filename, size = message.split()
                    size = int(size)
                    
                    add_files(client_socket, client_key, filename, size)

                elif message.startswith("CREATEFILE"):
                    _, filename, size = message.split()
                    size = int(size)

                    if any(f["filename"] == filename for f in all_files[client_key]):
                        client_socket.send(f"ERROR File {filename} already exists\n".encode("utf-8"))
                        # Melhoria: substituir o arquivo como opção
                    else:
                        add_files(client_socket, client_key, filename, size)

                # Melhoria: remoção do arquivo na pasta public deleta arquivo de all_files (ou quando arquivo não for encontrado)
                elif message.startswith("DELETEFILE"):
                    _, filename = message.split()
                    all_files[client_key] = [f for f in all_files[client_key] if f["filename"] != filename]
                    client_socket.send(f"CONFIRMDELETEFILE {filename}\n".encode("utf-8"))
                    print("DELETEFILE")
                    print(all_files)

                elif message.startswith("SEARCH"):
                    tokens = message.split(maxsplit=1)
                    pattern = tokens[1] if len(tokens) > 1 else ""

                    print("{pattern}")
                    print(all_files)

                    results = []

                    for key, files in all_files.items():
                        if client_key == key:
                            continue
                        try:
                            client_ip, client_port = key.split(":", 1)
                        except Exception as e:
                            client_ip = key
                            client_port = "0"
                        for file in files:
                            if pattern in file["filename"]:
                                results.append(f"FILE {file['filename']} {client_ip} {client_port} {file['size']}")

                    response = "\n".join(results) + "\n"
                    client_socket.send(response.encode("utf-8"))
                    print("SEARCH")
                    print(response)

                elif message.startswith("LEAVE"):
                    del all_files[client_key]
                    client_socket.send("CONFIRMLEAVE\n".encode("utf-8"))
                    print("LEAVE")
                    print(all_files)
                    break

            except socket.error as e:
                print(f"Erro de comunicação com {client_address}: {e}")
                break
            except Exception as e:
                print(f"Erro ao processar mensagem de {client_address}: {e}")

    finally:
        if client_key in all_files:
            del all_files[client_key]
            print(f"Cliente {client_address} removido.")
        client_socket.close()
        print(f"Cliente desconectado: {client_address}")

def add_files(client_socket, ip_address, filename, size):
    all_files[ip_address].append({"filename": filename, "size": size})
    client_socket.send(f"CONFIRMCREATEFILE {filename}\n".encode("utf-8"))
    print("CREATEFILE ADD")
    print(all_files)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 1234))
    server_socket.listen(5)
    print("Servidor escutando na porta 1234...")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()