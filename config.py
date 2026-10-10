# ===== Configuracoes do projeto =====
CAMINHO_MODELO_ROSTO = "models/face_landmarker.task"
CAMINHO_MODELO_MAOS = "models/hand_landmarker.task"
CAMINHO_GESTOS = "gestos.json"
CAMINHO_CSV = "dados_gestos.csv"

# Imagem mostrada quando nenhum gesto cadastrado e reconhecido
CAMINHO_IMAGEM_PADRAO = "imagens/macaco-olhar-perdido.png"

# Angulo minimo (graus) para considerar um dedo estendido
ANGULO_DEDO_ESTENDIDO = 160
# Quanto a ponta do polegar precisa estar mais longe que a base
FATOR_POLEGAR_ESTENDIDO = 1.2

# Nomes das janelas
JANELA_PRINCIPAL = "Expression Lab - Deteccao Facial"
JANELA_IMAGEM = "Imagem do gesto"

# Tamanho (largura, altura) e posicao (x, y) fixos da janela da imagem.
# A webcam costuma ter 640x480, entao x=680 coloca a janela ao lado dela
TAMANHO_JANELA_IMAGEM = (480, 480)
POSICAO_JANELA_IMAGEM = (680, 50)

# Quantos frames seguidos o gesto precisa aparecer para trocar a imagem
FRAMES_PARA_CONFIRMAR = 5

# Intervalo minimo entre dois exemplos registrados na coleta
INTERVALO_REGISTRO_MS = 200
