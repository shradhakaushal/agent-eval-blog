"""
Three Plotly animations for the agent eval blog post.

Run this as a notebook cell. It reads from:
  - `df` (the full aggregate_results DataFrame, must include both baseline
    and calibration_v1)
  - `df_baseline_w4` (the W4 phase-scoring DataFrame from score_w4_full_batch)

If df_baseline_w4 isn't in your namespace, reload it:
    from phase_scoring import score_w4_full_batch
    df_baseline_w4 = score_w4_full_batch("baseline")

Outputs three HTML files:
  - chart1_cost_accumulation.html
  - chart2_artifact_variance.html
  - chart3_phase_waterfall.html
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# ============================================================
# Chart 1: cost accumulates over trajectory steps
# ============================================================
# Animation: per step, show cumulative cost for each trajectory as a line.
# Baseline lines climb steadily and high. Intervention lines plateau early.
# The divergence point is the story.

def build_chart1_cost_accumulation(df, runs_root=Path("runs")):
    """Per-step cumulative cost across baseline + calibration_v1 G1 trajectories."""
    PRICE_IN = 3.00 / 1_000_000
    PRICE_OUT = 15.00 / 1_000_000

    rows = []
    g1 = df[df["task_id"] == "G1_short_forecast"]
    for _, r in g1.iterrows():
        run_dir = runs_root / f"{r['config_name']}__G1_short_forecast__seed{r['seed']}"
        traj_path = run_dir / "trajectory.json"
        if not traj_path.exists():
            continue
        with open(traj_path) as f:
            traj = json.load(f)
        cum_cost = 0.0
        # Step 0 = baseline cost (zero before any step)
        rows.append({
            "config_name": r["config_name"],
            "seed": int(r["seed"]),
            "step": 0,
            "cum_cost": 0.0,
            "outcome": r["outcome_category"],
        })
        for i, step in enumerate(traj["steps"], start=1):
            cum_cost += step["input_tokens"] * PRICE_IN + step["output_tokens"] * PRICE_OUT
            rows.append({
                "config_name": r["config_name"],
                "seed": int(r["seed"]),
                "step": i,
                "cum_cost": cum_cost,
                "outcome": r["outcome_category"],
            })

    df_steps = pd.DataFrame(rows)
    # Pad shorter trajectories with their final cost so the animation lines
    # don't disappear at different steps (carry-forward the last value).
    max_steps = df_steps["step"].max()
    padded = []
    for (config, seed), g in df_steps.groupby(["config_name", "seed"]):
        g = g.sort_values("step")
        final_cost = g["cum_cost"].iloc[-1]
        final_step = g["step"].iloc[-1]
        outcome = g["outcome"].iloc[-1]
        for s in range(int(final_step) + 1, int(max_steps) + 1):
            g = pd.concat([g, pd.DataFrame([{
                "config_name": config, "seed": seed, "step": s,
                "cum_cost": final_cost, "outcome": outcome,
            }])], ignore_index=True)
        padded.append(g)
    df_padded = pd.concat(padded, ignore_index=True)

    # Build one trace per (config, seed) — animation slider over `step`.
    fig = go.Figure()
    color_map = {
        "baseline": "rgba(136, 136, 136, 0.6)",
        "calibration_v1": "rgba(46, 134, 171, 0.85)",
    }
    legend_added = {"baseline": False, "calibration_v1": False}

    for (config, seed), g in df_padded.groupby(["config_name", "seed"]):
        g = g.sort_values("step")
        show_legend = not legend_added[config]
        legend_added[config] = True
        fig.add_trace(go.Scatter(
            x=g["step"], y=g["cum_cost"],
            mode="lines",
            line=dict(color=color_map[config], width=2),
            name=("Baseline" if config == "baseline" else "Calibration intervention"),
            legendgroup=config,
            showlegend=show_legend,
            hovertemplate=(
                f"<b>{config} seed {seed}</b><br>"
                "Step %{x}<br>"
                "Cumulative cost: $%{y:.3f}<br>"
                "<extra></extra>"
            ),
        ))

    # Build frames for animation: at each step, only show data up to that step.
    steps_axis = sorted(df_padded["step"].unique())
    frames = []
    for s in steps_axis:
        frame_data = []
        for (config, seed), g in df_padded.groupby(["config_name", "seed"]):
            g = g.sort_values("step")
            g_until = g[g["step"] <= s]
            frame_data.append(go.Scatter(
                x=g_until["step"], y=g_until["cum_cost"],
                mode="lines",
                line=dict(color=color_map[config], width=2),
            ))
        frames.append(go.Frame(data=frame_data, name=str(int(s))))
    fig.frames = frames

    fig.update_layout(
        title=dict(
            text=("<b>Cost accumulation per trajectory: G1 short-forecast task</b>"
                  "<br><sub>Baseline (gray) keeps spending; intervention (blue) plateaus early</sub>"),
            x=0.5, xanchor="center",
        ),
        xaxis=dict(title="Step within trajectory", range=[0, max_steps + 0.5]),
        yaxis=dict(title="Cumulative cost (USD)", range=[0,
                                                          df_padded["cum_cost"].max() * 1.1]),
        width=900, height=520,
        plot_bgcolor="white",
        updatemenus=[dict(
            type="buttons", showactive=False,
            x=0.0, y=-0.15, xanchor="left", yanchor="top",
            buttons=[
                dict(label="▶ Play", method="animate", args=[None, dict(
                    frame=dict(duration=300, redraw=True),
                    fromcurrent=True, transition=dict(duration=0),
                )]),
                dict(label="⏸ Pause", method="animate", args=[[None], dict(
                    frame=dict(duration=0, redraw=False),
                    mode="immediate", transition=dict(duration=0),
                )]),
            ],
        )],
        sliders=[dict(
            active=int(max_steps),
            steps=[dict(
                method="animate",
                args=[[str(int(s))], dict(
                    frame=dict(duration=0, redraw=True),
                    mode="immediate", transition=dict(duration=0),
                )],
                label=str(int(s)),
            ) for s in steps_axis],
            x=0.1, y=-0.05, len=0.85,
            currentvalue=dict(prefix="Step: ", font=dict(size=14)),
        )],
    )
    fig.update_xaxes(showgrid=True, gridcolor="lightgray")
    fig.update_yaxes(showgrid=True, gridcolor="lightgray", tickprefix="$")

    return fig


# ============================================================
# Chart 2: artifact variance per seed
# ============================================================
# Per-seed scatter for each config showing artifact counts. Animated reveal
# bar-by-bar so the eye tracks the spread.

def build_chart2_artifact_variance(df, runs_root=Path("runs")):
    """Per-seed artifact counts for baseline vs intervention on G1."""
    rows = []
    g1 = df[df["task_id"] == "G1_short_forecast"]
    for _, r in g1.iterrows():
        run_dir = runs_root / f"{r['config_name']}__G1_short_forecast__seed{r['seed']}"
        if not run_dir.exists():
            continue
        n_artifacts = sum(
            1 for p in run_dir.iterdir()
            if p.is_file() and p.name != "trajectory.json"
        )
        total_kb = sum(
            p.stat().st_size for p in run_dir.iterdir()
            if p.is_file() and p.name != "trajectory.json"
        ) / 1024
        rows.append({
            "config_name": r["config_name"],
            "seed": int(r["seed"]),
            "n_artifacts": n_artifacts,
            "total_kb": total_kb,
            "outcome": r["outcome_category"],
        })
    df_a = pd.DataFrame(rows).sort_values(["config_name", "seed"])

    # Two-panel: artifact count + total size
    fig = go.Figure()
    color_map = {"baseline": "#888888", "calibration_v1": "#2E86AB"}
    label_map = {"baseline": "Baseline", "calibration_v1": "Calibration"}

    for config in ["baseline", "calibration_v1"]:
        sub = df_a[df_a["config_name"] == config]
        fig.add_trace(go.Bar(
            x=sub["seed"], y=sub["n_artifacts"],
            name=label_map[config],
            marker_color=color_map[config],
            text=sub["n_artifacts"], textposition="outside",
            hovertemplate=(
                f"<b>{label_map[config]}, seed %{{x}}</b><br>"
                "Artifacts: %{y}<br>"
                "<extra></extra>"
            ),
        ))

    # Build frames revealing one seed at a time
    seeds_order = sorted(df_a["seed"].unique())
    frames = []
    for n in range(1, len(seeds_order) + 1):
        visible_seeds = set(seeds_order[:n])
        frame_data = []
        for config in ["baseline", "calibration_v1"]:
            sub = df_a[(df_a["config_name"] == config)
                       & (df_a["seed"].isin(visible_seeds))]
            frame_data.append(go.Bar(
                x=sub["seed"], y=sub["n_artifacts"],
                marker_color=color_map[config],
                text=sub["n_artifacts"], textposition="outside",
            ))
        frames.append(go.Frame(data=frame_data, name=f"seed_{seeds_order[n - 1]}"))
    fig.frames = frames

    baseline_mean = df_a[df_a["config_name"] == "baseline"]["n_artifacts"].mean()
    calib_mean = df_a[df_a["config_name"] == "calibration_v1"]["n_artifacts"].mean()

    fig.update_layout(
        title=dict(
            text=(f"<b>Artifacts produced per seed: G1 task</b>"
                  f"<br><sub>Baseline mean: {baseline_mean:.1f} files | "
                  f"Calibration mean: {calib_mean:.1f} files. "
                  f"Refusing agents produce fewer (and more relevant) deliverables.</sub>"),
            x=0.5, xanchor="center",
        ),
        xaxis=dict(title="Seed", tickmode="linear", dtick=1),
        yaxis=dict(title="Number of artifacts produced",
                   range=[0, df_a["n_artifacts"].max() + 1.5]),
        barmode="group",
        width=900, height=520,
        plot_bgcolor="white",
        updatemenus=[dict(
            type="buttons", showactive=False,
            x=0.0, y=-0.15, xanchor="left", yanchor="top",
            buttons=[
                dict(label="▶ Play", method="animate", args=[None, dict(
                    frame=dict(duration=400, redraw=True),
                    fromcurrent=True,
                )]),
                dict(label="⏸ Pause", method="animate", args=[[None], dict(
                    frame=dict(duration=0, redraw=False),
                    mode="immediate",
                )]),
            ],
        )],
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="lightgray")

    return fig


# ============================================================
# Chart 3: phase waterfall for W4
# ============================================================
# Animated waterfall: at each phase, show the % of trajectories still passing
# after that phase. The drop at phase 4 is the story.

def build_chart3_phase_waterfall(df_baseline_w4):
    """W4 phase survival as an animated waterfall."""
    n_total = len(df_baseline_w4)
    if n_total == 0:
        raise ValueError("df_baseline_w4 is empty")

    # For each k from 1..5, P(all phases 1..k passed)
    cumulative_pass = []
    for k in range(1, 6):
        cols = [f"phase_{j}" for j in range(1, k + 1)]
        n_pass = (df_baseline_w4[cols].sum(axis=1) == k).sum()
        cumulative_pass.append(n_pass / n_total * 100)

    phase_labels = [
        "Start", "Phase 1<br>Data Loading", "Phase 2<br>Assignment Diagnosis",
        "Phase 3<br>Bias Recognition", "Phase 4<br>Method Recommendation",
        "Phase 5<br>Deliverable Production",
    ]
    survival = [100.0] + cumulative_pass

    # Drop at each phase (for hover info)
    drops = [survival[i - 1] - survival[i] for i in range(1, len(survival))]

    fig = go.Figure()
    bar_colors = ["#2E8B57"] + [
        "#2E8B57" if d == 0 else "#DC143C" for d in drops
    ]
    fig.add_trace(go.Bar(
        x=phase_labels, y=survival,
        marker_color=bar_colors,
        text=[f"{v:.0f}%" for v in survival],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Trajectories still passing: %{y:.0f}%<extra></extra>",
    ))

    # Annotations for the drops
    annotations = []
    for i in range(1, len(survival)):
        if drops[i - 1] > 0:
            annotations.append(dict(
                x=phase_labels[i], y=(survival[i - 1] + survival[i]) / 2,
                text=f"−{drops[i - 1]:.0f}pp", showarrow=False,
                font=dict(color="#DC143C", size=12, family="Arial Black"),
                xshift=-40,
            ))

    # Frames: reveal phase by phase
    frames = []
    for k in range(len(survival)):
        partial = survival[: k + 1] + [None] * (len(survival) - k - 1)
        partial_text = [f"{v:.0f}%" if v is not None else "" for v in partial]
        frames.append(go.Frame(data=[go.Bar(
            x=phase_labels, y=partial,
            marker_color=bar_colors,
            text=partial_text, textposition="outside",
        )], name=str(k)))
    fig.frames = frames

    fig.update_layout(
        title=dict(
            text=(f"<b>W4 phase decomposition: where do baseline agents fail?</b>"
                  f"<br><sub>{n_total} trajectories. Outcome-only scoring says "
                  f"{100 - cumulative_pass[-1]:.0f}% fail. Phase scoring shows the failure "
                  f"is concentrated at Phase 4.</sub>"),
            x=0.5, xanchor="center",
        ),
        xaxis=dict(title=""),
        yaxis=dict(title="% trajectories passing through this phase", range=[0, 110]),
        width=950, height=550,
        plot_bgcolor="white",
        showlegend=False,
        annotations=annotations,
        updatemenus=[dict(
            type="buttons", showactive=False,
            x=0.0, y=-0.15, xanchor="left", yanchor="top",
            buttons=[
                dict(label="▶ Play", method="animate", args=[None, dict(
                    frame=dict(duration=700, redraw=True),
                    fromcurrent=True,
                )]),
                dict(label="⏸ Pause", method="animate", args=[[None], dict(
                    frame=dict(duration=0, redraw=False),
                    mode="immediate",
                )]),
            ],
        )],
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="lightgray", ticksuffix="%")

    return fig


# ============================================================
# Build and save all three
# ============================================================

if __name__ == "__main__" or True:
    # In notebook usage, expect df and df_baseline_w4 to be in scope.
    # If running as a script, this would need adapting.
    pass


def build_all(df, df_baseline_w4, outdir=Path(".")):
    """Build all three charts, save as HTML, return the figures."""
    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True)

    print("Building chart 1: cost accumulation...")
    fig1 = build_chart1_cost_accumulation(df)
    fig1.write_html(outdir / "chart1_cost_accumulation.html")
    print(f"  Saved {outdir / 'chart1_cost_accumulation.html'}")

    print("Building chart 2: artifact variance...")
    fig2 = build_chart2_artifact_variance(df)
    fig2.write_html(outdir / "chart2_artifact_variance.html")
    print(f"  Saved {outdir / 'chart2_artifact_variance.html'}")

    print("Building chart 3: phase waterfall...")
    fig3 = build_chart3_phase_waterfall(df_baseline_w4)
    fig3.write_html(outdir / "chart3_phase_waterfall.html")
    print(f"  Saved {outdir / 'chart3_phase_waterfall.html'}")

    return fig1, fig2, fig3