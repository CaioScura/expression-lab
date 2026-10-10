import math

import cv2

from desenho import AMARELO, VERDE, escrever_texto, para_pixels


def calcular_abertura_boca(rosto, largura, altura):
    # Converte os pontos dos labios para pixels
    superior_xy = para_pixels(rosto[13], largura, altura)
    inferior_xy = para_pixels(rosto[14], largura, altura)
    esquerdo_xy = para_pixels(rosto[61], largura, altura)
    direito_xy = para_pixels(rosto[291], largura, altura)

    # Calcula as distancias entre os pontos
    abertura = math.dist(superior_xy, inferior_xy)
    largura_boca = math.dist(esquerdo_xy, direito_xy)

    # Normaliza a abertura pelo tamanho da boca
    if largura_boca == 0:
        return 0

    return abertura / largura_boca


def processar_rosto(frame, resultado_rosto):
    altura, largura, _ = frame.shape

    for rosto in resultado_rosto.face_landmarks:
        proporcao_abertura = calcular_abertura_boca(rosto, largura, altura)

        # Mostra quantos pontos foram detectados
        escrever_texto(frame, f"Pontos faciais: {len(rosto)}", (20, 40))

        escrever_texto(
            frame,
            f"Abertura da boca: {proporcao_abertura:.3f}",
            (20, 75),
            cor=AMARELO
        )

        for ponto in rosto:
            cv2.circle(
                frame,
                para_pixels(ponto, largura, altura),
                1,
                VERDE,
                -1
            )
