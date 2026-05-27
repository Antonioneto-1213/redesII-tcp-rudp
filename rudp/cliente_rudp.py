import hashlib

matricula = "20249007292"
nome = "Antonio Francisco da Silva Neto"
auth_hash = hashlib.sha256((matricula + nome).encode()).hexdigest()
X_CUSTOM_AUTH = auth_hash

import socket, hashlib, struct, time, sys, os

HOST = '10.0.0.2'
PORT = 5002
BUFFER = 1024  
TIMEOUT = 2    
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
    dados = pacote[101:]
    return seq, tipo, dados

def enviar_com_retry(s, pacote, seq_esperado, addr, max_tentativas=10):
    for tentativa in range(max_tentativas):
        s.sendto(pacote, addr)
        try:
            resposta, _ = s.recvfrom(HEADER_SIZE + 200)
            seq_ack, tipo_ack, _ = desmontar_pacote(resposta)
            if tipo_ack == 1 and seq_ack == seq_esperado:
                return True
        except socket.timeout:
            print(f"  [timeout] Retransmitindo seq {seq_esperado} (tentativa {tentativa+1})")
    return False

def enviar_arquivo(caminho):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(TIMEOUT)
    addr = (HOST, PORT)

    nome = os.path.basename(caminho)

    pkt_inicio = montar_pacote(0, 2, nome.encode())
    if not enviar_com_retry(s, pkt_inicio, 0, addr):
        print("Falha ao iniciar transferência")
        return

    seq = 0
    total = 0
    inicio = time.time()

    with open(caminho, 'rb') as f:
        while True:
            chunk = f.read(BUFFER)
            if not chunk:
                break
            pkt = montar_pacote(seq, 0, chunk)
            if not enviar_com_retry(s, pkt, seq, addr):
                print(f"Falha no seq {seq}")
                return
            total += len(chunk)
            seq += 1

    
    pkt_fim = montar_pacote(seq, 3, b"FIM")
    enviar_com_retry(s, pkt_fim, seq, addr)

    duracao = time.time() - inicio
    throughput = total / duracao if duracao > 0 else 0
    print(f"[R-UDP] Enviado: {total} bytes em {duracao:.4f}s | {throughput/1024:.2f} KB/s")

    with open("logs/rudp_cliente.log", "a") as log:
        log.write(f"{duracao:.6f},{total},{throughput:.2f}\n")

enviar_arquivo(sys.argv[1])