import time

import cv2
import mediapipe as mp

from config import (
    CAMINHO_IMAGEM_OCIOSA,
    CAMINHO_IMAGEM_PADRAO,
    CAMINHO_MODELO_MAOS,
    CAMINHO_MODELO_ROSTO,
    JANELA_PRINCIPAL,
)
from desenho import desenhar_mao, mostrar_gesto
from exibicao import (
    ExibidorImagem,
    carregar_imagem_obrigatoria,
    carregar_imagens_gestos,
)
from reconhecimento import reconhecer_gesto
from rosto import desenhar_rosto, extrair_info_rosto


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
    num_faces=1,
    # Notas de 0 a 1 para expressoes (boca aberta, olhos arregalados...)
    output_face_blendshapes=True
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


# ===== Programa principal =====
def main():
    exibidor = ExibidorImagem(
        carregar_imagens_gestos(),
        carregar_imagem_obrigatoria(CAMINHO_IMAGEM_PADRAO),
        carregar_imagem_obrigatoria(CAMINHO_IMAGEM_OCIOSA)
    )

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

            altura, largura, _ = frame.shape
            maos = resultado_maos.hand_landmarks

            # Decide o gesto juntando maos e rosto
            info_rosto = extrair_info_rosto(resultado_rosto, largura, altura)
            gesto = reconhecer_gesto(maos, info_rosto, largura, altura)

            # So manda para a janela de imagens gestos que tem imagem
            if exibidor.tem_imagem(gesto):
                exibidor.atualizar(gesto)
            else:
                exibidor.atualizar(None)

            # Desenha tudo no frame da camera
            for mao in maos:
                desenhar_mao(frame, mao, largura, altura)

            desenhar_rosto(frame, resultado_rosto)
            mostrar_gesto(frame, gesto)

            cv2.imshow(JANELA_PRINCIPAL, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
