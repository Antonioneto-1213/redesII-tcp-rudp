import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


colunas = ['duracao', 'bytes', 'throughput']

logs = {
    'TCP_A':  pd.read_csv('../logs/tcp_cenarioA.log',  names=colunas),
    'TCP_B':  pd.read_csv('../logs/tcp_cenarioB.log',  names=colunas),
    'TCP_C':  pd.read_csv('../logs/tcp_cenarioC.log',  names=colunas),
    'RUDP_A': pd.read_csv('../logs/rudp_cenarioA.log', names=colunas),
    'RUDP_B': pd.read_csv('../logs/rudp_cenarioB.log', names=colunas),
    'RUDP_C': pd.read_csv('../logs/rudp_cenarioC.log', names=colunas),
}


for key in ['RUDP_A', 'RUDP_B', 'RUDP_C']:
    logs[key]['throughput'] = logs[key]['throughput'] / 1024

for key in ['TCP_A', 'TCP_B', 'TCP_C']:
    logs[key]['throughput'] = logs[key]['throughput'] / 1024


print("=" * 60)
print("ESTATÍSTICAS DE THROUGHPUT (KB/s)")
print("=" * 60)
for nome, df in logs.items():
    t = df['throughput']
    print(f"{nome}: min={t.min():.2f} | média={t.mean():.2f} | max={t.max():.2f} | dp={t.std():.2f}")

print("\n" + "=" * 60)
print("ESTATÍSTICAS DE TEMPO (segundos)")
print("=" * 60)
for nome, df in logs.items():
    d = df['duracao']
    print(f"{nome}: min={d.min():.4f} | média={d.mean():.4f} | max={d.max():.4f} | dp={d.std():.4f}")


cenarios = ['A (0%/10ms)', 'B (5%/50ms)', 'C (10%/100ms)']
x = np.arange(len(cenarios))
largura = 0.35

tcp_medias  = [logs['TCP_A']['throughput'].mean(),  logs['TCP_B']['throughput'].mean(),  logs['TCP_C']['throughput'].mean()]
tcp_dp      = [logs['TCP_A']['throughput'].std(),   logs['TCP_B']['throughput'].std(),   logs['TCP_C']['throughput'].std()]
rudp_medias = [logs['RUDP_A']['throughput'].mean(), logs['RUDP_B']['throughput'].mean(), logs['RUDP_C']['throughput'].mean()]
rudp_dp     = [logs['RUDP_A']['throughput'].std(),  logs['RUDP_B']['throughput'].std(),  logs['RUDP_C']['throughput'].std()]

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - largura/2, tcp_medias,  largura, yerr=tcp_dp,  label='TCP',   capsize=5, color='steelblue')
ax.bar(x + largura/2, rudp_medias, largura, yerr=rudp_dp, label='R-UDP', capsize=5, color='tomato')
ax.set_xlabel('Cenário de Rede')
ax.set_ylabel('Throughput Médio (KB/s)')
ax.set_title('Comparativo TCP vs R-UDP — Throughput por Cenário')
ax.set_xticks(x)
ax.set_xticklabels(cenarios)
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('comparativo_tcp_rudp.png', dpi=150)
plt.show()
print("Gráfico 1 salvo: comparativo_tcp_rudp.png")


tcp_tempo_medias  = [logs['TCP_A']['duracao'].mean(),  logs['TCP_B']['duracao'].mean(),  logs['TCP_C']['duracao'].mean()]
tcp_tempo_dp      = [logs['TCP_A']['duracao'].std(),   logs['TCP_B']['duracao'].std(),   logs['TCP_C']['duracao'].std()]
rudp_tempo_medias = [logs['RUDP_A']['duracao'].mean(), logs['RUDP_B']['duracao'].mean(), logs['RUDP_C']['duracao'].mean()]
rudp_tempo_dp     = [logs['RUDP_A']['duracao'].std(),  logs['RUDP_B']['duracao'].std(),  logs['RUDP_C']['duracao'].std()]

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - largura/2, tcp_tempo_medias,  largura, yerr=tcp_tempo_dp,  label='TCP',   capsize=5, color='steelblue')
ax.bar(x + largura/2, rudp_tempo_medias, largura, yerr=rudp_tempo_dp, label='R-UDP', capsize=5, color='tomato')
ax.set_xlabel('Cenário de Rede')
ax.set_ylabel('Tempo Médio de Transferência (s)')
ax.set_title('Comparativo TCP vs R-UDP — Tempo de Transferência por Cenário')
ax.set_xticks(x)
ax.set_xticklabels(cenarios)
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('comparativo_tempo.png', dpi=150)
plt.show()
print("Gráfico 2 salvo: comparativo_tempo.png")


def carregar_wireshark(arquivo):
    try:
        df = pd.read_csv(arquivo)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Erro ao carregar {arquivo}: {e}")
        return None

ws = {
    'TCP_A':  carregar_wireshark('wireshark_tcp_A.csv'),
    'TCP_B':  carregar_wireshark('wireshark_tcp_B.csv'),
    'TCP_C':  carregar_wireshark('wireshark_tcp_C.csv'),
    'RUDP_A': carregar_wireshark('wireshark_rudp_A.csv'),
    'RUDP_B': carregar_wireshark('wireshark_rudp_B.csv'),
    'RUDP_C': carregar_wireshark('wireshark_rudp_C.csv'),
}


print("\n" + "=" * 60)
print("CRUZAMENTO DE DADOS — PYTHON vs WIRESHARK")
print("=" * 60)

resultados = []

for key in ['TCP_A', 'TCP_B', 'TCP_C', 'RUDP_A', 'RUDP_B', 'RUDP_C']:
    df_log = logs[key]
    df_ws  = ws[key]

    if df_ws is None:
        print(f"{key}: arquivo Wireshark não encontrado")
        continue

    tempo_python = df_log['duracao'].mean()

    
    col_duracao = 'Duração'
    if col_duracao not in df_ws.columns:
    
        possiveis = [c for c in df_ws.columns if 'ura' in c.lower() or 'dur' in c.lower()]
        if possiveis:
            col_duracao = possiveis[0]
        else:
            print(f"{key}: coluna de duração não encontrada. Colunas: {list(df_ws.columns)}")
            continue

    tempo_wireshark = df_ws[col_duracao].mean()

    
    bytes_python = df_log['bytes'].mean()

    
    col_bytes = 'Bytes'
    if col_bytes not in df_ws.columns:
        possiveis = [c for c in df_ws.columns if 'byte' in c.lower()]
        if possiveis:
            col_bytes = possiveis[0]

    bytes_wireshark = df_ws[col_bytes].sum() / len(df_log) if col_bytes in df_ws.columns else 0

   
    disc_tempo = abs(tempo_python - tempo_wireshark) / tempo_python * 100 if tempo_python > 0 else 0
    disc_bytes = abs(bytes_python - bytes_wireshark) / bytes_python * 100 if bytes_python > 0 else 0

    print(f"\n{key}:")
    print(f"  Tempo  — Python: {tempo_python:.4f}s | Wireshark: {tempo_wireshark:.4f}s | Discrepância: {disc_tempo:.1f}%")
    print(f"  Bytes  — Python: {bytes_python:.0f}  | Wireshark: {bytes_wireshark:.0f}  | Discrepância: {disc_bytes:.1f}%")

    resultados.append({
        'Cenário': key,
        'Tempo Python (s)': round(tempo_python, 4),
        'Tempo Wireshark (s)': round(tempo_wireshark, 4),
        'Disc. Tempo (%)': round(disc_tempo, 1),
        'Bytes Python': round(bytes_python, 0),
        'Bytes Wireshark': round(bytes_wireshark, 0),
        'Disc. Bytes (%)': round(disc_bytes, 1),
    })


if resultados:
    df_res = pd.DataFrame(resultados)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Gráfico de tempo
    cenarios_label = df_res['Cenário'].tolist()
    x3 = np.arange(len(cenarios_label))
    largura3 = 0.35

    axes[0].bar(x3 - largura3/2, df_res['Tempo Python (s)'],    largura3, label='Python',    color='steelblue')
    axes[0].bar(x3 + largura3/2, df_res['Tempo Wireshark (s)'], largura3, label='Wireshark', color='orange')
    axes[0].set_xlabel('Cenário')
    axes[0].set_ylabel('Tempo Médio (s)')
    axes[0].set_title('Tempo de Transferência\nPython vs Wireshark')
    axes[0].set_xticks(x3)
    axes[0].set_xticklabels(cenarios_label, rotation=45, ha='right')
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)

    
    axes[1].bar(x3, df_res['Disc. Tempo (%)'], color='tomato')
    axes[1].set_xlabel('Cenário')
    axes[1].set_ylabel('Discrepância (%)')
    axes[1].set_title('Discrepância de Tempo\nPython vs Wireshark (%)')
    axes[1].set_xticks(x3)
    axes[1].set_xticklabels(cenarios_label, rotation=45, ha='right')
    axes[1].grid(axis='y', alpha=0.3)
    axes[1].axhline(y=15, color='red', linestyle='--', alpha=0.5, label='Limite 15%')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig('cruzamento_python_wireshark.png', dpi=150)
    plt.show()
    print("\nGráfico 3 salvo: cruzamento_python_wireshark.png")

    
    df_res.to_csv('cruzamento_dados.csv', index=False)
    print("Tabela salva: cruzamento_dados.csv")

print("\nAnálise completa!")