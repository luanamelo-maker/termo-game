# Registro de decisões

Diário do projeto: **o que** foi decidido, **por quê**, e **qual teste protege**. É a memória de
longo prazo — quando algo parecer estranho ou um teste quebrar, comece por aqui.

Regras: entrada nova em cima; título curto; três linhas (`O que`, `Por quê`, `Protegido por`); cinco
linhas no máximo. Adicione uma entrada sempre que criar uma feature, mudar ou remover um
comportamento, acrescentar uma dependência ou tomar uma decisão que alguém poderia questionar depois.

Modelo:

```
## AAAA-MM-DD — Título curto
- **O que:** …
- **Por quê:** …
- **Protegido por:** `tests/arquivo.py::nome_do_teste` (ou "sem teste — só visual", explicando por quê)
```

---

## 2026-09-18 — Letra já eliminada não pode ser digitada de novo

- **O que:** `Jogo.digitar()` recusa uma letra cuja melhor marca (via `letras_usadas()`) já é
  `AUSENTE`; o chute não aceita mais aquela letra em nenhuma tentativa seguinte.
- **Por quê:** digitar de novo uma letra que já saiu cinza não ajuda em nada e confundia quem está
  aprendendo a jogar por eliminação. Uma letra repetida no chute (uma ocorrência certa, outra
  ausente) continua liberada, porque `letras_usadas()` já prioriza certa/deslocada sobre ausente.
- **Protegido por:** `tests/test_jogo.py::test_letra_marcada_ausente_nao_pode_ser_digitada_de_novo`,
  `::test_letra_com_uma_ocorrencia_certa_e_outra_ausente_continua_digitavel`

## 2026-09-17 — A palavra é guardada com cada acento colado na sua letra (forma NFC)

- **O que:** `palavras.canonica()` normaliza toda palavra que entra, ao carregar o arquivo e ao
  começar uma partida.
- **Por quê:** `LIÇÃO` pode vir escrito de dois jeitos que parecem iguais na tela — com o `Ç` inteiro
  ou com um `C` seguido de uma cedilha solta. No segundo, a palavra tem 7 caracteres, e a grade
  mostraria um acento sozinho num quadradinho. Vai acontecer quando alguém colar uma lista de
  palavras achada na internet.
- **Protegido por:** `tests/test_jogo.py::test_palavra_escrita_com_acento_solto_e_arrumada`

## 2026-09-17 — O aviso da tela tem largura máxima conferida por teste

- **O que:** nenhum texto da faixa de aviso pode passar de `LARGURA_JANELA - 2 * MARGEM`.
- **Por quê:** a primeira versão da dica tinha 60 caracteres e aparecia cortada nas duas pontas
  ("igite uma palavra … Esc sa"). O teste mede o texto na fonte de verdade e usa a palavra mais larga
  da lista inteira, para não depender de uma palavra escolhida a dedo.
- **Protegido por:** `tests/test_gui_smoke.py::test_todo_aviso_cabe_na_largura_da_janela`

## 2026-09-17 — O teclado da tela mostra as letras, mas não recebe clique

- **O que:** as três fileiras embaixo da grade são um resumo colorido do que já se sabe; para jogar,
  usa-se o teclado de verdade.
- **Por quê:** o valor do teclado na tela é lembrar quais letras já saíram — isso ele entrega sem
  clique nenhum. Deixar clicável é uma feature legítima, e está no `IDEIAS.md` como exercício.
- **Protegido por:** sem teste — a ausência de clique não quebra nada; o que há é o teste de que o
  teclado desenha com a cor certa.

## 2026-09-17 — A tecla R só reinicia depois do fim da partida

- **O que:** durante o jogo, R é uma letra como outra qualquer; acabada a partida, R começa outra.
- **Por quê:** se R reiniciasse a qualquer momento, ninguém conseguiria chutar TERRA nem CARRO — a
  pessoa perderia a partida sem entender o que aconteceu.
- **Protegido por:** `tests/test_gui_smoke.py::test_tecla_r_durante_a_partida_e_uma_letra_como_outra_qualquer`

## 2026-09-17 — Qualquer sequência de 5 letras é aceita como chute

- **O que:** o jogo não recusa palavra inventada; só recusa chute com menos de 5 letras, e sem gastar
  tentativa.
- **Por quê:** recusar exige uma segunda lista, com milhares de palavras, e transforma o primeiro
  contato numa briga com o dicionário. Validar o chute está no `IDEIAS.md` como feature de quem
  quiser encarar.
- **Protegido por:** `tests/test_jogo.py::test_chute_incompleto_nao_gasta_tentativa`

## 2026-09-17 — Acento é comparado sem acento e revelado só na letra certa

- **O que:** quem joga digita `LICAO` e acerta `LIÇÃO`; a letra volta acentuada para a tela quando
  está na posição certa, e aparece sem acento quando fica amarela.
- **Por quê:** perder uma das seis tentativas por não saber onde vai o til é castigo por ortografia,
  não por dedução. E mostrar o `Ç` num quadradinho amarelo entregaria uma pista que o Termo original
  só dá quando você acerta a posição.
- **Protegido por:** `tests/test_jogo.py::test_chute_sem_acento_acerta_palavra_acentuada`,
  `::test_acento_aparece_na_tela_quando_a_letra_esta_no_lugar_certo`, `::test_letra_amarela_nao_revela_o_acento`

## 2026-09-17 — A avaliação do chute é feita em dois passos

- **O que:** `avaliar()` marca primeiro todas as letras na posição certa, contando o que sobra da
  palavra secreta, e só depois marca as deslocadas, consumindo dessa contagem.
- **Por quê:** num passo só, chutar duas letras iguais numa palavra que tem uma acenderia as duas —
  e a pessoa jogaria a partida inteira achando que existem dois Ts. É o erro clássico de quem
  implementa este jogo.
- **Protegido por:** `tests/test_jogo.py::test_letra_repetida_no_chute_nao_acende_duas_vezes`,
  `::test_letra_repetida_acende_tantas_vezes_quantas_existem`, `::test_letra_repetida_na_palavra_pode_gerar_dois_amarelos`

## 2026-09-17 — Janela de 445×640, calculada a partir do tamanho da casa

- **O que:** `LADO_CASA = 56` e as outras constantes de `gui.py` geram a janela; a largura é a do
  teclado, que é mais largo que a grade.
- **Por quê:** 640 de altura cabe em notebook de 1366×768 com a barra de tarefas — mais que isso e o
  teclado some embaixo da barra. Calcular em vez de fixar faz mudar o tamanho da casa ajustar a
  janela sozinho.
- **Protegido por:** `tests/test_gui_smoke.py::test_a_janela_cabe_em_notebook_pequeno`,
  `::test_a_grade_cabe_dentro_da_janela`

## 2026-09-17 — As palavras vivem num arquivo de texto ordenado, com teste de formato

- **O que:** `src/termo/palavras.txt`, uma palavra por linha, maiúscula, com acento, em ordem
  alfabética ignorando o acento. 506 palavras hoje.
- **Por quê:** é a parte que mais gente vai querer editar, e editar um `.txt` não assusta ninguém. O
  teste olha o arquivo de verdade porque um erro ali (palavra de 6 letras, repetida, minúscula) só
  apareceria como bug estranho no meio de uma partida.
- **Protegido por:** `tests/test_palavras.py` inteiro

## 2026-09-17 — Testes rodam sem abrir janela (SDL dummy)

- **O que:** `tests/conftest.py` define `SDL_VIDEODRIVER=dummy` e `SDL_AUDIODRIVER=dummy` antes de
  qualquer `import pygame`.
- **Por quê:** o Claude Code precisa validar mudanças na interface sem travar o terminal com uma
  janela aberta; e a suíte roda em qualquer máquina, com ou sem tela.
- **Protegido por:** toda a `tests/test_gui_smoke.py` depende disso.

## 2026-09-17 — Toda função pública (inclusive teste) precisa de docstring

- **O que:** ruff com as regras `D100`–`D103` ligadas no `pyproject.toml`.
- **Por quê:** ninguém aqui lê código; a docstring do teste é o que explica por que uma regra existe
  quando ela quebra. Cobrar mecanicamente evita que o hábito se perca entre sessões.
- **Protegido por:** `uv run ruff check .` falha sem docstring.

## 2026-09-17 — Código, testes e comentários em português

- **O que:** `jogo.py`, `avaliar(chute, secreta)`, `test_letra_em_outro_lugar_fica_amarela` — nada de
  identificador em inglês, ao contrário do repositório irmão `eight-queens-game`.
- **Por quê:** quem lê este código está aprendendo a programar, em português. `avaliar(chute,
  secreta)` se entende na primeira leitura; `evaluate(guess, secret)` cobra um segundo idioma antes
  do primeiro conceito.
- **Protegido por:** sem teste — é convenção, e está no `CLAUDE.md` e no Checklist de Pronto.

## 2026-09-17 — Sem skills locais: o repositório usa o plugin `engenharia@39a`

- **O que:** não existe `.claude/skills/` aqui. O `CLAUDE.md` roteia para `/nova-feature`,
  `/verificar`, `/revisar` e `/investigar` do plugin, e lista os comandos crus para quem não o tem.
- **Por quê:** o irmão `eight-queens-game` reimplementou `/verificar` e `/revisar` dentro do repo, e
  duas versões da mesma skill divergem em silêncio. Aprender a chamar a skill da casa é metade do que
  se aprende aqui.
- **Protegido por:** sem teste — está no `CLAUDE.md`, seções "O plugin `engenharia@39a` é o caminho"
  e "Se você não tem o plugin".

## 2026-09-17 — O trabalho acontece em fork, com branch e PR; só existe `main`

- **O que:** cada pessoa forka o repositório e abre PR para a `main` do próprio fork, com
  `gh pr create --base main --repo <usuario>/termo-game`.
- **Por quê:** é o fluxo da casa, e é o hábito que a pessoa leva para o primeiro projeto de verdade.
  Não existe `hml` porque não há ambiente para promover — e o `--repo` é obrigatório porque, dentro
  de um fork, o `gh` propõe o repositório pai por padrão e a pessoa abriria PR na 39A sem querer.
- **Protegido por:** sem teste — está no `CLAUDE.md` e no `README.md`.

## 2026-09-17 — Regras em `jogo.py`, desenho em `gui.py`

- **O que:** `jogo.py` não importa pygame; `gui.py` não decide regra de jogo. `palavras.py` fica na
  base, sem conhecer nenhum dos dois.
- **Por quê:** testar as regras sem abrir janela e trocar a aparência sem mexer nas regras. É a regra
  de ouro do `CLAUDE.md`.
- **Protegido por:** `tests/test_jogo.py::test_as_regras_nao_dependem_de_pygame`, que lê os imports
  do código-fonte. Só "a suíte roda sem janela" não protegia nada: o pygame está instalado, e um
  `import pygame` no meio das regras deixaria a suíte inteira verde.

## 2026-09-17 — `pygame-ce` em vez de `pygame`

- **O que:** dependência `pygame-ce>=2.5` no `pyproject.toml`.
- **Por quê:** fork mantido ativamente, com wheels para Python 3.12+ e Windows on ARM. Mesma API
  (`import pygame`). Os dois pacotes instalados juntos quebram um ao outro.
- **Protegido por:** sem teste — comentário no `pyproject.toml` e regra no `CLAUDE.md`.

## 2026-09-17 — Jogo desktop sai da stack que a skill `novo-projeto` prescreve

- **O que:** Python + `uv` + `pygame-ce`, sem Falcon, sem Postgres, sem Alembic, sem manifesto de
  deploy — tudo o que a skill `engenharia:novo-projeto` manda usar num projeto da casa.
- **Por quê:** a skill descreve serviço que atende HTTP e vai para o cluster; um jogo de janela não
  tem rota nem banco. O repositório irmão `eight-queens-game` já abriu esse caminho. Divergir do
  padrão registrado é permitido; divergir calado, não — e essa é a primeira lição deste repositório.
- **Protegido por:** sem teste — está aqui, que é onde a próxima sessão vai procurar.
