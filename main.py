
import cv2
import mediapipe as mp
import math

from mediapipe.tasks.python.vision import HandLandmarksConnections

# Caminho do modelo facial
CAMINHO_MODELO = "models/face_landmarker.task"

# Configuração do MediaPipe
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode


# Configuracao do detector de maos
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

opcoes_maos = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="models/hand_landmarker.task"
    ),
    running_mode=RunningMode.VIDEO,
    num_hands=2
)


#Configuração do detector facial
opcoes = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=CAMINHO_MODELO),
    running_mode=RunningMode.VIDEO,
    num_faces=1
)

# Inicializa o detector facial
with (
    FaceLandmarker.create_from_options(opcoes) as detector,
    HandLandmarker.create_from_options(opcoes_maos) as detector_maos
):
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Não foi possível acessar a webcam.")
        exit()

    while True:
        sucesso, frame = camera.read()

        if not sucesso:
            print("Não foi possível capturar a imagem.")
            break

        # OpenCV usa BGR; MediaPipe espera RGB
        imagem_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Converte a imagem para o formato do MediaPipe
        imagem_mp = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=imagem_rgb
        )

        # Tempo do vídeo em milissegundos
        tempo_ms = int(camera.get(cv2.CAP_PROP_POS_MSEC))

        # Detecta os pontos faciais
        resultado = detector.detect_for_video(imagem_mp, tempo_ms)


        #Detecta os pontos das mãos
        resultado_maos = detector_maos.detect_for_video(
            imagem_mp,
            tempo_ms
        )

        # Desenha os pontos e as conexoes das maos
        altura, largura, _ = frame.shape

        for mao in resultado_maos.hand_landmarks:
            # Desenha as conexoes entre os pontos
            for conexao in HandLandmarksConnections.HAND_CONNECTIONS:
                inicio = mao[conexao.start]
                fim = mao[conexao.end]

                x1, y1 = int(inicio.x * largura), int(inicio.y * altura)
                x2, y2 = int(fim.x * largura), int(fim.y * altura)

                cv2.line(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 0, 0),
                    2
                )

            # Desenha cada ponto da mao
            for ponto in mao:
                x = int(ponto.x * largura)
                y = int(ponto.y * altura)

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 255),
                    -1
                )


        # Desenha os pontos encontrados do rosto
        if resultado.face_landmarks:
            altura, largura, _ = frame.shape

            for rosto in resultado.face_landmarks:
                # Seleciona os pontos dos labios
                labio_superior = rosto[13]
                labio_inferior = rosto[14]
                canto_esquerdo = rosto[61]
                canto_direito = rosto[291]

                # Converte as coordenadas normalizadas para pixels
                superior_xy = (
                    labio_superior.x * largura,
                    labio_superior.y * altura
                )

                inferior_xy = (
                    labio_inferior.x * largura,
                    labio_inferior.y * altura
                )

                esquerdo_xy = (
                    canto_esquerdo.x * largura,
                    canto_esquerdo.y * altura
                )

                direito_xy = (
                    canto_direito.x * largura,
                    canto_direito.y * altura
                )

                # Calcula as distancias entre os pontos
                abertura = math.dist(superior_xy, inferior_xy)
                largura_boca = math.dist(esquerdo_xy, direito_xy)

                # Normaliza a abertura pelo tamanho da boca
                if largura_boca > 0:
                    proporcao_abertura = abertura / largura_boca
                else:
                    proporcao_abertura = 0

                # Mostra quantos pontos foram detectados
                quantidade = len(rosto)

                cv2.putText(
                    frame,
                    f"Pontos faciais: {quantidade}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                
                cv2.putText(
                    frame,
                    f"Abertura da boca: {proporcao_abertura:.3f}",
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

                for ponto in rosto:
                    x = int(ponto.x * largura)
                    y = int(ponto.y * altura)

                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        cv2.imshow("Expression Lab - Deteccao Facial", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()