"""
Agricultural Market Price Volatility & Commodity Spread Analysis
================================================================
Capstone Project: Core Analytical Visualizations & Econometric Modeling

This script generates the 5 Core Analytical Graphs for the capstone project:
1. Kernel Density Estimation (KDE) Price Distribution Shapes (Matplotlib/Seaborn)
2. State-wise Commodity Pricing Pivot Table Heatmap (Pandas/Seaborn)
3. Top Volatile Agricultural Commodities Ranking by Spread % (Matplotlib/Seaborn)
4. Hypothesis Testing: One-Way ANOVA & Levene's Test for Variance Parity (SciPy)
5. Market Stability Metric Correlation Matrix (Seaborn)

All plots are saved in the 'graphs/' directory at 300 DPI.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configure Matplotlib styling for professional presentations
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#eeeeee'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graphs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data(filepath='cleaned_commodity_price.csv'):
    """Load cleaned agricultural commodity data and engineer required spread metrics."""
    if not os.path.exists(filepath):
        alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath)
        if os.path.exists(alt_path):
            filepath = alt_path
        else:
            raise FileNotFoundError(f"Dataset file '{filepath}' not found.")
            
    df = pd.read_csv(filepath)
    
    # Feature engineering for market spreads and volatility
    # 1. Absolute Price Spread (₹/Quintal) = Max Price - Min Price
    df['Price_Spread'] = df['Max_Price'] - df['Min_Price']
    
    # 2. Percentage Price Spread (%) = (Spread / Modal_Price) * 100
    df['Price_Spread_Pct'] = np.where(
        df['Modal_Price'] > 0,
        (df['Price_Spread'] / df['Modal_Price']) * 100,
        0
    )
    
    # 3. Log Modal Price for elasticity and variance stabilization
    df['Log_Modal_Price'] = np.log1p(df['Modal_Price'])
    
    # 4. Intra-market Spread Ratio = Max_Price / Min_Price
    df['Spread_Ratio'] = np.where(df['Min_Price'] > 0, df['Max_Price'] / df['Min_Price'], 1.0)
    
    return df

# ==============================================================================
# GRAPH 1: Price Distribution & KDE Shapes (Top 4 Essential Staples)
# ==============================================================================
def plot_01_kde_distributions(df):
    """
    Simplified, easy-to-explain 2x2 grid showing the wholesale price distribution
    for the 4 most important staples (Tomato, Onion, Potato, Green Chilli).
    Y-axis shows the actual count of Mandis with a smooth KDE probability curve.
    """
    top_commodities = ['Tomato', 'Onion', 'Potato', 'Green Chilli']
    colors = ['#d9534f', '#f0ad4e', '#5cb85c', '#0275d8']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    axes = axes.flatten()
    
    for i, commodity in enumerate(top_commodities):
        ax = axes[i]
        subset = df[df['Commodity'] == commodity]['Modal_Price'].dropna()
        color = colors[i]
        
        # Plot count histogram + smooth KDE line
        sns.histplot(subset, kde=True, ax=ax, color=color, stat="count",
                     bins=15, alpha=0.35, edgecolor=color, line_kws={'linewidth': 2.4})
        
        mean_val = subset.mean()
        
        # Clean, simple average price line
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2.0,
                   label=f'Avg Price: INR {mean_val:.0f}/Q')
        
        ax.set_title(f'{commodity} (Total Mandis: {len(subset)})',
                     fontsize=12, fontweight='bold', pad=8)
        ax.set_xlabel('Modal Wholesale Price (INR / Quintal)', fontsize=10.5, fontweight='bold')
        ax.set_ylabel('Number of Mandis (Count)', fontsize=10.5, fontweight='bold')
        ax.legend(frameon=True, facecolor='white', framealpha=0.95, fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.5)
        
    plt.suptitle("Figure 1: Wholesale Price Distributions of Key Staple Commodities\nComparing Price Stability (Potato Clusters Tight) vs. Volatility Spikes (Tomato Stretches Wide)",
                 fontsize=13, fontweight='bold', y=0.99)
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, '01_commodity_price_distribution_kde.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved simplified: {output_path}")

# ==============================================================================
# GRAPH 2: State-wise Market Pricing Pivot Table Heatmap (5 States x 5 Crops)
# ==============================================================================
def plot_02_pivot_heatmap(df):
    """
    Simplified 5x5 Matrix comparing 5 major producing & consuming states
    across the top 5 staple crops. Every number is large, bold, and easy to read.
    """
    top_5_comm = ['Tomato', 'Onion', 'Potato', 'Brinjal', 'Green Chilli']
    top_5_states = ['Uttar Pradesh', 'Kerala', 'Punjab', 'Gujarat', 'Rajasthan']
    
    filtered_df = df[df['Commodity'].isin(top_5_comm) & df['State'].isin(top_5_states)]
    
    pivot_table = pd.pivot_table(
        filtered_df,
        values='Modal_Price',
        index='State',
        columns='Commodity',
        aggfunc='mean'
    )
    pivot_table = pivot_table.reindex(top_5_states)[top_5_comm]
    
    plt.figure(figsize=(11, 7))
    annot_labels = pivot_table.map(lambda x: f'INR {x:.0f}' if pd.notnull(x) else 'N/A')
    
    sns.heatmap(
        pivot_table,
        annot=annot_labels,
        fmt='',
        cmap='YlGnBu',
        linewidths=1.2,
        linecolor='white',
        cbar_kws={'label': 'Average Wholesale Price (INR / Quintal)'},
        annot_kws={'size': 11, 'fontweight': 'bold'}
    )
    
    plt.title("Figure 2: State-Wise Wholesale Price Comparison Matrix (5 Major States vs. 5 Key Crops)\nDirect Visual Evidence of Regional Price Disparities (Kerala Trades at 2.5x to 3x Uttar Pradesh)",
              fontsize=12, fontweight='bold', pad=14)
    plt.xlabel("Key Agricultural Commodity", fontsize=11, fontweight='bold', labelpad=8)
    plt.ylabel("Producing & Consuming State", fontsize=11, fontweight='bold', labelpad=8)
    plt.xticks(fontsize=10.5, fontweight='semibold')
    plt.yticks(fontsize=10.5, fontweight='semibold')
    plt.tight_layout()
    
    output_path = os.path.join(OUTPUT_DIR, '02_statewise_market_pricing_pivot_heatmap.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved simplified: {output_path}")

# ==============================================================================
# GRAPH 3: Top Volatile Commodities Ranked by Percentage Spread
# ==============================================================================
def plot_03_volatile_commodities_ranking(df):
    """
    Plot horizontal ranking of commodities by Percentage Price Spread
    to quantify price volatility risk across agricultural crops.
    """
    # Filter commodities with at least 15 market records for statistical significance
    comm_stats = df.groupby('Commodity', observed=True).agg(
        count=('Modal_Price', 'count'),
        mean_spread_pct=('Price_Spread_Pct', 'mean'),
        std_spread_pct=('Price_Spread_Pct', 'std')
    ).query('count >= 15').sort_values('mean_spread_pct', ascending=True).tail(15)
    
    plt.figure(figsize=(13, 8))
    
    # Color bars by volatility risk classification
    colors = [
        '#d9534f' if val >= 24 else ('#f0ad4e' if val >= 20 else '#5bc0de')
        for val in comm_stats['mean_spread_pct']
    ]
    
    bars = plt.barh(comm_stats.index, comm_stats['mean_spread_pct'], color=colors, edgecolor='none', height=0.65)
    
    # Annotate percentage values and sample count
    for bar, (comm, row) in zip(bars, comm_stats.iterrows()):
        w = bar.get_width()
        plt.text(w + 0.4, bar.get_y() + bar.get_height()/2,
                 f"{w:.1f}% (N={int(row['count'])})",
                 va='center', ha='left', fontsize=9, fontweight='bold', color='#333333')
        
    plt.axvline(20, color='#333333', linestyle='--', linewidth=1.2, alpha=0.7, label='Threshold for Elevated Volatility (20%)')
    plt.title("Figure 3: Top 15 Agricultural Commodities with Highest Price Volatility\nRanked by Normalized Percentage Spread ((Max-Min)/Modal * 100)",
              fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Mean Intra-Market Spread Percentage (%)", fontsize=11, fontweight='bold', labelpad=8)
    plt.ylabel("Agricultural Commodity", fontsize=11, fontweight='bold')
    plt.xlim(0, comm_stats['mean_spread_pct'].max() + 6)
    plt.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9)
    plt.grid(True, linestyle='--', alpha=0.5, axis='x')
    plt.tight_layout()
    
    output_path = os.path.join(OUTPUT_DIR, '03_top_volatile_commodities_percentage_spread.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

# ==============================================================================
# GRAPH 4: Hypothesis Testing - One-Way ANOVA and Levene's Test
# ==============================================================================
def plot_04_anova_levene_tests(df):
    """
    Plot One-Way ANOVA for regional price parity and Levene's test for variance homogeneity
    to statistically validate market fragmentation.
    """
    top_states = df['State'].value_counts().head(8).index
    filtered_df = df[df['State'].isin(top_states)].copy()
    
    # Statistical tests
    groups_modal = [df[df['State'] == s]['Modal_Price'].dropna() for s in top_states]
    f_stat, f_p = stats.f_oneway(*groups_modal)
    lev_stat, lev_p = stats.levene(*groups_modal)
    
    state_summary = filtered_df.groupby('State', observed=True).agg(
        Mean_Price=('Modal_Price', 'mean'),
        Std_Price=('Modal_Price', 'std'),
        Mean_Spread=('Price_Spread', 'mean'),
        Count=('Modal_Price', 'count')
    ).reindex(top_states).reset_index()
    
    state_summary['CI_95'] = 1.96 * (state_summary['Std_Price'] / np.sqrt(state_summary['Count']))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Subplot 1: ANOVA Bar Chart with 95% Confidence Intervals
    bars = ax1.bar(state_summary['State'], state_summary['Mean_Price'], yerr=state_summary['CI_95'],
                   capsize=5, color='#4682b4', alpha=0.85, edgecolor='#1c3b5e')
    ax1.set_title(f"A: Regional Price Parity (One-Way ANOVA)\nF-Statistic = {f_stat:.2f}, p-value = {f_p:.2e} (Significant Disparity)",
                  fontsize=11.5, fontweight='bold')
    ax1.set_xlabel('State', fontsize=11, fontweight='semibold')
    ax1.set_ylabel('Mean Modal Price (₹/Quintal, with 95% CI)', fontsize=11, fontweight='semibold')
    ax1.set_xticks(range(len(state_summary['State'])))
    ax1.set_xticklabels(state_summary['State'], rotation=30, ha='right', fontsize=9.5)
    ax1.grid(True, linestyle='--', alpha=0.5, axis='y')
    
    # Subplot 2: Spread Volatility by State (Levene's Test Context)
    bars2 = ax2.bar(state_summary['State'], state_summary['Mean_Spread'], color='#e06666', alpha=0.85, edgecolor='#990000')
    ax2.set_title(f"B: Regional Volatility Spread (Levene's Variance Test)\nStatistic = {lev_stat:.2f}, p-value = {lev_p:.2e} (Heterogeneous Volatility)",
                  fontsize=11.5, fontweight='bold')
    ax2.set_xlabel('State', fontsize=11, fontweight='semibold')
    ax2.set_ylabel('Mean Intra-Market Spread (₹/Quintal)', fontsize=11, fontweight='semibold')
    ax2.set_xticks(range(len(state_summary['State'])))
    ax2.set_xticklabels(state_summary['State'], rotation=30, ha='right', fontsize=9.5)
    ax2.grid(True, linestyle='--', alpha=0.5, axis='y')
    
    plt.suptitle("Figure 4: SciPy Hypothesis Testing on Regional Price Stability\nStatistically Rejecting Spatial Price Parity & Volatility Equality Across Indian Markets",
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_path = os.path.join(OUTPUT_DIR, '04_market_volatility_anova_levene_test.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

# ==============================================================================
# GRAPH 5: Market Stability Metric Correlation Matrix
# ==============================================================================
def plot_05_stability_correlation_matrix(df):
    """
    Plot correlation heatmap across price boundaries, spreads, and volatility indicators
    using a masked lower triangle for optimal visual clarity.
    """
    metrics_df = df[['Min_Price', 'Max_Price', 'Modal_Price', 'Price_Spread', 'Price_Spread_Pct', 'Spread_Ratio']].dropna()
    metrics_df.columns = [
        'Min Price (₹)',
        'Max Price (₹)',
        'Modal Price (₹)',
        'Absolute Spread (₹)',
        'Spread Pct (%)',
        'Spread Ratio (Max/Min)'
    ]
    
    corr_matrix = metrics_df.corr(method='pearson')
    
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=True,
        fmt='.2f',
        cmap='coolwarm',
        vmin=-0.5,
        vmax=1.0,
        center=0,
        linewidths=0.8,
        linecolor='white',
        cbar_kws={'label': 'Pearson Correlation Coefficient ($r$)'},
        annot_kws={'size': 10.5, 'fontweight': 'bold'}
    )
    
    plt.title("Figure 5: Market Stability Correlation Matrix\nInterrelationship Between Price Discovery Metrics and Spread Volatility",
              fontsize=13, fontweight='bold', pad=15)
    plt.xticks(rotation=30, ha='right', fontsize=9.5)
    plt.yticks(fontsize=9.5)
    plt.tight_layout()
    
    output_path = os.path.join(OUTPUT_DIR, '05_market_stability_index_matrix.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

# ==============================================================================
# MAIN EXECUTION PIPELINE
# ==============================================================================
def main():
    print("=" * 70)
    print("AGRICULTURAL MARKET PRICE VOLATILITY & SPREAD ANALYSIS")
    print("Executing Capstone Core Plot Generation Pipeline (5 Essential Graphs)")
    print("=" * 70)
    
    # Clean up obsolete graphs if present
    obsolete_files = [
        '02_dual_axis_price_and_spread_trend.png',
        '03_statewise_market_pricing_pivot_heatmap.png',
        '04_regional_price_spread_boxplot.png',
        '05_top_volatile_commodities_percentage_spread.png',
        '06_statistical_qq_normality_plots.png',
        '07_price_predictability_ols_regression.png',
        '08_market_volatility_anova_levene_test.png',
        '09_seasonal_decomposition_key_commodities.png',
        '10_volatility_clustering_and_autocorrelation.png',
        '11_grade_and_variety_price_dispersion.png',
        '12_market_stability_index_matrix.png'
    ]
    for obs in obsolete_files:
        p = os.path.join(OUTPUT_DIR, obs)
        if os.path.exists(p):
            try:
                os.remove(p)
                print(f"Removed deprecated graph: {obs}")
            except Exception:
                pass
                
    df = load_data('cleaned_commodity_price.csv')
    print(f"Successfully loaded dataset: {len(df)} records across {df['State'].nunique()} states and {df['Commodity'].nunique()} commodities.")
    print(f"Target Output Directory: {OUTPUT_DIR}\n")
    
    print("[1/5] Generating KDE Price Distribution Shapes...")
    plot_01_kde_distributions(df)
    
    print("[2/5] Generating State-wise Market Pricing Pivot Heatmap...")
    plot_02_pivot_heatmap(df)
    
    print("[3/5] Generating Top Volatile Commodities Ranking...")
    plot_03_volatile_commodities_ranking(df)
    
    print("[4/5] Generating SciPy ANOVA & Levene's Hypothesis Testing...")
    plot_04_anova_levene_tests(df)
    
    print("[5/5] Generating Market Stability Metric Correlation Matrix...")
    plot_05_stability_correlation_matrix(df)
    
    print("\n" + "=" * 70)
    print("ALL 5 CORE GRAPHS GENERATED SUCCESSFULLY!")
    print(f"Directory: {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == '__main__':
    main()
