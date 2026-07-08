"""
Calcula estatísticas robustas (mediana, IQR, distribuição por faixas de WER)
a partir dos resultados já gerados no Colab. Roda localmente, sem GPU e sem
depender de nenhuma variável do notebook: só precisa de predictions_v2.jsonl
e summary_v2.json na mesma pasta deste script.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_BOOTSTRAP = 1000

HERE = Path(__file__).parent
predictions_path = HERE / "predictions_v2.jsonl"
summary_path = HERE / "summary_v2.json"

if not predictions_path.exists():
    raise FileNotFoundError(
        f"Não encontrei {predictions_path}. Coloque o predictions_v2.jsonl "
        f"nesta mesma pasta antes de rodar o script."
    )

records = []
with open(predictions_path, "r", encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))
df = pd.DataFrame(records)
n = len(df)
print(f"N amostras carregadas: {n}")

bins = [0, 10, 30, 100, 150, 100000]
bin_labels = ["0-10%", "10-30%", "30-100%", "100-150%", ">150%"]

robust_stats = {}
for scenario, col in [("A_original", "wer_A_original"), ("B_pt_pinned", "wer_B_pt_pinned")]:
    wer_pct = df[col].values * 100

    median_ = np.median(wer_pct)
    q1, q3 = np.percentile(wer_pct, [25, 75])

    rng = np.random.default_rng(SEED)
    boot_medians = np.array([
        np.median(rng.choice(wer_pct, size=n, replace=True)) for _ in range(N_BOOTSTRAP)
    ])
    ci_low, ci_high = np.percentile(boot_medians, [2.5, 97.5])

    counts, _ = np.histogram(wer_pct, bins=bins)
    dist_pct = {label: float(c / n * 100) for label, c in zip(bin_labels, counts)}

    robust_stats[scenario] = {
        "median_wer_pct": float(median_),
        "iqr_wer_pct": [float(q1), float(q3)],
        "median_bootstrap_ci_95": [float(ci_low), float(ci_high)],
        "distribution_by_range_pct": dist_pct,
    }

    print(f"\n=== Cenário {scenario} ===")
    print(f"Mediana: {median_:.2f}%  IQR: [{q1:.2f}%, {q3:.2f}%]")
    print(f"IC 95% da mediana (bootstrap): [{ci_low:.2f}%, {ci_high:.2f}%]")
    print("Distribuição por faixa de WER:")
    for label, pct in dist_pct.items():
        print(f"  {label:10s}: {pct:5.1f}%")

# Atualiza o summary_v2.json existente (adiciona campos, não sobrescreve os já existentes)
if summary_path.exists():
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    for scenario in robust_stats:
        summary["scenarios"][scenario].update(robust_stats[scenario])
else:
    print(f"\nAviso: {summary_path} não encontrado — salvando só as novas estatísticas.")
    summary = {"scenarios": robust_stats}

with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"\nEstatísticas robustas adicionadas/atualizadas em: {summary_path}")
