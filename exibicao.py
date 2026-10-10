#import do json de gestos
import json

import cv2
import numpy as np

from config import (
    CAMINHO_GESTOS,
    CAMINHO_IMAGEM_PADRAO,
    FRAMES_PARA_CONFIRMAR,
    JANELA_IMAGEM,
    POSICAO_JANELA_IMAGEM,
    TAMANHO_JANELA_IMAGEM,
)


def ajustar_ao_tamanho(imagem, largura, altura):
    #redimensiona sem distorcer e centraliza sobre um fundo preto
    altura_original, largura_original = imagem.shape[:2]

    escala = min(largura / largura_original, altura / altura_original)
    nova_largura = int(largura_original * escala)
    nova_altura = int(altura_original * escala)

    redimensionada = cv2.resize(imagem, (nova_largura, nova_altura))

    fundo = np.zeros((altura, largura, 3), dtype=np.uint8)

    x = (largura - nova_largura) // 2
    y = (altura - nova_altura) // 2
    fundo[y:y + nova_altura, x:x + nova_largura] = redimensionada

    return fundo


def carregar_imagens_gestos():
    #le os gestos em gestos.json e devolve {nome do gesto: imagem ja carregada}
    with open(CAMINHO_GESTOS, "r", encoding="utf-8") as arquivo:
        gestos_cadastrados = json.load(arquivo)

    imagens_gestos = {}

    for nome_gesto, dados in gestos_cadastrados.items():
        caminho_imagem = dados["imagem"]
        imagem = cv2.imread(caminho_imagem)

        if imagem is not None:
            imagens_gestos[nome_gesto] = imagem
            print(f"{nome_gesto}: imagem carregada!")
        else:
            print(f"{nome_gesto}: não foi possível carregar {caminho_imagem}")

    return imagens_gestos


def carregar_imagem_padrao():
    imagem = cv2.imread(CAMINHO_IMAGEM_PADRAO)

    if imagem is None:
        raise FileNotFoundError(
            f"Imagem padrão não encontrada: {CAMINHO_IMAGEM_PADRAO}"
        )

    return imagem


class ExibidorImagem:
    #janela sempre aberta, mostra a imagem com o gesto ou imagem padrao
    def __init__(self, imagens_gestos, imagem_padrao):
        largura, altura = TAMANHO_JANELA_IMAGEM

        #ajusta o tamanho das imgens para ficar com tamanho padrao
        self.imagens_gestos = {
            nome: ajustar_ao_tamanho(imagem, largura, altura)
            for nome, imagem in imagens_gestos.items()
        }
        self.imagem_padrao = ajustar_ao_tamanho(imagem_padrao, largura, altura)

        self.candidato = None
        self.frames = 0


        #cria a janela na posicao fixa com a imagem padrao
        cv2.namedWindow(JANELA_IMAGEM)
        cv2.moveWindow(JANELA_IMAGEM, *POSICAO_JANELA_IMAGEM)
        self.mostrar(None)

    def tem_imagem(self, gesto):
        return gesto in self.imagens_gestos

    def mostrar(self, gesto):
        if gesto is None:
            cv2.imshow(JANELA_IMAGEM, self.imagem_padrao)
        else:
            cv2.imshow(JANELA_IMAGEM, self.imagens_gestos[gesto])

    def atualizar(self, gesto_com_imagem):
        #so muda a imagem se o gesto for diferente
        if gesto_com_imagem == self.candidato:
            self.frames += 1
        else:
            self.candidato = gesto_com_imagem
            self.frames = 1

        # None (sem gesto) tambem passa por aqui e volta para a padrao
        if self.frames == FRAMES_PARA_CONFIRMAR:
            self.mostrar(self.candidato)
