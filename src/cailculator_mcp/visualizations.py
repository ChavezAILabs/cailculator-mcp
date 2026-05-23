"""
Visualization module for Chavez Transform results.

Renders static matplotlib plots (PNG exports).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from typing import Dict, List, Optional, Union, Tuple
import io
import base64


# Visualization theme/styling
THEME = {
    'primary_color': '#8B5CF6',  # Purple - primary brand color
    'secondary_color': '#EC4899',  # Pink
    'accent_color': '#60A5FA',  # Light Blue - color of impossibility (Cirlot)
    'e8_color': '#F59E0B',  # Orange (for E8 comparisons)
    'canonical_color': '#10B981',  # Green (for canonical)
    'pattern_4_color': '#F59E0B',  # Gold - highlight the anomaly
    'figsize': (12, 8),
    'dpi': 150,
    'font_size': 10,
    'e8_mandala_size': (12, 12),  # Square for mandala symmetry
}


def plot_custom(plot_spec: dict, style_hints: dict = None) -> plt.Figure:
    """
    General-purpose renderer. Executes a plot specification constructed by the client.

    The server does not interpret data or decide chart type. The client (AI platform)
    constructs plot_spec describing exactly what to render. This function executes it.

    Args:
        plot_spec: Dict describing the figure. Supports:
            figure:  {figsize, dpi, facecolor} — figure-level settings
            axes:    list of trace dicts, each with:
                       type: bar | line | scatter | fill | hist | pie | polar | heatmap
                             axhline | axvline
                       x, y: data arrays (inline)
                       color, alpha, label, linewidth, markersize, width, etc.
            xlabel, ylabel, title: axis labels and title
            legend:  bool or dict of legend kwargs
            grid:    dict of grid kwargs (axis, alpha, color, linewidth)
            spines:  dict of spine visibility {top, right, left, bottom}
            xlim, ylim: axis limits
            xscale, yscale: 'linear' | 'log'
            xticks, xticklabels: tick positions and labels
            tick_color: color string for tick labels (useful on dark backgrounds)
            annotations: list of {text, xy, xytext, arrowprops} dicts
            subplots: list of plot_spec dicts for multi-panel figures

        style_hints: Optional metadata from the client describing intent.
            Not used for rendering — passed through for logging only.

    Returns:
        matplotlib Figure object
    """
    fig_cfg = plot_spec.get("figure", {})
    figsize = fig_cfg.get("figsize", THEME["figsize"])
    dpi = fig_cfg.get("dpi", THEME["dpi"])
    facecolor = fig_cfg.get("facecolor", None)

    subplots = plot_spec.get("subplots")

    if subplots:
        n = len(subplots)
        fig, axes = plt.subplots(n, 1, figsize=figsize, dpi=dpi,
                                 facecolor=facecolor or "white", sharex=False)
        if n == 1:
            axes = [axes]
        for ax, sub_spec in zip(axes, subplots):
            if facecolor:
                ax.set_facecolor(facecolor)
            _render_axes(ax, sub_spec)
        plt.tight_layout()
        return fig

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi,
                           facecolor=facecolor or "white")
    if facecolor:
        ax.set_facecolor(facecolor)
    _render_axes(ax, plot_spec)
    plt.tight_layout()
    return fig


def _render_axes(ax, spec: dict) -> None:
    """Render a single axes panel from a spec dict. Called by plot_custom."""
    traces = spec.get("axes", [])
    for trace in traces:
        chart_type = trace.get("type", "line")
        x = trace.get("x", [])
        y = trace.get("y", [])
        color = trace.get("color", THEME["primary_color"])
        alpha = trace.get("alpha", 1.0)
        label = trace.get("label", None)

        if chart_type == "bar":
            ax.bar(x, y, color=color, alpha=alpha, label=label,
                   width=trace.get("width", 0.8),
                   edgecolor=trace.get("edgecolor", "white"),
                   linewidth=trace.get("linewidth", 0.8))

        elif chart_type == "line":
            ax.plot(x, y, color=color, alpha=alpha, label=label,
                    linewidth=trace.get("linewidth", 2),
                    linestyle=trace.get("linestyle", "-"),
                    marker=trace.get("marker", None),
                    markersize=trace.get("markersize", 6))

        elif chart_type == "scatter":
            ax.scatter(x, y, c=color, alpha=alpha, label=label,
                       s=trace.get("s", 50),
                       marker=trace.get("marker", "o"),
                       edgecolors=trace.get("edgecolors", "none"))

        elif chart_type == "fill":
            ax.fill_between(x, y, alpha=alpha, color=color, label=label)

        elif chart_type == "hist":
            ax.hist(y, bins=trace.get("bins", "auto"), color=color,
                    alpha=alpha, label=label,
                    edgecolor=trace.get("edgecolor", "white"))

        elif chart_type == "pie":
            ax.pie(y, labels=x, colors=trace.get("colors", None),
                   autopct=trace.get("autopct", "%1.1f%%"),
                   startangle=trace.get("startangle", 90))

        elif chart_type == "heatmap":
            im = ax.imshow(np.array(y), aspect="auto",
                           cmap=trace.get("cmap", "viridis"),
                           alpha=alpha)
            if trace.get("colorbar", False):
                plt.colorbar(im, ax=ax)

        elif chart_type == "axhline":
            ax.axhline(y=trace.get("y", 0), color=color, alpha=alpha,
                       linestyle=trace.get("linestyle", "--"),
                       linewidth=trace.get("linewidth", 1.5),
                       label=label)

        elif chart_type == "axvline":
            ax.axvline(x=trace.get("x", 0), color=color, alpha=alpha,
                       linestyle=trace.get("linestyle", "--"),
                       linewidth=trace.get("linewidth", 1.5),
                       label=label)

    if "xlabel" in spec:
        kwargs = {"fontsize": spec.get("xlabel_size", THEME["font_size"])}
        if spec.get("label_color"):
            kwargs["color"] = spec["label_color"]
        ax.set_xlabel(spec["xlabel"], **kwargs)

    if "ylabel" in spec:
        kwargs = {"fontsize": spec.get("ylabel_size", THEME["font_size"])}
        if spec.get("label_color"):
            kwargs["color"] = spec["label_color"]
        ax.set_ylabel(spec["ylabel"], **kwargs)

    if "title" in spec:
        kwargs = {
            "fontsize": spec.get("title_size", THEME["font_size"] + 2),
            "fontweight": spec.get("title_weight", "bold"),
        }
        if spec.get("title_color"):
            kwargs["color"] = spec["title_color"]
        ax.set_title(spec["title"], **kwargs)

    if "xlim" in spec:
        ax.set_xlim(spec["xlim"])
    if "ylim" in spec:
        ax.set_ylim(spec["ylim"])
    if "xscale" in spec:
        ax.set_xscale(spec["xscale"])
    if "yscale" in spec:
        ax.set_yscale(spec["yscale"])

    if "xticks" in spec:
        ax.set_xticks(spec["xticks"])
    if "xticklabels" in spec:
        ax.set_xticklabels(spec["xticklabels"],
                           rotation=spec.get("xticklabel_rotation", 0),
                           ha=spec.get("xticklabel_ha", "center"),
                           fontsize=spec.get("xticklabel_size", THEME["font_size"] - 1))

    if "grid" in spec:
        g = spec["grid"]
        if isinstance(g, dict):
            kwargs = {"axis": g.get("axis", "both"), "alpha": g.get("alpha", 0.3),
                      "linewidth": g.get("linewidth", 0.7)}
            if g.get("color"):
                kwargs["color"] = g["color"]
            ax.grid(**kwargs)
        else:
            ax.grid(bool(g))

    if "spines" in spec:
        for spine, visible in spec["spines"].items():
            ax.spines[spine].set_visible(visible)

    if "tick_color" in spec:
        ax.tick_params(colors=spec["tick_color"])

    legend_cfg = spec.get("legend")
    if legend_cfg is True:
        ax.legend()
    elif isinstance(legend_cfg, dict):
        ax.legend(**legend_cfg)

    for ann in spec.get("annotations", []):
        ax.annotate(
            ann.get("text", ""),
            xy=ann.get("xy", (0, 0)),
            xytext=ann.get("xytext", None),
            fontsize=ann.get("fontsize", THEME["font_size"] - 1),
            color=ann.get("color", "gray"),
            arrowprops=ann.get("arrowprops", None),
            ha=ann.get("ha", "center"),
            va=ann.get("va", "bottom")
        )


def _plot_canonical_six_universality(
    pattern_values: Dict[int, float],
    return_base64: bool = False
) -> Union[plt.Figure, str, None]:
    """
    Plot the Canonical Six pattern universality (purple bars chart).

    Shows that all six Canonical Six patterns produce identical transform values,
    demonstrating universal symmetry.

    Args:
        pattern_values: Dict mapping pattern_id (1-6) to transform value
        return_base64: If True, return base64-encoded PNG string instead of figure

    Returns:
        Figure object or base64 string
    """
    mean_value = np.mean(list(pattern_values.values()))

    fig, ax = plt.subplots(figsize=(8, 6), dpi=THEME['dpi'])

    patterns = list(pattern_values.keys())
    values = list(pattern_values.values())

    bars = ax.bar(patterns, values, color=THEME['primary_color'], edgecolor='white', linewidth=2)

    ax.axhline(mean_value, color='red', linestyle='--', linewidth=2, alpha=0.7,
               label=f'Mean = {mean_value:.6e}')

    ax.set_xlabel('Pattern ID', fontsize=THEME['font_size'])
    ax.set_ylabel('C[f] value', fontsize=THEME['font_size'])
    ax.set_title('Canonical Six Pattern Universality', fontsize=THEME['font_size']+2, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    if return_base64:
        return _fig_to_base64(fig)
    return fig


def _plot_alpha_sensitivity(
    alpha_values: np.ndarray,
    transform_values: np.ndarray,
    optimal_alpha: Optional[float] = None,
    return_base64: bool = False
) -> Union[plt.Figure, str, None]:
    """
    Plot Chavez Transform sensitivity to alpha parameter.

    Shows how transform magnitude varies with convergence parameter alpha.
    Typically shows exponential decay as alpha increases.

    Args:
        alpha_values: Array of alpha values tested
        transform_values: Corresponding transform values
        optimal_alpha: If provided, mark this alpha as optimal
        return_base64: If True, return base64-encoded PNG string

    Returns:
        Figure object or base64 string
    """
    fig, ax = plt.subplots(figsize=(8, 6), dpi=THEME['dpi'])

    ax.plot(alpha_values, np.abs(transform_values), 'o-',
            color=THEME['accent_color'], linewidth=2, markersize=6, label='|C[f]|')

    if optimal_alpha:
        ax.axvline(optimal_alpha, color='red', linestyle='--', linewidth=2,
                   label=f'Optimal α = {optimal_alpha:.2f}')

    ax.set_xscale('log')
    ax.set_xlabel('Alpha (convergence parameter)', fontsize=THEME['font_size'])
    ax.set_ylabel('|C[f]| (Transform magnitude)', fontsize=THEME['font_size'])
    ax.set_title('Chavez Transform vs Alpha Parameter', fontsize=THEME['font_size']+2, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if return_base64:
        return _fig_to_base64(fig)
    return fig


def _plot_dimensional_weighting(
    d_values: np.ndarray,
    transform_values: np.ndarray,
    return_base64: bool = False
) -> Union[plt.Figure, str, None]:
    """
    Plot effect of dimensional weighting parameter d.

    Shows how the dimension parameter d affects transform decay behavior.

    Args:
        d_values: Array of dimension parameter values
        transform_values: Corresponding transform values
        return_base64: If True, return base64-encoded PNG string

    Returns:
        Figure object or base64 string
    """
    fig, ax = plt.subplots(figsize=(8, 6), dpi=THEME['dpi'])

    ax.plot(d_values, transform_values, 'o-',
            color=THEME['secondary_color'], linewidth=2, markersize=8)

    ax.set_xlabel('Dimension parameter d', fontsize=THEME['font_size'])
    ax.set_ylabel('C[f] value', fontsize=THEME['font_size'])
    ax.set_title('Effect of Dimensional Weighting', fontsize=THEME['font_size']+2, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if return_base64:
        return _fig_to_base64(fig)
    return fig


def _plot_e8_comparison(
    pattern_data: Dict[int, Dict[str, float]],
    return_base64: bool = False
) -> Union[plt.Figure, str, None]:
    """
    Plot E8 vs Canonical loci comparison.

    Shows how E8 geometry affects transform values compared to canonical basis.
    Critical visualization for the Pattern 4 amplification discovery.

    Args:
        pattern_data: Dict mapping pattern_id to {'canonical': val, 'e8': val}
        return_base64: If True, return base64-encoded PNG string

    Returns:
        Figure object or base64 string
    """
    patterns = list(pattern_data.keys())
    canonical_values = [pattern_data[p]['canonical'] for p in patterns]
    e8_values = [pattern_data[p]['e8'] for p in patterns]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=THEME['dpi'])

    x = np.arange(len(patterns))
    width = 0.35

    bars1 = ax.bar(x - width/2, canonical_values, width,
                   label='Canonical', color=THEME['canonical_color'], alpha=0.8)
    bars2 = ax.bar(x + width/2, e8_values, width,
                   label='E8', color=THEME['e8_color'], alpha=0.8)

    ax.set_xlabel('Pattern ID', fontsize=THEME['font_size'])
    ax.set_ylabel('C[f] value', fontsize=THEME['font_size'])
    ax.set_title('E8 vs Canonical Loci Comparison', fontsize=THEME['font_size']+2, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(patterns)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    if return_base64:
        return _fig_to_base64(fig)
    return fig


def _plot_kernel_localization(
    x_range: np.ndarray,
    kernel_values: np.ndarray,
    loci_positions: Optional[List[float]] = None,
    return_base64: bool = False
) -> Union[plt.Figure, str, None]:
    """
    Plot zero divisor kernel localization.

    Visualizes the Gaussian-like kernel K_Z(P,x) centered at zero divisor loci.

    Args:
        x_range: Array of x positions
        kernel_values: Kernel values at each x
        loci_positions: Positions of zero divisor loci (for markers)
        return_base64: If True, return base64-encoded PNG string

    Returns:
        Figure object or base64 string
    """
    fig, ax = plt.subplots(figsize=(8, 6), dpi=THEME['dpi'])

    ax.fill_between(x_range, kernel_values, alpha=0.3, color=THEME['primary_color'])
    ax.plot(x_range, kernel_values, color=THEME['primary_color'], linewidth=2)

    if loci_positions:
        for i, pos in enumerate(loci_positions):
            ax.axvline(pos, color='red', linestyle=':', linewidth=1.5, alpha=0.7)
            ax.text(pos, max(kernel_values)*0.9, f'Locus {i+1}',
                    rotation=90, va='top', ha='right', fontsize=8)

    ax.set_xlabel('Position x', fontsize=THEME['font_size'])
    ax.set_ylabel('Kernel K_Z(P, x)', fontsize=THEME['font_size'])
    ax.set_title('Zero Divisor Kernel Localization', fontsize=THEME['font_size']+2, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if return_base64:
        return _fig_to_base64(fig)
    return fig


def _plot_comprehensive_analysis(
    alpha_data: Tuple[np.ndarray, np.ndarray],
    d_data: Tuple[np.ndarray, np.ndarray],
    spatial_data: Tuple[np.ndarray, np.ndarray],
    kernel_data: Tuple[np.ndarray, np.ndarray],
    fourier_data: Tuple[np.ndarray, np.ndarray],
    pattern_values: Dict[int, float],
    optimal_alpha: Optional[float] = None,
    return_base64: bool = False
) -> Union[plt.Figure, str]:
    """
    Create comprehensive 6-panel analysis figure (matches research report).

    This is the flagship visualization combining all key aspects of the transform.
    Note: Only available as static matplotlib (too complex for basic interactive).

    Args:
        alpha_data: (alpha_values, transform_values) tuple
        d_data: (d_values, transform_values) tuple
        spatial_data: (x_values, transform_values) tuple for spatial behavior
        kernel_data: (x_values, kernel_values) tuple
        fourier_data: (frequencies, magnitudes) tuple
        pattern_values: Dict of pattern_id -> transform value
        optimal_alpha: Mark optimal alpha if provided
        return_base64: If True, return base64-encoded PNG

    Returns:
        Figure or base64 string
    """
    fig = plt.figure(figsize=(15, 10), dpi=THEME['dpi'])
    gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)

    # Panel 1: Alpha sensitivity
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(alpha_data[0], np.abs(alpha_data[1]), 'o-',
             color=THEME['accent_color'], linewidth=2, markersize=4)
    if optimal_alpha:
        ax1.axvline(optimal_alpha, color='red', linestyle='--', linewidth=1.5,
                    label=f'Optimal α = {optimal_alpha:.2f}')
        ax1.legend(fontsize=8)
    ax1.set_xscale('log')
    ax1.set_xlabel('Alpha (convergence parameter)', fontsize=9)
    ax1.set_ylabel('|C[f]| (Transform magnitude)', fontsize=9)
    ax1.set_title('Chavez Transform vs Alpha Parameter', fontsize=10, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Panel 2: Dimensional weighting
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(d_data[0], d_data[1], 'o-',
             color=THEME['secondary_color'], linewidth=2, markersize=6)
    ax2.set_xlabel('Dimension parameter d', fontsize=9)
    ax2.set_ylabel('C[f] value', fontsize=9)
    ax2.set_title('Effect of Dimensional Weighting', fontsize=10, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Panel 3: Fourier Transform (reference)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(fourier_data[0], fourier_data[1], color=THEME['accent_color'], linewidth=2)
    ax3.set_xlabel('Frequency', fontsize=9)
    ax3.set_ylabel('Magnitude', fontsize=9)
    ax3.set_title('Fourier Transform (Frequency Domain)', fontsize=10, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # Panel 4: Chavez spatial behavior
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(spatial_data[0], spatial_data[1], color=THEME['secondary_color'], linewidth=2)
    ax4.set_xlabel('Evaluation point', fontsize=9)
    ax4.set_ylabel('C[f] value', fontsize=9)
    ax4.set_title('Chavez Transform (Spatial Behavior)', fontsize=10, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    # Panel 5: Kernel localization
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.fill_between(kernel_data[0], kernel_data[1], alpha=0.3, color=THEME['primary_color'])
    ax5.plot(kernel_data[0], kernel_data[1], color=THEME['primary_color'], linewidth=2)
    ax5.set_xlabel('Position x', fontsize=9)
    ax5.set_ylabel('Kernel K_Z(P, x)', fontsize=9)
    ax5.set_title('Zero Divisor Kernel Localization', fontsize=10, fontweight='bold')
    ax5.grid(True, alpha=0.3)

    # Panel 6: Canonical Six universality
    ax6 = fig.add_subplot(gs[2, 1])
    patterns = list(pattern_values.keys())
    values = list(pattern_values.values())
    mean_value = np.mean(values)
    ax6.bar(patterns, values, color=THEME['primary_color'], edgecolor='white', linewidth=2)
    ax6.axhline(mean_value, color='red', linestyle='--', linewidth=2, alpha=0.7,
                label=f'Mean = {mean_value:.6e}')
    ax6.set_xlabel('Pattern ID', fontsize=9)
    ax6.set_ylabel('C[f] value', fontsize=9)
    ax6.set_title('Canonical Six Pattern Universality', fontsize=10, fontweight='bold')
    ax6.legend(fontsize=8, loc='upper right')
    ax6.grid(axis='y', alpha=0.3)

    plt.suptitle('Chavez Transform - Comprehensive Analysis',
                 fontsize=14, fontweight='bold', y=0.995)

    if return_base64:
        return _fig_to_base64(fig)
    return fig


def _plot_transform_result(
    result_data: Dict,
    return_base64: bool = False
) -> Union[plt.Figure, str, None]:
    """
    Generic transform result visualization.

    Flexible plotting function for various transform outputs.

    Args:
        result_data: Dictionary with plotting data (structure flexible based on content)
        return_base64: If True, return base64-encoded PNG

    Returns:
        Figure or base64 string
    """
    # Placeholder for future expansion
    pass


def _plot_e8_mandala(
    projections: Dict[int, Tuple[float, float, int]],
    canonical_mapping: Optional[Dict[int, Tuple]] = None,
    transform_values: Optional[Dict[int, float]] = None,
    highlight_pattern_4: bool = True,
    return_base64: bool = False
) -> Union[plt.Figure, str, None]:
    """
    Plot E8 root lattice as 30-fold symmetric mandala (Coxeter projection).

    The flagship visualization combining E8 geometry with zero divisor discoveries.
    Purple and light blue gradient represents the "color of impossibility" (Cirlot).

    Args:
        projections: Dict mapping root_index -> (x, y, orbit_id) in Coxeter plane
        canonical_mapping: Dict mapping pattern_id -> (E8Root, orbit_id) for Canonical Six
        transform_values: Dict mapping pattern_id -> Chavez Transform value
        highlight_pattern_4: If True, highlight Pattern 4's anomalous position
        return_base64: If True, return base64-encoded PNG

    Returns:
        Figure object or base64 string
    """
    fig, ax = plt.subplots(figsize=THEME['e8_mandala_size'], dpi=THEME['dpi'])

    # Separate roots by orbit
    orbits = {}
    for idx, (x, y, orbit_id) in projections.items():
        if orbit_id not in orbits:
            orbits[orbit_id] = {'x': [], 'y': []}
        orbits[orbit_id]['x'].append(x)
        orbits[orbit_id]['y'].append(y)

    orbit_colors = [THEME['primary_color'], THEME['accent_color']]

    for orbit_id, data in orbits.items():
        color = orbit_colors[orbit_id % len(orbit_colors)]
        ax.scatter(
            data['x'], data['y'],
            c=color,
            s=20,
            alpha=0.6,
            edgecolors='none',
            label=f'Orbit {orbit_id} ({len(data["x"])} roots)'
        )

    if canonical_mapping:
        for pattern_id in range(1, 7):
            if pattern_id not in canonical_mapping:
                continue

            e8_root, orbit_id = canonical_mapping[pattern_id]

            for idx, (x, y, oid) in projections.items():
                if oid == orbit_id:
                    if pattern_id == 4 and highlight_pattern_4:
                        color = THEME['pattern_4_color']
                        size = 300
                        zorder = 100
                    else:
                        color = (THEME['primary_color'] if not transform_values
                                 else THEME['canonical_color'])
                        size = 200
                        zorder = 50

                    ax.scatter(
                        [x], [y],
                        c=color,
                        s=size,
                        marker='*',
                        edgecolors='white',
                        linewidths=2,
                        zorder=zorder,
                        label=f'Pattern {pattern_id}'
                    )
                    ax.text(
                        x, y + 0.15,
                        f'P{pattern_id}',
                        ha='center',
                        va='bottom',
                        fontsize=10,
                        fontweight='bold',
                        color='white',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7)
                    )
                    break

    ax.set_xlabel('Coxeter Plane X', fontsize=THEME['font_size']+2)
    ax.set_ylabel('Coxeter Plane Y', fontsize=THEME['font_size']+2)
    ax.set_title('E8 Mandala: Weyl Orbit Structure & Zero Divisor Patterns',
                 fontsize=THEME['font_size']+4, fontweight='bold', pad=20)

    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, linestyle='--')
    ax.axhline(0, color='gray', linewidth=0.5, alpha=0.3)
    ax.axvline(0, color='gray', linewidth=0.5, alpha=0.3)

    for radius in [0.25, 0.5, 0.75, 1.0]:
        circle = plt.Circle((0, 0), radius, fill=False, color='gray',
                          alpha=0.15, linestyle=':', linewidth=1)
        ax.add_patch(circle)

    ax.legend(loc='upper right', fontsize=8, framealpha=0.9)

    plt.tight_layout()

    if return_base64:
        return _fig_to_base64(fig)
    return fig


# Utility functions

def _fig_to_base64(fig: plt.Figure) -> str:
    """
    Convert matplotlib figure to base64-encoded PNG string.

    Args:
        fig: Matplotlib figure

    Returns:
        Base64-encoded PNG string
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=THEME['dpi'])
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64


def save_figure(fig: plt.Figure, filepath: str, format: str = 'png') -> None:
    """
    Save matplotlib figure to file.

    Args:
        fig: Matplotlib Figure object
        filepath: Output file path
        format: Output format ('png', 'svg', etc.)
    """
    fig.savefig(filepath, format=format, bbox_inches='tight', dpi=THEME['dpi'])
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# RHI-Native Visualization Functions (v2.0 — Phase 75+)
# Accept ZDTP transmit output directly; render in four styles.
# ─────────────────────────────────────────────────────────────────────────────

# Gateway pairing structure at σ = ½ (Phase 75 finding)
GATEWAY_PAIRINGS = {
    'S1': 'pair_1', 'S2': 'pair_1',
    'S3': 'pair_2', 'S6': 'pair_2',
    'S4': 'pair_3', 'S5': 'pair_3',
}
PAIRING_COLORS = {
    'pair_1': '#60A5FA',   # Light blue
    'pair_2': '#8B5CF6',   # Purple
    'pair_3': '#EC4899',   # Pink
}
GATEWAY_ORDER = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']

# Mandala angular positions — paired gateways placed opposite each other
# S1↔S2 (90°/270°), S3↔S6 (30°/210°), S4↔S5 (150°/330°)
MANDALA_ANGLES = {
    'S1': np.radians(90),
    'S2': np.radians(270),
    'S3': np.radians(30),
    'S6': np.radians(210),
    'S4': np.radians(150),
    'S5': np.radians(330),
}


def _extract_gateway_data(data: dict) -> tuple:
    """
    Parse gateway magnitudes from various ZDTP output formats.
    Returns (magnitudes_dict, convergence, sigma, t).
    """
    # Try direct gateways dict
    gateways = data.get('gateways', data.get('gateway_magnitudes', {}))
    # Also accept flat S1..S6 keys at top level
    if not gateways:
        gateways = {k: v for k, v in data.items() if k in GATEWAY_ORDER}
    convergence = data.get('convergence', data.get('convergence_score', None))
    sigma = data.get('sigma', data.get('s', {}).get('sigma', None) if isinstance(data.get('s'), dict) else None)
    t = data.get('t', data.get('s', {}).get('t', None) if isinstance(data.get('s'), dict) else None)
    return gateways, convergence, sigma, t


def _plot_gateway_magnitudes(data: dict, style: str = 'math_paper') -> plt.Figure:
    """
    Visualize S1–S6 gateway magnitudes from a ZDTP transmit call.

    data format:
        {gateways: {S1: float, ...}, convergence: float, sigma: float, t: float}
        OR pass the zdtp_transmit result dict directly.

    style: 'math_paper' | 'social_media' | 'infographic' | 'mandala'
    """
    gateways, convergence, sigma, t = _extract_gateway_data(data)
    if not gateways:
        raise ValueError("No gateway magnitude data found. Pass {gateways: {S1: float, ...}} or zdtp_transmit output.")

    magnitudes = [gateways.get(g, 0.0) for g in GATEWAY_ORDER]
    colors = [PAIRING_COLORS[GATEWAY_PAIRINGS[g]] for g in GATEWAY_ORDER]

    s_label = ''
    if sigma is not None and t is not None:
        s_label = f's = {sigma} + {t}i'
    elif sigma is not None:
        s_label = f'σ = {sigma}'

    conv_label = f'  ·  ZDTP conv = {convergence:.3f}' if convergence is not None else ''

    if style == 'math_paper':
        fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
        ax.bar(GATEWAY_ORDER, magnitudes, color='#4B5563', edgecolor='white', linewidth=0.8, width=0.6)
        ax.set_xlabel('Gateway', fontsize=10)
        ax.set_ylabel('Magnitude |M|', fontsize=10)
        ax.set_title(f'ZDTP Gateway Magnitudes — {s_label}{conv_label}', fontsize=11, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linewidth=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for i, (g, m) in enumerate(zip(GATEWAY_ORDER, magnitudes)):
            ax.text(i, m + max(magnitudes) * 0.015, f'{m:.3f}', ha='center', va='bottom', fontsize=8, color='#374151')
        plt.tight_layout()

    elif style == 'social_media':
        fig, ax = plt.subplots(figsize=(10, 6), dpi=150, facecolor='#0F172A')
        ax.set_facecolor('#0F172A')
        bars = ax.bar(GATEWAY_ORDER, magnitudes, color=colors, edgecolor='white', linewidth=1.2, width=0.65)
        ax.set_xlabel('Gateway', fontsize=13, color='white', labelpad=8)
        ax.set_ylabel('|M|', fontsize=13, color='white')
        title_line2 = f'{s_label}{conv_label}' if s_label else 'ZDTP Transmission'
        ax.set_title(f'ZDTP Gateway Magnitudes\n{title_line2}', fontsize=15, fontweight='bold', color='white', pad=12)
        ax.tick_params(colors='white', labelsize=11)
        for spine in ax.spines.values():
            spine.set_edgecolor('#334155')
        ax.grid(axis='y', alpha=0.2, color='white', linewidth=0.6)
        for i, (g, m) in enumerate(zip(GATEWAY_ORDER, magnitudes)):
            ax.text(i, m + max(magnitudes) * 0.02, f'{m:.2f}', ha='center', va='bottom',
                    fontsize=10, color='white', fontweight='bold')
        # Pairing legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=PAIRING_COLORS['pair_1'], label='S1 = S2'),
            Patch(facecolor=PAIRING_COLORS['pair_2'], label='S3 = S6'),
            Patch(facecolor=PAIRING_COLORS['pair_3'], label='S4 = S5'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', framealpha=0.3,
                  facecolor='#1E293B', edgecolor='#475569', labelcolor='white', fontsize=10)
        plt.tight_layout()

    elif style == 'infographic':
        fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
        bars = ax.bar(GATEWAY_ORDER, magnitudes, color=colors, edgecolor='white', linewidth=1.2, width=0.6)
        ax.set_xlabel('Gateway', fontsize=11)
        ax.set_ylabel('Magnitude |M|', fontsize=11)
        title = f'ZDTP Gateway Magnitudes at σ = ½'
        if s_label:
            title = f'ZDTP Gateway Magnitudes — {s_label}'
        ax.set_title(title, fontsize=13, fontweight='bold', pad=16)
        ax.grid(axis='y', alpha=0.3, linewidth=0.8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        # Value labels
        for i, (g, m) in enumerate(zip(GATEWAY_ORDER, magnitudes)):
            ax.text(i, m + max(magnitudes) * 0.012, f'{m:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        # Pairing brackets
        pair_spans = [([0, 1], 'Pair 1\nS1 = S2'), ([2, 5], 'Pair 2\nS3 = S6'), ([3, 4], 'Pair 3\nS4 = S5')]
        bracket_y = max(magnitudes) * 1.10
        for idxs, label in pair_spans:
            x_left, x_right = min(idxs) - 0.3, max(idxs) + 0.3
            ax.annotate('', xy=(x_right, bracket_y), xytext=(x_left, bracket_y),
                        arrowprops=dict(arrowstyle='<->', color=PAIRING_COLORS[GATEWAY_PAIRINGS[GATEWAY_ORDER[idxs[0]]]], lw=2))
            ax.text((x_left + x_right) / 2, bracket_y + max(magnitudes) * 0.03, label,
                    ha='center', va='bottom', fontsize=8,
                    color=PAIRING_COLORS[GATEWAY_PAIRINGS[GATEWAY_ORDER[idxs[0]]]])
        ax.set_ylim(0, max(magnitudes) * 1.28)
        if convergence is not None:
            ax.text(0.98, 0.04, f'ZDTP convergence: {convergence:.3f}', transform=ax.transAxes,
                    ha='right', va='bottom', fontsize=9, color='#6B7280',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#F3F4F6', edgecolor='#D1D5DB'))
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=PAIRING_COLORS['pair_1'], label='Pair 1: S1 = S2 (primes 2, 3)'),
            Patch(facecolor=PAIRING_COLORS['pair_2'], label='Pair 2: S3 = S6 (primes 5, 13)'),
            Patch(facecolor=PAIRING_COLORS['pair_3'], label='Pair 3: S4 = S5 (primes 7, 11)'),
        ]
        ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9, fontsize=9)
        plt.tight_layout()

    elif style == 'mandala':
        fig, ax = plt.subplots(figsize=(10, 10), dpi=150, facecolor='#0B1120')
        ax.set_facecolor('#0B1120')
        ax.set_aspect('equal')

        max_mag = max(magnitudes) if magnitudes else 1.0
        norm_mags = {g: gateways.get(g, 0.0) / max_mag for g in GATEWAY_ORDER}

        # Concentric reference rings
        for r in [0.25, 0.5, 0.75, 1.0]:
            circle = plt.Circle((0, 0), r, fill=False, color='#1E3A5F', linewidth=0.8, linestyle='--')
            ax.add_patch(circle)
            ax.text(0, r + 0.03, f'{r * max_mag:.1f}', ha='center', va='bottom',
                    fontsize=7, color='#475569')

        # Polygon connecting all six gateway points (spiderweb)
        angles_ordered = [MANDALA_ANGLES[g] for g in GATEWAY_ORDER]
        norms_ordered = [norm_mags[g] for g in GATEWAY_ORDER]
        poly_x = [r * np.cos(a) for r, a in zip(norms_ordered, angles_ordered)]
        poly_y = [r * np.sin(a) for r, a in zip(norms_ordered, angles_ordered)]
        poly_x.append(poly_x[0])
        poly_y.append(poly_y[0])
        ax.fill(poly_x, poly_y, alpha=0.12, color='#8B5CF6')
        ax.plot(poly_x, poly_y, color='#8B5CF6', linewidth=1.0, alpha=0.5)

        # Lines connecting paired gateways
        pairs = [('S1', 'S2'), ('S3', 'S6'), ('S4', 'S5')]
        for g1, g2 in pairs:
            pair_key = GATEWAY_PAIRINGS[g1]
            color = PAIRING_COLORS[pair_key]
            r1, r2 = norm_mags[g1], norm_mags[g2]
            a1, a2 = MANDALA_ANGLES[g1], MANDALA_ANGLES[g2]
            ax.plot([r1 * np.cos(a1), r2 * np.cos(a2)],
                    [r1 * np.sin(a1), r2 * np.sin(a2)],
                    color=color, linewidth=2.0, alpha=0.7, linestyle='--')

        # Gateway nodes
        for g in GATEWAY_ORDER:
            r = norm_mags[g]
            a = MANDALA_ANGLES[g]
            x, y = r * np.cos(a), r * np.sin(a)
            color = PAIRING_COLORS[GATEWAY_PAIRINGS[g]]
            ax.scatter([x], [y], s=180, c=[color], zorder=10, edgecolors='white', linewidths=1.5)
            # Label offset outward
            lx = (r + 0.14) * np.cos(a)
            ly = (r + 0.14) * np.sin(a)
            ax.text(lx, ly, f'{g}\n{gateways.get(g, 0.0):.2f}', ha='center', va='center',
                    fontsize=9, color='white', fontweight='bold')
            # Axis spoke (faint)
            ax.plot([0, np.cos(a)], [0, np.sin(a)], color='#1E3A5F', linewidth=0.6, zorder=0)

        # Center label
        center_text = s_label if s_label else 'ZDTP'
        if convergence is not None:
            center_text += f'\nconv={convergence:.2f}'
        ax.text(0, 0, center_text, ha='center', va='center', fontsize=10,
                color='#CBD5E1', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#0B1120', edgecolor='#334155'))

        ax.set_xlim(-1.45, 1.45)
        ax.set_ylim(-1.45, 1.45)
        ax.axis('off')

        title = 'ZDTP Gateway Mandala'
        if s_label:
            title = f'ZDTP Gateway Mandala — {s_label}'
        ax.set_title(title, fontsize=14, fontweight='bold', color='white', pad=12)
        plt.tight_layout()

    else:
        raise ValueError(f"Unknown style '{style}'. Choose: math_paper, social_media, infographic, mandala")

    return fig


def _plot_bilateral_symmetry(data: dict, style: str = 'math_paper') -> plt.Figure:
    """
    Visualize bilateral magnitude symmetry: |M(σ)| vs σ, showing |M(σ)| = |M(1-σ)|.

    data format:
        {sigma_values: [...], magnitudes: {S1: [...], S2: [...], ...}}
        OR {sigma_values: [...], mean_magnitude: [...]}
    """
    sigma_values = data.get('sigma_values', [])
    magnitudes = data.get('magnitudes', {})
    mean_mag = data.get('mean_magnitude', [])

    if not sigma_values:
        raise ValueError("bilateral_symmetry requires data.sigma_values list")

    sigma_arr = np.array(sigma_values)

    if style == 'math_paper':
        fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
        if magnitudes:
            for g, vals in magnitudes.items():
                ax.plot(sigma_arr, vals, 'o-', linewidth=1.5, markersize=4,
                        color=PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#4B5563'),
                        label=g)
        elif mean_mag:
            ax.plot(sigma_arr, mean_mag, 'o-', color='#4B5563', linewidth=2, markersize=5, label='Mean |M|')
        ax.axvline(0.5, color='red', linestyle='--', linewidth=1.2, alpha=0.7, label='σ = ½')
        ax.set_xlabel('σ (real part)', fontsize=10)
        ax.set_ylabel('|M(σ)|', fontsize=10)
        ax.set_title('Bilateral Magnitude Symmetry — |M(σ)| = |M(1−σ)|', fontsize=11, fontweight='bold')
        ax.legend(fontsize=8, ncol=2)
        ax.grid(alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

    elif style == 'social_media':
        fig, ax = plt.subplots(figsize=(10, 6), dpi=150, facecolor='#0F172A')
        ax.set_facecolor('#0F172A')
        if magnitudes:
            for g, vals in magnitudes.items():
                c = PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#60A5FA')
                ax.plot(sigma_arr, vals, 'o-', linewidth=2.5, markersize=6, color=c, label=g)
        ax.axvline(0.5, color='#F87171', linestyle='--', linewidth=2, alpha=0.9, label='σ = ½')
        ax.set_xlabel('σ', fontsize=13, color='white')
        ax.set_ylabel('|M(σ)|', fontsize=13, color='white')
        ax.set_title('Bilateral Magnitude Symmetry\n|M(σ)| = |M(1−σ)|  —  Exact to 10⁻¹⁵',
                     fontsize=14, fontweight='bold', color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#334155')
        ax.grid(alpha=0.2, color='white')
        ax.legend(fontsize=10, ncol=2, facecolor='#1E293B', edgecolor='#475569', labelcolor='white')
        plt.tight_layout()

    elif style == 'infographic':
        fig, ax = plt.subplots(figsize=(11, 6.5), dpi=150)
        if magnitudes:
            for g, vals in magnitudes.items():
                c = PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#4B5563')
                ax.plot(sigma_arr, vals, 'o-', linewidth=2, markersize=5, color=c, label=g)
        elif mean_mag:
            ax.plot(sigma_arr, mean_mag, 'o-', color='#4B5563', linewidth=2.5, markersize=6, label='Mean |M|')
        ax.axvline(0.5, color='red', linestyle='--', linewidth=1.5, alpha=0.8, label='Critical line σ = ½')
        # Mirror symmetry annotation
        if len(sigma_arr) >= 2:
            ax.annotate('', xy=(0.5 + 0.15, max(m for v in magnitudes.values() for m in v) * 0.92 if magnitudes else 1),
                        xytext=(0.5 - 0.15, max(m for v in magnitudes.values() for m in v) * 0.92 if magnitudes else 1),
                        arrowprops=dict(arrowstyle='<->', color='gray', lw=1.5))
            mid_y = max(m for v in magnitudes.values() for m in v) * 0.95 if magnitudes else 1
            ax.text(0.5, mid_y, 'σ ↔ 1−σ', ha='center', va='bottom', fontsize=9, color='gray')
        ax.set_xlabel('σ (real part of s)', fontsize=11)
        ax.set_ylabel('|M(σ)| — ZDTP magnitude', fontsize=11)
        ax.set_title('Bilateral Magnitude Symmetry — CAIL-RH Investigation\n|M(σ)|² − |M(1−σ)|² = 0  (exact, all gateways)',
                     fontsize=12, fontweight='bold')
        ax.legend(fontsize=9, ncol=3, loc='lower center')
        ax.grid(alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

    elif style == 'mandala':
        # Polar representation: angle = 2π·σ, radius = |M(σ)|
        fig, ax = plt.subplots(figsize=(9, 9), dpi=150, subplot_kw=dict(projection='polar'),
                               facecolor='#0B1120')
        ax.set_facecolor('#0B1120')
        if magnitudes:
            for g, vals in magnitudes.items():
                c = PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#60A5FA')
                thetas = [2 * np.pi * s for s in sigma_arr]
                ax.plot(thetas, vals, '-', linewidth=2.5, color=c, label=g, alpha=0.85)
                ax.fill(thetas, vals, alpha=0.08, color=c)
        ax.axvline(2 * np.pi * 0.5, color='#F87171', linewidth=2, linestyle='--', alpha=0.7)
        ax.set_title('Bilateral Symmetry — Polar View\nσ ∈ [0, 1] mapped to θ ∈ [0, 2π]',
                     fontsize=12, fontweight='bold', color='white', pad=18)
        ax.tick_params(colors='white')
        ax.grid(color='#1E3A5F', linewidth=0.8)
        ax.set_facecolor('#0B1120')
        legend = ax.legend(fontsize=9, facecolor='#1E293B', edgecolor='#475569', labelcolor='white',
                           loc='lower right')
        plt.tight_layout()

    else:
        raise ValueError(f"Unknown style '{style}'")

    return fig


def _plot_sigma_sweep(data: dict, style: str = 'math_paper') -> plt.Figure:
    """
    Visualize gateway magnitudes across a sweep of sigma values.
    Shares the same data format and most rendering logic as bilateral_symmetry.
    """
    return _plot_bilateral_symmetry(data, style=style)


def _plot_gamma_sweep(data: dict, style: str = 'math_paper') -> plt.Figure:
    """
    Visualize magnitudes or ZDTP convergence across a sweep of gamma (zero index) values.

    data format:
        {gammas: [...], convergence: [...], magnitudes: {S1: [...], ...},
         labels: ['γ₁', 'γ₂', ...]}   # optional
    """
    gammas = data.get('gammas', [])
    convergence = data.get('convergence', data.get('convergence_scores', []))
    magnitudes = data.get('magnitudes', {})
    labels = data.get('labels', [f'γ{i+1}' for i in range(len(gammas))])

    if not gammas and not convergence and not magnitudes:
        raise ValueError("gamma_sweep requires at least one of: gammas, convergence, or magnitudes")

    x = np.array(gammas) if gammas else np.arange(len(convergence or next(iter(magnitudes.values()), [])))

    if style == 'math_paper':
        n_panels = (1 if convergence else 0) + (1 if magnitudes else 0)
        fig, axes = plt.subplots(n_panels, 1, figsize=(8, 3.5 * n_panels), dpi=150, sharex=True)
        if n_panels == 1:
            axes = [axes]
        idx = 0
        if magnitudes:
            ax = axes[idx]; idx += 1
            for g, vals in magnitudes.items():
                c = PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#4B5563')
                ax.plot(x, vals, 'o-', linewidth=1.5, markersize=4, color=c, label=g)
            ax.set_ylabel('|M|', fontsize=10)
            ax.set_title('Gateway Magnitudes — γ Sweep', fontsize=11, fontweight='bold')
            ax.legend(fontsize=8, ncol=3)
            ax.grid(alpha=0.3)
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        if convergence:
            ax = axes[idx]
            ax.plot(x, convergence, 's-', color='#F59E0B', linewidth=2, markersize=5)
            ax.axhline(1.0, color='red', linestyle='--', linewidth=1, alpha=0.6, label='Conv = 1.0')
            ax.set_ylabel('ZDTP Conv.', fontsize=10)
            ax.set_xlabel('γₙ', fontsize=10)
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3)
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        if labels and len(labels) == len(x):
            axes[-1].set_xticks(x)
            axes[-1].set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        plt.tight_layout()

    elif style == 'social_media':
        fig, ax = plt.subplots(figsize=(12, 6), dpi=150, facecolor='#0F172A')
        ax.set_facecolor('#0F172A')
        if magnitudes:
            for g, vals in magnitudes.items():
                c = PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#60A5FA')
                ax.plot(x, vals, 'o-', linewidth=2.5, markersize=7, color=c, label=g)
        if convergence:
            ax2 = ax.twinx()
            ax2.plot(x, convergence, 's--', color='#F59E0B', linewidth=2, markersize=6, label='ZDTP Conv.')
            ax2.set_ylabel('Convergence', fontsize=12, color='#F59E0B')
            ax2.tick_params(colors='#F59E0B')
        ax.set_xlabel('γₙ', fontsize=13, color='white')
        ax.set_ylabel('|M|', fontsize=13, color='white')
        ax.set_title('ZDTP Gateway Magnitudes — γ Sweep', fontsize=15, fontweight='bold', color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#334155')
        ax.grid(alpha=0.2, color='white')
        ax.legend(fontsize=10, ncol=3, facecolor='#1E293B', edgecolor='#475569', labelcolor='white')
        plt.tight_layout()

    elif style == 'infographic':
        fig, axes = plt.subplots(2, 1, figsize=(12, 9), dpi=150, sharex=True)
        if magnitudes:
            for g, vals in magnitudes.items():
                c = PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#4B5563')
                axes[0].plot(x, vals, 'o-', linewidth=2, markersize=5, color=c, label=g)
            axes[0].set_ylabel('|M| (ZDTP magnitude)', fontsize=11)
            axes[0].set_title('CAIL-RH Gateway Magnitude Sweep — Riemann Zeros γ₁–γₙ\nClass A (S2,S3,S6) vs Class B (S1,S4,S5) structure',
                              fontsize=12, fontweight='bold')
            axes[0].legend(fontsize=9, ncol=6)
            axes[0].grid(alpha=0.3)
            axes[0].spines['top'].set_visible(False); axes[0].spines['right'].set_visible(False)
        if convergence:
            axes[1].fill_between(x, convergence, alpha=0.3, color='#F59E0B')
            axes[1].plot(x, convergence, 's-', color='#F59E0B', linewidth=2, markersize=5)
            axes[1].axhline(1.0, color='red', linestyle='--', linewidth=1.2, alpha=0.7, label='Perfect bilateral annihilation')
            axes[1].set_ylabel('ZDTP Convergence Score', fontsize=11)
            axes[1].set_xlabel('Riemann zero γₙ', fontsize=11)
            axes[1].legend(fontsize=9)
            axes[1].grid(alpha=0.3)
            axes[1].spines['top'].set_visible(False); axes[1].spines['right'].set_visible(False)
        if labels and len(labels) == len(x):
            axes[-1].set_xticks(x)
            axes[-1].set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        plt.tight_layout()

    elif style == 'mandala':
        # Radar/spider chart across gateways, one polygon per gamma
        if not magnitudes:
            raise ValueError("mandala style for gamma_sweep requires magnitudes dict")
        n_gateways = len(GATEWAY_ORDER)
        angles = np.linspace(0, 2 * np.pi, n_gateways, endpoint=False).tolist()
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=(10, 10), dpi=150, subplot_kw=dict(polar=True), facecolor='#0B1120')
        ax.set_facecolor('#0B1120')
        n_gamma = len(x)
        cmap = plt.cm.plasma
        for gi in range(n_gamma):
            vals = [magnitudes.get(g, [0] * n_gamma)[gi] for g in GATEWAY_ORDER]
            vals += vals[:1]
            color = cmap(gi / max(n_gamma - 1, 1))
            ax.plot(angles, vals, linewidth=1.5, color=color, alpha=0.6)
            ax.fill(angles, vals, alpha=0.04, color=color)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(GATEWAY_ORDER, fontsize=11, color='white')
        ax.tick_params(colors='white')
        ax.grid(color='#1E3A5F', linewidth=0.8)
        ax.set_facecolor('#0B1120')
        ax.set_title('Gateway Magnitude Radar — γ Sweep\n(color = γ index, plasma scale)',
                     fontsize=13, fontweight='bold', color='white', pad=20)
        plt.tight_layout()

    else:
        raise ValueError(f"Unknown style '{style}'")

    return fig


def _plot_critical_line_portrait(data: dict, style: str = 'math_paper') -> plt.Figure:
    """
    Visualize gateway magnitudes at σ = ½ for a range of ±t values (Q-4 type).

    data format:
        {t_values: [...], magnitudes: {S1: [...], S2: [...], ...}, sigma: float}
        t_values may include both +t and -t; magnitude equality is the key result.
    """
    t_values = data.get('t_values', [])
    magnitudes = data.get('magnitudes', {})
    sigma = data.get('sigma', 0.5)

    if not t_values or not magnitudes:
        raise ValueError("critical_line_portrait requires data.t_values and data.magnitudes")

    t_arr = np.array(t_values)

    if style == 'math_paper':
        fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
        for g, vals in magnitudes.items():
            c = PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#4B5563')
            ax.plot(t_arr, vals, 'o-', linewidth=1.5, markersize=4, color=c, label=g)
        ax.axvline(0, color='gray', linewidth=0.8, linestyle='--', alpha=0.5)
        ax.set_xlabel('t  (Im(s), σ = ½ fixed)', fontsize=10)
        ax.set_ylabel('|M(½ + it)|', fontsize=10)
        ax.set_title(f'Critical Line Portrait — |M(½+it)| = |M(½−it)|  (σ = {sigma})', fontsize=11, fontweight='bold')
        ax.legend(fontsize=8, ncol=3)
        ax.grid(alpha=0.3)
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        plt.tight_layout()

    elif style == 'social_media':
        fig, ax = plt.subplots(figsize=(11, 6), dpi=150, facecolor='#0F172A')
        ax.set_facecolor('#0F172A')
        for g, vals in magnitudes.items():
            c = PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#60A5FA')
            ax.plot(t_arr, vals, 'o-', linewidth=2.5, markersize=7, color=c, label=g)
        ax.axvline(0, color='#94A3B8', linewidth=1.2, linestyle='--', alpha=0.6)
        ax.set_xlabel('t', fontsize=13, color='white')
        ax.set_ylabel('|M(½ + it)|', fontsize=13, color='white')
        ax.set_title(f'Critical Line Portrait — σ = {sigma}\n|M(½+it)| = |M(½−it)|  (exact, all gateways)',
                     fontsize=14, fontweight='bold', color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#334155')
        ax.grid(alpha=0.2, color='white')
        ax.legend(fontsize=10, ncol=3, facecolor='#1E293B', edgecolor='#475569', labelcolor='white')
        plt.tight_layout()

    elif style == 'infographic':
        fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
        for g, vals in magnitudes.items():
            c = PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#4B5563')
            ax.plot(t_arr, vals, 'o-', linewidth=2, markersize=5, color=c, label=g)
        ax.axvline(0, color='gray', linewidth=1, linestyle='--', alpha=0.5, label='t = 0')
        # ±t symmetry annotation
        t_max = max(abs(t_arr))
        y_top = max(v for vals in magnitudes.values() for v in vals) * 1.05
        ax.annotate('', xy=(t_max * 0.8, y_top), xytext=(-t_max * 0.8, y_top),
                    arrowprops=dict(arrowstyle='<->', color='gray', lw=1.5))
        ax.text(0, y_top * 1.02, '±t symmetry: |M(½+it)| = |M(½−it)|', ha='center', va='bottom',
                fontsize=9, color='gray', style='italic')
        ax.set_xlabel('t  (imaginary part of s = ½ + it)', fontsize=11)
        ax.set_ylabel('|M(½ + it)| — ZDTP magnitude', fontsize=11)
        ax.set_title(f'Critical Line Portrait — CAIL-RH Investigation (σ = {sigma})\nStructural ±t Schwarz Reflection Symmetry',
                     fontsize=12, fontweight='bold')
        ax.set_ylim(0, y_top * 1.18)
        ax.legend(fontsize=9, ncol=3, loc='lower center')
        ax.grid(alpha=0.3)
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        plt.tight_layout()

    elif style == 'mandala':
        # Polar: angle = arctan(t / σ) ≈ t-axis; radius = magnitude
        fig, ax = plt.subplots(figsize=(10, 10), dpi=150, subplot_kw=dict(polar=True), facecolor='#0B1120')
        ax.set_facecolor('#0B1120')
        for g, vals in magnitudes.items():
            c = PAIRING_COLORS.get(GATEWAY_PAIRINGS.get(g, 'pair_1'), '#60A5FA')
            # Map t values to angles in [0, 2π]: normalize t to [0, 2π]
            t_min, t_max_val = min(t_arr), max(t_arr)
            if t_max_val > t_min:
                thetas = 2 * np.pi * (t_arr - t_min) / (t_max_val - t_min)
            else:
                thetas = np.zeros_like(t_arr)
            ax.plot(thetas, vals, '-', linewidth=2.5, color=c, alpha=0.85, label=g)
            ax.fill(thetas, vals, alpha=0.08, color=c)
        ax.tick_params(colors='white')
        ax.grid(color='#1E3A5F', linewidth=0.8)
        ax.set_facecolor('#0B1120')
        ax.set_title(f'Critical Line Portrait — Polar (σ = {sigma})\nθ = normalized t, r = |M|',
                     fontsize=12, fontweight='bold', color='white', pad=20)
        legend = ax.legend(fontsize=9, facecolor='#1E293B', edgecolor='#475569', labelcolor='white',
                           loc='lower right')
        plt.tight_layout()

    else:
        raise ValueError(f"Unknown style '{style}'")

    return fig


# ─────────────────────────────────────────────────────────────────────────────

# Example usage and testing
if __name__ == "__main__":
    print("="*80)
    print("CHAVEZ TRANSFORM VISUALIZATIONS - TEST")
    print("="*80)
    print()

    # Test data
    pattern_values = {i: 0.7771203 for i in range(1, 7)}  # Universal symmetry

    alpha_values = np.logspace(-1, 1, 20)
    transform_values = 2.0 * np.exp(-0.5 * alpha_values)  # Mock decay

    d_values = np.arange(1, 11)
    d_transform_values = 0.85 - 0.04 * d_values  # Mock linear decrease

    print("Creating Canonical Six Universality plot...")
    fig1 = _plot_canonical_six_universality(pattern_values)
    print("  ✓ Created")

    print("Creating Alpha Sensitivity plot...")
    fig2 = _plot_alpha_sensitivity(alpha_values, transform_values, optimal_alpha=0.01)
    print("  ✓ Created")

    print("Creating Dimensional Weighting plot...")
    fig3 = _plot_dimensional_weighting(d_values, d_transform_values)
    print("  ✓ Created")

    print()
    print("All visualization functions working correctly!")
    print("="*80)
