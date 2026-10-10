import math

from config import ANGULO_DEDO_ESTENDIDO, FATOR_POLEGAR_ESTENDIDO


def calcular_angulo(a, b, c):
    vetor_ba = (a.x - b.x, a.y - b.y)
    vetor_bc = (c.x - b.x, c.y - b.y)

    produto_escalar = (
        vetor_ba[0] * vetor_bc[0]
        + vetor_ba[1] * vetor_bc[1]
    )

    norma_ba = math.hypot(*vetor_ba)
    norma_bc = math.hypot(*vetor_bc)

    if norma_ba == 0 or norma_bc == 0:
        return 0

    cosseno = produto_escalar / (norma_ba * norma_bc)
    cosseno = max(-1, min(1, cosseno))

    return math.degrees(math.acos(cosseno))



def calcular_angulo_dedo(mao, pontos):
    articulacao_media = mao[pontos[1]]
    articulacao_superior = mao[pontos[2]]
    ponta = mao[pontos[3]]

    return calcular_angulo(
        articulacao_media,
        articulacao_superior,
        ponta
    )



def polegar_estendido(mao):
    base_minimo = (mao[17].x, mao[17].y)
    ponta = (mao[4].x, mao[4].y)
    base_polegar = (mao[2].x, mao[2].y)

    distancia_ponta = math.dist(ponta, base_minimo)
    distancia_base = math.dist(base_polegar, base_minimo)

    return distancia_ponta > distancia_base * FATOR_POLEGAR_ESTENDIDO


def extrair_caracteristicas_mao(mao):
    pontos_dedos = {
        "indicador": (5, 6, 7, 8),
        "medio": (9, 10, 11, 12),
        "anelar": (13, 14, 15, 16),
        "minimo": (17, 18, 19, 20)
    }

    caracteristicas = {}

    for dedo, pontos in pontos_dedos.items():
        angulo = calcular_angulo_dedo(mao, pontos)

        caracteristicas[dedo] = {
            "angulo": angulo,
            "estendido": angulo > ANGULO_DEDO_ESTENDIDO
        }

    caracteristicas["polegar"] = {
        "estendido": polegar_estendido(mao)
    }

    return caracteristicas



def polegar_para_cima(mao):
    return mao[4].y < mao[3].y < mao[2].y and mao[4].y < mao[5].y


def indicador_horizontal(mao):
    deslocamento_x = abs(mao[8].x - mao[5].x)
    deslocamento_y = abs(mao[8].y - mao[5].y)

    return deslocamento_x > deslocamento_y


def classificar_gesto(mao):
    caracteristicas = extrair_caracteristicas_mao(mao)

    indicador = caracteristicas["indicador"]["estendido"]
    medio = caracteristicas["medio"]["estendido"]
    anelar = caracteristicas["anelar"]["estendido"]
    minimo = caracteristicas["minimo"]["estendido"]
    polegar = caracteristicas["polegar"]["estendido"]

    dedos = [indicador, medio, anelar, minimo]
    so_indicador = indicador and not medio and not anelar and not minimo


    #mesmos nomes usados no gestos.json
    if polegar and minimo and not indicador and not medio and not anelar:
        return "Hang loose"

    if polegar and so_indicador:
        return "Faz o L"

    if polegar and not any(dedos) and polegar_para_cima(mao):
        return "Gato joia"

    if medio and not indicador and not anelar and not minimo:
        return "Mario dedo do meio"

    if all(dedos):
        return "Mao aberta"

    if not any(dedos):
        return "Mao fechada"

    if so_indicador:
        if indicador_horizontal(mao):
            return "Gato apontando"

        return "Indicador levantado"

    return "Gesto nao identificado"
