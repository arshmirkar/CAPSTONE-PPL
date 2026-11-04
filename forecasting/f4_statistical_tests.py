"""
F4 - Hypothesis tests on the REAL cleaned mandi data (Lab 11 concepts):
descriptive stats & rank, Shapiro-Wilk, Levene, one-sample / independent / paired t-tests, one-way ANOVA,
Kruskal-Wallis, Mann-Whitney U, Wilcoxon, two-sample KS, Chi-square, Pearson vs Spearman.
Every test states H0/H1 and is interpreted at alpha = 0.05.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from common import load_cleaned, save_fig, OUT_DIR, C

A = 0.05
rows = []

def log(test, h0, h1, stat, p, note=""):
    verdict = "Reject H0" if p < A else "Fail to reject H0"
    rows.append({"Test": test, "H0": h0, "H1": h1, "Statistic": round(float(stat), 4), "p_value": float(f"{p:.3e}"), "Decision(alpha=0.05)": verdict, "Note": note})
    print(f"{test:55s} stat={stat:10.4f}  p={p:9.3e}  -> {verdict}")

if __name__ == "__main__":
    df = load_cleaned()
    top_states = df["State"].value_counts().head(8).index.tolist()           # same 8 states as the report's ANOVA
    key = ["Tomato", "Onion", "Potato", "Green Chilli"]

    # 1. Descriptive statistics and rank
    d = stats.describe(df["Modal_Price"])
    print(f"Modal price: n={d.nobs}, mean={d.mean:.1f}, var={d.variance:.0f}, skew={d.skewness:.2f}, kurt={d.kurtosis:.2f}")
    rank_tab = df.groupby("Commodity", observed=True).filter(lambda g: len(g) >= 15).groupby("Commodity", observed=True)["Spread_Pct"].mean()
    rank_tab = pd.Series(stats.rankdata(-rank_tab.values, method="min"), index=rank_tab.index).sort_values()   # 1 = most volatile
    print("Volatility rank (top 5):", rank_tab.head(5).to_dict())

    # 2. Shapiro-Wilk normality: decides parametric vs non-parametric below
    qq = {}
    for c in key:
        x = df.loc[df["Commodity"] == c, "Modal_Price"]
        w, p = stats.shapiro(x); qq[c] = x
        log(f"Shapiro-Wilk, {c} modal price", "Prices are normally distributed", "Prices are not normal", w, p)
    w, p = stats.shapiro(df["Spread_Pct"].sample(2500 if len(df) > 2500 else len(df), random_state=1))
    log("Shapiro-Wilk, spread % (all records)", "Spread % is normal", "Spread % is not normal", w, p)

    # 3. Levene: equal variance of modal price across states (assumption check before ANOVA)
    groups = [df.loc[df["State"] == s, "Modal_Price"] for s in top_states]
    lv, p = stats.levene(*groups); log("Levene, modal price across 8 states", "Equal variances", "At least one differs", lv, p)
    # 4. ANOVA (parametric) and Kruskal-Wallis (non-parametric) on the same groups
    f, p = stats.f_oneway(*groups); log("One-way ANOVA, modal price across 8 states", "Equal mean price", "At least one state differs", f, p)
    h, p = stats.kruskal(*groups); log("Kruskal-Wallis, modal price across 8 states", "Equal distributions/medians", "At least one differs", h, p, "non-parametric confirmation (prices are right-skewed)")

    # 5. Kerala vs Uttar Pradesh, Tomato: Levene -> t-test, Mann-Whitney, KS
    kl = df[(df.Commodity == "Tomato") & (df.State == "Kerala")]["Modal_Price"]
    up = df[(df.Commodity == "Tomato") & (df.State == "Uttar Pradesh")]["Modal_Price"]
    lv, pl = stats.levene(kl, up); log("Levene, Tomato Kerala vs UP", "Equal variance", "Unequal variance", lv, pl)
    t, p = stats.ttest_ind(kl, up, equal_var=pl >= A); log("Independent t-test, Tomato Kerala vs UP", "Equal mean price", "Mean prices differ", t, p, "Welch version used if Levene rejects" )
    u, p = stats.mannwhitneyu(kl, up); log("Mann-Whitney U, Tomato Kerala vs UP", "Same distribution", "Kerala prices stochastically different", u, p)
    ks, p = stats.ks_2samp(kl, up); log("Two-sample KS, Tomato Kerala vs UP", "Same distribution", "Distributions differ", ks, p)
    ratio = kl.mean() / up.mean()

    # 6. One-sample t-test and Wilcoxon: is mean spread % different from the 20 % 'elevated volatility' line used in Figure 3?
    for c in ["Tomato", "Onion", "Potato"]:
        x = df.loc[df["Commodity"] == c, "Spread_Pct"]
        t, p = stats.ttest_1samp(x, 20); log(f"One-sample t-test, {c} spread % vs 20", "Mean spread = 20 %", "Mean spread != 20 %", t, p, f"sample mean {x.mean():.1f} %")
    x = df.loc[df["Commodity"] == "Tomato", "Spread_Pct"] - 20
    w, p = stats.wilcoxon(x); log("Wilcoxon signed-rank, Tomato spread % vs 20", "Median spread = 20 %", "Median != 20 %", w, p, "non-parametric counterpart")

    # 7. Paired t-test and Wilcoxon: Tomato vs Potato price in the SAME market
    pm = df[df.Commodity.isin(["Tomato", "Potato"])].groupby(["State", "Market", "Commodity"], observed=True)["Modal_Price"].mean().unstack().dropna()
    t, p = stats.ttest_rel(pm["Tomato"], pm["Potato"]); log(f"Paired t-test, Tomato vs Potato (n={len(pm)} markets)", "Mean difference = 0", "Mean difference != 0", t, p)
    w, p = stats.wilcoxon(pm["Tomato"], pm["Potato"]); log("Wilcoxon signed-rank, Tomato vs Potato", "Median difference = 0", "Median difference != 0", w, p)

    # 8. Chi-square: is a record being 'high volatility' (spread > 20 %) independent of State?
    sub = df[df.State.isin(top_states)].assign(HighVol=lambda x: x.Spread_Pct > 20)
    ct = pd.crosstab(sub["State"], sub["HighVol"]); chi, p, dof, _ = stats.chi2_contingency(ct)
    cv = np.sqrt(chi / (ct.values.sum() * (min(ct.shape) - 1)))
    log("Chi-square, State vs High-volatility flag", "Volatility class independent of State", "Dependent", chi, p, f"Cramer's V = {cv:.2f}")
    hv_share = (ct[True] / ct.sum(axis=1) * 100).round(1)

    # 9. Pearson vs Spearman: modal price vs spread %
    pr, pp = stats.pearsonr(df["Modal_Price"], df["Spread_Pct"]); sr, sp = stats.spearmanr(df["Modal_Price"], df["Spread_Pct"])
    log("Pearson, modal price vs spread %", "r = 0", "r != 0", pr, pp); log("Spearman, modal price vs spread %", "rho = 0", "rho != 0", sr, sp, "same sign as Pearson" if pr * sr > 0 else "signs differ")

    pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "f4_statistical_tests.csv"), index=False)
    pd.Series({"kerala_up_tomato_ratio": ratio, "kerala_tomato_mean": kl.mean(), "up_tomato_mean": up.mean(), "n_paired_markets": len(pm)}).to_csv(os.path.join(OUT_DIR, "f4_extra.csv"), header=["value"])
    hv_share.to_csv(os.path.join(OUT_DIR, "f4_highvol_share_by_state.csv"), header=["HighVol_%"])
    print("\nHigh-volatility share by state (%):\n", hv_share.to_string()); print(f"Kerala/UP tomato ratio {ratio:.2f}")

    # Figure: Q-Q plots (normality) + Kruskal-Wallis style boxplot
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    for c, col in zip(["Tomato", "Onion", "Potato"], [C["red"], C["orange"], C["green"]]):
        (osm, osr), _ = stats.probplot(qq[c], dist="norm"); ax[0].scatter(osm, osr, s=8, color=col, label=c, alpha=.7)
    lim = ax[0].get_xlim(); ax[0].plot(lim, np.mean(qq["Tomato"]) + np.std(qq["Tomato"]) * np.array(lim), color=C["grey"], ls="--", lw=1)
    ax[0].set_title("A: Q-Q plot vs normal (Shapiro-Wilk rejects)"); ax[0].set_xlabel("Theoretical quantiles"); ax[0].set_ylabel("Modal price (INR/q)"); ax[0].legend()
    ax[1].boxplot(groups, tick_labels=[s.replace("Himachal Pradesh", "H.P.").replace("Uttar Pradesh", "U.P.") for s in top_states], showfliers=False)
    ax[1].set_title("B: Modal price by state (Kruskal-Wallis p < 0.001)"); ax[1].tick_params(axis="x", rotation=35, labelsize=8)
    ax[2].bar(hv_share.index.str.replace("Himachal Pradesh", "H.P.").str.replace("Uttar Pradesh", "U.P."), hv_share.values, color=C["maroon"], alpha=.8)
    ax[2].set_title("C: Share of high-volatility records (spread > 20 %)"); ax[2].set_ylabel("%"); ax[2].tick_params(axis="x", rotation=35, labelsize=8)
    fig.suptitle("Figure F5: Distribution Checks and Non-Parametric Tests on Real Mandi Data", fontsize=12, fontweight="bold")
    fig.tight_layout(); save_fig(fig, "F5_statistical_tests.png")
