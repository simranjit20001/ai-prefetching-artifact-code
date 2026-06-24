#!/usr/bin/env python3
"""Build figures from the packaged CSV summaries."""

from __future__ import annotations

import math
import re
from os.path import basename
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
FIG = REPO_ROOT / "figures"
LATEX_ROOT = REPO_ROOT / "latex"
LATEX_FIG = LATEX_ROOT / "figures"
PACKAGED_GRAPH_PACK = REPO_ROOT / "data"
GRAPH_PACK = PACKAGED_GRAPH_PACK
DAGGER_ROOT = REPO_ROOT / "results" / "mlp_lightgbm" / "dagger_mlp_20260515_lite"


PALETTE = {
    "no": "#8A8A8E",
    "ppf": "#8A8A8E",
    "pythia": "#3B6F9E",
    "umama": "#2F7D72",
    "mlp": "#6B5CA5",
    "lgbm": "#9B6A3D",
    "llm": "#5D7A55",
    "grid": "#E7E8EA",
    "text": "#1D1D1F",
    "muted": "#6E6E73",
    "face": "#FFFFFF",
    "panel": "#F6F7F8",
    "line": "#343437",
}


APPLE_CMAP = LinearSegmentedColormap.from_list(
    "apple_blues",
    ["#F8F9FA", "#E8EEF4", "#D2DFEA", "#8CAFCB", "#3B6F9E"],
)


def geomean(values: pd.Series | np.ndarray) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr) & (arr > 0)]
    if len(arr) == 0:
        return float("nan")
    return float(np.exp(np.mean(np.log(arr))))


def speedup_to_pct(values: pd.Series | np.ndarray | list[float]) -> np.ndarray:
    return (np.asarray(values, dtype=float) - 1.0) * 100.0


def trace_key(path_value: str | Path) -> str:
    name = basename(str(path_value))
    for suffix in (
        ".champsimtrace.xz",
        ".champsimtrace.gz",
        ".champsim.gz",
        ".trace.gz",
        ".xz",
        ".gz",
    ):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def savefig(*names: str) -> None:
    output_dirs = [FIG]
    if LATEX_ROOT.exists():
        output_dirs.append(LATEX_FIG)
    for name in names:
        for ext in ("pdf", "png"):
            for out_dir in output_dirs:
                out_dir.mkdir(parents=True, exist_ok=True)
                out = out_dir / f"{name}.{ext}"
                plt.savefig(out, bbox_inches="tight", dpi=260, facecolor="white")
    plt.close()


def style_axes(ax, title: str | None = None, ylabel: str | None = None) -> None:
    ax.set_facecolor(PALETTE["face"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D2D2D7")
    ax.spines["bottom"].set_color("#D2D2D7")
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(colors=PALETTE["text"], length=3, width=0.7, labelsize=8.5)
    ax.grid(axis="y", color=PALETTE["grid"], linewidth=0.65, alpha=0.9)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, loc="left", fontsize=10, fontweight=600, color=PALETTE["text"], pad=7)
    if ylabel:
        ax.set_ylabel(ylabel, color=PALETTE["text"], fontsize=8.8)


def resolve_packaged_path(path_value: str | Path) -> Path:
    """Map absolute run paths to the lightweight packaged run when possible."""
    p = Path(path_value)
    if p.exists():
        return p
    if not p.is_absolute():
        candidate = REPO_ROOT / p
        if candidate.exists():
            return candidate
    marker = "ml_l2_dagger_branches_20260515_001200/mlp/"
    text = str(p)
    if marker in text and DAGGER_ROOT.exists():
        rel = text.split(marker, 1)[1]
        candidate = DAGGER_ROOT / rel
        if candidate.exists():
            return candidate
    return p


def diagram_box(
    ax,
    xy,
    w,
    h,
    title,
    subtitle="",
    fill=None,
    edge=None,
    title_size=7.6,
    sub_size=6.4,
    lw=0.8,
    rounded=0.04,
    weight=600,
):
    x, y = xy
    fill = fill or PALETTE["panel"]
    edge = edge or "#C8CCD0"
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.012,rounding_size={rounded}",
        linewidth=lw,
        edgecolor=edge,
        facecolor=fill,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.60, title, ha="center", va="center", fontsize=title_size, fontweight=weight, color=PALETTE["text"])
    if subtitle:
        ax.text(x + w / 2, y + h * 0.30, subtitle, ha="center", va="center", fontsize=sub_size, color=PALETTE["muted"])
    return patch


def diagram_arrow(ax, start, end, rad=0.0, color=None, style="-|>", lw=0.9, dashed=False):
    color = color or PALETTE["line"]
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=12,
        linewidth=lw,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=5,
        shrinkB=5,
        linestyle=(0, (3, 3)) if dashed else "solid",
    )
    ax.add_patch(arrow)
    return arrow


def diagram_canvas(width=10.5, height=3.6):
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax


def diagram_label(ax, x, y, text, size=6.3, color=None, ha="center"):
    ax.text(x, y, text, fontsize=size, color=color or PALETTE["muted"], ha=ha, va="center")


def simple_box(ax, x, y, w, h, title, subtitle="", fill="#FFFFFF", edge="#1D1D1F", title_size=9.2, sub_size=7.3):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            linewidth=1.15,
            edgecolor=edge,
            facecolor=fill,
        )
    )
    ax.text(x + w / 2, y + h * 0.60, title, ha="center", va="center", fontsize=title_size, fontweight=700, color=PALETTE["text"])
    if subtitle:
        ax.text(x + w / 2, y + h * 0.32, subtitle, ha="center", va="center", fontsize=sub_size, color=PALETTE["muted"])


def weight_table(ax, x, y, w, h, title):
    ax.add_patch(
        Rectangle(
            (x, y),
            w,
            h,
            linewidth=0.75,
            edgecolor="#9DA3AA",
            facecolor="#FFFFFF",
        )
    )
    header_h = h * 0.22
    ax.add_patch(
        Rectangle(
            (x, y + h - header_h),
            w,
            header_h,
            linewidth=0,
            facecolor="#F1F3F5",
        )
    )
    ax.text(x + w / 2, y + h - header_h / 2, title, ha="center", va="center", fontsize=5.6, fontweight=600, color=PALETTE["text"])
    for i in range(1, 5):
        yy = y + (h - header_h) * i / 5
        ax.plot([x, x + w], [yy, yy], color="#D4D7DA", linewidth=0.45)
    for i, lab in enumerate(["w1", "w2", "w3", "..."]):
        yy = y + (h - header_h) * (4.5 - i) / 5
        ax.text(x + w / 2, yy, lab, ha="center", va="center", fontsize=5.0, color=PALETTE["muted"])


def stacked_table(ax, x, y, w, h, fontsize=5.8):
    ax.add_patch(Rectangle((x, y), w, h, linewidth=0.75, edgecolor="#9DA3AA", facecolor="#FFFFFF"))
    ax.plot([x, x + w], [y + h * 0.55, y + h * 0.55], color="#9DA3AA", linewidth=0.65)
    ax.plot([x + w * 0.52, x + w * 0.52], [y, y + h * 0.55], color="#D4D7DA", linewidth=0.55)
    ax.text(x + w / 2, y + h * 0.78, "reject", ha="center", va="center", fontsize=fontsize, color=PALETTE["text"])
    ax.text(x + w / 2, y + h * 0.40, "prefetch", ha="center", va="center", fontsize=fontsize, color=PALETTE["text"])
    ax.text(x + w * 0.26, y + h * 0.14, "idx", ha="center", va="center", fontsize=fontsize - 0.7, color=PALETTE["muted"])
    ax.text(x + w * 0.76, y + h * 0.14, "meta", ha="center", va="center", fontsize=fontsize - 0.7, color=PALETTE["muted"])


def figure_diagram_ppf() -> None:
    fig, ax = diagram_canvas(10.8, 3.05)
    blue = "#2E5E8C"
    warm = "#8A5A2B"
    gray = "#1D1D1F"
    light = "#F7F8FA"

    simple_box(ax, 0.40, 2.10, 1.08, 0.58, "SPP", "candidata", fill="#F3F7FB", edge=blue)
    simple_box(ax, 2.05, 2.02, 1.50, 0.74, "contexto", "señales e índices", fill=light, edge=gray, title_size=8.7, sub_size=6.2)
    simple_box(ax, 4.32, 1.98, 1.34, 0.82, "tablas PPF", "$W_j[h_j]$", fill="#F3F7FB", edge=blue)
    simple_box(
        ax,
        6.42,
        1.98,
        1.48,
        0.82,
        "decisión",
        "$s=b+\\sum w_j$",
        fill="#FAF4EA",
        edge=warm,
        title_size=8.4,
        sub_size=6.6,
    )

    diagram_arrow(ax, (1.48, 2.39), (2.05, 2.39), color=gray, lw=1.1)
    diagram_arrow(ax, (3.55, 2.39), (4.32, 2.39), color=gray, lw=1.1)
    diagram_arrow(ax, (5.66, 2.39), (6.42, 2.39), color=gray, lw=1.1)

    ax.add_patch(
        FancyBboxPatch(
            (9.26, 1.66),
            1.10,
            1.18,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            linewidth=1.15,
            edgecolor=gray,
            facecolor="#FFFFFF",
        )
    )
    for yy in [2.05, 2.45]:
        ax.plot([9.26, 10.36], [yy, yy], color="#C6C8CB", linewidth=0.9)
    ax.text(9.81, 2.64, "L2", ha="center", va="center", fontsize=7.8, fontweight=700, color=PALETTE["text"])
    ax.text(9.81, 2.25, "LLC", ha="center", va="center", fontsize=7.8, fontweight=700, color=PALETTE["text"])
    ax.text(9.81, 1.85, "rechazo", ha="center", va="center", fontsize=7.2, fontweight=700, color=PALETTE["text"])
    diagram_arrow(ax, (7.90, 2.39), (9.26, 2.39), color=gray, lw=1.1)

    ax.plot([0.28, 10.36], [1.18, 1.18], color="#D6D8DB", linewidth=0.9)
    ax.text(0.30, 0.69, "actualización online", ha="left", va="center", fontsize=8.0, fontweight=700, color=PALETTE["text"])
    simple_box(ax, 3.05, 0.43, 1.20, 0.52, "evento", "hit / eviction", fill=light, edge=gray, title_size=8.0, sub_size=6.0)
    simple_box(ax, 5.18, 0.43, 1.24, 0.52, "entrenar", "$W_j \\leftarrow W_j \\pm 1$", fill="#FAF4EA", edge=warm, title_size=8.0, sub_size=5.7)
    diagram_arrow(ax, (4.25, 0.69), (5.18, 0.69), color=warm, lw=1.0)
    diagram_arrow(ax, (5.80, 0.95), (4.98, 1.98), rad=-0.12, color=warm, dashed=True, lw=0.9)
    savefig("diagram_ppf")


def figure_diagram_pythia() -> None:
    fig, ax = diagram_canvas(7.8, 3.10)
    blue = "#2E5E8C"
    warm = "#8A5A2B"
    gray = "#1D1D1F"
    light = "#F7F8FA"
    simple_box(ax, 0.45, 1.88, 1.45, 0.62, "estado", "features", fill=light, edge=gray)
    simple_box(ax, 2.45, 1.88, 1.55, 0.62, "SARSA", "tabla Q", fill="#F3F7FB", edge=blue)
    simple_box(ax, 4.55, 1.88, 1.45, 0.62, "acción", "offset", fill=light, edge=gray)
    simple_box(ax, 4.55, 0.72, 1.45, 0.62, "recompensa", "utilidad, coste", fill="#FAF4EA", edge=warm)
    simple_box(ax, 2.45, 0.72, 1.55, 0.62, "actualizar", "$Q(s,a)$", fill=light, edge=gray, title_size=8.3)
    diagram_arrow(ax, (1.90, 2.19), (2.45, 2.19), color=gray, lw=1.2)
    diagram_arrow(ax, (4.00, 2.19), (4.55, 2.19), color=gray, lw=1.2)
    diagram_arrow(ax, (5.28, 1.88), (5.28, 1.34), color=gray, lw=1.2)
    diagram_arrow(ax, (4.55, 1.03), (4.00, 1.03), color=gray, lw=1.2)
    diagram_arrow(ax, (3.22, 1.34), (3.22, 1.88), color=gray, lw=1.2)
    savefig("diagram_pythia")


def figure_diagram_mab() -> None:
    fig, ax = diagram_canvas(8.4, 3.05)
    blue = "#2E5E8C"
    warm = "#8A5A2B"
    gray = "#1D1D1F"
    light = "#F7F8FA"
    y_top = 2.10
    y_bottom = 0.72

    simple_box(ax, 0.36, 1.73, 1.42, 0.74, "ventana", "fase actual", fill=light, edge=gray)
    simple_box(ax, 2.18, 1.61, 1.56, 0.98, "selector", "explora / explota", fill="#FAF4EA", edge=warm)

    ax.text(4.88, 2.82, "brazos disponibles", ha="center", va="center", fontsize=7.5, fontweight=700, color=PALETTE["text"])
    simple_box(ax, 4.30, 2.35, 1.16, 0.36, "config. 1", "", fill=light, edge=gray, title_size=7.0)
    simple_box(ax, 4.30, y_top - 0.18, 1.16, 0.36, "config. 2", "", fill="#F3F7FB", edge=blue, title_size=7.0)
    simple_box(ax, 4.30, 1.49, 1.16, 0.36, "config. k", "", fill=light, edge=gray, title_size=7.0)

    simple_box(ax, 6.42, 1.61, 1.46, 0.98, "ejecución", "prefetcher activo", fill=light, edge=gray)
    simple_box(ax, 6.42, 0.41, 1.46, 0.62, "recompensa", "IPC ventana", fill="#FAF4EA", edge=warm, title_size=8.0, sub_size=6.0)
    simple_box(ax, 2.18, 0.41, 1.56, 0.62, "actualizar", "estimaciones", fill=light, edge=gray, title_size=8.0, sub_size=6.0)

    diagram_arrow(ax, (1.78, y_top), (2.18, y_top), color=gray, lw=1.2)
    diagram_arrow(ax, (3.74, y_top), (4.30, y_top), color=gray, lw=1.2)
    diagram_arrow(ax, (5.46, y_top), (6.42, y_top), color=gray, lw=1.2)
    diagram_arrow(ax, (7.15, 1.61), (7.15, 1.03), color=gray, lw=1.2)
    diagram_arrow(ax, (6.42, y_bottom), (3.74, y_bottom), color=gray, lw=1.2)
    diagram_arrow(ax, (2.96, 1.03), (2.96, 1.61), color=gray, lw=1.2)
    savefig("diagram_mab")


def figure_diagram_dagger() -> None:
    fig, ax = diagram_canvas(7.7, 4.05)
    blue = "#2E5E8C"
    warm = "#8A5A2B"
    gray = "#1D1D1F"
    light = "#F7F8FA"

    simple_box(ax, 0.42, 2.55, 1.65, 0.62, "dataset", "estados etiquetados", fill=light, edge=gray)
    simple_box(ax, 2.92, 2.55, 1.65, 0.62, "entrenar", "MLP / LightGBM", fill="#F3F7FB", edge=blue)
    simple_box(ax, 5.42, 2.55, 1.65, 0.62, "simular", "ChampSim", fill=light, edge=gray)
    simple_box(ax, 5.42, 1.05, 1.65, 0.62, "etiquetar", "utilidad posterior", fill="#FAF4EA", edge=warm)
    simple_box(ax, 2.92, 1.05, 1.65, 0.62, "agregar", "nuevos estados", fill=light, edge=gray)

    diagram_arrow(ax, (2.07, 2.86), (2.92, 2.86), color=gray, lw=1.2)
    diagram_arrow(ax, (4.57, 2.86), (5.42, 2.86), color=gray, lw=1.2)
    diagram_arrow(ax, (6.25, 2.55), (6.25, 1.67), color=gray, lw=1.2)
    diagram_arrow(ax, (5.42, 1.36), (4.57, 1.36), color=gray, lw=1.2)
    diagram_arrow(ax, (2.92, 1.36), (1.25, 2.55), rad=-0.22, color=gray, lw=1.2)
    savefig("diagram_dagger")


def read_common_12_metrics() -> pd.DataFrame:
    df = pd.read_csv(GRAPH_PACK / "dagger_12_common_metrics.csv").copy()
    df["method"] = df["method"].astype(str)
    return df


def common_12_row(df: pd.DataFrame, method: str) -> pd.Series:
    rows = df[df["method"] == method]
    if rows.empty:
        raise KeyError(f"Missing method in dagger_12_common_metrics.csv: {method}")
    return rows.iloc[0]


def common_12_trace_keys() -> set[str]:
    ml = pd.read_csv(GRAPH_PACK / "ml_collection_by_trace.csv").copy()
    ml = ml[(ml["mode"] == "train_20M_20M") & (ml["policy"] == "mlp")].copy()
    ml["trace_key"] = ml["trace"].map(trace_key)
    return set(ml["trace_key"].dropna().unique())


def figure_online_speedup() -> dict[str, float]:
    common = read_common_12_metrics()
    methods = ["PPF", "Pythia", "uMAMA"]
    speedups = np.array([float(common_12_row(common, m)["speedup"]) for m in methods], dtype=float)
    values = speedup_to_pct(speedups)

    fig, ax = plt.subplots(figsize=(7.6, 4.35))
    colors = [PALETTE["ppf"], PALETTE["pythia"], PALETTE["umama"]]
    ax.bar(
        np.arange(len(methods)),
        values,
        width=0.62,
        color=colors,
        edgecolor="white",
        linewidth=0.8,
        zorder=2,
    )
    ax.axhline(0.0, color=PALETTE["text"], linestyle=(0, (4, 3)), linewidth=0.85, alpha=0.7)
    display_methods = ["SPP+PPF", "Pythia", "uMAMA"]
    ax.set_xticks(np.arange(len(methods)))
    ax.set_xticklabels(display_methods)
    ax.set_ylim(min(-4.0, float(np.nanmin(values)) - 1.0), max(12.0, float(np.nanmax(values)) + 1.0))
    style_axes(ax, "Políticas online", "Mejora geométrica (%)")
    ax.grid(axis="y", color=PALETTE["grid"], linewidth=0.65, alpha=0.9)
    fig.tight_layout()
    savefig("fig_online_speedup")

    detail = online_trace_metrics()
    return {
        "online_ppf_global": float(common_12_row(common, "PPF")["speedup"]),
        "online_pythia_global": float(common_12_row(common, "Pythia")["speedup"]),
        "online_umama_global": float(common_12_row(common, "uMAMA")["speedup"]),
        "online_ppf_improvement_pct": float(speedup_to_pct([common_12_row(common, "PPF")["speedup"]])[0]),
        "online_pythia_improvement_pct": float(speedup_to_pct([common_12_row(common, "Pythia")["speedup"]])[0]),
        "online_umama_improvement_pct": float(speedup_to_pct([common_12_row(common, "uMAMA")["speedup"]])[0]),
        "online_umama_traces": int(common_12_row(common, "uMAMA")["traces"]),
        **detail,
    }


def figure_intel_l2_history() -> None:
    df = pd.read_csv(GRAPH_PACK / "intel_l2_history.csv").sort_values("order")
    fig, ax = plt.subplots(figsize=(7.4, 3.7))
    x = np.arange(len(df))
    colors = ["#9B9EA3"] * 4 + ["#7FAEA8", "#4B9288", PALETTE["umama"]]
    bars = ax.bar(
        x,
        df["l2_kb"],
        width=0.68,
        color=colors,
        edgecolor="#FFFFFF",
        linewidth=0.8,
    )

    def label_size(kb: float) -> str:
        return f"{kb / 1024:g} MB" if kb >= 1024 else f"{int(kb)} KB"

    for bar, kb in zip(bars, df["l2_kb"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            float(kb) + 70,
            label_size(float(kb)),
            ha="center",
            va="bottom",
            fontsize=7.2,
            color=PALETTE["text"],
        )

    ax.set_xticks(x)
    tick_labels = []
    for row in df.itertuples(index=False):
        arch = str(row.architecture).replace(" ", "\n")
        tick_labels.append(f"{int(row.year)}\n{arch}")
    ax.set_xticklabels(tick_labels, fontsize=7.3)
    ax.set_xlim(-0.6, len(df) - 0.4)
    ax.set_ylim(0, 2350)
    style_axes(ax, "L2/MLC por núcleo en Intel", None)
    fig.tight_layout()
    savefig("fig_intel_l2_history")


def online_trace_metrics() -> dict[str, float | int]:
    df = pd.read_csv(GRAPH_PACK / "classic_champsim_by_trace.csv")
    df = df[df["l1_prefetcher"] == "berti"].copy()
    source = df["trace_path_reported"].fillna(df["trace_file"])
    df["trace_key"] = source.map(trace_key)
    trace_keys = common_12_trace_keys()
    df = df[df["trace_key"].isin(trace_keys)].copy()

    policies = ["no", "ppf", "pythia", "umama"]
    wide = (
        df[df["l2_prefetcher"].isin(policies)]
        .pivot_table(index=["trace_key", "workload_group"], columns="l2_prefetcher", values="ipc", aggfunc="first")
        .dropna(subset=policies)
        .reset_index()
    )
    for policy in ("ppf", "pythia", "umama"):
        wide[f"{policy}_speedup"] = wide[policy] / wide["no"]

    wide["winner"] = wide[["ppf", "pythia", "umama"]].idxmax(axis=1)
    pythia_over_umama = wide[wide["pythia"] > wide["umama"]].copy()
    umama_over_pythia = wide[wide["umama"] > wide["pythia"]].copy()
    pythia_win_margin_pct = (
        (geomean(pythia_over_umama["pythia"] / pythia_over_umama["umama"]) - 1.0) * 100.0
        if not pythia_over_umama.empty
        else 0.0
    )
    umama_win_margin_pct = (
        (geomean(umama_over_pythia["umama"] / umama_over_pythia["pythia"]) - 1.0) * 100.0
        if not umama_over_pythia.empty
        else 0.0
    )
    winners = wide["winner"].value_counts()
    by_group = (
        pd.crosstab(wide["workload_group"], wide["winner"])
        .reindex(columns=["ppf", "pythia", "umama"], fill_value=0)
        .reset_index()
        .rename(columns={"workload_group": "tipo_carga", "ppf": "PPF", "pythia": "Pythia", "umama": "uMAMA"})
    )
    by_group.insert(1, "trazas", by_group["PPF"] + by_group["Pythia"] + by_group["uMAMA"])
    by_group.to_csv(PACKAGED_GRAPH_PACK / "online_berti_l2_winner_counts.csv", index=False)

    traffic = {}
    common_traces = set(wide["trace_key"])
    for policy in ("ppf", "pythia", "umama"):
        rows = df[(df["l2_prefetcher"] == policy) & (df["trace_key"].isin(common_traces))]
        issued = float(rows["l2_pf_issued"].sum())
        useful = float(rows["l2_pf_useful"].sum())
        traffic[f"online_{policy}_issued_m"] = issued / 1_000_000.0
        traffic[f"online_{policy}_useful_m"] = useful / 1_000_000.0
        traffic[f"online_{policy}_accuracy_pct"] = 100.0 * useful / issued if issued else 0.0
        traffic[f"online_{policy}_losses"] = int((wide[f"{policy}_speedup"] < 1.0).sum())

    group_counts = by_group.set_index("tipo_carga").to_dict(orient="index")
    def group_value(group: str, col: str) -> int:
        return int(group_counts.get(group, {}).get(col, 0))

    def group_geomean(group: str, policy: str) -> float:
        rows = wide[wide["workload_group"] == group]
        if rows.empty:
            return 0.0
        return float(geomean(rows[f"{policy}_speedup"]))

    return {
        "online_common_traces": int(len(wide)),
        "online_ppf_wins": int(winners.get("ppf", 0)),
        "online_pythia_wins": int(winners.get("pythia", 0)),
        "online_umama_wins": int(winners.get("umama", 0)),
        "online_pythia_over_umama": int((wide["pythia"] > wide["umama"]).sum()),
        "online_umama_over_pythia": int((wide["umama"] > wide["pythia"]).sum()),
        "online_pythia_umama_ties": int((wide["umama"] == wide["pythia"]).sum()),
        "online_pythia_win_margin_pct": float(pythia_win_margin_pct),
        "online_umama_win_margin_pct": float(umama_win_margin_pct),
        "online_aiml_pythia_speedup": group_geomean("AI-ML", "pythia"),
        "online_aiml_umama_speedup": group_geomean("AI-ML", "umama"),
        "online_aiml_traces": group_value("AI-ML", "trazas"),
        "online_aiml_ppf_wins": group_value("AI-ML", "PPF"),
        "online_aiml_pythia_wins": group_value("AI-ML", "Pythia"),
        "online_aiml_umama_wins": group_value("AI-ML", "uMAMA"),
        "online_gtrace_traces": group_value("GTrace", "trazas"),
        "online_gtrace_ppf_wins": group_value("GTrace", "PPF"),
        "online_gtrace_pythia_wins": group_value("GTrace", "Pythia"),
        "online_gtrace_umama_wins": group_value("GTrace", "uMAMA"),
        "online_gms_traces": group_value("Graph-GMS", "trazas"),
        "online_gms_ppf_wins": group_value("Graph-GMS", "PPF"),
        "online_gms_pythia_wins": group_value("Graph-GMS", "Pythia"),
        "online_gms_umama_wins": group_value("Graph-GMS", "uMAMA"),
        "online_ligra_traces": group_value("Graph-Ligra", "trazas"),
        "online_ligra_ppf_wins": group_value("Graph-Ligra", "PPF"),
        "online_ligra_pythia_wins": group_value("Graph-Ligra", "Pythia"),
        "online_ligra_umama_wins": group_value("Graph-Ligra", "uMAMA"),
        "online_spec_traces": group_value("SPEC17", "trazas"),
        "online_spec_ppf_wins": group_value("SPEC17", "PPF"),
        "online_spec_pythia_wins": group_value("SPEC17", "Pythia"),
        "online_spec_umama_wins": group_value("SPEC17", "uMAMA"),
        **traffic,
    }


def short_trace_label(trace_name: str) -> str:
    replacements = [
        ("602.gcc_s", "gcc"),
        ("623.xalancbmk_s", "xalancbmk"),
        ("627.cam4_s", "cam4"),
        ("649.fotonik3d_s", "fotonik3d"),
        ("657.xz_s", "xz"),
        ("gms.triangle_count", "triangle count"),
        ("ligra_Triangle", "Triangle"),
        ("bark.cpp", "Bark"),
        ("llama2.c-stories15M", "LLaMA2"),
        ("whisper_trace_1", "Whisper"),
        ("arizona_0000", "arizona"),
        ("yankee_0010", "yankee"),
    ]
    for prefix, label in replacements:
        if trace_name.startswith(prefix):
            return label
    return trace_name.split(".")[0].replace("_", " ")[:18]


def common_trace_speedups() -> pd.DataFrame:
    common = read_common_12_metrics()
    trace_keys = common_12_trace_keys()

    classic = pd.read_csv(GRAPH_PACK / "classic_champsim_by_trace.csv").copy()
    source = classic["trace_path_reported"].fillna(classic["trace_file"])
    classic["trace_key"] = source.map(trace_key)
    classic = classic[(classic["l1_prefetcher"] == "berti") & (classic["trace_key"].isin(trace_keys))].copy()

    base = (
        classic[classic["l2_prefetcher"] == "no"]
        .drop_duplicates("trace_key")
        [["trace_key", "workload_group", "ipc"]]
        .rename(columns={"ipc": "no_ipc"})
    )
    group_order = {"SPEC17": 0, "Graph-GMS": 1, "Graph-Ligra": 2, "AI-ML": 3, "GTrace": 4}
    base["group_order"] = base["workload_group"].map(group_order).fillna(99)
    base["trace_label"] = base["trace_key"].map(short_trace_label)
    base = base.sort_values(["group_order", "trace_label"]).reset_index(drop=True)

    records = []
    classic_labels = {"ppf": "SPP+PPF", "pythia": "Pythia", "umama": "uMAMA"}
    for policy, label in classic_labels.items():
        rows = classic[classic["l2_prefetcher"] == policy].drop_duplicates("trace_key")[["trace_key", "ipc"]]
        merged = base.merge(rows, on="trace_key", how="inner")
        for _, row in merged.iterrows():
            records.append(
                {
                    "trace_key": row["trace_key"],
                    "trace_label": row["trace_label"],
                    "workload_group": row["workload_group"],
                    "method": label,
                    "speedup": float(row["ipc"] / row["no_ipc"]),
                }
            )

    ml = pd.read_csv(GRAPH_PACK / "ml_collection_by_trace.csv").copy()
    ml["trace_key"] = ml["trace"].map(trace_key)
    ml = ml[(ml["mode"] == "train_20M_20M") & (ml["policy"] == "mlp") & (ml["trace_key"].isin(trace_keys))].copy()
    target_mlp = float(common_12_row(common, "MLP")["geo_ipc"])
    ml_candidates = []
    for (iteration, threshold), group in ml.groupby(["iteration", "threshold"]):
        if group["trace_key"].nunique() != len(trace_keys):
            continue
        geo = geomean(group.drop_duplicates("trace_key")["ipc"])
        ml_candidates.append((abs(geo - target_mlp), int(iteration), float(threshold), group))
    if not ml_candidates:
        raise RuntimeError("No MLP per-trace rows found for the common 12-trace set.")
    _, _, _, ml_best = sorted(ml_candidates, key=lambda item: (item[0], -item[1]))[0]
    merged = base.merge(ml_best.drop_duplicates("trace_key")[["trace_key", "ipc"]], on="trace_key", how="inner")
    for _, row in merged.iterrows():
        records.append(
            {
                "trace_key": row["trace_key"],
                "trace_label": row["trace_label"],
                "workload_group": row["workload_group"],
                "method": "MLP",
                "speedup": float(row["ipc"] / row["no_ipc"]),
            }
        )

    llm = pd.read_csv(GRAPH_PACK / "llm_results_all.csv").copy()
    llm["trace_key"] = llm["trace_path"].map(trace_key)
    llm = llm[llm["trace_key"].isin(trace_keys)].copy()
    target_llm = float(common_12_row(common, "LLM")["geo_ipc"])
    llm_candidates = []
    for result_set, group in llm.groupby("source_result_set"):
        if group["trace_key"].nunique() != len(trace_keys):
            continue
        dedup = group.drop_duplicates("trace_key")
        geo = geomean(dedup["ipc"])
        iteration = int(dedup["source_iteration_num"].max())
        llm_candidates.append((abs(geo - target_llm), -iteration, str(result_set), dedup))
    if not llm_candidates:
        raise RuntimeError("No LLM per-trace rows found for the common 12-trace set.")
    _, _, _, llm_best = sorted(llm_candidates, key=lambda item: (item[0], item[1], item[2]))[0]
    merged = base.merge(llm_best[["trace_key", "ipc"]], on="trace_key", how="inner")
    for _, row in merged.iterrows():
        records.append(
            {
                "trace_key": row["trace_key"],
                "trace_label": row["trace_label"],
                "workload_group": row["workload_group"],
                "method": "LLM",
                "speedup": float(row["ipc"] / row["no_ipc"]),
            }
        )

    out = pd.DataFrame(records)
    order = base[["trace_key", "trace_label", "workload_group"]].copy()
    out = out.merge(order.assign(trace_order=np.arange(len(order))), on=["trace_key", "trace_label", "workload_group"])
    out = out.sort_values(["trace_order", "method"]).drop(columns=["trace_order"])
    return out


def figure_all_methods_by_trace() -> None:
    df = common_trace_speedups()
    df["improvement_pct"] = speedup_to_pct(df["speedup"])
    df.to_csv(FIG / "all_methods_by_trace_speedup.csv", index=False)
    if PACKAGED_GRAPH_PACK.exists():
        df.to_csv(PACKAGED_GRAPH_PACK / "all_methods_by_trace_speedup.csv", index=False)

    method_order = ["SPP+PPF", "Pythia", "uMAMA", "MLP", "LLM"]
    trace_order = df.drop_duplicates("trace_key")["trace_key"].tolist()
    labels = df.drop_duplicates("trace_key").set_index("trace_key")["trace_label"].to_dict()
    mat = (
        df.pivot_table(index="method", columns="trace_key", values="improvement_pct", aggfunc="first")
        .reindex(index=method_order, columns=trace_order)
    )

    fig, ax = plt.subplots(figsize=(10.2, 4.3))
    cmap = LinearSegmentedColormap.from_list("speedup_diverging", ["#B65A55", "#F7F7F7", "#2F7D72"])
    norm = TwoSlopeNorm(vmin=-25.0, vcenter=0.0, vmax=25.0)
    im = ax.imshow(mat.values, cmap=cmap, norm=norm, aspect="auto")

    ax.set_xticks(np.arange(len(trace_order)))
    ax.set_xticklabels([labels[t] for t in trace_order], rotation=35, ha="right", rotation_mode="anchor")
    ax.set_yticks(np.arange(len(method_order)))
    ax.set_yticklabels(method_order)
    ax.tick_params(length=0)
    ax.set_title("Mejora por traza", loc="left", fontsize=10, fontweight=600, color=PALETTE["text"], pad=7)

    for i, method in enumerate(method_order):
        for j, trace in enumerate(trace_order):
            value = float(mat.loc[method, trace])
            label = "0.0" if abs(value) < 0.05 else f"{value:+.1f}"
            ax.text(j, i, label, ha="center", va="center", fontsize=6.8, color=PALETTE["text"])

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.025)
    cbar.set_label("Mejora (%)")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(trace_order), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(method_order), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.0)
    ax.tick_params(which="minor", bottom=False, left=False)
    fig.tight_layout()
    savefig("fig_all_methods_by_trace")


def read_dagger_summary() -> pd.DataFrame:
    p = DAGGER_ROOT / "summary.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.read_csv(GRAPH_PACK / "ml_dagger_summary.csv")


def read_val_summary() -> pd.DataFrame:
    p = GRAPH_PACK / "ml_validation_summary_from_by_trace.csv"
    if p.exists():
        return pd.read_csv(p)
    df = read_dagger_summary()
    return df[df["kind"].astype(str).str.endswith("_val")].rename(columns={"geo_ipc": "geomean_ipc"})


def figure_dagger_dataset_growth() -> dict[str, float]:
    rows = []
    progress = pd.read_csv(DAGGER_ROOT / "models_progress.csv") if (DAGGER_ROOT / "models_progress.csv").exists() else pd.read_csv(GRAPH_PACK / "ml_models_progress.csv")
    for _, r in progress.drop_duplicates(["iteration", "sample_counts"]).iterrows():
        p = resolve_packaged_path(r["sample_counts"])
        if not p.exists():
            continue
        sc = pd.read_csv(p)
        rows.append(
            {
                "iteration": int(r["iteration"]),
                "total_rows": float(sc["rows"].sum()),
                "positive_rows": float(sc["positive_rows"].sum()),
                "sampled_rows": float(sc["sampled_rows"].sum()),
                "traces": int(sc["trace_id"].nunique()),
            }
        )
    df = pd.DataFrame(rows).drop_duplicates("iteration").sort_values("iteration")
    df["positive_pct"] = 100.0 * df["positive_rows"] / df["total_rows"]

    fig, ax1 = plt.subplots(figsize=(10.5, 5.4))
    x = np.arange(len(df))
    ax1.bar(x, df["total_rows"] / 1e6, color="#D6E4F2", label="Filas etiquetadas", width=0.62, edgecolor="white", linewidth=0.6)
    ax1.bar(x, df["positive_rows"] / 1e6, color="#2E6EA6", label="Filas positivas", width=0.62, edgecolor="white", linewidth=0.6)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"iter {i}" for i in df["iteration"]])
    style_axes(ax1, None, "Filas antes de muestreo (millones)")

    ax2 = ax1.twinx()
    ax2.plot(x, df["positive_pct"], color=PALETTE["mlp"], marker="o", linewidth=2.4, markersize=5.5, label="% positivo")
    ax2.set_ylabel("Clase positiva (%)")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color("#D2D2D7")
    ax2.set_ylim(0, max(65, df["positive_pct"].max() + 8))

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, frameon=False, loc="upper right")
    fig.tight_layout()
    savefig("fig_dagger_data")

    best = df.iloc[-1]
    return {
        "dagger_iters": int(df["iteration"].max()) + 1,
        "dagger_iter03_rows_m": float(df.loc[df["iteration"] == 3, "total_rows"].iloc[0] / 1e6) if (df["iteration"] == 3).any() else float("nan"),
        "dagger_iter03_positive_pct": float(df.loc[df["iteration"] == 3, "positive_pct"].iloc[0]) if (df["iteration"] == 3).any() else float("nan"),
        "dagger_last_rows_m": float(best["total_rows"] / 1e6),
    }


def figure_dagger_validation() -> dict[str, float]:
    val = read_val_summary()
    if "geo_ipc" in val.columns and "geomean_ipc" not in val.columns:
        val = val.rename(columns={"geo_ipc": "geomean_ipc"})
    val = val[val["policy"].isin(["mlp", "lgbm"])].copy()

    best = val.sort_values("geomean_ipc", ascending=False).groupby(["iteration", "policy"], as_index=False).first()

    fig, ax = plt.subplots(figsize=(9.8, 5.2))
    for pol in ["mlp", "lgbm"]:
        sub = best[best["policy"] == pol].sort_values("iteration")
        ax.plot(
            sub["iteration"],
            sub["geomean_ipc"],
            marker="o",
            linewidth=2.4,
            color=PALETTE[pol],
            label=pol.upper() if pol == "mlp" else "LightGBM",
        )
        for _, r in sub.iterrows():
            pass

    style_axes(ax, None, "IPC geométrico en validación")
    ax.set_xlabel("Iteración DAgger")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    savefig("fig_dagger_validation")

    overall_best = best.loc[best["geomean_ipc"].idxmax()]
    best_lgbm = best[best["policy"] == "lgbm"].sort_values("geomean_ipc", ascending=False).iloc[0]
    return {
        "dagger_best_policy": str(overall_best["policy"]).upper() if overall_best["policy"] == "mlp" else "LightGBM",
        "dagger_best_iter": int(overall_best["iteration"]),
        "dagger_best_ipc": float(overall_best["geomean_ipc"]),
        "dagger_best_threshold": float(overall_best["threshold"]),
        "dagger_lgbm_best_ipc": float(best_lgbm["geomean_ipc"]),
        "dagger_lgbm_best_iter": int(best_lgbm["iteration"]),
        "dagger_lgbm_best_threshold": float(best_lgbm["threshold"]),
    }


def read_dagger_offline_metrics() -> pd.DataFrame:
    packaged = GRAPH_PACK / "dagger_offline_metrics.csv"
    if packaged.exists():
        return pd.read_csv(packaged)

    pattern = re.compile(
        r"val(?: epoch=(?P<epoch>\d+))? pos_rows=(?P<pos_rows>\d+) "
        r"base=(?P<base>[0-9.]+) top1_hit=(?P<top1_hit>[0-9.]+) "
        r"top4_hit=(?P<top4_hit>[0-9.]+) top4_wrecall=(?P<top4_wrecall>[0-9.]+) "
        r"top4_precision=(?P<top4_precision>[0-9.]+)"
    )
    selected_epoch = re.compile(r"selected best_epoch=(?P<epoch>\d+)")
    rows: list[dict[str, float | int | str]] = []
    for iteration in range(5):
        for policy, rel in [("mlp", "models/mlp/train.log"), ("lgbm", "models/lgbm/train_lgbm.log")]:
            path = DAGGER_ROOT / f"iter{iteration:02d}" / rel
            if not path.exists():
                continue
            text = path.read_text(errors="replace")
            candidates = []
            for match in pattern.finditer(text):
                item: dict[str, float | int | str] = {
                    "iteration": iteration,
                    "policy": policy,
                    "epoch": int(match.group("epoch")) if match.group("epoch") is not None else -1,
                }
                for key in ["pos_rows", "base", "top1_hit", "top4_hit", "top4_wrecall", "top4_precision"]:
                    value = match.group(key)
                    item[key] = int(value) if key == "pos_rows" else float(value)
                candidates.append(item)
            if not candidates:
                continue
            selected = selected_epoch.search(text)
            if selected:
                epoch = int(selected.group("epoch"))
                chosen = next((row for row in candidates if row["epoch"] == epoch), None)
                if chosen is None:
                    chosen = max(candidates, key=lambda row: float(row["top4_wrecall"]))
            else:
                chosen = candidates[-1]
            rows.append(chosen)
    return pd.DataFrame(rows)


def figure_dagger_offline_metrics() -> dict[str, float]:
    df = read_dagger_offline_metrics()
    df.to_csv(FIG / "dagger_offline_metrics.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6), sharex=True)
    specs = [
        ("top4_wrecall", "Recall ponderado Top-4"),
        ("top4_precision", "Precisión Top-4"),
    ]
    labels = {"mlp": "MLP", "lgbm": "LightGBM"}
    for ax, (metric, title) in zip(axes, specs):
        for policy in ["mlp", "lgbm"]:
            sub = df[df["policy"] == policy].sort_values("iteration")
            ax.plot(
                sub["iteration"],
                sub[metric] * 100.0,
                marker="o",
                linewidth=2.6,
                markersize=5.5,
                color=PALETTE[policy],
                label=labels[policy],
            )
        style_axes(ax, title, "Porcentaje (%)")
        ax.set_xlabel("Iteración DAgger")
        ax.set_xticks(sorted(df["iteration"].unique()))
        ax.set_xlim(-0.15, 4.45)
        ax.set_ylim(20, 75)
    axes[0].legend(frameon=False, loc="upper right")
    fig.tight_layout()
    savefig("fig_dagger_offline_metrics")

    iter3 = df[df["iteration"] == 3].set_index("policy")
    return {
        "dagger_mlp_top1_pct": float(iter3.loc["mlp", "top1_hit"] * 100.0),
        "dagger_mlp_top4_hit_pct": float(iter3.loc["mlp", "top4_hit"] * 100.0),
        "dagger_mlp_top4_recall_pct": float(iter3.loc["mlp", "top4_wrecall"] * 100.0),
        "dagger_mlp_top4_precision_pct": float(iter3.loc["mlp", "top4_precision"] * 100.0),
        "dagger_lgbm_top1_pct": float(iter3.loc["lgbm", "top1_hit"] * 100.0),
        "dagger_lgbm_top4_hit_pct": float(iter3.loc["lgbm", "top4_hit"] * 100.0),
        "dagger_lgbm_top4_recall_pct": float(iter3.loc["lgbm", "top4_wrecall"] * 100.0),
        "dagger_lgbm_top4_precision_pct": float(iter3.loc["lgbm", "top4_precision"] * 100.0),
    }


def figure_dagger_offline_online() -> None:
    offline = read_dagger_offline_metrics()
    val = read_val_summary()
    if "geo_ipc" in val.columns and "geomean_ipc" not in val.columns:
        val = val.rename(columns={"geo_ipc": "geomean_ipc"})
    val = val[val["policy"].isin(["mlp", "lgbm"])].copy()
    online = val.sort_values("geomean_ipc", ascending=False).groupby(["iteration", "policy"], as_index=False).first()

    labels = {"mlp": "MLP", "lgbm": "LightGBM"}
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 6.2), sharex=True)
    for policy in ["mlp", "lgbm"]:
        off = offline[offline["policy"] == policy].sort_values("iteration")
        on = online[online["policy"] == policy].sort_values("iteration")
        axes[0].plot(
            off["iteration"],
            off["top4_wrecall"] * 100.0,
            marker="o",
            linewidth=2.5,
            markersize=5.2,
            color=PALETTE[policy],
            label=labels[policy],
        )
        axes[1].plot(
            on["iteration"],
            on["geomean_ipc"],
            marker="o",
            linewidth=2.5,
            markersize=5.2,
            color=PALETTE[policy],
            label=labels[policy],
        )

    style_axes(axes[0], None, "Recall Top-4 offline (%)")
    style_axes(axes[1], None, "IPC geométrico online")
    axes[1].set_xlabel("Iteración DAgger")
    axes[0].set_ylim(20, 75)
    axes[1].set_ylim(
        min(online["geomean_ipc"].min() - 0.01, 1.70),
        max(online["geomean_ipc"].max() + 0.01, 1.85),
    )
    ticks = sorted(offline["iteration"].unique())
    axes[1].set_xticks(ticks)
    axes[1].set_xticklabels([f"iter {i}" for i in ticks])
    axes[0].legend(frameon=False, loc="upper right")
    fig.tight_layout(h_pad=1.6)
    savefig("fig_dagger_offline_online")


def figure_dagger_same_traces() -> dict[str, float | int]:
    common = read_common_12_metrics()
    labels = ["No L2", "PPF", "Pythia", "uMAMA", "MLP", "LLM"]
    display_labels = {
        "No L2": "Sin prebúsqueda",
        "PPF": "SPP+PPF",
        "Pythia": "Pythia",
        "uMAMA": "uMAMA",
        "MLP": "MLP",
        "LLM": "LLM",
    }
    method_values = {label: float(common_12_row(common, label)["geo_ipc"]) for label in labels}
    trace_count = int(common["traces"].max())

    out = pd.DataFrame(
        {
            "method": [display_labels[label] for label in labels],
            "geomean_ipc": list(method_values.values()),
            "traces": trace_count,
        }
    )
    out.to_csv(FIG / "dagger_same_traces_compare.csv", index=False)
    if PACKAGED_GRAPH_PACK.exists():
        out.to_csv(PACKAGED_GRAPH_PACK / "dagger_same_traces_compare.csv", index=False)

    colors = {
        "No L2": "#B8B8BD",
        "PPF": PALETTE["ppf"],
        "Pythia": PALETTE["pythia"],
        "uMAMA": PALETTE["umama"],
        "MLP": PALETTE["mlp"],
        "LLM": PALETTE["llm"],
    }
    speedups = {label: float(common_12_row(common, label)["speedup"]) for label in labels}
    vals = speedup_to_pct([speedups[k] for k in labels])
    fig, ax = plt.subplots(figsize=(9.6, 4.85))
    ax.bar(
        np.arange(len(labels)),
        vals,
        color=[colors[k] for k in labels],
        edgecolor="white",
        linewidth=0.8,
        width=0.66,
    )
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels([display_labels[label] for label in labels])
    ax.axhline(0.0, color=PALETTE["text"], linestyle=(0, (4, 3)), linewidth=0.85, alpha=0.7)
    low = min(-5.0, float(np.nanmin(vals)) - 1.0)
    high = max(12.0, float(np.nanmax(vals)) + 1.0)
    ax.set_ylim(low, high)
    style_axes(ax, "Comparación principal", "Mejora geométrica (%)")
    fig.tight_layout()
    savefig("fig_dagger_same_traces")

    return {
        "dagger_compare_traces": trace_count,
        "dagger_compare_no_ipc": method_values["No L2"],
        "dagger_compare_ppf_ipc": method_values["PPF"],
        "dagger_compare_lgbm_ipc": 0.0,
        "dagger_compare_pythia_ipc": method_values["Pythia"],
        "dagger_compare_mlp_ipc": method_values["MLP"],
        "dagger_compare_umama_ipc": method_values["uMAMA"],
        "dagger_compare_llm_ipc": method_values["LLM"],
        "dagger_compare_no_improvement_pct": float(speedup_to_pct([speedups["No L2"]])[0]),
        "dagger_compare_ppf_improvement_pct": float(speedup_to_pct([speedups["PPF"]])[0]),
        "dagger_compare_pythia_improvement_pct": float(speedup_to_pct([speedups["Pythia"]])[0]),
        "dagger_compare_umama_improvement_pct": float(speedup_to_pct([speedups["uMAMA"]])[0]),
        "dagger_compare_mlp_improvement_pct": float(speedup_to_pct([speedups["MLP"]])[0]),
        "dagger_compare_llm_improvement_pct": float(speedup_to_pct([speedups["LLM"]])[0]),
        "dagger_compare_mlp_vs_pythia_pct": 100.0 * (method_values["MLP"] / method_values["Pythia"] - 1.0),
        "dagger_compare_mlp_vs_umama_pct": 100.0 * (1.0 - method_values["MLP"] / method_values["uMAMA"]),
    }


def figure_threshold_matrix() -> None:
    val = read_val_summary()
    if "geo_ipc" in val.columns and "geomean_ipc" not in val.columns:
        val = val.rename(columns={"geo_ipc": "geomean_ipc"})
    val = val[val["policy"].isin(["mlp", "lgbm"])].copy()
    row_labels = {
        ("mlp", -2.0): "MLP permisiva",
        ("mlp", -0.5): "MLP intermedia",
        ("mlp", 0.0): "MLP restrictiva",
        ("lgbm", -0.5): "LightGBM permisiva",
        ("lgbm", 0.0): "LightGBM intermedia",
        ("lgbm", 0.5): "LightGBM restrictiva",
    }
    val["row"] = val.apply(lambda r: row_labels.get((r["policy"], float(r["threshold"])), r["policy"].upper()), axis=1)
    order_rows = [
        "MLP permisiva",
        "MLP intermedia",
        "MLP restrictiva",
        "LightGBM permisiva",
        "LightGBM intermedia",
        "LightGBM restrictiva",
    ]
    mat = val.pivot_table(index="row", columns="iteration", values="geomean_ipc", aggfunc="first").reindex(order_rows)

    fig, ax = plt.subplots(figsize=(8.6, 4.9))
    im = ax.imshow(mat.values, cmap=APPLE_CMAP, aspect="auto")
    ax.set_xticks(np.arange(len(mat.columns)))
    ax.set_xticklabels([f"iter {i}" for i in mat.columns])
    ax.set_yticks(np.arange(len(mat.index)))
    ax.set_yticklabels(mat.index)
    ax.set_xlabel("Iteración DAgger")
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cbar.set_label("IPC geométrico")
    fig.tight_layout()
    savefig("fig_threshold_matrix")


def llm_process_metrics() -> dict[str, float]:
    llm = pd.read_csv(GRAPH_PACK / "llm_iteration_summary.csv")
    llm_all = pd.read_csv(GRAPH_PACK / "llm_results_all.csv")
    attempts_per_iteration = llm.groupby("source_iteration_num")["source_attempt"].nunique()

    return {
        "llm_iteration_count": int(llm["source_iteration_num"].nunique()),
        "llm_result_set_count": int(llm["source_result_set"].nunique()),
        "llm_trace_result_rows": int(len(llm_all)),
        "llm_max_attempts_per_iter": int(attempts_per_iteration.max()),
    }


def figure_llm_methods_12() -> dict[str, float]:
    common = read_common_12_metrics()
    labels = ["No L2", "PPF", "Pythia", "uMAMA", "LLM"]
    display_labels = {
        "No L2": "Sin prebúsqueda",
        "PPF": "SPP+PPF",
        "Pythia": "Pythia",
        "uMAMA": "uMAMA",
        "LLM": "LLM",
    }
    values_by_method = {label: float(common_12_row(common, label)["geo_ipc"]) for label in labels}

    colors = {
        "No L2": "#B8B8BD",
        "PPF": PALETTE["ppf"],
        "Pythia": PALETTE["pythia"],
        "uMAMA": PALETTE["umama"],
        "LLM": PALETTE["llm"],
    }
    speedups = {label: float(common_12_row(common, label)["speedup"]) for label in labels}
    values = speedup_to_pct([speedups[k] for k in labels])

    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    ax.bar(
        np.arange(len(labels)),
        values,
        color=[colors[k] for k in labels],
        edgecolor="white",
        linewidth=0.8,
        width=0.64,
    )
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels([display_labels[label] for label in labels])
    ax.axhline(0.0, color=PALETTE["text"], linestyle=(0, (4, 3)), linewidth=0.85, alpha=0.7)
    ax.set_ylim(min(-5.0, float(np.nanmin(values)) - 1.0), max(12.0, float(np.nanmax(values)) + 1.0))
    style_axes(ax, "LLM frente a referencias", "Mejora geométrica (%)")
    fig.tight_layout()
    savefig("fig_llm_methods_12")

    return {
        "llm_compare_trace_count": int(common["traces"].max()),
        "llm_compare_no_ipc": float(values_by_method["No L2"]),
        "llm_compare_ppf_ipc": float(values_by_method["PPF"]),
        "llm_compare_pythia_ipc": float(values_by_method["Pythia"]),
        "llm_compare_umama_ipc": float(values_by_method["uMAMA"]),
        "llm_compare_llm_ipc": float(values_by_method["LLM"]),
    }


def figure_shap() -> dict[str, float]:
    shap_file = GRAPH_PACK / "ml_lgbm_treeshap.csv"
    shap = pd.read_csv(shap_file).head(12)
    display_names = {
        "min_target_distance": "distancia de la candidata",
        "abs_delta": "magnitud del cambio",
        "delta": "dirección del cambio",
        "cache_hit": "acierto previo en caché",
        "mshr_occupancy_ratio": "presión de memoria",
        "ip_hist_count": "historial de la instrucción",
        "pq_occupancy_ratio": "ocupación de cola",
        "touch_mask[cand]": "actividad local reciente",
        "candidate_offset": "desplazamiento candidato",
        "useful_prefetch": "utilidad histórica",
        "pending_evicted_mask[cand]": "descartes recientes",
        "ml_pf_latency_bucket": "latencia observada",
    }
    shap["display_feature"] = shap["feature"].map(display_names).fillna(shap["feature"])
    shap = shap.iloc[::-1]
    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    ax.barh(shap["display_feature"], shap["share_of_total"] * 100, color="#2E6EA6", alpha=0.92)
    style_axes(ax, None, "Participación en |SHAP| total (%)")
    ax.grid(axis="x", color=PALETTE["grid"], linewidth=0.8, alpha=0.9)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    savefig("fig_lgbm_shap")

    top = pd.read_csv(shap_file).iloc[0]
    return {
        "shap_top_feature": display_names.get(str(top["feature"]), str(top["feature"])),
        "shap_top_share": float(top["share_of_total"]),
    }


def write_metrics(metrics: dict[str, float | int | str]) -> None:
    def compact_number(value: float) -> str:
        return f"{value:g}"

    def fmt(name: str, value: float | int | str) -> str:
        if isinstance(value, str):
            return f"\\newcommand{{\\{name}}}{{{value}}}"
        if isinstance(value, int):
            return f"\\newcommand{{\\{name}}}{{{value}}}"
        if name.endswith("Threshold"):
            return f"\\newcommand{{\\{name}}}{{{compact_number(value)}}}"
        if name.endswith("Pct") or "Pct" in name:
            return f"\\newcommand{{\\{name}}}{{{value:.1f}}}"
        return f"\\newcommand{{\\{name}}}{{{value:.3f}}}"

    derived = {
        "OnlinePpfGlobal": metrics["online_ppf_global"],
        "OnlinePythiaGlobal": metrics["online_pythia_global"],
        "OnlineUmamaGlobal": metrics["online_umama_global"],
        "OnlinePpfImprovementPct": metrics["online_ppf_improvement_pct"],
        "OnlinePythiaImprovementPct": metrics["online_pythia_improvement_pct"],
        "OnlineUmamaImprovementPct": metrics["online_umama_improvement_pct"],
        "OnlineUmamaTraces": metrics["online_umama_traces"],
        "OnlineCommonTraces": metrics["online_common_traces"],
        "OnlinePpfWins": metrics["online_ppf_wins"],
        "OnlinePythiaWins": metrics["online_pythia_wins"],
        "OnlineUmamaWins": metrics["online_umama_wins"],
        "OnlinePythiaOverUmama": metrics["online_pythia_over_umama"],
        "OnlineUmamaOverPythia": metrics["online_umama_over_pythia"],
        "OnlinePythiaUmamaTies": metrics["online_pythia_umama_ties"],
        "OnlinePythiaWinMarginPct": metrics["online_pythia_win_margin_pct"],
        "OnlineUmamaWinMarginPct": metrics["online_umama_win_margin_pct"],
        "OnlineAimlPythiaSpeedup": metrics["online_aiml_pythia_speedup"],
        "OnlineAimlUmamaSpeedup": metrics["online_aiml_umama_speedup"],
        "OnlinePpfLosses": metrics["online_ppf_losses"],
        "OnlinePythiaLosses": metrics["online_pythia_losses"],
        "OnlineUmamaLosses": metrics["online_umama_losses"],
        "OnlinePpfIssuedM": metrics["online_ppf_issued_m"],
        "OnlinePythiaIssuedM": metrics["online_pythia_issued_m"],
        "OnlineUmamaIssuedM": metrics["online_umama_issued_m"],
        "OnlinePpfUsefulM": metrics["online_ppf_useful_m"],
        "OnlinePythiaUsefulM": metrics["online_pythia_useful_m"],
        "OnlineUmamaUsefulM": metrics["online_umama_useful_m"],
        "OnlinePpfAccuracyPct": metrics["online_ppf_accuracy_pct"],
        "OnlinePythiaAccuracyPct": metrics["online_pythia_accuracy_pct"],
        "OnlineUmamaAccuracyPct": metrics["online_umama_accuracy_pct"],
        "OnlineAimlTraces": metrics["online_aiml_traces"],
        "OnlineAimlPpfWins": metrics["online_aiml_ppf_wins"],
        "OnlineAimlPythiaWins": metrics["online_aiml_pythia_wins"],
        "OnlineAimlUmamaWins": metrics["online_aiml_umama_wins"],
        "OnlineGtraceTraces": metrics["online_gtrace_traces"],
        "OnlineGtracePpfWins": metrics["online_gtrace_ppf_wins"],
        "OnlineGtracePythiaWins": metrics["online_gtrace_pythia_wins"],
        "OnlineGtraceUmamaWins": metrics["online_gtrace_umama_wins"],
        "OnlineGmsTraces": metrics["online_gms_traces"],
        "OnlineGmsPpfWins": metrics["online_gms_ppf_wins"],
        "OnlineGmsPythiaWins": metrics["online_gms_pythia_wins"],
        "OnlineGmsUmamaWins": metrics["online_gms_umama_wins"],
        "OnlineLigraTraces": metrics["online_ligra_traces"],
        "OnlineLigraPpfWins": metrics["online_ligra_ppf_wins"],
        "OnlineLigraPythiaWins": metrics["online_ligra_pythia_wins"],
        "OnlineLigraUmamaWins": metrics["online_ligra_umama_wins"],
        "OnlineSpecTraces": metrics["online_spec_traces"],
        "OnlineSpecPpfWins": metrics["online_spec_ppf_wins"],
        "OnlineSpecPythiaWins": metrics["online_spec_pythia_wins"],
        "OnlineSpecUmamaWins": metrics["online_spec_umama_wins"],
        "DaggerIterations": metrics["dagger_iters"],
        "DaggerIterThreeRowsM": metrics["dagger_iter03_rows_m"],
        "DaggerIterThreePositivePct": metrics["dagger_iter03_positive_pct"],
        "DaggerBestPolicy": metrics["dagger_best_policy"],
        "DaggerBestIter": metrics["dagger_best_iter"],
        "DaggerBestIpc": metrics["dagger_best_ipc"],
        "DaggerBestThreshold": metrics["dagger_best_threshold"],
        "DaggerLgbmBestIpc": metrics["dagger_lgbm_best_ipc"],
        "DaggerLgbmBestIter": metrics["dagger_lgbm_best_iter"],
        "DaggerLgbmBestThreshold": metrics["dagger_lgbm_best_threshold"],
        "DaggerMlpTopOnePct": metrics["dagger_mlp_top1_pct"],
        "DaggerMlpTopFourHitPct": metrics["dagger_mlp_top4_hit_pct"],
        "DaggerMlpTopFourRecallPct": metrics["dagger_mlp_top4_recall_pct"],
        "DaggerMlpTopFourPrecisionPct": metrics["dagger_mlp_top4_precision_pct"],
        "DaggerLgbmTopOnePct": metrics["dagger_lgbm_top1_pct"],
        "DaggerLgbmTopFourHitPct": metrics["dagger_lgbm_top4_hit_pct"],
        "DaggerLgbmTopFourRecallPct": metrics["dagger_lgbm_top4_recall_pct"],
        "DaggerLgbmTopFourPrecisionPct": metrics["dagger_lgbm_top4_precision_pct"],
        "DaggerCompareTraces": metrics["dagger_compare_traces"],
        "DaggerCompareNoIpc": metrics["dagger_compare_no_ipc"],
        "DaggerComparePpfIpc": metrics["dagger_compare_ppf_ipc"],
        "DaggerComparePythiaIpc": metrics["dagger_compare_pythia_ipc"],
        "DaggerCompareMlpIpc": metrics["dagger_compare_mlp_ipc"],
        "DaggerCompareUmamaIpc": metrics["dagger_compare_umama_ipc"],
        "DaggerCompareLlmIpc": metrics["dagger_compare_llm_ipc"],
        "DaggerCompareNoImprovementPct": metrics["dagger_compare_no_improvement_pct"],
        "DaggerComparePpfImprovementPct": metrics["dagger_compare_ppf_improvement_pct"],
        "DaggerComparePythiaImprovementPct": metrics["dagger_compare_pythia_improvement_pct"],
        "DaggerCompareMlpImprovementPct": metrics["dagger_compare_mlp_improvement_pct"],
        "DaggerCompareUmamaImprovementPct": metrics["dagger_compare_umama_improvement_pct"],
        "DaggerCompareLlmImprovementPct": metrics["dagger_compare_llm_improvement_pct"],
        "DaggerCompareMlpVsPythiaPct": metrics["dagger_compare_mlp_vs_pythia_pct"],
        "DaggerCompareMlpVsUmamaPct": metrics["dagger_compare_mlp_vs_umama_pct"],
        "LlmIterationCount": metrics["llm_iteration_count"],
        "LlmResultSetCount": metrics["llm_result_set_count"],
        "LlmTraceResultRows": metrics["llm_trace_result_rows"],
        "LlmMaxAttemptsPerIter": metrics["llm_max_attempts_per_iter"],
        "LlmCompareTraceCount": metrics["llm_compare_trace_count"],
        "LlmCompareNoIpc": metrics["llm_compare_no_ipc"],
        "LlmComparePpfIpc": metrics["llm_compare_ppf_ipc"],
        "LlmComparePythiaIpc": metrics["llm_compare_pythia_ipc"],
        "LlmCompareUmamaIpc": metrics["llm_compare_umama_ipc"],
        "LlmCompareLlmIpc": metrics["llm_compare_llm_ipc"],
        "ShapTopFeature": metrics["shap_top_feature"].replace("_", "\\_"),
        "ShapTopSharePct": metrics["shap_top_share"] * 100.0,
    }

    lines = [
        "% Auto-generated by scripts/build_figures.py. Do not edit manually.",
        *[fmt(k, v) for k, v in derived.items()],
        "",
    ]
    text = "\n".join(lines)
    (REPO_ROOT / "generated_metrics.tex").write_text(text, encoding="utf-8")
    if LATEX_ROOT.exists():
        (LATEX_ROOT / "generated_metrics.tex").write_text(text, encoding="utf-8")


def main() -> None:
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.dpi": 120,
            "figure.facecolor": "white",
            "axes.facecolor": PALETTE["face"],
            "savefig.facecolor": "white",
        }
    )

    metrics: dict[str, float | int | str] = {}
    figure_diagram_ppf()
    figure_diagram_pythia()
    figure_diagram_mab()
    figure_diagram_dagger()
    figure_intel_l2_history()
    metrics.update(figure_online_speedup())
    figure_all_methods_by_trace()
    metrics.update(figure_dagger_dataset_growth())
    metrics.update(figure_dagger_validation())
    metrics.update(figure_dagger_offline_metrics())
    figure_dagger_offline_online()
    metrics.update(figure_dagger_same_traces())
    figure_threshold_matrix()
    metrics.update(llm_process_metrics())
    metrics.update(figure_llm_methods_12())
    metrics.update(figure_shap())
    write_metrics(metrics)
    print("Generated figures and generated_metrics.tex")
    for p in sorted(FIG.glob("fig_*.pdf")):
        print(p.name)


if __name__ == "__main__":
    main()
