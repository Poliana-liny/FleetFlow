# FleetFlow — Storytelling: Custo x Confiabilidade no Transporte CD-a-CD

## 1. A pergunta de negócio

> "Vale a pena escolher a transportadora mais barata por km? E o que
> realmente diferencia o desempenho entre regiões: a transportadora ou
> a rota?"

## 2. Custo não é só o valor por km cobrado

A **TransRápido Sul** tem o menor custo por km cobrado
(R$ 3.40), mas quando se soma o custo das
ocorrências que ela gera (avarias, atrasos por manutenção, sinistros) e
se divide pelo total de km rodados, o **custo efetivo** sobe para
R$ 3.79/km — ainda a opção mais barata
do grupo, mas a diferença para as demais **diminui**.

O que essa transportadora entrega em troca do preço:
- **68.9%** de entregas no prazo (a pior
  taxa entre as 5 transportadoras)
- **14.5%** de viagens com alguma
  ocorrência (a maior taxa do grupo)

Do outro lado, a **LogExpress Nacional** custa R$ 5.20/km
efetivo — quase o dobro — mas entrega **100.0%**
de pontualidade e a menor taxa de ocorrência do grupo
(4.2%).

**A decisão não é "qual é mais barata", é "o que a operação está
disposta a pagar por confiabilidade".** Para cargas urgentes ou de alto
valor, o prêmio de preço da LogExpress Nacional se paga sozinho
evitando o custo (e o risco reputacional) de atrasos e sinistros.

## 3. Região difícil não significa necessariamente atraso — mas significa mais ocorrência

Comparando rotas que passam por Norte/Nordeste contra as demais:

| Indicador | Sudeste/Sul/Centro-Oeste | Norte/Nordeste |
|---|---|---|
| % On Time | 85.3% | 86.0% |
| Lead time médio | 14.4 h | 54.9 h |
| % Ocorrência | 7.5% | 10.6% |

O percentual de pontualidade é parecido entre as duas regiões — porque o
SLA já é calculado considerando a velocidade média mais baixa das rotas
difíceis. Mas a **taxa de ocorrência é 40% maior**
nas rotas de Norte/Nordeste — reflexo de estradas, distância a pontos de
manutenção e maior desgaste da frota nessas condições.

A rota com pior desempenho de pontualidade é **São Paulo → Goiânia**,
com apenas 83.1% de entregas no prazo — mais
um indício de que a dificuldade real está concentrada em rotas
específicas, não distribuída igualmente por toda a malha.

## 4. O custo real das ocorrências

No total da base, as ocorrências (avarias, atrasos por manutenção e
sinistros) somaram **R$ 3,488,653.10** em 6 meses —
um custo que não aparece na cotação de frete, mas que impacta
diretamente a margem da operação. A transportadora com maior taxa de
ocorrência (TransRápido Sul, 14.5%)
é justamente uma das mais baratas por km — reforçando que negociar só
pelo preço, sem olhar o histórico de ocorrências, é decisão incompleta.

## 5. Gráficos de apoio

- `01_custo_x_confiabilidade.png` — o trade-off central do projeto
- `02_ocorrencias_por_tipo.png` — quais transportadoras concentram quais tipos de problema
- `03_comparativo_regiao.png` — Sudeste/Sul/Centro-Oeste x Norte/Nordeste
- `04_piores_rotas.png` — rotas com pior pontualidade
- `05_custo_efetivo_km.png` — ranking de custo real (frete + ocorrências)

## 6. Conclusão

A pergunta certa não é "qual transportadora é mais barata", mas **"qual
é o custo total esperado por km, dado o histórico de confiabilidade
dessa transportadora?"** — uma decisão de sourcing logístico que só fica
visível cruzando custo de frete, taxa de ocorrência e o tipo de rota
operada.
