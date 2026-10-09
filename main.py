
import cv2
import mediapipe as mp

# Caminho do modelo facial
CAMINHO_MODELO = "models/face_landmarker.task"

# Configuração do MediaPipe
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

opcoes = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=CAMINHO_MODELO),
    running_mode=RunningMode.VIDEO,
    num_faces=1
)

# Inicializa o detector facial
with FaceLandmarker.create_from_options(opcoes) as detector:
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

        # Desenha os pontos encontrados
        if resultado.face_landmarks:
            altura, largura, _ = frame.shape

            for rosto in resultado.face_landmarks:
                for ponto in rosto:
                    x = int(ponto.x * largura)
                    y = int(ponto.y * altura)

                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        cv2.imshow("Expression Lab - Deteccao Facial", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()