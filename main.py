import time

import cv2
import mediapipe as mp

from config import (
    CAMINHO_MODELO_MAOS,
    CAMINHO_MODELO_ROSTO,
    JANELA_PRINCIPAL,
)
from coleta import alternar_coleta, coletar_exemplo, encerrar_coleta
from desenho import desenhar_mao, mostrar_info_mao
from exibicao import ExibidorImagem, carregar_imagens_gestos
from gestos import classificar_gesto, extrair_caracteristicas_mao
from rosto import processar_rosto


# ===== Configuracao do MediaPipe =====
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

opcoes_maos = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=CAMINHO_MODELO_MAOS),
    running_mode=RunningMode.VIDEO,
    num_hands=2
)

opcoes_rosto = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=CAMINHO_MODELO_ROSTO),
    running_mode=RunningMode.VIDEO,
    num_faces=1
)


# ===== Processamento de cada frame =====
def detectar(frame, detector_rosto, detector_maos, tempo_ms):
    #openCV usa BGR; MediaPipe usa RGB, converta a imagem
    imagem_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #converte a imagem para o formato do MediaPipe
    imagem_mp = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=imagem_rgb
    )

    resultado_rosto = detector_rosto.detect_for_video(imagem_mp, tempo_ms)
    resultado_maos = detector_maos.detect_for_video(imagem_mp, tempo_ms)

    return resultado_rosto, resultado_maos


#Funcao para processar as maos, classificar o gesto e desenhar na tela o gesto caso tenha
def processar_maos(frame, resultado_maos, exibidor):
    altura, largura, _ = frame.shape
    gesto_com_imagem = None

    for mao in resultado_maos.hand_landmarks:
        caracteristicas = extrair_caracteristicas_mao(mao)
        gesto = classificar_gesto(caracteristicas)

        if exibidor.tem_imagem(gesto):
            gesto_com_imagem = gesto

        mostrar_info_mao(frame, caracteristicas, gesto)
        desenhar_mao(frame, mao, largura, altura)

    return gesto_com_imagem


# ===== Programa principal =====
def main():
    exibidor = ExibidorImagem(carregar_imagens_gestos())

    # Estado da coleta de exemplos (tecla "c")
    estado_coleta = {
        "ativa": False,
        "nome_gesto": "",
        "dados": [],
        "ultimo_registro_ms": 0
    }

    with (
        FaceLandmarker.create_from_options(opcoes_rosto) as detector_rosto,
        HandLandmarker.create_from_options(opcoes_maos) as detector_maos
    ):
        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            print("Não foi possível acessar a webcam.")
            return

        while True:
            sucesso, frame = camera.read()

            if not sucesso:
                print("Não foi possível capturar a imagem.")
                break


            #tempo em ms
            tempo_ms = int(time.monotonic() * 1000)

            resultado_rosto, resultado_maos = detectar(
                frame, detector_rosto, detector_maos, tempo_ms
            )

            gesto_com_imagem = processar_maos(frame, resultado_maos, exibidor)
            exibidor.atualizar(gesto_com_imagem)

            processar_rosto(frame, resultado_rosto)

            cv2.imshow(JANELA_PRINCIPAL, frame)

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == ord("q"):
                break

            if tecla == ord("c"):
                alternar_coleta(estado_coleta)
            elif estado_coleta["ativa"]:
                coletar_exemplo(estado_coleta, resultado_maos)
                

        # Se saiu com a coleta ainda ativa, salva o que foi coletado
        if estado_coleta["ativa"]:
            encerrar_coleta(estado_coleta)

        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
