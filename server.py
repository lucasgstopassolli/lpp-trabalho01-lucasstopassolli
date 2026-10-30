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

async def recusar(sid, motivo, causa):
    """Emite operacao.recusada exclusivamente para o cliente que originou o pedido inválido."""
    await sio.emit("operacao.recusada", {"motivo": motivo, "causa": causa}, to=sid)

async def producao():
    """Temporizador de produção: colhe uvas e refina vinho periodicamente enquanto a safra está aberta."""
    while estado["fase"] == "aberta":
        await sio.sleep(INTERVALO)
        if estado["fase"] != "aberta":
            break
        # 1) Colheita do recurso primário (uvas)
        estado["uvas"] += estado["producao"]
        await sio.emit("recurso.produzido", fato("temporizador"))

        # 2) Refino (uvas -> vinho) proporcional às construções concluídas (Lagar/Adega)
        if estado["concluidas"] > 0:
            custo_refino = estado["concluidas"] * 2
            if estado["uvas"] >= custo_refino:
                vinho_gerado = estado["concluidas"]
                estado["uvas"] -= custo_refino
                estado["vinho"] += vinho_gerado
                await sio.emit(
                    "vinho.produzido",
                    fato("temporizador", vinho_gerado=vinho_gerado, uvas_consumidas=custo_refino),
                )

async def expiracao():
    """Temporizador de perecibilidade: verifica se há excesso de uvas acumuladas passando do ponto."""
    while estado["fase"] == "aberta":
        await sio.sleep(INTERVALO_EXPIRA)
        if estado["fase"] != "aberta":
            break
        if estado["uvas"] > LIMITE_PERECIVEL:
            estado["uvas"] = max(0, estado["uvas"] - PERDA_EXPIRACAO)
            await sio.emit(
                "uva.expirada",
                fato("temporizador", perdidas=PERDA_EXPIRACAO, motivo="uva passa do ponto"),
            )

async def obra(nome, estrutura):
    """Temporizador de obra: conclui a estrutura após TEMPO_OBRA segundos e libera o vindimador."""
    await sio.sleep(TEMPO_OBRA)
    if estado["fase"] != "aberta":
        return
    estado["trabalhadores"] -= 1
    estado["em_obra"] -= 1
    estado["concluidas"] += 1
    estado["producao"] += 5  # cada estrutura concluída amplia a produção de uvas
    causa = "construcao.iniciada (temporizador)"
    await sio.emit("construcao.concluida", fato(causa, por=nome, estrutura=estrutura))

@sio.on("vila.abertura_solicitada")
async def abrir_vila(sid, dados=None):
    """Escuta o pedido do Mestre para iniciar a temporada da vinícola."""
    pedido = "vila.abertura_solicitada"
    if jogadores.get(sid, {}).get("papel") != "mestre":
        await recusar(sid, "Só o Mestre pode abrir a temporada da vinícola", pedido)
        return
    if estado["fase"] != "aguardando":
        await recusar(sid, "A temporada já foi aberta", pedido)
        return

    estado["fase"] = "aberta"
    sio.start_background_task(producao)
    sio.start_background_task(expiracao)
    # Emite o fato vila.iniciada para todos os clientes conectados
    await sio.emit("vila.iniciada", fato(pedido))

@sio.on("construcao.solicitada")
async def construir(sid, dados=None):
    """Escuta o pedido de construção, valida regras atomicamente e emite construcao.iniciada ou operacao.recusada."""
    pedido = "construcao.solicitada"

    # Validação atômica ANTES de alterar o estado e sem await intermediário:
    # garante que dois pedidos simultâneos sejam decididos um por vez sem condição de corrida.
    if estado["fase"] != "aberta":
        motivo = "A temporada não está aberta"
    elif estado["uvas"] < CUSTO:
        motivo = "Uvas insuficientes (necessário 50 uvas)"
    elif estado["trabalhadores"] >= estado["limite"]:
        motivo = "Sem vindimador livre no momento"
    else:
        motivo = None

    if motivo:
        # Emite a recusa exclusivamente para o cliente que fez o pedido (to=sid)
        await recusar(sid, motivo, pedido)
        return

    indice_obra = estado["concluidas"] + estado["em_obra"]
    estrutura = TIPOS_CONSTRUCAO[indice_obra % len(TIPOS_CONSTRUCAO)]

    estado["uvas"] -= CUSTO
    estado["trabalhadores"] += 1
    estado["em_obra"] += 1
    nome = jogadores.get(sid, {}).get("nome", "Anônimo")

    # Emite o fato construcao.iniciada para todos os clientes conectados
    await sio.emit("construcao.iniciada", fato(pedido, por=nome, estrutura=estrutura))
    sio.start_background_task(obra, nome, estrutura)


