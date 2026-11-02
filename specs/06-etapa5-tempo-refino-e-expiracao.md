# Etapa 5: Passagem do Tempo, Refino de Vinho e Expiração de Uvas

## Contexto para o Agente CLI
Temporizadores no servidor são fontes de eventos (`sio.start_background_task` com `await sio.sleep`). Nesta etapa implementamos:
1. `producao()`: a cada `INTERVALO` (5s), soma `estado["producao"]` em `uvas` e emite `recurso.produzido` (`causa: "temporizador"`). Em seguida, se houver construções concluídas (`estado["concluidas"] > 0`) e uvas suficientes (`>= concluidas * 2`), refina `2 * concluidas` uvas em `1 * concluidas` vinhos e emite `vinho.produzido` (`causa: "temporizador (refino no lagar/adega)"`).
2. `expiracao()`: a cada `INTERVALO_EXPIRA` (15s), verifica se `estado["uvas"] > LIMITE_PERECIVEL` (180). Se sim, desconta `PERDA_EXPIRACAO` (20 uvas) e emite `uva.expirada` (`causa: "temporizador (uva passa do ponto)"`).
3. `obra(nome, estrutura)`: aguarda `TEMPO_OBRA` (8s) e, se a temporada continuar aberta, libera 1 vindimador, incrementa `concluidas`, aumenta `producao` em `+5` e emite `construcao.concluida` (`causa: "construcao.iniciada (temporizador)"`).

## 1. Alterações em `server.py`
1. Adicione as três corrotinas de temporizador antes dos handlers `@sio.on` (ou ao final do arquivo):

```python
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
```

2. Na função `abrir_vila`, inicie as tasks de `producao` e `expiracao` logo após `estado["fase"] = "aberta"`:
```python
    estado["fase"] = "aberta"
    sio.start_background_task(producao)
    sio.start_background_task(expiracao)
    await sio.emit("vila.iniciada", fato(pedido))
```

3. Na função `construir`, inicie a task `obra` ao final:
```python
    await sio.emit("construcao.iniciada", fato(pedido, por=nome, estrutura=estrutura))
    sio.start_background_task(obra, nome, estrutura)
```

## 2. Alterações em `client/index.html`
Dentro de `entrar(p)`, na região `ESCUTAS`, adicione as escutas dos eventos de tempo:

```javascript
        // ETAPA 5: Escuta a colheita automática de uvas gerada pelo temporizador do servidor
        ouvir("recurso.produzido", "atualiza o estoque de uvas e mostra +N na vinícola", (d) => {
          atualizar(d);
          jogo.recursoProduzido(d.estado);
        });

        // ETAPA 5 (Tema Vinícola): Escuta o refino automático de uvas em vinho
        ouvir("vinho.produzido", "atualiza o estoque de vinho refinado e mostra +N 🍷", (d) => {
          atualizar(d);
          jogo.vinhoProduzido(d.vinho_gerado || 1);
        });

        // ETAPA 5 (Tema Vinícola): Escuta a expiração quando a uva passa do ponto por excesso de estoque
        ouvir("uva.expirada", "reduz uvas que passaram do ponto e alerta os jogadores", (d) => {
          atualizar(d);
          avisar("⚠️ " + d.perdidas + " uvas passaram do ponto por excesso no estoque!", "erro");
          jogo.uvaExpirada(d.perdidas || 20);
        });

        // ETAPA 5: Escuta o término de uma obra pelo temporizador do servidor
        ouvir("construcao.concluida", "transforma o canteiro em estrutura pronta e libera vindimador", (d) => {
          atualizar(d);
          const tipo = d.estrutura || "Obra";
          avisar(tipo + " de " + d.por + " concluído(a)! Colheita e refino de vinho aumentaram.", "ok");
          jogo.obraConcluida(d.estado);
        });
```

## 3. Verificação e Commit
1. Reinicie/recarregue as abas, abra a temporada e construa uma obra. Verifique a colheita de uvas a cada 5s, a conclusão da obra em 8s, o início do refino `vinho.produzido` e, ao deixar as uvas passarem de 180, o disparo de `uva.expirada`.
2. Faça o commit:
   ```bash
   git add server.py client/index.html
   git commit -m "feat: produção automática e obra com tempo"
   ```