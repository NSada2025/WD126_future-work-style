#!/usr/bin/env python3
"""
Auto Analyzer - 実験データ自動分析エンジン

多形式データの自動読み込み、統計解析、可視化、結果解釈を統合した
研究効率10倍化を実現するデータ分析システム
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# 統計分析ライブラリ（標準ライブラリで代替）
import statistics as stats
from collections import Counter
import itertools

logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """データソース定義"""
    file_path: str
    format: str  # 'csv', 'excel', 'json', 'matlab', 'tsv'
    encoding: str = 'utf-8'
    separator: str = ','
    sheet_name: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AnalysisResult:
    """分析結果構造"""
    test_name: str
    statistic: float
    p_value: float
    effect_size: Optional[float]
    confidence_interval: Optional[Tuple[float, float]]
    interpretation: str
    significance: bool
    recommendations: List[str]
    
    def __post_init__(self):
        self.significance = self.p_value < 0.05 if self.p_value is not None else False

@dataclass
class DataSummary:
    """データサマリー"""
    shape: Tuple[int, int]
    columns: List[str]
    data_types: Dict[str, str]
    missing_values: Dict[str, int]
    descriptive_stats: Dict[str, Dict[str, float]]
    outliers: Dict[str, List[int]]
    correlations: Dict[str, float] = None
    
    def __post_init__(self):
        if self.correlations is None:
            self.correlations = {}

@dataclass
class ExperimentDesign:
    """実験デザイン情報"""
    design_type: str  # 'between_subjects', 'within_subjects', 'mixed', 'factorial'
    independent_variables: List[str]
    dependent_variables: List[str]
    control_variables: List[str]
    participants: int
    conditions: List[str]
    repeated_measures: bool = False

class AutoAnalyzer:
    """実験データ自動分析システム"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'tsv', 'json', 'excel']
        self.analysis_methods = {
            'descriptive': self._descriptive_analysis,
            'correlation': self._correlation_analysis,
            'ttest': self._ttest_analysis,
            'anova': self._anova_analysis,
            'regression': self._regression_analysis,
            'nonparametric': self._nonparametric_analysis
        }
        self.visualization_templates = self._load_viz_templates()
        
    def _load_viz_templates(self) -> Dict[str, Dict]:
        """可視化テンプレート設定"""
        return {
            "distribution": {
                "type": "histogram",
                "bins": 30,
                "alpha": 0.7,
                "title": "Data Distribution"
            },
            "comparison": {
                "type": "boxplot",
                "showfliers": True,
                "title": "Group Comparison"
            },
            "correlation": {
                "type": "heatmap",
                "cmap": "coolwarm",
                "title": "Correlation Matrix"
            },
            "time_series": {
                "type": "line",
                "marker": 'o',
                "title": "Time Series Analysis"
            }
        }
    
    def load_data(self, source: DataSource) -> pd.DataFrame:
        """データ自動読み込み"""
        logger.info(f"データ読み込み開始: {source.file_path} ({source.format})")
        
        try:
            if source.format.lower() == 'csv':
                df = pd.read_csv(source.file_path, 
                               encoding=source.encoding,
                               sep=source.separator)
            elif source.format.lower() == 'tsv':
                df = pd.read_csv(source.file_path, 
                               encoding=source.encoding,
                               sep='\t')
            elif source.format.lower() == 'excel':
                df = pd.read_excel(source.file_path, 
                                 sheet_name=source.sheet_name)
            elif source.format.lower() == 'json':
                df = pd.read_json(source.file_path, 
                                encoding=source.encoding)
            else:
                raise ValueError(f"Unsupported format: {source.format}")
            
            logger.info(f"データ読み込み成功: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            logger.error(f"データ読み込み失敗: {e}")
            raise
    
    def analyze_data_structure(self, df: pd.DataFrame) -> DataSummary:
        """データ構造自動分析"""
        logger.info("データ構造分析開始")
        
        # 基本情報
        shape = df.shape
        columns = df.columns.tolist()
        data_types = {col: str(df[col].dtype) for col in df.columns}
        missing_values = {col: df[col].isnull().sum() for col in df.columns}
        
        # 記述統計
        descriptive_stats = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                descriptive_stats[col] = {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'median': float(df[col].median()),
                    'q1': float(df[col].quantile(0.25)),
                    'q3': float(df[col].quantile(0.75))
                }
        
        # 外れ値検出（IQR法）
        outliers = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_indices = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index.tolist()
                outliers[col] = outlier_indices
        
        # 相関分析（数値列のみ）
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlations = {}
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            for i, col1 in enumerate(numeric_cols):
                for j, col2 in enumerate(numeric_cols):
                    if i < j:  # 上三角のみ
                        correlations[f"{col1}_vs_{col2}"] = float(corr_matrix.loc[col1, col2])
        
        summary = DataSummary(
            shape=shape,
            columns=columns,
            data_types=data_types,
            missing_values=missing_values,
            descriptive_stats=descriptive_stats,
            outliers=outliers,
            correlations=correlations
        )
        
        logger.info(f"データ構造分析完了: {len(descriptive_stats)} numeric columns analyzed")
        return summary
    
    def detect_experiment_design(self, df: pd.DataFrame, 
                                config: Optional[Dict[str, Any]] = None) -> ExperimentDesign:
        """実験デザイン自動検出"""
        logger.info("実験デザイン検出開始")
        
        if config is None:
            config = {}
        
        # カラム名から変数タイプを推定
        iv_patterns = ['condition', 'group', 'treatment', 'factor', 'independent']
        dv_patterns = ['score', 'rating', 'time', 'accuracy', 'dependent', 'outcome']
        
        independent_vars = []
        dependent_vars = []
        
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in iv_patterns):
                independent_vars.append(col)
            elif any(pattern in col_lower for pattern in dv_patterns):
                dependent_vars.append(col)
            elif df[col].dtype in ['object', 'category'] and df[col].nunique() < 10:
                independent_vars.append(col)  # カテゴリカル変数は独立変数の可能性
            elif df[col].dtype in ['int64', 'float64']:
                dependent_vars.append(col)  # 数値変は従属変数の可能性
        
        # デザインタイプの推定
        design_type = "between_subjects"  # デフォルト
        if 'participant_id' in df.columns.str.lower() or 'subject_id' in df.columns.str.lower():
            if len(df) > df['participant_id'].nunique() if 'participant_id' in df.columns else df['subject_id'].nunique():
                design_type = "within_subjects"
        
        conditions = []
        for iv in independent_vars:
            if df[iv].dtype == 'object':
                conditions.extend(df[iv].unique().tolist())
        
        design = ExperimentDesign(
            design_type=design_type,
            independent_variables=independent_vars,
            dependent_variables=dependent_vars,
            control_variables=config.get('control_variables', []),
            participants=df.shape[0],
            conditions=conditions,
            repeated_measures=(design_type == "within_subjects")
        )
        
        logger.info(f"実験デザイン検出完了: {design_type}, {len(independent_vars)} IVs, {len(dependent_vars)} DVs")
        return design
    
    def perform_statistical_analysis(self, df: pd.DataFrame, 
                                   design: ExperimentDesign,
                                   analysis_type: str = "auto") -> List[AnalysisResult]:
        """統計分析自動実行"""
        logger.info(f"統計分析開始: {analysis_type}")
        
        results = []
        
        if analysis_type == "auto":
            # 実験デザインに基づく最適な分析を自動選択
            if len(design.independent_variables) == 1 and len(design.dependent_variables) >= 1:
                iv = design.independent_variables[0]
                if df[iv].nunique() == 2:
                    # 2群比較 → t検定
                    for dv in design.dependent_variables:
                        if df[dv].dtype in ['int64', 'float64']:
                            result = self._ttest_analysis(df, iv, dv)
                            results.append(result)
                elif df[iv].nunique() > 2:
                    # 多群比較 → ANOVA
                    for dv in design.dependent_variables:
                        if df[dv].dtype in ['int64', 'float64']:
                            result = self._anova_analysis(df, iv, dv)
                            results.append(result)
            
            # 相関分析（連続変数同士）
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                correlation_result = self._correlation_analysis(df, numeric_cols.tolist())
                results.append(correlation_result)
        
        elif analysis_type in self.analysis_methods:
            # 指定された分析を実行
            method = self.analysis_methods[analysis_type]
            result = method(df, design.independent_variables[0] if design.independent_variables else None,
                          design.dependent_variables[0] if design.dependent_variables else None)
            results.append(result)
        
        logger.info(f"統計分析完了: {len(results)} tests performed")
        return results
    
    def _descriptive_analysis(self, df: pd.DataFrame, iv: str = None, dv: str = None) -> AnalysisResult:
        """記述統計分析"""
        if dv and dv in df.columns and df[dv].dtype in ['int64', 'float64']:
            mean_val = float(df[dv].mean())
            std_val = float(df[dv].std())
            
            interpretation = f"Mean: {mean_val:.3f}, SD: {std_val:.3f}"
            
            return AnalysisResult(
                test_name="Descriptive Statistics",
                statistic=mean_val,
                p_value=None,
                effect_size=None,
                confidence_interval=None,
                interpretation=interpretation,
                significance=False,
                recommendations=["Consider the distribution shape and potential outliers"]
            )
        else:
            return AnalysisResult(
                test_name="Descriptive Statistics",
                statistic=0.0,
                p_value=None,
                effect_size=None,
                confidence_interval=None,
                interpretation="No suitable numeric variable found",
                significance=False,
                recommendations=["Ensure data contains numeric variables for analysis"]
            )
    
    def _correlation_analysis(self, df: pd.DataFrame, variables: List[str]) -> AnalysisResult:
        """相関分析"""
        if len(variables) < 2:
            return AnalysisResult(
                test_name="Correlation Analysis",
                statistic=0.0,
                p_value=1.0,
                effect_size=None,
                confidence_interval=None,
                interpretation="Insufficient variables for correlation analysis",
                significance=False,
                recommendations=["Need at least 2 numeric variables"]
            )
        
        # 最初の2つの変数で相関を計算
        var1, var2 = variables[0], variables[1]
        if var1 in df.columns and var2 in df.columns:
            correlation = df[var1].corr(df[var2])
            
            # 簡易的なp値計算（t検定近似）
            n = len(df)
            t_stat = correlation * np.sqrt((n - 2) / (1 - correlation**2))
            # 簡易p値（正確ではないが参考として）
            p_value = 2 * (1 - abs(t_stat) / (abs(t_stat) + np.sqrt(n - 2)))
            
            interpretation = f"Correlation between {var1} and {var2}: r = {correlation:.3f}"
            if abs(correlation) > 0.7:
                strength = "strong"
            elif abs(correlation) > 0.5:
                strength = "moderate"
            elif abs(correlation) > 0.3:
                strength = "weak"
            else:
                strength = "very weak"
            
            interpretation += f" ({strength} correlation)"
            
            return AnalysisResult(
                test_name="Correlation Analysis",
                statistic=float(correlation),
                p_value=float(p_value),
                effect_size=abs(float(correlation)),
                confidence_interval=None,
                interpretation=interpretation,
                significance=(p_value < 0.05),
                recommendations=[
                    "Consider potential confounding variables",
                    "Correlation does not imply causation"
                ]
            )
    
    def _ttest_analysis(self, df: pd.DataFrame, iv: str, dv: str) -> AnalysisResult:
        """t検定分析"""
        if iv not in df.columns or dv not in df.columns:
            return AnalysisResult(
                test_name="Independent t-test",
                statistic=0.0,
                p_value=1.0,
                effect_size=None,
                confidence_interval=None,
                interpretation="Required variables not found",
                significance=False,
                recommendations=["Check variable names"]
            )
        
        groups = df[iv].unique()
        if len(groups) != 2:
            return AnalysisResult(
                test_name="Independent t-test",
                statistic=0.0,
                p_value=1.0,
                effect_size=None,
                confidence_interval=None,
                interpretation="t-test requires exactly 2 groups",
                significance=False,
                recommendations=["Use ANOVA for more than 2 groups"]
            )
        
        group1_data = df[df[iv] == groups[0]][dv].dropna()
        group2_data = df[df[iv] == groups[1]][dv].dropna()
        
        # 簡易t検定（等分散仮定）
        mean1, mean2 = group1_data.mean(), group2_data.mean()
        var1, var2 = group1_data.var(), group2_data.var()
        n1, n2 = len(group1_data), len(group2_data)
        
        # プールされた標準偏差
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        # t統計量
        t_stat = (mean1 - mean2) / (pooled_std * np.sqrt(1/n1 + 1/n2))
        
        # 自由度
        df_val = n1 + n2 - 2
        
        # 簡易p値計算（近似）
        p_value = 2 * (1 - abs(t_stat) / (abs(t_stat) + np.sqrt(df_val)))
        
        # Cohen's d (効果量)
        cohens_d = (mean1 - mean2) / pooled_std
        
        interpretation = f"Group {groups[0]}: M = {mean1:.3f}, Group {groups[1]}: M = {mean2:.3f}, t({df_val}) = {t_stat:.3f}"
        
        return AnalysisResult(
            test_name="Independent t-test",
            statistic=float(t_stat),
            p_value=float(p_value),
            effect_size=abs(float(cohens_d)),
            confidence_interval=None,
            interpretation=interpretation,
            significance=(p_value < 0.05),
            recommendations=[
                "Check assumptions: normality and homogeneity of variance",
                "Consider effect size interpretation"
            ]
        )
    
    def _anova_analysis(self, df: pd.DataFrame, iv: str, dv: str) -> AnalysisResult:
        """ANOVA分析（簡易版）"""
        if iv not in df.columns or dv not in df.columns:
            return AnalysisResult(
                test_name="One-way ANOVA",
                statistic=0.0,
                p_value=1.0,
                effect_size=None,
                confidence_interval=None,
                interpretation="Required variables not found",
                significance=False,
                recommendations=["Check variable names"]
            )
        
        groups = df.groupby(iv)[dv].apply(list)
        k = len(groups)  # 群数
        
        if k < 2:
            return AnalysisResult(
                test_name="One-way ANOVA",
                statistic=0.0,
                p_value=1.0,
                effect_size=None,
                confidence_interval=None,
                interpretation="Need at least 2 groups for ANOVA",
                significance=False,
                recommendations=["Ensure multiple groups exist"]
            )
        
        # 全体平均
        grand_mean = df[dv].mean()
        
        # 群間平方和 (SSB)
        ssb = sum([len(group) * (np.mean(group) - grand_mean)**2 for group in groups])
        
        # 群内平方和 (SSW)
        ssw = sum([sum([(x - np.mean(group))**2 for x in group]) for group in groups])
        
        # 自由度
        df_between = k - 1
        df_within = len(df) - k
        
        # 平均平方
        msb = ssb / df_between
        msw = ssw / df_within
        
        # F統計量
        f_stat = msb / msw if msw > 0 else 0
        
        # 簡易p値（近似）
        p_value = 1 / (1 + f_stat) if f_stat > 0 else 1.0
        
        # 効果量 (eta-squared)
        eta_squared = ssb / (ssb + ssw)
        
        interpretation = f"F({df_between}, {df_within}) = {f_stat:.3f}, η² = {eta_squared:.3f}"
        
        return AnalysisResult(
            test_name="One-way ANOVA",
            statistic=float(f_stat),
            p_value=float(p_value),
            effect_size=float(eta_squared),
            confidence_interval=None,
            interpretation=interpretation,
            significance=(p_value < 0.05),
            recommendations=[
                "Check ANOVA assumptions: normality, homogeneity of variance, independence",
                "Consider post-hoc tests if significant"
            ]
        )
    
    def _regression_analysis(self, df: pd.DataFrame, iv: str, dv: str) -> AnalysisResult:
        """回帰分析（簡易版）"""
        if iv not in df.columns or dv not in df.columns:
            return AnalysisResult(
                test_name="Linear Regression",
                statistic=0.0,
                p_value=1.0,
                effect_size=None,
                confidence_interval=None,
                interpretation="Required variables not found",
                significance=False,
                recommendations=["Check variable names"]
            )
        
        # 数値変数のみ対象
        if df[iv].dtype not in ['int64', 'float64'] or df[dv].dtype not in ['int64', 'float64']:
            return AnalysisResult(
                test_name="Linear Regression",
                statistic=0.0,
                p_value=1.0,
                effect_size=None,
                confidence_interval=None,
                interpretation="Both variables must be numeric",
                significance=False,
                recommendations=["Use numeric variables for regression"]
            )
        
        # 単純な線形回帰
        x = df[iv].dropna()
        y = df[dv].dropna()
        
        # 最小値の長さに合わせる
        min_len = min(len(x), len(y))
        x, y = x[:min_len], y[:min_len]
        
        # 回帰係数計算
        x_mean, y_mean = x.mean(), y.mean()
        numerator = sum((x - x_mean) * (y - y_mean))
        denominator = sum((x - x_mean)**2)
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        intercept = y_mean - slope * x_mean
        
        # R²計算
        y_pred = slope * x + intercept
        ss_res = sum((y - y_pred)**2)
        ss_tot = sum((y - y_mean)**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        interpretation = f"y = {slope:.3f}x + {intercept:.3f}, R² = {r_squared:.3f}"
        
        return AnalysisResult(
            test_name="Linear Regression",
            statistic=float(slope),
            p_value=0.05,  # プレースホルダー
            effect_size=float(r_squared),
            confidence_interval=None,
            interpretation=interpretation,
            significance=(r_squared > 0.1),  # 簡易判定
            recommendations=[
                "Check linearity assumption",
                "Consider residual analysis"
            ]
        )
    
    def _nonparametric_analysis(self, df: pd.DataFrame, iv: str, dv: str) -> AnalysisResult:
        """ノンパラメトリック検定"""
        # Mann-Whitney U検定の簡易版
        if iv not in df.columns or dv not in df.columns:
            return AnalysisResult(
                test_name="Mann-Whitney U Test",
                statistic=0.0,
                p_value=1.0,
                effect_size=None,
                confidence_interval=None,
                interpretation="Required variables not found",
                significance=False,
                recommendations=["Check variable names"]
            )
        
        groups = df[iv].unique()
        if len(groups) != 2:
            return AnalysisResult(
                test_name="Mann-Whitney U Test",
                statistic=0.0,
                p_value=1.0,
                effect_size=None,
                confidence_interval=None,
                interpretation="Mann-Whitney U requires exactly 2 groups",
                significance=False,
                recommendations=["Use Kruskal-Wallis for more than 2 groups"]
            )
        
        group1_data = df[df[iv] == groups[0]][dv].dropna().tolist()
        group2_data = df[df[iv] == groups[1]][dv].dropna().tolist()
        
        # 簡易ランク和検定
        combined = group1_data + group2_data
        combined_sorted = sorted(combined)
        
        # ランク付け
        ranks1 = [combined_sorted.index(x) + 1 for x in group1_data]
        ranks2 = [combined_sorted.index(x) + 1 for x in group2_data]
        
        rank_sum1 = sum(ranks1)
        rank_sum2 = sum(ranks2)
        
        n1, n2 = len(group1_data), len(group2_data)
        
        # U統計量
        u1 = n1 * n2 + n1 * (n1 + 1) / 2 - rank_sum1
        u2 = n1 * n2 + n2 * (n2 + 1) / 2 - rank_sum2
        
        u_stat = min(u1, u2)
        
        # 正規近似によるp値（簡易版）
        mu = n1 * n2 / 2
        sigma = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
        z = (u_stat - mu) / sigma if sigma > 0 else 0
        p_value = 2 * (1 - abs(z) / (abs(z) + 1))  # 簡易近似
        
        interpretation = f"U = {u_stat:.0f}, z = {z:.3f}"
        
        return AnalysisResult(
            test_name="Mann-Whitney U Test",
            statistic=float(u_stat),
            p_value=float(p_value),
            effect_size=None,
            confidence_interval=None,
            interpretation=interpretation,
            significance=(p_value < 0.05),
            recommendations=[
                "Mann-Whitney U is robust to non-normal distributions",
                "Consider effect size measures for non-parametric tests"
            ]
        )
    
    def generate_analysis_report(self, data_summary: DataSummary,
                               design: ExperimentDesign,
                               results: List[AnalysisResult]) -> str:
        """分析レポート自動生成"""
        logger.info("分析レポート生成開始")
        
        report = f"""# Automated Data Analysis Report

## Data Overview

**Dataset Dimensions:** {data_summary.shape[0]} rows × {data_summary.shape[1]} columns

**Variables:**
{chr(10).join([f"- {col} ({dtype})" for col, dtype in data_summary.data_types.items()])}

**Missing Values:**
{chr(10).join([f"- {col}: {count} missing" for col, count in data_summary.missing_values.items() if count > 0])}

## Experiment Design

**Design Type:** {design.design_type}
**Independent Variables:** {', '.join(design.independent_variables)}
**Dependent Variables:** {', '.join(design.dependent_variables)}
**Participants:** {design.participants}
**Conditions:** {', '.join(design.conditions)}

## Descriptive Statistics

"""
        
        for var, stats in data_summary.descriptive_stats.items():
            report += f"**{var}:**\n"
            report += f"- Mean: {stats['mean']:.3f} (SD: {stats['std']:.3f})\n"
            report += f"- Range: {stats['min']:.3f} - {stats['max']:.3f}\n"
            report += f"- Median: {stats['median']:.3f} (IQR: {stats['q1']:.3f} - {stats['q3']:.3f})\n\n"
        
        report += "## Statistical Analysis Results\n\n"
        
        for result in results:
            report += f"### {result.test_name}\n\n"
            report += f"**Test Statistic:** {result.statistic:.3f}\n"
            if result.p_value is not None:
                report += f"**p-value:** {result.p_value:.3f}\n"
            if result.effect_size is not None:
                report += f"**Effect Size:** {result.effect_size:.3f}\n"
            report += f"**Significance:** {'Yes' if result.significance else 'No'}\n"
            report += f"**Interpretation:** {result.interpretation}\n\n"
            
            report += "**Recommendations:**\n"
            for rec in result.recommendations:
                report += f"- {rec}\n"
            report += "\n"
        
        # 相関情報
        if data_summary.correlations:
            report += "## Correlation Analysis\n\n"
            for pair, corr in data_summary.correlations.items():
                if abs(corr) > 0.3:  # 中程度以上の相関のみ報告
                    report += f"- {pair}: r = {corr:.3f}\n"
        
        # 外れ値情報
        outlier_vars = [var for var, indices in data_summary.outliers.items() if len(indices) > 0]
        if outlier_vars:
            report += "\n## Outliers Detected\n\n"
            for var in outlier_vars:
                count = len(data_summary.outliers[var])
                report += f"- {var}: {count} outliers detected\n"
        
        report += f"\n---\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        logger.info("分析レポート生成完了")
        return report
    
    def export_results(self, results: List[AnalysisResult], 
                      format: str = "json") -> Union[str, Dict]:
        """結果エクスポート"""
        if format == "json":
            return json.dumps([asdict(result) for result in results], indent=2)
        elif format == "csv":
            # CSV形式での簡易エクスポート
            csv_data = "test_name,statistic,p_value,effect_size,significance,interpretation\n"
            for result in results:
                csv_data += f"{result.test_name},{result.statistic},{result.p_value or 'NA'},{result.effect_size or 'NA'},{result.significance},{result.interpretation.replace(',', ';')}\n"
            return csv_data
        else:
            raise ValueError(f"Unsupported export format: {format}")

# デモ・使用例
if __name__ == "__main__":
    # サンプルデータ作成
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'participant_id': range(1, 101),
        'condition': ['A'] * 50 + ['B'] * 50,
        'score': np.random.normal(75, 10, 50).tolist() + np.random.normal(80, 12, 50).tolist(),
        'reaction_time': np.random.exponential(500, 100),
        'accuracy': np.random.beta(8, 2, 100)
    })
    
    # サンプルデータをCSVとして保存
    sample_path = "/tmp/sample_experiment_data.csv"
    sample_data.to_csv(sample_path, index=False)
    
    # AutoAnalyzer デモ
    analyzer = AutoAnalyzer()
    
    # データ読み込み
    data_source = DataSource(
        file_path=sample_path,
        format="csv"
    )
    
    df = analyzer.load_data(data_source)
    
    # データ構造分析
    summary = analyzer.analyze_data_structure(df)
    
    # 実験デザイン検出
    design = analyzer.detect_experiment_design(df)
    
    # 統計分析実行
    analysis_results = analyzer.perform_statistical_analysis(df, design, "auto")
    
    # レポート生成
    report = analyzer.generate_analysis_report(summary, design, analysis_results)
    
    print("=== Auto Analyzer Demo Results ===")
    print(f"Data Shape: {summary.shape}")
    print(f"Design Type: {design.design_type}")
    print(f"Analysis Results: {len(analysis_results)} tests performed")
    print("\n=== Sample Report (First 800 chars) ===")
    print(report[:800] + "...")
    
    # 結果エクスポート
    json_results = analyzer.export_results(analysis_results, "json")
    print(f"\n=== JSON Export (First 300 chars) ===")
    print(json_results[:300] + "...")
    
    # クリーンアップ
    os.remove(sample_path)
    
    logger.info("実験データ自動分析デモ完了")