# Eureka Audio Replication

[DOI Zenodo](https://doi.org/10.5281/zenodo.21252103)
Este repositório reúne o material necessário para reproduzir um experimento de replicação do trabalho "Eureka-Audio: Triggering Audio Intelligence in Compact Language Models", com foco na tarefa de reconhecimento automático de fala (ASR) em português europeu.

O projeto foi organizado para que qualquer pessoa que volte a este repositório no futuro consiga entender: qual era o objetivo do experimento, como ele foi conduzido, quais arquivos foram gerados e como interpretar os resultados.

## 1. Objetivo do experimento

O notebook principal, [notebooks/replicat_eureka_minds.ipynb](notebooks/replicat_eureka_minds.ipynb), avalia o modelo
[cslys1999/Eureka-Audio-Instruct](https://huggingface.co/cslys1999/Eureka-Audio-Instruct) sobre o subconjunto em português europeu do dataset [PolyAI/minds14](https://huggingface.co/datasets/PolyAI/minds14).

A ideia central é comparar dois cenários de prompt para a transcrição de áudio:

- Cenário A: prompt original do artigo, usado como referência de replicação.
- Cenário B: prompt com reforço explícito de idioma, para tentar reduzir transcrições em outro idioma e melhorar a fidelidade ao português.

A métrica principal é o Word Error Rate (WER), calculado para cada amostra e comparado entre os dois cenários.

## 2. Resumo executivo dos resultados observados

Ao executar o fluxo completo do notebook, foram processadas 604 amostras. Os resultados agregados encontrados neste repositório indicam:

- Cenário A: WER médio aproximado de 71,20%
- Cenário B: WER médio aproximado de 41,78%
- Diferença média entre os cenários: cerca de 29,41 pontos percentuais a favor do prompt com reforço de idioma
- Teste pareado de Wilcoxon: p-valor extremamente pequeno, sugerindo diferença estatisticamente significativa entre os prompts

Esses valores são armazenados em [results/summary_v2.json](results/summary_v2.json) e podem servir como ponto de partida para análise posterior.

## 3. Estrutura do repositório

- [notebooks/replicat_eureka_minds.ipynb](notebooks/replicat_eureka_minds.ipynb): notebook principal com todo o fluxo experimental.
- [requirements.txt](requirements.txt): dependências Python necessárias para executar o experimento.
- [docs/results_dictionary.md](docs/results_dictionary.md): documento com a descrição dos principais campos e significados dos arquivos de resultados.
- [scripts/calcular_estatisticas.py](scripts/calcular_estatisticas.py): script auxiliar para calcular estatísticas a partir dos resultados salvos.
- [results/](results/): pasta com os artefatos produzidos pela execução.

### Conteúdo da pasta results

- [results/predictions_v2.jsonl](results/predictions_v2.jsonl): resultados por amostra, incluindo referência, hipóteses geradas em cada cenário e WER.
- [results/per_sample_results_v2.csv](results/per_sample_results_v2.csv): versão tabular dos resultados para análise em planilhas ou pandas.
- [results/summary_v2.json](results/summary_v2.json): resumo estatístico das métricas agregadas e testes comparativos.
- [results/plots/](results/plots/): gráficos gerados para comparação visual dos cenários.

## 4. Como o experimento foi montado

O notebook segue uma pipeline em etapas:

1. Instalação de dependências para leitura de áudio, processamento de sinais e execução do modelo.
2. Detecção do ambiente de execução (Google Colab, VS Code, Jupyter local ou outro).
3. Autenticação no Hugging Face para evitar problemas de rate-limit nas downloads.
4. Clonagem do repositório de inferência do modelo Eureka Audio.
5. Download dos pesos do modelo e carregamento com compatibilidade para ambientes sem suporte nativo ao flash-attn.
6. Definição dos dois prompts experimentais.
7. Geração de transcrições para cada amostra e cálculo do WER.
8. Armazenamento incremental dos resultados em arquivos JSONL/CSV.
9. Geração de estatísticas agregadas e gráficos comparativos.

## 5. Requisitos e ambiente recomendado

- Python com dependências listadas em [requirements.txt](requirements.txt)
- GPU NVIDIA recomendada, preferencialmente L4 ou A100
- Token do Hugging Face configurado para downloads mais confiáveis
- Espaço em disco suficiente para armazenar os pesos do modelo e os resultados

Importante: o arquivo [requirements.txt](requirements.txt) contém versões mínimas de dependências, não uma pinagem rígida das bibliotecas utilizadas na execução. Ou seja, ele é um ponto de partida útil para instalar o ambiente, mas não garante exatamente a mesma combinação de versões que foi usada no notebook em uma execução anterior. Em ambientes diferentes, pode ser necessário ajustar versões conforme o sistema, a GPU e a compatibilidade com o PyTorch/Transformers.

O notebook também inclui uma estratégia de fallback para GPUs com menos VRAM, mas a execução principal foi feita em precisão total, sem quantização.

## 6. Como reproduzir o experimento

### Opção A: localmente

1. Crie e ative um ambiente virtual (venv) antes de instalar qualquer dependência:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
   Se estiver no Linux/macOS, use `source .venv/bin/activate`.
2. Instale as dependências dentro desse ambiente:
   ```bash
   pip install -r requirements.txt
   ```
3. Abra o notebook [notebooks/replicat_eureka_minds.ipynb](notebooks/replicat_eureka_minds.ipynb).
4. Execute as células em ordem.
5. Aguarde o download do modelo e o processamento das amostras.

> Para rodar o script de análise estatística [scripts/calcular_estatisticas.py](scripts/calcular_estatisticas.py), também é recomendável usar o mesmo ambiente virtual criado acima, pois as dependências precisam estar instaladas nesse contexto.

### Opção B: Google Colab

1. Faça upload do notebook para o Colab.
2. Ative o runtime com GPU.
3. Configure um token do Hugging Face em Secrets como HF_TOKEN.
4. Execute as células em sequência.
5. Os resultados serão salvos em uma pasta dedicada no Google Drive.

## 7. O que cada arquivo de saída significa

- [results/predictions_v2.jsonl](results/predictions_v2.jsonl): cada linha representa uma amostra processada. Inclui a transcrição de referência, as hipóteses geradas para cada cenário e os valores de WER correspondentes.
- [results/per_sample_results_v2.csv](results/per_sample_results_v2.csv): mesma informação em formato tabular para análise mais simples.
- [results/summary_v2.json](results/summary_v2.json): métricas agregadas, intervalos de confiança, testes estatísticos e resumo comparativo entre os cenários.
- [results/plots/](results/plots/): visualizações do comportamento do WER por cenário.

## 8. Observações importantes

- O notebook usa uma semente fixa para garantir reprodutibilidade parcial do experimento.
- O processamento é feito de forma incremental, então uma execução interrompida pode ser retomada sem perder os resultados já salvos.
- A compatibilidade com GPUs sem suporte ao flash-attn foi tratada por meio de patches de atenção usando SDPA, o que é uma adaptação prática do fluxo original.
- O experimento não é uma cópia literal de todos os detalhes do artigo em todos os ambientes, mas busca seguir o protocolo principal de avaliação e compará-lo em português europeu.

## 9. Como explorar os resultados

Se quiser revisar as estatísticas de forma mais direta, pode usar o script [scripts/calcular_estatisticas.py](scripts/calcular_estatisticas.py) para complementar a análise com medidas robustas como mediana, IQR e distribuição por faixas de WER.

Este repositório foi pensado como uma base documental e reprodutível para o experimento, permitindo que futuras leituras compreendam não só o código, mas também o contexto científico e metodológico da replicação.