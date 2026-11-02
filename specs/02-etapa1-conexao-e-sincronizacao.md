# Etapa 1: Conectar e Sincronizar o Estado (`estado.sincronizado`)

## Contexto para o Agente CLI
Quando um cliente se conecta, o servidor armazena seu `sid`, `nome` e `papel` e emite `estado.sincronizado` **apenas para quem acabou de conectar** (`to=sid`), pois quem já está conectado já possui o estado atualizado.

## 1. Alterações em `server.py`
Acrescente ao final de `server.py`:

```python
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
```

## 2. Alterações em `client/index.html`
Dentro da função `entrar(p)`, na seção `// ===== ESCUTAS (on): o cliente reage aos FATOS do servidor =====`, adicione a escuta comentada:

```javascript
        // ETAPA 1: Escuta a sincronização inicial enviada pelo servidor ao conectar
        ouvir("estado.sincronizado", "guarda o estado e desenha a vinícola", (d) => {
          atualizar(d);
          jogo.mostrarEstado(d.estado);
        });
```

## 3. Verificação e Commit
1. Teste com `uvicorn server:app --reload` abrindo duas abas em `http://localhost:8000` (deve exibir Uvas: 150, Vinho: 0, Vindimadores: 0/2 e `estado.sincronizado` no painel).
2. Faça o commit:
   ```bash
   git add server.py client/index.html
   git commit -m "feat: conexão e estado.sincronizado"
   ```