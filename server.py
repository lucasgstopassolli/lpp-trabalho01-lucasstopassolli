import socketio

# Instancia o servidor Socket.IO assíncrono (ASGI) permitindo conexões locais
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# Serve o front-end (index.html) e os assets do mapa/sprites do Phaser
app = socketio.ASGIApp(sio, static_files={
    "/": "client/index.html",
    "/assets": "client/assets",
})

# A partir da Etapa 1, adicione o seu código ABAIXO desta linha.

CUSTO = 50           # uvas necessárias por construção (Parreiral, Lagar ou Adega)
TEMPO_OBRA = 8       # segundos até a obra terminar
INTERVALO = 5        # segundos entre cada colheita de uvas e refino de vinho
INTERVALO_EXPIRA = 15 # segundos entre verificações de uva passando do ponto
LIMITE_PERECIVEL = 180 # acima deste estoque, parte das uvas passa do ponto
PERDA_EXPIRACAO = 20   # quantidade de uvas perdidas quando passam do ponto
TIPOS_CONSTRUCAO = ["Parreiral", "Lagar", "Adega"]

estado = {
    "fase": "aguardando",   # aguardando -> aberta -> encerrada
    "uvas": 150,            # recurso primário
    "vinho": 0,             # recurso refinado
    "toras": 150,           # espelho de uvas para compatibilidade com o kit
    "trabalhadores": 0,     # vindimadores ocupados agora
    "limite": 2,            # máximo de vindimadores simultâneos
    "producao": 10,         # uvas colhidas a cada INTERVALO
    "intervalo": INTERVALO,
    "tempo_obra": TEMPO_OBRA,
    "custo": CUSTO,
    "concluidas": 0,
    "em_obra": 0,
}

jogadores = {}  # sid -> {"nome": ..., "papel": ...}

def fato(causa, **extras):
    """Monta o payload de um FATO: o estado atual, a CAUSA (evento ou temporizador) e dados extras."""
    estado["toras"] = estado["uvas"]
    return {"estado": dict(estado), "causa": causa, **extras}

@sio.event
async def connect(sid, environ, auth):
    """Escuta a conexão de um novo cliente e envia o estado atual somente para ele."""
    auth = auth or {}
    jogadores[sid] = {
        "nome": auth.get("nome", "Anônimo"),
        "papel": auth.get("papel", "jogador"),
    }
    # Emite estado.sincronizado apenas para o cliente recém-conectado (to=sid)
    await sio.emit("estado.sincronizado", fato("conexao"), to=sid)

@sio.event
async def disconnect(sid):
    """Remove o jogador desconectado do dicionário de sessão."""
    jogadores.pop(sid, None)

@sio.on("construcao.solicitada")
async def construir(sid, dados=None):
    """Escuta o pedido de construção de um jogador e inicia a obra na vinícola."""
    pedido = "construcao.solicitada"
    indice_obra = estado["concluidas"] + estado["em_obra"]
    estrutura = TIPOS_CONSTRUCAO[indice_obra % len(TIPOS_CONSTRUCAO)]

    estado["uvas"] -= CUSTO
    estado["trabalhadores"] += 1
    estado["em_obra"] += 1
    nome = jogadores.get(sid, {}).get("nome", "Anônimo")

    # Emite o fato construcao.iniciada para todos os jogadores
    await sio.emit("construcao.iniciada", fato(pedido, por=nome, estrutura=estrutura))


