"""Testes das regras do jogo — rodam sem pygame e sem abrir janela.

Cada teste guarda o porquê de uma regra existir. Quando um deles quebrar, leia a docstring
antes de mexer no código: ela diz o que a pessoa que joga perderia.
"""

import ast
import unicodedata
from pathlib import Path

import pytest

from termo import jogo as modulo_jogo
from termo import palavras as modulo_palavras
from termo.jogo import (
    AVISO_FALTAM_LETRAS,
    AVISO_LETRA_ELIMINADA,
    MAXIMO_TENTATIVAS,
    TAMANHO_PALAVRA,
    Jogo,
    Marca,
    Situacao,
    avaliar,
)

CERTA = Marca.CERTA
DESLOCADA = Marca.DESLOCADA
AUSENTE = Marca.AUSENTE


def marcas(chute: str, secreta: str) -> list[Marca]:
    """Atalho: só as cores de um chute, sem as letras, para o teste caber numa linha."""
    return [letra.marca for letra in avaliar(chute, secreta)]


def exibicao(chute: str, secreta: str) -> str:
    """Atalho: só o texto que apareceria na tela depois de avaliar o chute."""
    return "".join(letra.letra for letra in avaliar(chute, secreta))


def modulos_importados_por(modulo) -> set[str]:
    """Lê o código-fonte de um módulo e devolve os nomes que ele importa."""
    importados: set[str] = set()
    codigo = Path(modulo.__file__).read_text(encoding="utf-8")
    for no in ast.walk(ast.parse(codigo)):
        if isinstance(no, ast.Import):
            importados.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module.split(".")[0])
    return importados


# ----- A fronteira do projeto -----


def test_as_regras_nao_dependem_de_pygame():
    """Nem `jogo.py` nem `palavras.py` podem importar pygame.

    Por quê: é a regra de ouro deste projeto — as regras têm de rodar sem abrir janela. E o
    pygame está instalado de qualquer jeito, então um `import pygame` no meio das regras
    deixaria a suíte inteira verde: a fronteira dependeria de alguém reparar no diff.
    """
    for modulo in (modulo_jogo, modulo_palavras):
        assert "pygame" not in modulos_importados_por(modulo), (
            f"{modulo.__name__} passou a importar pygame — leia a regra de ouro no CLAUDE.md"
        )


# ----- Avaliar um chute -----


def test_acertar_a_palavra_deixa_tudo_verde():
    """Chutar a palavra exata pinta as cinco letras de verde — é o fim feliz do jogo."""
    assert marcas("TERMO", "TERMO") == [CERTA] * 5


def test_letra_no_lugar_certo_fica_verde():
    """Letra certa na posição certa é verde, mesmo com o resto do chute errado."""
    assert marcas("TUDOS", "TERMO")[0] is CERTA


def test_letra_que_nao_existe_fica_cinza():
    """Letra que não está na palavra fica cinza — é o que elimina opções."""
    assert marcas("ZZZZZ", "TERMO") == [AUSENTE] * 5


def test_letra_em_outro_lugar_fica_amarela():
    """Letra que existe, mas noutra posição, fica amarela.

    Sem isso o jogo perde a graça: amarelo é a única dica que diz "você está perto".
    """
    assert marcas("OTERM", "TERMO") == [DESLOCADA] * 5


def test_letra_repetida_no_chute_nao_acende_duas_vezes():
    """Chutar a mesma letra duas vezes numa palavra que só tem uma acende apenas uma.

    Por quê: é o erro clássico de quem implementa este jogo num passo só. Em TETRA contra
    TERMO, o primeiro T é verde e o segundo TEM de ser cinza — se os dois acendessem, a
    pessoa concluiria que existem dois Ts na palavra e jogaria a partida inteira errado.
    """
    assert marcas("TETRA", "TERMO") == [CERTA, CERTA, AUSENTE, DESLOCADA, AUSENTE]


def test_letra_repetida_acende_tantas_vezes_quantas_existem():
    """Chutar cinco letras iguais acende só as que a palavra realmente tem.

    Por quê: AMORA tem dois As, nas pontas. Chutar AAAAA tem de devolver exatamente dois
    verdes e três cinzas — nem mais nem menos, senão a contagem de letras está furada.
    """
    assert marcas("AAAAA", "AMORA") == [CERTA, AUSENTE, AUSENTE, AUSENTE, CERTA]


def test_letra_repetida_na_palavra_pode_gerar_dois_amarelos():
    """Quando a palavra tem a letra duas vezes, dois amarelos são legítimos.

    Por quê: o teste acima não pode ser "consertado" limitando a um amarelo por letra.
    Em ALADO contra AMORA, o segundo A é amarelo porque AMORA ainda tem outro A sobrando.
    """
    assert marcas("ALADO", "AMORA") == [CERTA, AUSENTE, DESLOCADA, AUSENTE, DESLOCADA]


def test_chute_de_outro_tamanho_e_recusado():
    """Avaliar um chute de tamanho diferente estoura na hora, em vez de devolver bobagem."""
    with pytest.raises(ValueError):
        avaliar("OI", "TERMO")


# ----- Acentos -----


def test_chute_sem_acento_acerta_palavra_acentuada():
    """Quem digita LICAO acerta LIÇÃO.

    Por quê: o teclado de quem joga nem sempre tem acento fácil, e perder uma das seis
    tentativas por não saber onde vai o til seria castigo por ortografia, não por dedução.
    """
    assert marcas("LICAO", "LIÇÃO") == [CERTA] * 5


def test_acento_aparece_na_tela_quando_a_letra_esta_no_lugar_certo():
    """A letra verde volta acentuada para a tela, como no Termo original."""
    assert exibicao("LICAO", "LIÇÃO") == "LIÇÃO"


def test_letra_amarela_nao_revela_o_acento():
    """Letra amarela aparece sem acento.

    Por quê: mostrar o Ç num quadradinho amarelo entregaria de graça uma informação que o
    jogo original só dá quando você acerta a posição.
    """
    assert exibicao("CALOS", "LIÇÃO") == "CALOS"


# ----- Digitar, apagar e enviar -----


def test_digitar_monta_o_chute_letra_por_letra():
    """Digitar acrescenta ao chute atual — é o gesto principal do jogo."""
    jogo = Jogo("TERMO")
    for tecla in "CASA":
        jogo.digitar(tecla)
    assert jogo.digitando == "CASA"


def test_digitar_aceita_letra_acentuada_do_teclado():
    """Quem tem teclado ABNT e digita ç ou á vê a letra sem acento no quadradinho."""
    jogo = Jogo("TERMO")
    jogo.digitar("ç")
    jogo.digitar("á")
    assert jogo.digitando == "CA"


def test_digitar_ignora_tecla_que_nao_e_letra():
    """Número, espaço e pontuação não entram no chute — senão a grade mostraria lixo."""
    jogo = Jogo("TERMO")
    for tecla in "1 -%":
        jogo.digitar(tecla)
    assert jogo.digitando == ""


def test_nao_da_para_digitar_a_sexta_letra():
    """O chute para na quinta letra: a palavra tem cinco, e a grade também."""
    jogo = Jogo("TERMO")
    for tecla in "CARROS":
        jogo.digitar(tecla)
    assert jogo.digitando == "CARRO"


def test_apagar_remove_a_ultima_letra():
    """Backspace desfaz a última letra — é como a pessoa corrige um erro de digitação."""
    jogo = Jogo("TERMO")
    for tecla in "CASA":
        jogo.digitar(tecla)
    jogo.apagar()
    assert jogo.digitando == "CAS"


def test_chute_incompleto_nao_gasta_tentativa():
    """Enter com o chute pela metade avisa e não consome uma das seis chances.

    Por quê: apertar Enter cedo demais é escorregão de dedo, não jogada. Gastar tentativa
    por isso faria a pessoa perder a partida sem ter errado nenhum palpite.
    """
    jogo = Jogo("TERMO")
    jogo.digitar("A")
    assert jogo.enviar() is False
    assert jogo.tentativas == []
    assert jogo.aviso == AVISO_FALTAM_LETRAS
    assert jogo.digitando == "A"


def test_enviar_guarda_a_tentativa_e_limpa_o_que_estava_digitado():
    """Depois de enviar, a linha vira histórico e a próxima começa vazia."""
    jogo = Jogo("TERMO")
    for tecla in "CASAL":
        jogo.digitar(tecla)
    assert jogo.enviar() is True
    assert len(jogo.tentativas) == 1
    assert jogo.digitando == ""


# ----- Letra eliminada -----


def test_letra_marcada_ausente_nao_pode_ser_digitada_de_novo():
    """Uma letra que já saiu cinza não entra mais no chute.

    Por quê: depois que o jogo já disse que a letra não está na palavra, deixar digitar ela de
    novo não ajuda em nada — só faz quem está aprendendo a jogar por eliminação perder tempo, ou
    achar que a letra "pode ter mudado".
    """
    jogo = Jogo("TERMO")
    for tecla in "CASAL":
        jogo.digitar(tecla)
    jogo.enviar()  # C, A, S e L saem cinza contra TERMO

    jogo.digitar("C")
    assert jogo.digitando == ""
    assert jogo.aviso == AVISO_LETRA_ELIMINADA


def test_letra_com_uma_ocorrencia_certa_e_outra_ausente_continua_digitavel():
    """Letra repetida no chute, com uma ocorrência certa e outra cinza, continua liberada.

    Por quê: em TETRA contra TERMO, o segundo T fica cinza só porque apareceu demais no
    chute — o T existe na palavra (o primeiro é verde). Bloquear T pela ocorrência cinza
    impediria chutar qualquer palavra nova com essa letra, mesmo ela estando certa.
    """
    jogo = Jogo("TERMO")
    for tecla in "TETRA":
        jogo.digitar(tecla)
    jogo.enviar()
    assert jogo.letras_usadas()["T"] is CERTA

    jogo.digitar("T")
    assert jogo.digitando == "T"


def test_digitar_letra_valida_limpa_aviso_de_letra_eliminada():
    """Depois do aviso de letra eliminada, digitar uma letra válida limpa o recado.

    Por quê: senão o aviso "Letra já eliminada" ficaria preso na tela mesmo depois da pessoa
    corrigir e seguir jogando normalmente.
    """
    jogo = Jogo("TERMO")
    for tecla in "CASAL":
        jogo.digitar(tecla)
    jogo.enviar()

    jogo.digitar("C")
    assert jogo.aviso == AVISO_LETRA_ELIMINADA
    jogo.digitar("B")
    assert jogo.aviso == ""


# ----- Fim de partida -----


def test_acertar_termina_a_partida_com_vitoria():
    """Acertar encerra a partida na hora, mesmo sobrando tentativa."""
    jogo = Jogo("TERMO")
    for tecla in "TERMO":
        jogo.digitar(tecla)
    jogo.enviar()
    assert jogo.situacao is Situacao.VITORIA
    assert jogo.acabou


def test_errar_todas_as_tentativas_termina_em_derrota_e_revela_a_palavra():
    """Na sexta errada o jogo acaba e conta qual era a palavra.

    Por quê: terminar sem revelar deixa a pessoa sem aprender nada com a derrota — e a
    palavra secreta não tem mais nenhum valor depois do fim.

    O chute repetido é OTERM — um anagrama de TERMO fora de ordem: como usa exatamente as
    letras da secreta, nenhuma delas fica cinza, e por isso pode ser digitado de novo em
    todas as seis tentativas sem cair na regra de letra eliminada.
    """
    jogo = Jogo("TERMO")
    for _ in range(MAXIMO_TENTATIVAS):
        for tecla in "OTERM":
            jogo.digitar(tecla)
        jogo.enviar()
    assert jogo.situacao is Situacao.DERROTA
    assert "TERMO" in jogo.aviso


def test_partida_acabada_ignora_o_teclado():
    """Depois do fim, digitar e enviar não fazem nada — a grade fica congelada."""
    jogo = Jogo("TERMO")
    for tecla in "TERMO":
        jogo.digitar(tecla)
    jogo.enviar()

    jogo.digitar("A")
    jogo.apagar()
    assert jogo.digitando == ""
    assert jogo.enviar() is False
    assert len(jogo.tentativas) == 1


def test_tentativas_restantes_diminui_a_cada_chute():
    """O contador de chances reflete o que já foi gasto."""
    jogo = Jogo("TERMO")
    assert jogo.tentativas_restantes == MAXIMO_TENTATIVAS
    for tecla in "CASAL":
        jogo.digitar(tecla)
    jogo.enviar()
    assert jogo.tentativas_restantes == MAXIMO_TENTATIVAS - 1


def test_reiniciar_limpa_a_grade():
    """Reiniciar devolve uma partida zerada, pronta para o primeiro chute."""
    jogo = Jogo("TERMO")
    for tecla in "CASAL":
        jogo.digitar(tecla)
    jogo.enviar()
    jogo.reiniciar()
    assert jogo.tentativas == []
    assert jogo.digitando == ""
    assert jogo.situacao is Situacao.JOGANDO


def test_palavra_secreta_de_tamanho_errado_e_recusada():
    """Começar uma partida com palavra que não tem 5 letras falha na hora.

    Por quê: a grade tem cinco colunas. Uma palavra de seis letras só apareceria como bug
    estranho no meio do jogo, e o erro aqui diz exatamente o que está errado.
    """
    with pytest.raises(ValueError):
        Jogo("PALAVRA")


def test_palavra_escrita_com_acento_solto_e_arrumada():
    """Palavra com o acento separado da letra é normalizada ao começar a partida.

    Por quê: LIÇÃO pode vir escrito com o Ç inteiro ou com um C seguido de uma cedilha solta —
    parecem iguais na tela, mas o segundo tem 7 caracteres, e a grade mostraria um acento
    sozinho num quadradinho. Isso acontece de verdade ao colar uma lista de palavras da
    internet.
    """
    jogo = Jogo(unicodedata.normalize("NFD", "LIÇÃO"))
    assert jogo.secreta == "LIÇÃO"
    assert len(jogo.secreta) == TAMANHO_PALAVRA


# ----- Teclado da tela -----


def test_teclado_guarda_a_melhor_marca_de_cada_letra():
    """Uma letra que já ficou verde não volta a amarelo num chute posterior.

    Por quê: o teclado colorido é um resumo do que já se sabe. Se o T rebaixasse de verde
    para amarelo, a pessoa acharia que tinha errado a posição que já tinha acertado.
    """
    jogo = Jogo("TERMO")
    for tecla in "TECLA":
        jogo.digitar(tecla)
    jogo.enviar()
    assert jogo.letras_usadas()["T"] is CERTA

    for tecla in "MOTOR":
        jogo.digitar(tecla)
    jogo.enviar()
    assert jogo.letras_usadas()["T"] is CERTA
    assert jogo.letras_usadas()["C"] is AUSENTE
