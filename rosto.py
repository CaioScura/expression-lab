import math

import cv2

from config import (
    LIMITE_BOCA_ABERTA,
    LIMITE_NOJO,
    LIMITE_OLHAR_DE_LADO,
    LIMITE_OLHOS_ARREGALADOS,
)
from desenho import VERDE, para_pixels


def extrair_info_rosto(resultado_rosto, largura, altura):
    #junta o que precisamos do rosto; devolve None se nao houver rosto
    if not resultado_rosto.face_landmarks:
        return None

    rosto = resultado_rosto.face_landmarks[0]

    blendshapes = {}

    if resultado_rosto.face_blendshapes:
        blendshapes = {
            categoria.category_name: categoria.score
            for categoria in resultado_rosto.face_blendshapes[0]
        }

    labio_superior = para_pixels(rosto[13], largura, altura)
    labio_inferior = para_pixels(rosto[14], largura, altura)


    boca = (
        (labio_superior[0] + labio_inferior[0]) / 2,
        (labio_superior[1] + labio_inferior[1]) / 2
    )


    largura_rosto = math.dist(
        para_pixels(rosto[234], largura, altura),
        para_pixels(rosto[454], largura, altura)
    )

    return {
        "blendshapes": blendshapes,
        "boca": boca,
        "queixo": para_pixels(rosto[152], largura, altura),
        "testa": para_pixels(rosto[10], largura, altura),
        "largura_rosto": largura_rosto
    }


def media_blendshapes(blendshapes, *nomes):
    return sum(blendshapes.get(nome, 0) for nome in nomes) / len(nomes)


def boca_aberta(info_rosto):
    return info_rosto["blendshapes"].get("jawOpen", 0) > LIMITE_BOCA_ABERTA


def classificar_expressao(info_rosto):
    blendshapes = info_rosto["blendshapes"]

    nojo = media_blendshapes(blendshapes, "noseSneerLeft", "noseSneerRight")

    if nojo > LIMITE_NOJO:
        return "Gato nojo"

    olhos_arregalados = media_blendshapes(
        blendshapes, "eyeWideLeft", "eyeWideRight"
    )

    if olhos_arregalados > LIMITE_OLHOS_ARREGALADOS:
        return "Olhar assustado"


    #olhando para o lado, um olho pra fora e outro pra dentro
    olhando_um_lado = media_blendshapes(
        blendshapes, "eyeLookOutLeft", "eyeLookInRight"
    )
    olhando_outro_lado = media_blendshapes(
        blendshapes, "eyeLookInLeft", "eyeLookOutRight"
    )

    if max(olhando_um_lado, olhando_outro_lado) > LIMITE_OLHAR_DE_LADO:
        return "Olhando de lado"

    return None


def desenhar_rosto(frame, resultado_rosto):
    altura, largura, _ = frame.shape

    for rosto in resultado_rosto.face_landmarks:
        for ponto in rosto:
            cv2.circle(
                frame,
                para_pixels(ponto, largura, altura),
                1,
                VERDE,
                -1
            )
