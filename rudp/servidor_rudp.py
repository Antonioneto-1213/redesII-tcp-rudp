import hashlib

matricula = "20249007292"
nome = "Antonio Francisco da Silva Neto"
auth_hash = hashlib.sha256((matricula + nome).encode()).hexdigest()
X_CUSTOM_AUTH = auth_hash

import socket, hashlib, struct, time

HOST = '0.0.0.0'
PORT = 5002
BUFFER = 4096
AUTH = hashlib.sha256(("MATRICULA" + "NOME").encode()).hexdigest()


HEADER_SIZE = 4 + 1 + 64 + 32  

def calcular_checksum(dados):
    return hashlib.md5(dados).hexdigest()  

def montar_pacote(seq, tipo, dados):
  
    header_fixo = struct.pack('!IB', seq, tipo)
    auth_bytes = AUTH.encode()[:64]
    checksum = calcular_checksum(dados).encode()
    return header_fixo + auth_bytes + checksum + dados

def desmontar_pacote(pacote):
    seq, tipo = struct.unpack('!IB', pacote[:5])
    auth = pacote[5:69].decode().strip()
    checksum_recebido = pacote[69:101].decode()
    dados = pacote[101:]
    return seq, tipo, auth, checksum_recebido, dados

def iniciar_servidor():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    s.settimeout(10)
    print(f"[R-UDP] Servidor em {HOST}:{PORT}")

    esperado = 0
    arquivo_dados = b""
    addr_cliente = None
    nome_arquivo = ""
    inicio = None

    while True:
        try:
            pacote, addr = s.recvfrom(BUFFER + HEADER_SIZE + 200)
            addr_cliente = addr
            seq, tipo, auth, checksum_recv, dados = desmontar_pacote(pacote)

          
            if AUTH not in auth:
                print(f"[R-UDP] Auth inválida!")
                continue

            if tipo == 2:  
                nome_arquivo = dados.decode()
                inicio = time.time()
                esperado = 0
                arquivo_dados = b""
                print(f"[R-UDP] Recebendo arquivo: {nome_arquivo}")
                ack = montar_pacote(seq, 1, b"OK")
                s.sendto(ack, addr)

            elif tipo == 0: 
                checksum_calculado = calcular_checksum(dados)
                if checksum_recv != checksum_calculado:
                    print(f"[R-UDP] Checksum inválido no seq {seq}, ignorando")
                    continue  
                if seq == esperado:
                    arquivo_dados += dados
                    ack = montar_pacote(seq, 1, b"ACK")
                    s.sendto(ack, addr)
                    esperado += 1
                else:
                    
                    ack = montar_pacote(esperado - 1, 1, b"ACK")
                    s.sendto(ack, addr)

            elif tipo == 3:  
                duracao = time.time() - inicio
                total = len(arquivo_dados)
                throughput = total / duracao if duracao > 0 else 0
                with open(f"recebido_{nome_arquivo}", 'wb') as f:
                    f.write(arquivo_dados)
                print(f"[R-UDP] Concluído: {total} bytes em {duracao:.4f}s | {throughput/1024:.2f} KB/s")
                cenario = "C"
                with open(f"logs/rudp_cenario{cenario}.log", "a") as log:
                    log.write(f"{duracao:.6f},{total},{throughput:.2f}\n")
                ack = montar_pacote(seq, 1, b"FIM_OK")
                s.sendto(ack, addr)
                break

        except socket.timeout:
            print("[R-UDP] Timeout aguardando pacotes")
            break

while True:
    iniciar_servidor()