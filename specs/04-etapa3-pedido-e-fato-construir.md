# Etapa 3: Pedido e Fato — Construir (`construcao.solicitada` e `construcao.iniciada`)

## Contexto para o Agente CLI
Seguindo a progressão pedagógica do Guia de Implementação, na Etapa 3 implementamos o fluxo de pedido `construcao.solicitada` (cliente -> servidor) e o fato `construcao.iniciada` (servidor -> todos), identificando também qual estrutura da vinícola está sendo erguida (`Parreiral`, `Lagar` ou `Adega`). A validação de limites será adicionada na Etapa 4.

## 1. Alterações em `server.py`
Acrescente ao final de `server.py`:

```python
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
```

## 2. Alterações em `client/index.html`
1. Dentro de `entrar(p)`, na região `ESCUTAS`, adicione:
```javascript
        // ETAPA 3: Escuta o fato de que uma nova construção foi iniciada na vinícola
        ouvir("construcao.iniciada", "mostra o canteiro de obras e debita uvas", (d) => {
          atualizar(d);
          const tipo = d.estrutura || "estrutura";
          avisar(d.por + " iniciou a obra de um(a) " + tipo);
          jogo.obraIniciada(d.estado);
        });
```
2. Na função `construir()`, na região `PEDIDOS`, adicione:
```javascript
      function construir() {
        // ETAPA 3: Emite o pedido do jogador ao servidor para construir na vinícola
        pedir("construcao.solicitada");
      }
```

## 3. Verificação e Commit
1. Teste clicando em construir como Jogador e verifique o canteiro de obras surgindo e o estoque de uvas caindo em 50.
2. Faça o commit:
   ```bash
   git add server.py client/index.html
   git commit -m "feat: construção (construcao.solicitada e construcao.iniciada)"
   ```