# Etapa 4: Validações de Estado e Recusa (`operacao.recusada`)

## Contexto para o Agente CLI
O servidor é a única fonte da verdade. Para evitar condições de corrida quando dois jogadores clicam ao mesmo tempo disputando o último vindimador ou as últimas 50 uvas, toda a validação e a mutação do estado devem ocorrer de forma síncrona (sem `await` entre validar e alterar). Se inválido, emite `operacao.recusada` exclusivamente para `sid`.

## 1. Alterações em `server.py`
Substitua a função `construir` em `server.py` pela versão validada abaixo:

```python
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
```

## 2. Alterações em `client/index.html`
Dentro de `entrar(p)`, na região `ESCUTAS`, adicione:

```javascript
        // ETAPA 4: Escuta a recusa enviada pelo servidor apenas para quem fez um pedido inválido
        ouvir("operacao.recusada", "avisa o motivo da recusa e treme a tela", (d) => {
          avisar(d.motivo, "erro");
          jogo.recusado(d.motivo);
        });
```

## 3. Verificação e Commit
1. Teste clicar em Construir antes de abrir a temporada ("A temporada não está aberta") e clicar 3 vezes seguidas após abrir ("Sem vindimador livre no momento" no 3º clique, apenas na aba de quem clicou).
2. Faça o commit:
   ```bash
   git add server.py client/index.html
   git commit -m "feat: validações e operacao.recusada"
   ```