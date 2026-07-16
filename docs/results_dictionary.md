## Descrição dos arquivos de resultados

O arquivo [results/per_sample_results_v2.csv](results/per_sample_results_v2.csv) contém uma linha por amostra, com a referência, as hipóteses geradas por duas configurações e métricas de desempenho.

### Colunas do CSV

| coluna | tipo | descrição |
|---|---|---|
| sample_id | string | Identificador da amostra ou do áudio analisado. |
| reference_raw | string | Texto de referência original, tal como foi fornecido na amostra. |
| reference_norm | string | Versão normalizada da referência, com texto padronizado e limpo. |
| hypothesis_A_original | string | Hipótese gerada pela configuração A original. |
| wer_A_original | float | Word Error Rate (WER) entre a hipótese A original e a referência. Valores mais baixos indicam melhor qualidade. |
| latency_mean_A_original | float | Latência média observada para a configuração A original, em segundos. |
| latency_std_A_original | float | Desvio padrão da latência para a configuração A original. |
| hypothesis_B_pt_pinned | string | Hipótese gerada pela configuração B com o setting/ prompt pt-pinned. |
| wer_B_pt_pinned | float | Word Error Rate (WER) entre a hipótese B pt-pinned e a referência. |
| latency_mean_B_pt_pinned | float | Latência média observada para a configuração B pt-pinned, em segundos. |
| latency_std_B_pt_pinned | float | Desvio padrão da latência para a configuração B pt-pinned. |
| peak_vram_mb | float | Pico de utilização de VRAM durante a execução, em MB. |
| quantized | boolean | Indica se a execução foi feita com quantização (True/False). |

### Explicação adicional dos outros arquivos

- O arquivo [results/predictions_v2.jsonl](results/predictions_v2.jsonl) contém as mesmas informações do CSV, mas em formato JSON Lines, com uma entrada JSON por linha. |
- O arquivo [results/summary_v2.json](results/summary_v2.json) é um resumo gerado pelo script de estatísticas, contendo métricas agregadas e informações consolidadas dos resultados. |