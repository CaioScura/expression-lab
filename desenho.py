import cv2
from mediapipe.tasks.python.vision import HandLandmarksConnections


# Cores no formato BGR (azul, verde, vermelho) usado pelo OpenCV
VERDE = (0, 255, 0)
AMARELO = (0, 255, 255)
AZUL = (255, 0, 0)


def escrever_texto(frame, texto, posicao, cor=VERDE, tamanho=0.8):
    cv2.putText(
        frame,
        texto,
        posicao,
        cv2.FONT_HERSHEY_SIMPLEX,
        tamanho,
        cor,
        2
    )


def para_pixels(ponto, largura, altura):
    #MediaPipe devolve cooredenadas entre 0 e 1, é convertido para px
    return int(ponto.x * largura), int(ponto.y * altura)


def mostrar_gesto(frame, gesto):
    #mostra so o nome do gesto reconhecido ("-" quando nao ha nenhum)
    escrever_texto(frame, f"Gesto: {gesto or '-'}", (20, 40))


def desenhar_mao(frame, mao, largura, altura):
    #desenha as conexoes entre os pontos da mao
    for conexao in HandLandmarksConnections.HAND_CONNECTIONS:
        inicio = para_pixels(mao[conexao.start], largura, altura)
        fim = para_pixels(mao[conexao.end], largura, altura)

        cv2.line(frame, inicio, fim, AZUL, 2)

    #desenha cada ponto da mao
    for ponto in mao:
        cv2.circle(
            frame,
            para_pixels(ponto, largura, altura),
            5,
            AMARELO,
            -1
        )
