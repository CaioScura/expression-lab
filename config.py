# ===== Configuracoes do projeto =====
CAMINHO_MODELO_ROSTO = "models/face_landmarker.task"
CAMINHO_MODELO_MAOS = "models/hand_landmarker.task"
CAMINHO_GESTOS = "gestos.json"
CAMINHO_CSV = "dados_gestos.csv"

# Angulo minimo (graus) para considerar um dedo estendido
ANGULO_DEDO_ESTENDIDO = 160
# Quanto a ponta do polegar precisa estar mais longe que a base
FATOR_POLEGAR_ESTENDIDO = 1.2

# Nomes das janelas
JANELA_PRINCIPAL = "Expression Lab - Deteccao Facial"
JANELA_IMAGEM = "Imagem do gesto"

# Quantos frames seguidos o gesto precisa aparecer para trocar a imagem
FRAMES_PARA_CONFIRMAR = 5

# Intervalo minimo entre dois exemplos registrados na coleta
INTERVALO_REGISTRO_MS = 200
