#para salvar os gestos em uma tabela CSV
import csv

#verificar se o arquivo existe
import os

import cv2

from config import CAMINHO_CSV, INTERVALO_REGISTRO_MS
from gestos import extrair_caracteristicas_mao, transformar_em_vetor


#funcao que recebe um vetor e o nome do gesto, monta um registro e o adiciona à lista
def registrar_exemplo(dados, vetor, nome_gesto):
    exemplo = {
        "caracteristicas": vetor,
        "gesto": nome_gesto
    }

    dados.append(exemplo)


#funcao que salva os dados coletados em um arquivo CSV
def salvar_dados_csv(dados):
    if not dados:
        return

    arquivo_existe = os.path.exists(CAMINHO_CSV)

    with open(
        CAMINHO_CSV,
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

        for exemplo in dados:
            escritor.writerow(
                exemplo["caracteristicas"]
                + [exemplo["gesto"]]
            )

    print(f"Dados adicionados em {CAMINHO_CSV}")


def encerrar_coleta(estado):
    #salva os exemplos no CSV e limpa a lista para nao salvar duas vezes
    print(
        f"Coleta encerrada. "
        f"Exemplos registrados: {len(estado['dados'])}"
    )

    salvar_dados_csv(estado["dados"])

    estado["dados"] = []
    estado["ativa"] = False


def alternar_coleta(estado):
    #chamada quando a tecla "c" é pressionada, comecar ou encerrar a coleta
    if estado["ativa"]:
        encerrar_coleta(estado)
        return

    nome_gesto = input(
        "Digite o nome do gesto que deseja cadastrar: "
    ).strip()

    if not nome_gesto:
        print("Nome inválido. Coleta não iniciada.")
        return

    estado["ativa"] = True
    estado["nome_gesto"] = nome_gesto
    estado["dados"] = []
    estado["ultimo_registro_ms"] = 0
    print(f"Coleta iniciada para: {nome_gesto}")


def coletar_exemplo(estado, resultado_maos):
    # Registra a primeira mao detectada, respeitando o intervalo minimo
    if not resultado_maos.hand_landmarks:
        return

    tempo_atual_ms = cv2.getTickCount() / cv2.getTickFrequency() * 1000

    if tempo_atual_ms - estado["ultimo_registro_ms"] < INTERVALO_REGISTRO_MS:
        return

    mao = resultado_maos.hand_landmarks[0]

    caracteristicas = extrair_caracteristicas_mao(mao)
    vetor = transformar_em_vetor(caracteristicas)

    registrar_exemplo(estado["dados"], vetor, estado["nome_gesto"])

    estado["ultimo_registro_ms"] = tempo_atual_ms
