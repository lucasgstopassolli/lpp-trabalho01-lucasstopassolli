# Etapa 2: O Mestre Abre a Temporada (`vila.abertura_solicitada` e `vila.iniciada`)

## Contexto para o Agente CLI
O Mestre solicita a abertura da vindima emitindo `vila.abertura_solicitada`. O servidor valida se quem pediu tem o papel `"mestre"` e se a fase atual é `"aguardando"`. Caso contrário, emite `operacao.recusada` apenas para quem pediu (`to=sid`). Se válido, muda `estado["fase"] = "aberta"` e emite `vila.iniciada` em broadcast para todos os clientes.

## 1. Alterações em `server.py`
Acrescente ao final de `server.py`:

```python
async def recusar(sid, motivo, causa):
    """Emite operacao.recusada exclusivamente para o cliente que originou o pedido inválido."""
    await sio.emit("operacao.recusada", {"motivo": motivo, "causa": causa}, to=sid)

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
    # Emite o fato vila.iniciada para todos os clientes conectados
    await sio.emit("vila.iniciada", fato(pedido))
```

## 2. Alterações em `client/index.html`
1. Dentro de `entrar(p)`, na região `ESCUTAS`, adicione:
```javascript
        // ETAPA 2: Escuta a confirmação do servidor de que o Mestre abriu a temporada
        ouvir("vila.iniciada", "muda a faixa para temporada aberta", (d) => {
          atualizar(d);
          avisar("A temporada de vindima começou!", "ok");
          jogo.vilaIniciada();
        });
```
2. Na função `abrirVila()`, na região `PEDIDOS`, adicione:
```javascript
      function abrirVila() {
        // ETAPA 2: Emite o pedido do Mestre ao servidor para abrir a temporada
        pedir("vila.abertura_solicitada");
      }
```

## 3. Verificação e Commit
1. Teste com 1 aba Mestre e 1 aba Jogador. Ao clicar em "Abrir temporada" no Mestre, ambas mudam para `aberta`.
2. Faça o commit:
   ```bash
   git add server.py client/index.html
   git commit -m "feat: Mestre abre a temporada (vila.iniciada)"
   ```w