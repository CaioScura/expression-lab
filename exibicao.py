#import do json de gestos
import json
import time

import cv2
import numpy as np

from config import (
    CAMINHO_GESTOS,
    FRAMES_PARA_CONFIRMAR,
    JANELA_IMAGEM,
    POSICAO_JANELA_IMAGEM,
    SEGUNDOS_PARA_IMAGEM_OCIOSA,
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


def carregar_imagem_obrigatoria(caminho):
    #usada para as imagens padrao: sem elas a janela nao tem o que mostrar
    imagem = cv2.imread(caminho)

    if imagem is None:
        raise FileNotFoundError(f"Imagem não encontrada: {caminho}")

    return imagem


class ExibidorImagem:
    #janela sempre aberta, mostra a imagem com o gesto ou imagem padrao
    def __init__(self, imagens_gestos, imagem_padrao, imagem_ociosa):
        largura, altura = TAMANHO_JANELA_IMAGEM

        #ajusta o tamanho das imgens para ficar com tamanho padrao
        self.imagens_gestos = {
            nome: ajustar_ao_tamanho(imagem, largura, altura)
            for nome, imagem in imagens_gestos.items()
        }
        self.imagem_padrao = ajustar_ao_tamanho(imagem_padrao, largura, altura)
        self.imagem_ociosa = ajustar_ao_tamanho(imagem_ociosa, largura, altura)

        self.candidato = None
        self.frames = 0


        # Gesto que esta na tela (None = imagem padrao ou ociosa)
        self.gesto_exibido = None
        # Momento em que a tela ficou sem gesto
        self.inicio_sem_gesto = time.monotonic()
        self.ociosa = False


        #cria a janela na posicao fixa com a imagem padrao
        cv2.namedWindow(JANELA_IMAGEM)
        cv2.moveWindow(JANELA_IMAGEM, *POSICAO_JANELA_IMAGEM)
        self.mostrar(self.imagem_padrao)

    def tem_imagem(self, gesto):
        return gesto in self.imagens_gestos

    def mostrar(self, imagem):
        cv2.imshow(JANELA_IMAGEM, imagem)

    def atualizar(self, gesto_com_imagem):
        #so muda a imagem se o gesto se repetir por alguns frames
        if gesto_com_imagem == self.candidato:
            self.frames += 1
        else:
            self.candidato = gesto_com_imagem
            self.frames = 1

        gesto_confirmado = self.frames >= FRAMES_PARA_CONFIRMAR

        
        if gesto_confirmado and self.candidato != self.gesto_exibido:
            self.gesto_exibido = self.candidato

            if self.candidato is None:
                self.mostrar(self.imagem_padrao)
                self.inicio_sem_gesto = time.monotonic()
                self.ociosa = False
            else:
                self.mostrar(self.imagens_gestos[self.candidato])


        #muito tempo parado muda para a imagem ociosa
        tempo_sem_gesto = time.monotonic() - self.inicio_sem_gesto

        if (
            self.gesto_exibido is None
            and not self.ociosa
            and tempo_sem_gesto >= SEGUNDOS_PARA_IMAGEM_OCIOSA
        ):
            self.mostrar(self.imagem_ociosa)
            self.ociosa = True
