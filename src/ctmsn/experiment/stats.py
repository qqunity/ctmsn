"""Статистические методы для сравнения условий эксперимента.

Требует extras: ``pip install -e '.[experiment]'`` (numpy/scipy/statsmodels).
Импортируется только при необходимости — базовый контур остаётся zero-dependency.
"""

from __future__ import annotations

from dataclasses import dataclass


def _require_scipy():
    try:
        import numpy  # noqa: F401
        import scipy.stats  # noqa: F401
    except ImportError as e:  # pragma: no cover - зависит от окружения
        raise ImportError(
            "Статистический модуль требует extras: pip install -e '.[experiment]'"
        ) from e
    import numpy
    import scipy.stats
    return numpy, scipy.stats


@dataclass(frozen=True)
class MannWhitneyResult:
    u: float
    p_value: float
    n1: int
    n2: int
    alternative: str


def mann_whitney_u(a, b, alternative: str = "two-sided") -> MannWhitneyResult:
    """Непараметрический тест Манна–Уитни для двух независимых выборок."""
    _np, stats = _require_scipy()
    a = list(a)
    b = list(b)
    res = stats.mannwhitneyu(a, b, alternative=alternative)
    return MannWhitneyResult(
        u=float(res.statistic),
        p_value=float(res.pvalue),
        n1=len(a),
        n2=len(b),
        alternative=alternative,
    )


@dataclass(frozen=True)
class BootstrapCI:
    point: float
    low: float
    high: float
    confidence: float
    method: str


def bootstrap_ci_diff(
    a,
    b,
    statistic: str = "mean",
    confidence: float = 0.95,
    n_resamples: int = 2000,
    method: str = "percentile",
    seed: int = 0,
) -> BootstrapCI:
    """Бутстреп доверительный интервал для разности статистик (a − b).

    statistic ∈ {"mean", "median"}. method ∈ {"percentile", "basic", "BCa"};
    по умолчанию "percentile" (устойчив к вырожденным выборкам, напр. все нули).
    """
    np, stats = _require_scipy()
    a_arr = np.asarray(list(a), dtype=float)
    b_arr = np.asarray(list(b), dtype=float)
    agg = np.median if statistic == "median" else np.mean
    point = float(agg(a_arr) - agg(b_arr))

    def stat(x, y, axis=-1):
        return agg(x, axis=axis) - agg(y, axis=axis)

    rng = np.random.default_rng(seed)
    res = stats.bootstrap(
        (a_arr, b_arr),
        stat,
        vectorized=True,
        paired=False,
        confidence_level=confidence,
        n_resamples=n_resamples,
        method=method,
        random_state=rng,
    )
    ci = res.confidence_interval
    return BootstrapCI(
        point=round(point, 4),
        low=round(float(ci.low), 4),
        high=round(float(ci.high), 4),
        confidence=confidence,
        method=method,
    )


def required_sample_size(
    effect_size: float,
    power: float = 0.8,
    alpha: float = 0.05,
    ratio: float = 1.0,
) -> float:
    """Размер выборки на группу для заданного размера эффекта (statsmodels)."""
    try:
        from statsmodels.stats.power import TTestIndPower
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Power-анализ требует statsmodels: pip install -e '.[experiment]'"
        ) from e
    analysis = TTestIndPower()
    return float(
        analysis.solve_power(
            effect_size=effect_size, power=power, alpha=alpha, ratio=ratio,
            alternative="two-sided",
        )
    )
