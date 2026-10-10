# ===== Configuracoes do projeto =====
CAMINHO_MODELO_ROSTO = "models/face_landmarker.task"
CAMINHO_MODELO_MAOS = "models/hand_landmarker.task"
CAMINHO_GESTOS = "gestos.json"

# Imagem mostrada quando nenhum gesto cadastrado e reconhecido
CAMINHO_IMAGEM_PADRAO = "imagens/macaco-olhar-perdido.png"

# Imagem mostrada quando fica muito tempo sem nenhum gesto
CAMINHO_IMAGEM_OCIOSA = "imagens/gato-frente.png"
SEGUNDOS_PARA_IMAGEM_OCIOSA = 10

# Angulo minimo (graus) para considerar um dedo estendido
ANGULO_DEDO_ESTENDIDO = 160
# Quanto a ponta do polegar precisa estar mais longe que a base
FATOR_POLEGAR_ESTENDIDO = 1.2

# Mao "perto" do rosto: distancia menor que esta fracao da largura do rosto
DISTANCIA_MAO_ROSTO = 0.35
# Mao "em cima da cabeca": centro da palma ate a testa, em larguras de rosto
DISTANCIA_MAO_CABECA = 1.0


#limites das expressoes
LIMITE_BOCA_ABERTA = 0.5         
LIMITE_NOJO = 0.5                
LIMITE_OLHOS_ARREGALADOS = 0.35  
LIMITE_OLHAR_DE_LADO = 0.6       

# Nomes das janelas
JANELA_PRINCIPAL = "Expression Lab - Deteccao Facial"
JANELA_IMAGEM = "Imagem do gesto"


#tamanho da janela
TAMANHO_JANELA_IMAGEM = (480, 480)
POSICAO_JANELA_IMAGEM = (680, 50)

# Quantos frames seguidos o gesto precisa aparecer para trocar a imagem
FRAMES_PARA_CONFIRMAR = 5