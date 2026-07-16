"""
Calcula todas as estatísticas apresentadas no artigo a partir dos resultados já gerados no Colab. Roda localmente, sem GPU e sem
depender de nenhuma variável do notebook: só precisa de predictions_v2.jsonl e summary_v2.json na mesma pasta deste script.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

SEED = 42
N_BOOTSTRAP = 1000

REFERENCE_VALUES = {
    "Inglês - LibriSpeech test-clean": 1.46,
    "Inglês - Fleurs-en": 5.39,
    "Mandarim - WenetSpeech test-meeting": 9.14,
    "Mandarim - WenetSPeech test-net": 7.55,
}

HERE = Path(__file__).parent.parent
predictions_path = HERE / "results" /"predictions_v2.jsonl"
summary_path = HERE / "results" / "summary_v2.json"

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

# helper de bootstrap

def bootstrap_ci(values, stat_func=np.mean, n_boot=N_BOOTSTRAP, seed=SEED):
    rng = np.random.default_rng(seed)
    boots = np.array([stat_func(rng.choice(values, size=len(values), replace=True)) for _ in range(n_boot)])
    return np.percentile(boots, [2.5, 97.5])

bins = [0, 10, 30, 100, 150, 100000]
bin_labels = ["0-10%", "10-30%", "30-100%", "100-150%", ">150%"]

results = {}

for scenario, col in [("A_original", "wer_A_original"), ("B_pt_pinned", "wer_B_pt_pinned")]:
    wer_pct = df[col].values * 100

    # calcula estatísticas
    mean_ = wer_pct.mean()
    std_ = wer_pct.std(ddof=1)
    median_ = np.median(wer_pct)
    q1, q3 = np.percentile(wer_pct, [25, 75])

    # calcula IC bootstrap
    ci_mean_low, ci_mean_high = bootstrap_ci(wer_pct, stat_func=np.mean)
    ci_median_low, ci_median_high = bootstrap_ci(wer_pct, stat_func=np.median)

    shapiro_stat, shapiro_p = stats.shapiro(wer_pct) if n>=3 else (np.nan, np.nan)

    counts, _ = np.histogram(wer_pct, bins=bins)
    dist_pct = {label:float(c / n * 100) for label, c in zip(bin_labels, counts)}

    print(f"\nCenário {scenario}:")
    print(f"  Média: {mean_:.2f}%  (DP: {std_:.2f}%)  IC 95%: [{ci_mean_low:.2f}%, {ci_mean_high:.2f}%]")
    print(f"  Mediana: {median_:.2f}%  (IC 95%: [{ci_median_low:.2f}%, {ci_median_high:.2f}%])")
    print(f" IQR: [{q1:.2f}%, {q3:.2f}%]")
    print(f" Teste de Shapiro-Wilk: estatística={shapiro_stat:.4f}, p-valor={shapiro_p:.4g}")

    results[scenario] = {
        "mean_wer_pct": float(mean_),
        "std_wer_pct": float(std_),
        "median_wer_pct": float(median_),
        "iqr_wer_pct": [float(q1), float(q3)],
        "bootstrap_ci_mean_95": [float(ci_mean_low), float(ci_mean_high)],
        "bootstrap_ci_median_95": [float(ci_median_low), float(ci_median_high)],
        "shapiro_wilk": {"statistic": float(shapiro_stat), "p_value": float(shapiro_p)},
        "distribution_pct": dist_pct,
    }

# teste pareado

wer_A = df["wer_A_original"].values * 100
wer_B = df["wer_B_pt_pinned"].values * 100
diff = wer_A - wer_B
diffs_ab_nz = diff[diff != 0]

if len(diffs_ab_nz) >=1:
    stat_ab, p_ab = stats.wilcoxon(diffs_ab_nz)
else:
    stat_ab, p_ab = (np.nan, np.nan)
d_ab = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) > 0 else np.nan

print(f"\nTeste pareado Wilcoxon entre cenários A e B:")
print(f"  Estatística: {stat_ab:.4f}, p-valor: {p_ab:.4g}, d de Cohen: {d_ab:.4f}")
print(f" Média da diferença (A-B): {diff.mean():.2f}%  (DP: {diff.std(ddof=1):.2f}%)")

# latência e VRAM

for col_lat, label in [("latency_mean_A_original", "A"), ("latency_mean_B_pt_pinned", "B")]:
    if col_lat in df.columns:
        lat_mean = df[col_lat].mean()
        lat_std = df[col_lat].std(ddof=1)
        print(f"\nLatência média do cenário {label}: {lat_mean:.2f} s (DP: {lat_std:.2f} s)")

if "peak_vram_mb" in df.columns and df["peak_vram_mb"].notna().any():
    print(f"\nValor mais alto de VRAM: {df['peak_vram_mb'].max():.2f} MB \n média: {df['peak_vram_mb'].mean():.2f} MB")

summary = {
    "n_samples": n,
    "quantized": bool(df["quantized"].iloc[0]) if "quantized" in df.columns else None,
    "scenarios": results,
    "paired_test": {
        "statistic": float(stat_ab),
        "p_value": float(p_ab),
        "cohen_d": float(d_ab),
        "mean_diff": float(diff.mean()),
    },
}

with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"\nResumo das estatísticas salvas em {summary_path}")