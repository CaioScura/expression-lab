# Expression Lab

Reconhecimento de gestos e expressões faciais em tempo real pela webcam. Cada gesto reconhecido mostra um meme correspondente numa janela ao lado da câmera.

Feito em Python com [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/guide) (detecção de mãos e rosto) e [OpenCV](https://opencv.org/) (câmera e janelas).

---

## Como funciona

O programa abre duas janelas:

- **Câmera:** a imagem da webcam com os pontos das mãos e do rosto desenhados e o nome do gesto reconhecido.
- **Imagem do gesto:** mostra o meme do gesto atual, sempre com o mesmo tamanho e na mesma posição.

A janela de imagem segue este ciclo:

```
macaco-olhar-perdido ──10s sem gesto──▶ gato-frente
        ▲                                    │
        │                               faz um gesto
  sai do gesto                               │
        │                                    ▼
        └────────────────────────── imagem do gesto
```

A imagem só troca quando o gesto se repete por alguns frames seguidos. Assim ela não fica piscando se a detecção falhar por um instante.

A cada frame acontece o seguinte:

1. O MediaPipe encontra os **21 pontos de cada mão** (até 2 mãos) e os **478 pontos do rosto**, além de 52 notas de expressão (*blendshapes*), como boca aberta, olhos arregalados e nariz franzido.
2. Para cada dedo, o programa calcula se ele está **esticado ou dobrado** pelo ângulo das articulações. O polegar usa a distância até a base do dedo mínimo.
3. As regras em `reconhecimento.py` juntam mãos e rosto e decidem **um** gesto final.
4. Se o gesto tiver uma imagem cadastrada em `gestos.json`, ela aparece na janela.

---

## Gestos reconhecidos

Quando mais de um gesto se encaixa ao mesmo tempo, vale o de cima da tabela.

| Gesto | Como fazer | Imagem |
|---|---|---|
| Macaco mãos na cabeça | As duas mãos em cima da cabeça | `macaco-maos-atras-da-cabeca.png` |
| Mãos pra cima | As duas mãos levantadas acima do queixo, com a boca aberta | `maos-pra-cima.png` |
| Kojima cinema | As duas mãos abertas levantadas ao lado da cabeça, com a boca fechada | `kojima-cinema.png` |
| Não grita | Indicador levantado encostado na boca ("shhh") | `nao-grita.jpg` |
| Pensativo | Mão embaixo do queixo | `pensativo.jpg` |
| Gato mão na boca | Palma da mão tapando a boca | `gato-mao-boca.png` |
| Hang loose | Polegar e dedo mínimo esticados | `hang-loose.png` |
| Faz o L | Polegar e indicador esticados | `faz-o-l.jpg` |
| Gato joia | Polegar para cima, outros dedos fechados | `gato-dando-joia.png` |
| Mario dedo do meio | Só o dedo médio esticado | `mario-dedo-meio.jpg` |
| Gato apontando | Só o indicador esticado, apontando para o lado | `gato-apontando.png` |
| Indicador levantado | Só o indicador esticado, apontando para cima | `macaco-ideia.png` |
| Gato nojo | Franzir o nariz | `gato-nojo.jpg` |
| Olhar assustado | Arregalar os olhos | `olhar-assustado.jpg` |
| Olhando de lado | Olhar para o lado, só com os olhos | `olhando-de-lado.png` |

Imagens padrão (não são gestos):

| Situação | Imagem |
|---|---|
| Nenhum gesto | `macaco-olhar-perdido.png` |
| 10 segundos sem gesto | `gato-frente.png` |

---

## Requisitos

- **Python 3.12.** Foi a versão usada no desenvolvimento.
- **Uma webcam.**
- **Windows, Linux ou macOS.** Os comandos abaixo são para Windows (PowerShell); no Linux e no macOS, a única diferença é a ativação do ambiente virtual.

Os modelos do MediaPipe (`models/*.task`) já estão no repositório; não é preciso baixar nada à parte.

---

## Instalação

```powershell
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd expression-lab

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1        # Linux/macOS: source .venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt
```

> **Importante:** não instale o `opencv-python` junto com o `opencv-contrib-python`. Os dois fornecem o mesmo módulo `cv2` e entram em conflito. O `mediapipe` já instala a versão `contrib`.

---

## Como usar

```powershell
python main.py
```

| Tecla | Ação |
|---|---|
| `q` | Fecha o programa. A janela da câmera precisa estar em foco. |

---

## Estrutura do projeto

```
expression-lab/
├── main.py             # Ponto de entrada: configura o MediaPipe e roda o loop da câmera
├── config.py           # Todas as configurações: caminhos, limites e janelas
├── gestos.py           # Gestos de uma mão: dedos esticados/dobrados e classificação
├── rosto.py            # Dados do rosto (boca, queixo, testa) e expressões
├── reconhecimento.py   # Junta mãos e rosto e decide o gesto final (prioridades)
├── exibicao.py         # Janela de imagem: carrega, redimensiona e troca as imagens
├── desenho.py          # Desenho no frame: pontos, linhas e texto
├── gestos.json         # Liga o nome de cada gesto à sua imagem
├── imagens/            # As imagens (memes) exibidas
├── models/             # Modelos do MediaPipe (mãos e rosto)
└── requirements.txt
```

---

## Configuração

Todos os ajustes ficam em [`config.py`](config.py):

| Configuração | Padrão | O que faz |
|---|---|---|
| `CAMINHO_IMAGEM_PADRAO` | `macaco-olhar-perdido.png` | Imagem mostrada quando não há gesto |
| `CAMINHO_IMAGEM_OCIOSA` | `gato-frente.png` | Imagem mostrada depois de muito tempo sem gesto |
| `SEGUNDOS_PARA_IMAGEM_OCIOSA` | `10` | Quanto tempo sem gesto até mostrar a imagem ociosa |
| `FRAMES_PARA_CONFIRMAR` | `5` | Quantos frames seguidos um gesto precisa aparecer para trocar a imagem |
| `TAMANHO_JANELA_IMAGEM` | `(480, 480)` | Largura e altura da janela de imagem |
| `POSICAO_JANELA_IMAGEM` | `(680, 50)` | Posição (x, y) da janela de imagem na tela |
| `ANGULO_DEDO_ESTENDIDO` | `160` | Ângulo mínimo, em graus, para um dedo contar como esticado |
| `FATOR_POLEGAR_ESTENDIDO` | `1.2` | Sensibilidade do polegar esticado |
| `DISTANCIA_MAO_ROSTO` | `0.35` | Distância para a mão contar como "no rosto", em larguras de rosto |
| `DISTANCIA_MAO_CABECA` | `1.0` | Distância para a mão contar como "em cima da cabeça", em larguras de rosto |
| `LIMITE_BOCA_ABERTA` | `0.5` | Nota mínima de `jawOpen` para a boca contar como aberta |
| `LIMITE_NOJO` | `0.5` | Nota mínima de `noseSneer` (nariz franzido) |
| `LIMITE_OLHOS_ARREGALADOS` | `0.35` | Nota mínima de `eyeWide` |
| `LIMITE_OLHAR_DE_LADO` | `0.6` | Nota mínima de `eyeLookIn` / `eyeLookOut` |

Os limites dependem do rosto, da iluminação e da câmera de cada pessoa. Se um gesto não ativa, ou ativa sem querer, ajuste o limite dele.

### Descobrindo os valores das expressões

Para ver as notas que o MediaPipe dá para o seu rosto, adicione temporariamente esta linha em `main.py`, logo depois de `extrair_info_rosto`:

```python
if info_rosto: print({k: round(v, 2) for k, v in info_rosto["blendshapes"].items() if v > 0.3})
```

Faça a expressão na frente da câmera e use os valores que aparecerem no terminal para escolher o limite.

---

## Adicionando um gesto novo

1. **Coloque a imagem** na pasta `imagens/`.
2. **Cadastre no `gestos.json`**, com o nome do gesto como chave:
   ```json
   "Meu gesto": {
       "imagem": "imagens/meu-gesto.png"
   }
   ```
3. **Crie a regra** que devolve exatamente esse nome:
   - **Gesto de uma mão:** adicione um `if` em `classificar_gesto` ([`gestos.py`](gestos.py)) e o nome em `GESTOS_DE_UMA_MAO` ([`reconhecimento.py`](reconhecimento.py)).
   - **Gesto com duas mãos ou com a mão no rosto:** adicione a regra em `reconhecer_gesto` ou em `gesto_perto_do_rosto` ([`reconhecimento.py`](reconhecimento.py)).
   - **Expressão facial:** adicione a regra em `classificar_expressao` ([`rosto.py`](rosto.py)), usando os blendshapes.

   Lembre que a ordem dos `if` define a prioridade. Um gesto mais específico precisa vir antes de um mais genérico.

O nome no `gestos.json` e o nome devolvido pela regra precisam ser **idênticos**, inclusive maiúsculas e espaços.

---

## Problemas comuns

| Problema | Solução |
|---|---|
| `Não foi possível acessar a webcam.` | Feche outros programas que estejam usando a câmera (Teams, Zoom, navegador). |
| `FileNotFoundError: Imagem não encontrada` | Confira os caminhos de `CAMINHO_IMAGEM_PADRAO` e `CAMINHO_IMAGEM_OCIOSA` em `config.py`. Rode o programa a partir da pasta do projeto. |
| Uma imagem do JSON não aparece | O terminal mostra `não foi possível carregar` ao iniciar. Confira o caminho e o nome do arquivo no `gestos.json`. |
| Erros estranhos do `cv2` | Provavelmente há `opencv-python` e `opencv-contrib-python` instalados juntos. Rode `pip uninstall opencv-python opencv-contrib-python -y` e depois `pip install -r requirements.txt`. |
| Gesto com a mão no rosto falha | Com a mão cobrindo o rosto, o MediaPipe às vezes perde o rosto ou a mão. Aumente `DISTANCIA_MAO_ROSTO` ou melhore a iluminação. |
| A janela de imagem fica em cima da câmera | Ajuste `POSICAO_JANELA_IMAGEM` em `config.py`. |

### Limitações conhecidas

- **Gato apontando:** apontar para a câmera não é detectado, porque o MediaPipe trabalha em 2D. Aponte para o lado.
- **Gato nojo:** usa o nariz franzido. O MediaPipe não detecta língua para fora.

---

## Tecnologias

| Tecnologia | Para que foi usada |
|---|---|
| [Python 3.12](https://www.python.org/) | Linguagem do projeto |
| [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/guide) | Pontos das mãos e do rosto, e blendshapes de expressão |
| [OpenCV](https://opencv.org/) | Webcam, janelas, redimensionamento e desenho |
| [NumPy](https://numpy.org/) | Fundo das imagens na janela de exibição |

---

## Aprendizados

- Usar os pontos (landmarks) do MediaPipe para montar regras de gestos.
- Geometria aplicada: ângulo entre vetores para saber se um dedo está esticado, e distâncias relativas ao tamanho do rosto.
- Estabilizar a detecção, exigindo que o gesto se repita por alguns frames.
- Refatorar um script grande em módulos, com configurações centralizadas e sem variáveis globais.
- Gerenciar dependências e evitar conflitos entre pacotes (`opencv-python` × `opencv-contrib-python`).
