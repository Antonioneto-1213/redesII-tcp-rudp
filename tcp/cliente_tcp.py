import socket, hashlib, os, time, sys

HOST = '10.0.0.2'
PORT = 5001
BUFFER = 4096
matricula = "20249007292"
nome = "Antonio Francisco da Silva Neto"
AUTH = hashlib.sha256((matricula + nome).encode()).hexdigest()

def enviar_arquivo(caminho, cenario="A"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        s.send(f"X-Custom-Auth: {AUTH}".encode())
        if s.recv(BUFFER) != b"AUTH_OK":
            print("Auth falhou!")
            return

        nome = os.path.basename(caminho)
        s.send(nome.encode())
        s.recv(BUFFER)

        tamanho = os.path.getsize(caminho)
        s.send(str(tamanho).encode())
        s.recv(BUFFER)

        inicio = time.time()
        total = 0
        with open(caminho, 'rb') as f:
            while True:
                chunk = f.read(BUFFER)
                if not chunk:
                    break
                s.send(chunk)
                total += len(chunk)

        duracao = time.time() - inicio
        throughput = total / duracao if duracao > 0 else 0
        print(f"[TCP] Enviado: {total} bytes em {duracao:.4f}s")
        print(f"[TCP] Throughput: {throughput/1024:.2f} KB/s")

        with open(f"logs/tcp_cenario{cenario}.log", "a") as log:
            log.write(f"{duracao:.6f},{total},{throughput:.2f}\n")

cenario = sys.argv[2] if len(sys.argv) > 2 else "A"
enviar_arquivo(sys.argv[1], cenario)