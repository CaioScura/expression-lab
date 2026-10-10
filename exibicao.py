#import do json de gestos
import json

import cv2

from config import CAMINHO_GESTOS, FRAMES_PARA_CONFIRMAR, JANELA_IMAGEM


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


class ExibidorImagem:
    # Abre e fecha a janela com a imagem do gesto reconhecido
    def __init__(self, imagens_gestos):
        self.imagens_gestos = imagens_gestos
        self.candidato = None
        self.frames = 0
        self.aberta = False

    def tem_imagem(self, gesto):
        return gesto in self.imagens_gestos

    def atualizar(self, gesto_com_imagem):
        #so muda a imagem se o gesto for diferente
        if gesto_com_imagem == self.candidato:
            self.frames += 1
        else:
            self.candidato = gesto_com_imagem
            self.frames = 1

        if self.frames == FRAMES_PARA_CONFIRMAR:
            if self.candidato is not None:
                cv2.imshow(JANELA_IMAGEM, self.imagens_gestos[self.candidato])
                self.aberta = True
            elif self.aberta:
                cv2.destroyWindow(JANELA_IMAGEM)
                self.aberta = False
