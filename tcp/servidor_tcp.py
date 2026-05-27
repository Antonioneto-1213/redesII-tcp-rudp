import socket, hashlib, os, time

HOST = '0.0.0.0'
PORT = 5001
BUFFER = 4096
matricula = "20249007292"
nome = "Antonio Francisco da Silva Neto"
AUTH = hashlib.sha256((matricula + nome).encode()).hexdigest()

def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"[TCP] Servidor aguardando em {HOST}:{PORT}")
        conn, addr = s.accept()
        with conn:
            print(f"[TCP] Conectado: {addr}")

            
            header = conn.recv(BUFFER).decode()
            conn.send(b"AUTH_OK")

          
            nome_arquivo = conn.recv(BUFFER).decode().strip()
            conn.send(b"OK")

   
            tamanho = int(conn.recv(BUFFER).decode().strip())
            conn.send(b"OK")

            inicio = time.time()
            total = 0
            dados = b""
            while total < tamanho:
                chunk = conn.recv(BUFFER)
                if not chunk:
                    break
                dados += chunk
                total += len(chunk)

            duracao = time.time() - inicio
            throughput = total / duracao if duracao > 0 else 0
            print(f"[TCP] Recebido: {total} bytes em {duracao:.4f}s")
            print(f"[TCP] Throughput: {throughput/1024:.2f} KB/s")

            with open(f"recebido_{nome_arquivo}", 'wb') as f:
                f.write(dados)

            cenario = "C"
            with open(f"logs/tcp_cenario{cenario}.log", "a") as log:
                log.write(f"{duracao:.6f},{total},{throughput:.2f}\n")

while True:
    iniciar_servidor()