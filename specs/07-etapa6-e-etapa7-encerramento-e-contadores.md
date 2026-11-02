# Etapas 6 e 7: Encerramento da Temporada e Contadores por Evento

## Contexto para o Agente CLI
Faremos duas etapas com seus respectivos commits individuais:
- **Etapa 6:** O Mestre solicita o encerramento (`vila.encerramento_solicitado`) e o servidor emite `vila.encerrada` para todos, parando os loops de produção/expiração e bloqueando novas construções.
- **Etapa 7:** Adição dos chips de contadores por evento (`v-for="(n, nome) in contadores"`) no topo do Painel de Eventos em `client/index.html`.

---

## Parte A — Etapa 6: Encerramento (`vila.encerramento_solicitado` e `vila.encerrada`)

### 1. Alterações em `server.py`
Acrescente ao final de `server.py`:

```python
@sio.on("vila.encerramento_solicitado")
async def encerrar_vila(sid, dados=None):
    """Escuta o pedido do Mestre para encerrar a temporada e bloqueia novas ações."""
    pedido = "vila.encerramento_solicitado"
    if jogadores.get(sid, {}).get("papel") != "mestre":
        await recusar(sid, "Só o Mestre pode encerrar a temporada", pedido)
        return
    if estado["fase"] != "aberta":
        await recusar(sid, "A temporada não está aberta", pedido)
        return

    estado["fase"] = "encerrada"
    # Emite o fato vila.encerrada para todos os clientes conectados
    await sio.emit("vila.encerrada", fato(pedido))
```

### 2. Alterações em `client/index.html` (Etapa 6)
1. Dentro de `entrar(p)`, na região `ESCUTAS`, adicione:
```javascript
        // ETAPA 6: Escuta o encerramento da temporada e escurece a vinícola
        ouvir("vila.encerrada", "escurece a vinícola e bloqueia novas ações", (d) => {
          atualizar(d);
          avisar("Temporada de vindima encerrada.");
          jogo.vilaEncerrada();
        });
```
2. Na função `encerrarVila()`, na região `PEDIDOS`, adicione:
```javascript
      function encerrarVila() {
        // ETAPA 6: Emite o pedido do Mestre ao servidor para encerrar a temporada
        pedir("vila.encerramento_solicitado");
      }
```

### 3. Commit da Etapa 6
```bash
git add server.py client/index.html
git commit -m "feat: encerramento da temporada"
```

---

## Parte B — Etapa 7: Contadores por Evento no Painel

### 1. Alterações em `client/index.html` (Etapa 7)
No `<section class="eventos">` do `client/index.html`, substitua o comentário `<!-- ETAPA 7 (dupla): cole aqui os contadores por evento -->` por:

```html
      <div class="contadores">
        <span v-for="(n, nome) in contadores" :key="nome" class="chip">{{ nome }} ×{{ n }}</span>
      </div>
```

### 2. Commit da Etapa 7
```bash
git add client/index.html
git commit -m "feat: contadores por evento"
```