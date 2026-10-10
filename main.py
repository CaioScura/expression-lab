
import cv2
import mediapipe as mp
import math

#para salvar os gestos em uma tabela CSV
import csv

#verificar se o arquivo existe
import os

#import do json de gestos
import json



with open("gestos.json", "r", encoding="utf-8") as arquivo:
    gestos_cadastrados = json.load(arquivo)

for nome_gesto, dados in gestos_cadastrados.items():
    caminho_imagem = dados["imagem"]

    if os.path.exists(caminho_imagem):
        print(f"{nome_gesto}: imagem encontrada!")
    else:
        print(f"{nome_gesto}: imagem NÃO encontrada em {caminho_imagem}")


# Exemplos coletados para treinar o classificador
dados_treinamento = []
coletando_gesto = False

#controlar intervalo entre os registros de gestos
ultimo_registro_ms = 0
INTERVALO_REGISTRO_MS = 200


#nome do gesto
nome_gesto_atual = ""

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


def dedo_estendido(mao, pontos):
    angulo = calcular_angulo_dedo(mao, pontos)

    return angulo > 160


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
            "estendido": angulo > 160
        }

    return caracteristicas



def transformar_em_vetor(caracteristicas):
    return [
        caracteristicas["indicador"]["angulo"],
        caracteristicas["medio"]["angulo"],
        caracteristicas["anelar"]["angulo"],
        caracteristicas["minimo"]["angulo"]
    ]

#funcao que recebe um vetor e o nome do gesto, monta um registro e o adiciona à lista
def registrar_exemplo(vetor, nome_gesto):
    exemplo = {
        "caracteristicas": vetor,
        "gesto": nome_gesto
    }

    dados_treinamento.append(exemplo)


#funcao que salva os dados coletados em um arquivo CSV
def salvar_dados_csv():
    caminho_arquivo = "dados_gestos.csv"
    arquivo_existe = os.path.exists(caminho_arquivo)

    with open(
        caminho_arquivo,
        "a",
        newline="",
        encoding="utf-8"
    ) as arquivo:
        escritor = csv.writer(arquivo)

        if not arquivo_existe:
            escritor.writerow([
                "indicador",
                "medio",
                "anelar",
                "minimo",
                "gesto"
            ])

        for exemplo in dados_treinamento:
            escritor.writerow(
                exemplo["caracteristicas"]
                + [exemplo["gesto"]]
            )

    print("Dados adicionados em dados_gestos.csv")


def classificar_gesto(caracteristicas):
    indicador = caracteristicas["indicador"]["estendido"]
    medio = caracteristicas["medio"]["estendido"]
    anelar = caracteristicas["anelar"]["estendido"]
    minimo = caracteristicas["minimo"]["estendido"]

    dedos = [indicador, medio, anelar, minimo]

    if all(dedos):
        return "Mao aberta"

    if not any(dedos):
        return "Mao fechada"

    if indicador and not medio and not anelar and not minimo:
        return "Indicador levantado"

    return "Gesto nao identificado"

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
            # Seleciona os pontos do indicador
            base_indicador = mao[5]
            articulacao_media = mao[6]
            articulacao_superior = mao[7]
            ponta_indicador = mao[8]


           # Extrai as caracteristicas da mao 
            caracteristicas = extrair_caracteristicas_mao(mao)

            vetor = transformar_em_vetor(caracteristicas)
            print(vetor)

            indicador = caracteristicas["indicador"]["estendido"]
            medio = caracteristicas["medio"]["estendido"]
            anelar = caracteristicas["anelar"]["estendido"]
            minimo = caracteristicas["minimo"]["estendido"]


            # Classifica o gesto da mao com base nos dedos estendidos
            gesto = classificar_gesto(caracteristicas)


            # Mostra o gesto detectado na tela
            cv2.putText(
                frame,
                f"Gesto: {gesto}",
                (20, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )
            
            
            
            texto_dedos = (
                f"Indicador: {indicador} | Medio: {medio}"
            )

            cv2.putText(
                frame,
                texto_dedos,
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )

            texto_outros = f"Anelar: {anelar} | Minimo: {minimo}"

            cv2.putText(
                frame,
                texto_outros,
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )

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

        
        tecla = cv2.waitKey(1) & 0xFF

        
        
        
        if tecla == ord("c"):
            coletando_gesto = not coletando_gesto

            if coletando_gesto:
                nome_gesto_atual = input(
                    "Digite o nome do gesto que deseja cadastrar: "
                ).strip()

                if not nome_gesto_atual:
                    print("Nome inválido. Coleta não iniciada.")
                    coletando_gesto = False
                else:
                    dados_treinamento = []
                    ultimo_registro_ms = 0
                    print(
                        f"Coleta iniciada para: {nome_gesto_atual}"
                    )
            else:
                print(
                    f"Coleta encerrada. "
                    f"Exemplos registrados: {len(dados_treinamento)}"
                )

        
        elif coletando_gesto:
            tempo_atual_ms = cv2.getTickCount() / cv2.getTickFrequency() * 1000

            if (
                resultado_maos.hand_landmarks
                and tempo_atual_ms - ultimo_registro_ms >= INTERVALO_REGISTRO_MS
            ):
                mao = resultado_maos.hand_landmarks[0]

                caracteristicas = extrair_caracteristicas_mao(mao)
                vetor = transformar_em_vetor(caracteristicas)

                registrar_exemplo(vetor, nome_gesto_atual)

                ultimo_registro_ms = tempo_atual_ms


        if tecla == ord("q"):
            break

    camera.release()
    salvar_dados_csv()
    cv2.destroyAllWindows()