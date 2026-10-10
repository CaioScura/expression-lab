import math

from config import DISTANCIA_MAO_CABECA, DISTANCIA_MAO_ROSTO
from desenho import para_pixels
from gestos import classificar_gesto
from rosto import boca_aberta, classificar_expressao


#gestos de uma mao so
GESTOS_DE_UMA_MAO = (
    "Hang loose",
    "Faz o L",
    "Gato joia",
    "Mario dedo do meio",
    "Gato apontando",
    "Indicador levantado",
)


def perto(ponto, alvo, info_rosto):
    limite = info_rosto["largura_rosto"] * DISTANCIA_MAO_ROSTO

    return math.dist(ponto, alvo) < limite


def maos_levantadas(maos, info_rosto, altura):
    #maos acima do queixo
    queixo_y = info_rosto["queixo"][1]

    return all(mao[0].y * altura < queixo_y for mao in maos)


def maos_na_cabeca(maos, info_rosto, largura, altura):
    #maos perto da testa, acima da testa, e com a palma virada para frente
    testa = info_rosto["testa"]
    limite = info_rosto["largura_rosto"] * DISTANCIA_MAO_CABECA

    for mao in maos:
        centro_palma = para_pixels(mao[9], largura, altura)

        acima_da_testa = centro_palma[1] < testa[1]
        perto_da_testa = math.dist(centro_palma, testa) < limite

        if not (acima_da_testa and perto_da_testa):
            return False

    return True


def gesto_perto_do_rosto(mao, gesto_mao, info_rosto, largura, altura):
    pontos = [para_pixels(ponto, largura, altura) for ponto in mao]

    #gesto de silencio, mao indicador na boca
    if (
        gesto_mao in ("Indicador levantado", "Faz o L")
        and perto(pontos[8], info_rosto["boca"], info_rosto)
    ):
        return "Nao grita"

    #pensativo, mao no queixo
    ponto_mais_alto_y = min(y for _, y in pontos)
    mao_abaixo_da_boca = ponto_mais_alto_y > info_rosto["boca"][1]

    if mao_abaixo_da_boca and any(
        perto(ponto, info_rosto["queixo"], info_rosto) for ponto in pontos
    ):
        return "Pensativo"

    
    if perto(pontos[9], info_rosto["boca"], info_rosto):
        return "Gato mao na boca"

    return None


def reconhecer_gesto(maos, info_rosto, largura, altura):
    #decide um gesto final juntando mao e rosto
    gestos_maos = [classificar_gesto(mao) for mao in maos]


    #1 - 2 maos levantadas
    if (
        len(maos) == 2
        and info_rosto is not None
        and maos_levantadas(maos, info_rosto, altura)
    ):
        
        if maos_na_cabeca(maos, info_rosto, largura, altura):
            return "Macaco maos na cabeca"

        if boca_aberta(info_rosto):
            return "Maos pra cima"

        if all(gesto == "Mao aberta" for gesto in gestos_maos):
            return "Kojima cinema"


    #2 - mao enconstando no rosto
    if info_rosto is not None:
        for mao, gesto_mao in zip(maos, gestos_maos):
            gesto = gesto_perto_do_rosto(
                mao, gesto_mao, info_rosto, largura, altura
            )

            if gesto is not None:
                return gesto


    #3 - gesto de uma mao so
    for gesto_mao in gestos_maos:
        if gesto_mao in GESTOS_DE_UMA_MAO:
            return gesto_mao


    #4 - expressao facial
    if info_rosto is not None:
        expressao = classificar_expressao(info_rosto)

        if expressao is not None:
            return expressao


    #5 - sem gesto com a mao
    if gestos_maos:
        return gestos_maos[0]

    return None
