#!/usr/bin/env python3
"""
Productivity Analyzer - 生産性分析システム

研究生産性の包括的分析・パターン発見・最適化提案を行う
研究効率10倍化を実現する生産性インテリジェンスエンジン
"""

import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
from enum import Enum
import logging

# Optional imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False

try:
    from .schedule_optimizer import ResearchTask, TaskType, TaskPriority, DailySchedule
    from .focus_tracker import FocusSession, DistractionEvent, FocusLevel
except ImportError:
    from schedule_optimizer import ResearchTask, TaskType, TaskPriority, DailySchedule
    from focus_tracker import FocusSession, DistractionEvent, FocusLevel

logger = logging.getLogger(__name__)

class ProductivityPeriod(Enum):
    """生産性期間"""
    MORNING = "morning"         # 6:00-12:00
    AFTERNOON = "afternoon"     # 12:00-18:00
    EVENING = "evening"         # 18:00-24:00
    NIGHT = "night"            # 0:00-6:00

class ProductivityTrend(Enum):
    """生産性トレンド"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"

@dataclass
class ProductivityMetric:
    """生産性指標"""
    metric_id: str
    timestamp: datetime
    task_id: Optional[str]
    
    # Time metrics
    planned_duration: int       # minutes
    actual_duration: int        # minutes
    focused_duration: int       # minutes
    
    # Quality metrics
    completion_quality: float   # 0.0-1.0
    focus_efficiency: float     # 0.0-1.0
    task_complexity: float      # 0.0-1.0
    
    # Context metrics
    interruption_count: int
    context_switches: int
    energy_level: float         # 0.0-1.0
    
    # Calculated metrics
    time_efficiency: float = 0.0      # actual vs planned
    output_per_minute: float = 0.0    # quality per minute
    distraction_impact: float = 0.0   # impact of distractions
    
    def __post_init__(self):
        if self.planned_duration > 0:
            self.time_efficiency = min(1.0, self.planned_duration / self.actual_duration)
        
        if self.actual_duration > 0:
            self.output_per_minute = self.completion_quality / self.actual_duration
        
        self.distraction_impact = min(1.0, (self.interruption_count + self.context_switches) * 0.1)

@dataclass
class ProductivityPattern:
    """生産性パターン"""
    pattern_id: str
    name: str
    description: str
    
    # Time patterns
    optimal_periods: List[ProductivityPeriod]
    peak_hours: List[int]
    low_performance_hours: List[int]
    
    # Task patterns
    preferred_task_types: List[TaskType]
    high_performance_tasks: Dict[TaskType, float]
    optimal_session_length: int     # minutes
    
    # Environmental patterns
    optimal_conditions: Dict[str, Any]
    productivity_factors: Dict[str, float]
    
    # Performance metrics
    average_efficiency: float
    consistency_score: float        # How consistent the pattern is
    sample_size: int               # Number of data points
    
    def __post_init__(self):
        if not hasattr(self, 'optimal_conditions'):
            self.optimal_conditions = {}
        if not hasattr(self, 'productivity_factors'):
            self.productivity_factors = {}

@dataclass
class ProductivityInsight:
    """生産性インサイト"""
    insight_id: str
    category: str               # "pattern", "trend", "optimization", "warning"
    title: str
    description: str
    confidence: float           # 0.0-1.0
    impact_score: float         # 0.0-1.0
    actionable: bool
    recommendations: List[str]
    supporting_data: Dict[str, Any]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class ProductivityReport:
    """生産性レポート"""
    report_id: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    
    # Summary metrics
    total_work_hours: float
    focused_work_hours: float
    average_efficiency: float
    task_completion_rate: float
    
    # Trends
    productivity_trend: ProductivityTrend
    trend_strength: float       # How strong the trend is
    
    # Insights and patterns
    insights: List[ProductivityInsight]
    patterns: List[ProductivityPattern]
    
    # Recommendations
    optimization_opportunities: List[str]
    time_management_suggestions: List[str]
    focus_improvement_suggestions: List[str]

class ProductivityAnalyzer:
    """生産性分析システム"""
    
    def __init__(self):
        self.productivity_metrics: List[ProductivityMetric] = []
        self.patterns: Dict[str, ProductivityPattern] = {}
        self.insights: List[ProductivityInsight] = []
        self.reports: List[ProductivityReport] = []
        
        # External data sources
        self.tasks: Dict[str, ResearchTask] = {}
        self.focus_sessions: List[FocusSession] = []
        self.schedules: Dict[str, DailySchedule] = {}
        
        # Analysis configuration
        self.config = {
            "min_pattern_confidence": 0.7,
            "trend_analysis_window": 14,        # days
            "pattern_detection_window": 30,     # days
            "min_data_points": 10,              # minimum for pattern detection
            "outlier_threshold": 2.0,           # standard deviations
            "efficiency_benchmark": 0.75,       # target efficiency
            "focus_benchmark": 0.8,             # target focus ratio
            "completion_benchmark": 0.9         # target completion rate
        }
    
    def add_task_data(self, tasks: Dict[str, ResearchTask]):
        """タスクデータ追加"""
        self.tasks.update(tasks)
        logger.info(f"タスクデータ追加: {len(tasks)}件")
    
    def add_focus_data(self, sessions: List[FocusSession]):
        """集中データ追加"""
        self.focus_sessions.extend(sessions)
        logger.info(f"集中セッション追加: {len(sessions)}件")
    
    def add_schedule_data(self, schedules: Dict[str, DailySchedule]):
        """スケジュールデータ追加"""
        self.schedules.update(schedules)
        logger.info(f"スケジュールデータ追加: {len(schedules)}件")
    
    def calculate_productivity_metrics(self, start_date: datetime = None, 
                                     end_date: datetime = None):
        """生産性指標計算"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()
        
        # Clear existing metrics in range
        self.productivity_metrics = [m for m in self.productivity_metrics 
                                   if not (start_date <= m.timestamp <= end_date)]
        
        # Calculate metrics from tasks and focus sessions
        self._calculate_task_metrics(start_date, end_date)
        self._calculate_focus_metrics(start_date, end_date)
        self._calculate_schedule_metrics(start_date, end_date)
        
        logger.info(f"生産性指標計算完了: {len(self.productivity_metrics)}件")
    
    def _calculate_task_metrics(self, start_date: datetime, end_date: datetime):
        """タスクベース指標計算"""
        for task in self.tasks.values():
            if task.created_at and start_date <= task.created_at <= end_date:
                # Find related focus session
                related_session = None
                for session in self.focus_sessions:
                    if session.task_id == task.task_id:
                        related_session = session
                        break
                
                # Calculate complexity based on task attributes
                complexity = self._calculate_task_complexity(task)
                
                # Create productivity metric
                metric = ProductivityMetric(
                    metric_id=f"task_{task.task_id}_{int(task.created_at.timestamp())}",
                    timestamp=task.created_at,
                    task_id=task.task_id,
                    planned_duration=task.estimated_duration,
                    actual_duration=task.completed_duration,
                    focused_duration=related_session.focused_duration if related_session else task.completed_duration,
                    completion_quality=task.completion_ratio,
                    focus_efficiency=related_session.focus_efficiency if related_session else 0.8,
                    task_complexity=complexity,
                    interruption_count=related_session.distraction_count if related_session else 0,
                    context_switches=0,  # Would need additional tracking
                    energy_level=0.7     # Default value
                )
                
                self.productivity_metrics.append(metric)
    
    def _calculate_focus_metrics(self, start_date: datetime, end_date: datetime):
        """集中ベース指標計算"""
        for session in self.focus_sessions:
            if start_date <= session.start_time <= end_date and session.end_time:
                metric = ProductivityMetric(
                    metric_id=f"focus_{session.session_id}",
                    timestamp=session.start_time,
                    task_id=session.task_id,
                    planned_duration=session.total_duration // 60,  # Convert to minutes
                    actual_duration=session.total_duration // 60,
                    focused_duration=session.focused_duration // 60,
                    completion_quality=1.0 if session.focus_efficiency > 0.8 else session.focus_efficiency,
                    focus_efficiency=session.focus_efficiency,
                    task_complexity=0.5,  # Default complexity
                    interruption_count=session.distraction_count,
                    context_switches=session.flow_interruptions,
                    energy_level=session.average_focus_level / 4.0  # Normalize to 0-1
                )
                
                self.productivity_metrics.append(metric)
    
    def _calculate_schedule_metrics(self, start_date: datetime, end_date: datetime):
        """スケジュールベース指標計算"""
        for date_str, schedule in self.schedules.items():
            schedule_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= schedule_date <= end_date:
                # Calculate metrics for each schedule block
                for block in schedule.schedule_blocks:
                    metric = ProductivityMetric(
                        metric_id=f"schedule_{block.block_id}",
                        timestamp=block.time_slot.start_time,
                        task_id=block.task.task_id,
                        planned_duration=block.time_slot.duration_minutes,
                        actual_duration=block.effective_duration,
                        focused_duration=int(block.effective_duration * block.estimated_efficiency),
                        completion_quality=block.estimated_efficiency,
                        focus_efficiency=block.estimated_efficiency,
                        task_complexity=self._calculate_task_complexity(block.task),
                        interruption_count=0,  # Would need tracking
                        context_switches=0,
                        energy_level=block.time_slot.energy_level.value / 4.0
                    )
                    
                    self.productivity_metrics.append(metric)
    
    def _calculate_task_complexity(self, task: ResearchTask) -> float:
        """タスク複雑度計算"""
        complexity = 0.5  # Base complexity
        
        # Task type complexity
        type_complexity = {
            TaskType.RESEARCH: 0.8,
            TaskType.ANALYSIS: 0.9,
            TaskType.WRITING: 0.7,
            TaskType.CODING: 0.8,
            TaskType.READING: 0.5,
            TaskType.MEETING: 0.3,
            TaskType.REVIEW: 0.6,
            TaskType.ADMIN: 0.2
        }
        complexity = type_complexity.get(task.task_type, 0.5)
        
        # Duration complexity
        if task.estimated_duration > 180:  # > 3 hours
            complexity += 0.2
        elif task.estimated_duration > 60:  # > 1 hour
            complexity += 0.1
        
        # Deep focus requirement
        if task.requires_deep_focus:
            complexity += 0.1
        
        # Priority complexity
        if task.priority == TaskPriority.CRITICAL:
            complexity += 0.1
        
        return min(1.0, complexity)
    
    def detect_productivity_patterns(self, days_back: int = 30) -> List[ProductivityPattern]:
        """生産性パターン検出"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        relevant_metrics = [m for m in self.productivity_metrics 
                          if m.timestamp >= cutoff_date]
        
        if len(relevant_metrics) < self.config["min_data_points"]:
            logger.warning("パターン検出には十分なデータがありません")
            return []
        
        patterns = []
        
        # Time-based patterns
        time_pattern = self._detect_time_patterns(relevant_metrics)
        if time_pattern:
            patterns.append(time_pattern)
        
        # Task-type patterns
        task_pattern = self._detect_task_type_patterns(relevant_metrics)
        if task_pattern:
            patterns.append(task_pattern)
        
        # Session length patterns
        session_pattern = self._detect_session_length_patterns(relevant_metrics)
        if session_pattern:
            patterns.append(session_pattern)
        
        # Energy level patterns
        energy_pattern = self._detect_energy_patterns(relevant_metrics)
        if energy_pattern:
            patterns.append(energy_pattern)
        
        # Store detected patterns
        for pattern in patterns:
            self.patterns[pattern.pattern_id] = pattern
        
        logger.info(f"生産性パターン検出: {len(patterns)}パターン")
        return patterns
    
    def _detect_time_patterns(self, metrics: List[ProductivityMetric]) -> Optional[ProductivityPattern]:
        """時間ベースパターン検出"""
        # Group metrics by hour
        hourly_performance = defaultdict(list)
        for metric in metrics:
            hour = metric.timestamp.hour
            efficiency = metric.focus_efficiency * metric.time_efficiency
            hourly_performance[hour].append(efficiency)
        
        # Calculate average performance per hour
        hour_averages = {}
        for hour, performances in hourly_performance.items():
            if len(performances) >= 3:  # Minimum sample size
                hour_averages[hour] = sum(performances) / len(performances)
        
        if len(hour_averages) < 4:
            return None
        
        # Find peak and low hours
        sorted_hours = sorted(hour_averages.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [hour for hour, perf in sorted_hours[:3] if perf > 0.7]
        low_hours = [hour for hour, perf in sorted_hours[-3:] if perf < 0.5]
        
        # Determine optimal periods
        optimal_periods = []
        for hour in peak_hours:
            if 6 <= hour < 12:
                optimal_periods.append(ProductivityPeriod.MORNING)
            elif 12 <= hour < 18:
                optimal_periods.append(ProductivityPeriod.AFTERNOON)
            elif 18 <= hour < 24:
                optimal_periods.append(ProductivityPeriod.EVENING)
            else:
                optimal_periods.append(ProductivityPeriod.NIGHT)
        
        optimal_periods = list(set(optimal_periods))
        
        # Calculate consistency
        all_performances = [perf for hour_perfs in hourly_performance.values() for perf in hour_perfs]
        consistency = 1.0 - (np.std(all_performances) / np.mean(all_performances)) if all_performances else 0.0
        consistency = max(0.0, min(1.0, consistency))
        
        return ProductivityPattern(
            pattern_id=f"time_pattern_{int(datetime.now().timestamp())}",
            name="時間ベース生産性パターン",
            description=f"最高効率時間帯: {peak_hours}時台",
            optimal_periods=optimal_periods,
            peak_hours=peak_hours,
            low_performance_hours=low_hours,
            preferred_task_types=[],
            high_performance_tasks={},
            optimal_session_length=90,  # Default
            average_efficiency=np.mean(all_performances),
            consistency_score=consistency,
            sample_size=len(metrics)
        )
    
    def _detect_task_type_patterns(self, metrics: List[ProductivityMetric]) -> Optional[ProductivityPattern]:
        """タスクタイプパターン検出"""
        # Group by task type (need to match with tasks)
        task_type_performance = defaultdict(list)
        
        for metric in metrics:
            if metric.task_id and metric.task_id in self.tasks:
                task = self.tasks[metric.task_id]
                efficiency = metric.focus_efficiency * metric.time_efficiency
                task_type_performance[task.task_type].append(efficiency)
        
        if len(task_type_performance) < 2:
            return None
        
        # Calculate averages
        type_averages = {}
        for task_type, performances in task_type_performance.items():
            if len(performances) >= 3:
                type_averages[task_type] = sum(performances) / len(performances)
        
        if not type_averages:
            return None
        
        # Find preferred types
        sorted_types = sorted(type_averages.items(), key=lambda x: x[1], reverse=True)
        preferred_types = [task_type for task_type, perf in sorted_types[:3] if perf > 0.6]
        
        return ProductivityPattern(
            pattern_id=f"task_type_pattern_{int(datetime.now().timestamp())}",
            name="タスクタイプ生産性パターン",
            description=f"高効率タスクタイプ: {[t.value for t in preferred_types]}",
            optimal_periods=[],
            peak_hours=[],
            low_performance_hours=[],
            preferred_task_types=preferred_types,
            high_performance_tasks=type_averages,
            optimal_session_length=90,
            average_efficiency=np.mean(list(type_averages.values())),
            consistency_score=0.8,  # Placeholder
            sample_size=len(metrics)
        )
    
    def _detect_session_length_patterns(self, metrics: List[ProductivityMetric]) -> Optional[ProductivityPattern]:
        """セッション長パターン検出"""
        # Group by session length ranges
        length_performance = defaultdict(list)
        
        for metric in metrics:
            duration = metric.actual_duration
            efficiency = metric.focus_efficiency * metric.time_efficiency
            
            if duration <= 30:
                length_range = "short"
            elif duration <= 90:
                length_range = "medium"
            elif duration <= 180:
                length_range = "long"
            else:
                length_range = "very_long"
            
            length_performance[length_range].append(efficiency)
        
        # Find optimal length
        best_range = None
        best_performance = 0
        
        for length_range, performances in length_performance.items():
            if len(performances) >= 3:
                avg_performance = sum(performances) / len(performances)
                if avg_performance > best_performance:
                    best_performance = avg_performance
                    best_range = length_range
        
        if not best_range:
            return None
        
        # Map to actual session length
        optimal_lengths = {
            "short": 25,
            "medium": 60,
            "long": 90,
            "very_long": 120
        }
        
        return ProductivityPattern(
            pattern_id=f"session_length_pattern_{int(datetime.now().timestamp())}",
            name="セッション長生産性パターン",
            description=f"最適セッション長: {best_range} ({optimal_lengths[best_range]}分)",
            optimal_periods=[],
            peak_hours=[],
            low_performance_hours=[],
            preferred_task_types=[],
            high_performance_tasks={},
            optimal_session_length=optimal_lengths[best_range],
            average_efficiency=best_performance,
            consistency_score=0.7,
            sample_size=len(metrics)
        )
    
    def _detect_energy_patterns(self, metrics: List[ProductivityMetric]) -> Optional[ProductivityPattern]:
        """エネルギーレベルパターン検出"""
        # Analyze relationship between energy level and performance
        energy_performance = []
        
        for metric in metrics:
            efficiency = metric.focus_efficiency * metric.time_efficiency
            energy_performance.append((metric.energy_level, efficiency))
        
        if len(energy_performance) < 10:
            return None
        
        # Calculate correlation
        energies, performances = zip(*energy_performance)
        correlation = np.corrcoef(energies, performances)[0, 1] if len(energies) > 1 else 0
        
        if abs(correlation) < 0.3:  # Weak correlation
            return None
        
        # Find optimal energy range
        high_energy_performance = [perf for energy, perf in energy_performance if energy > 0.7]
        low_energy_performance = [perf for energy, perf in energy_performance if energy < 0.4]
        
        avg_high = sum(high_energy_performance) / len(high_energy_performance) if high_energy_performance else 0
        avg_low = sum(low_energy_performance) / len(low_energy_performance) if low_energy_performance else 0
        
        return ProductivityPattern(
            pattern_id=f"energy_pattern_{int(datetime.now().timestamp())}",
            name="エネルギーレベル生産性パターン",
            description=f"高エネルギー時効率: {avg_high:.1%}, 低エネルギー時効率: {avg_low:.1%}",
            optimal_periods=[],
            peak_hours=[],
            low_performance_hours=[],
            preferred_task_types=[],
            high_performance_tasks={},
            optimal_session_length=90,
            average_efficiency=np.mean(performances),
            consistency_score=abs(correlation),
            sample_size=len(metrics),
            productivity_factors={"energy_correlation": correlation}
        )
    
    def analyze_productivity_trends(self, days_back: int = 30) -> ProductivityTrend:
        """生産性トレンド分析"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        relevant_metrics = [m for m in self.productivity_metrics 
                          if m.timestamp >= cutoff_date]
        
        if len(relevant_metrics) < 7:  # Need at least a week of data
            return ProductivityTrend.STABLE
        
        # Group by day and calculate daily efficiency
        daily_efficiency = defaultdict(list)
        for metric in relevant_metrics:
            date_key = metric.timestamp.date()
            efficiency = metric.focus_efficiency * metric.time_efficiency
            daily_efficiency[date_key].append(efficiency)
        
        # Calculate daily averages
        daily_averages = []
        for date_key in sorted(daily_efficiency.keys()):
            avg_efficiency = sum(daily_efficiency[date_key]) / len(daily_efficiency[date_key])
            daily_averages.append(avg_efficiency)
        
        if len(daily_averages) < 5:
            return ProductivityTrend.STABLE
        
        # Calculate trend using linear regression
        x = np.arange(len(daily_averages))
        slope = np.polyfit(x, daily_averages, 1)[0]
        
        # Determine trend
        if slope > 0.01:
            return ProductivityTrend.IMPROVING
        elif slope < -0.01:
            return ProductivityTrend.DECLINING
        else:
            # Check for volatility
            volatility = np.std(daily_averages) / np.mean(daily_averages)
            if volatility > 0.3:
                return ProductivityTrend.VOLATILE
            else:
                return ProductivityTrend.STABLE
    
    def generate_insights(self, days_back: int = 30) -> List[ProductivityInsight]:
        """生産性インサイト生成"""
        insights = []
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        relevant_metrics = [m for m in self.productivity_metrics 
                          if m.timestamp >= cutoff_date]
        
        if not relevant_metrics:
            return insights
        
        # Efficiency insights
        avg_efficiency = np.mean([m.focus_efficiency * m.time_efficiency for m in relevant_metrics])
        if avg_efficiency < self.config["efficiency_benchmark"]:
            insights.append(ProductivityInsight(
                insight_id=f"efficiency_low_{int(datetime.now().timestamp())}",
                category="warning",
                title="効率性の低下",
                description=f"平均効率が基準値({self.config['efficiency_benchmark']:.1%})を下回っています ({avg_efficiency:.1%})",
                confidence=0.9,
                impact_score=0.8,
                actionable=True,
                recommendations=[
                    "より短いセッションでの作業を試してください",
                    "高集中時間帯での重要タスク実行を推奨します",
                    "作業環境の最適化を検討してください"
                ],
                supporting_data={"average_efficiency": avg_efficiency, "benchmark": self.config["efficiency_benchmark"]}
            ))
        
        # Time management insights
        time_overruns = [m for m in relevant_metrics if m.time_efficiency < 0.8]
        if len(time_overruns) > len(relevant_metrics) * 0.3:
            insights.append(ProductivityInsight(
                insight_id=f"time_overrun_{int(datetime.now().timestamp())}",
                category="pattern",
                title="時間見積もりの改善が必要",
                description=f"タスクの{len(time_overruns)/len(relevant_metrics):.1%}で時間超過が発生しています",
                confidence=0.8,
                impact_score=0.7,
                actionable=True,
                recommendations=[
                    "タスクの見積もり時間を20%増やしてください",
                    "複雑なタスクはより小さく分割してください",
                    "バッファー時間を設けてください"
                ],
                supporting_data={"overrun_rate": len(time_overruns)/len(relevant_metrics)}
            ))
        
        # Focus insights
        low_focus_sessions = [m for m in relevant_metrics if m.focus_efficiency < 0.6]
        if len(low_focus_sessions) > len(relevant_metrics) * 0.25:
            insights.append(ProductivityInsight(
                insight_id=f"focus_issue_{int(datetime.now().timestamp())}",
                category="optimization",
                title="集中力の改善機会",
                description=f"セッションの{len(low_focus_sessions)/len(relevant_metrics):.1%}で低い集中力が観測されました",
                confidence=0.7,
                impact_score=0.8,
                actionable=True,
                recommendations=[
                    "ポモドーロテクニックの導入を検討してください",
                    "作業前の準備時間を設けてください",
                    "妨害要因を特定し除去してください"
                ],
                supporting_data={"low_focus_rate": len(low_focus_sessions)/len(relevant_metrics)}
            ))
        
        # Pattern-based insights
        for pattern in self.patterns.values():
            if pattern.confidence_score > self.config["min_pattern_confidence"]:
                insights.append(ProductivityInsight(
                    insight_id=f"pattern_{pattern.pattern_id}",
                    category="pattern",
                    title=f"生産性パターン発見: {pattern.name}",
                    description=pattern.description,
                    confidence=pattern.confidence_score,
                    impact_score=0.6,
                    actionable=True,
                    recommendations=[
                        f"パターンに基づいてスケジュールを最適化してください",
                        f"高効率時間帯を最大限活用してください"
                    ],
                    supporting_data={"pattern": asdict(pattern)}
                ))
        
        # Store insights
        self.insights.extend(insights)
        
        logger.info(f"生産性インサイト生成: {len(insights)}件")
        return insights
    
    def generate_comprehensive_report(self, days_back: int = 30) -> ProductivityReport:
        """包括的生産性レポート生成"""
        period_end = datetime.now()
        period_start = period_end - timedelta(days=days_back)
        
        # Calculate metrics
        self.calculate_productivity_metrics(period_start, period_end)
        
        # Detect patterns
        patterns = self.detect_productivity_patterns(days_back)
        
        # Analyze trends
        trend = self.analyze_productivity_trends(days_back)
        
        # Generate insights
        insights = self.generate_insights(days_back)
        
        # Calculate summary metrics
        relevant_metrics = [m for m in self.productivity_metrics 
                          if period_start <= m.timestamp <= period_end]
        
        if relevant_metrics:
            total_work_hours = sum(m.actual_duration for m in relevant_metrics) / 60.0
            focused_work_hours = sum(m.focused_duration for m in relevant_metrics) / 60.0
            average_efficiency = np.mean([m.focus_efficiency * m.time_efficiency for m in relevant_metrics])
            completion_rates = [m.completion_quality for m in relevant_metrics if m.completion_quality > 0]
            task_completion_rate = np.mean(completion_rates) if completion_rates else 0.0
        else:
            total_work_hours = 0
            focused_work_hours = 0
            average_efficiency = 0
            task_completion_rate = 0
        
        # Generate recommendations
        optimization_opportunities = self._generate_optimization_recommendations(insights, patterns)
        time_management_suggestions = self._generate_time_management_suggestions(relevant_metrics)
        focus_improvement_suggestions = self._generate_focus_suggestions(relevant_metrics)
        
        report = ProductivityReport(
            report_id=f"productivity_report_{int(period_end.timestamp())}",
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.now(),
            total_work_hours=total_work_hours,
            focused_work_hours=focused_work_hours,
            average_efficiency=average_efficiency,
            task_completion_rate=task_completion_rate,
            productivity_trend=trend,
            trend_strength=0.5,  # Placeholder
            insights=insights,
            patterns=patterns,
            optimization_opportunities=optimization_opportunities,
            time_management_suggestions=time_management_suggestions,
            focus_improvement_suggestions=focus_improvement_suggestions
        )
        
        self.reports.append(report)
        
        logger.info(f"包括的生産性レポート生成完了: {report.report_id}")
        return report
    
    def _generate_optimization_recommendations(self, insights: List[ProductivityInsight], 
                                            patterns: List[ProductivityPattern]) -> List[str]:
        """最適化推奨事項生成"""
        recommendations = []
        
        # Pattern-based recommendations
        for pattern in patterns:
            if pattern.peak_hours:
                recommendations.append(f"最高効率時間帯({pattern.peak_hours}時台)での重要タスク実行")
            
            if pattern.preferred_task_types:
                task_names = [t.value for t in pattern.preferred_task_types]
                recommendations.append(f"高効率タスクタイプ({task_names})への集中")
            
            if pattern.optimal_session_length:
                recommendations.append(f"最適セッション長({pattern.optimal_session_length}分)の採用")
        
        # Insight-based recommendations
        high_impact_insights = [i for i in insights if i.impact_score > 0.7 and i.actionable]
        for insight in high_impact_insights[:3]:  # Top 3
            recommendations.extend(insight.recommendations[:2])  # Top 2 per insight
        
        return list(set(recommendations))[:10]  # Remove duplicates, limit to 10
    
    def _generate_time_management_suggestions(self, metrics: List[ProductivityMetric]) -> List[str]:
        """時間管理提案生成"""
        suggestions = []
        
        if not metrics:
            return suggestions
        
        # Time efficiency analysis
        avg_time_efficiency = np.mean([m.time_efficiency for m in metrics])
        if avg_time_efficiency < 0.8:
            suggestions.append("タスク見積もり精度の改善が必要です")
            suggestions.append("タスクを小さく分割してより正確な見積もりを行ってください")
        
        # Planning vs execution analysis
        overestimated = [m for m in metrics if m.time_efficiency > 1.2]
        underestimated = [m for m in metrics if m.time_efficiency < 0.7]
        
        if len(overestimated) > len(underestimated):
            suggestions.append("時間見積もりが過大な傾向があります。空いた時間を追加タスクに活用してください")
        elif len(underestimated) > len(overestimated):
            suggestions.append("時間見積もりが過小な傾向があります。バッファー時間を設けてください")
        
        # Session length optimization
        long_sessions = [m for m in metrics if m.actual_duration > 120]
        if len(long_sessions) > len(metrics) * 0.3:
            suggestions.append("長時間セッションが多いです。休憩を挟んでセッションを分割してください")
        
        return suggestions[:5]  # Limit to 5
    
    def _generate_focus_suggestions(self, metrics: List[ProductivityMetric]) -> List[str]:
        """集中改善提案生成"""
        suggestions = []
        
        if not metrics:
            return suggestions
        
        # Focus efficiency analysis
        avg_focus = np.mean([m.focus_efficiency for m in metrics])
        if avg_focus < self.config["focus_benchmark"]:
            suggestions.append("集中力改善のためのテクニック導入を推奨します")
            suggestions.append("作業環境の最適化（照明、騒音、整理整頓）を検討してください")
        
        # Interruption analysis
        high_interruption = [m for m in metrics if m.interruption_count > 3]
        if len(high_interruption) > len(metrics) * 0.2:
            suggestions.append("中断要因の特定と除去が必要です")
            suggestions.append("集中時間中の通知オフやドアクローズドポリシーを導入してください")
        
        # Energy level analysis
        low_energy = [m for m in metrics if m.energy_level < 0.4]
        if len(low_energy) > len(metrics) * 0.3:
            suggestions.append("エネルギー管理の改善が必要です")
            suggestions.append("十分な睡眠、適度な運動、栄養管理を見直してください")
        
        return suggestions[:5]  # Limit to 5
    
    def visualize_productivity_dashboard(self, days_back: int = 30, save_path: str = None) -> str:
        """生産性ダッシュボード可視化"""
        if not HAS_VISUALIZATION:
            return "visualization libraries not available"
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        relevant_metrics = [m for m in self.productivity_metrics 
                          if m.timestamp >= cutoff_date]
        
        if len(relevant_metrics) < 5:
            return "データ不足"
        
        # Create dashboard
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Daily efficiency trend
        daily_efficiency = defaultdict(list)
        for metric in relevant_metrics:
            date_key = metric.timestamp.date()
            efficiency = metric.focus_efficiency * metric.time_efficiency
            daily_efficiency[date_key].append(efficiency)
        
        dates = sorted(daily_efficiency.keys())
        daily_averages = [sum(daily_efficiency[date]) / len(daily_efficiency[date]) for date in dates]
        
        axes[0, 0].plot(dates, daily_averages, marker='o', linewidth=2)
        axes[0, 0].set_title('日次効率トレンド')
        axes[0, 0].set_ylabel('効率スコア')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Hourly performance heatmap
        hourly_performance = defaultdict(list)
        for metric in relevant_metrics:
            hour = metric.timestamp.hour
            efficiency = metric.focus_efficiency * metric.time_efficiency
            hourly_performance[hour].append(efficiency)
        
        hour_matrix = []
        for hour in range(24):
            if hour in hourly_performance and hourly_performance[hour]:
                hour_matrix.append(sum(hourly_performance[hour]) / len(hourly_performance[hour]))
            else:
                hour_matrix.append(0)
        
        # Reshape for heatmap (4x6 grid)
        hour_matrix_2d = np.array(hour_matrix).reshape(4, 6)
        im = axes[0, 1].imshow(hour_matrix_2d, cmap='YlOrRd', aspect='auto')
        axes[0, 1].set_title('時間帯別効率ヒートマップ')
        plt.colorbar(im, ax=axes[0, 1])
        
        # 3. Task complexity vs efficiency scatter
        complexities = [m.task_complexity for m in relevant_metrics]
        efficiencies = [m.focus_efficiency * m.time_efficiency for m in relevant_metrics]
        
        axes[1, 0].scatter(complexities, efficiencies, alpha=0.6)
        axes[1, 0].set_xlabel('タスク複雑度')
        axes[1, 0].set_ylabel('効率スコア')
        axes[1, 0].set_title('複雑度vs効率の関係')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Focus efficiency distribution
        focus_efficiencies = [m.focus_efficiency for m in relevant_metrics]
        axes[1, 1].hist(focus_efficiencies, bins=20, alpha=0.7, color='skyblue')
        axes[1, 1].axvline(np.mean(focus_efficiencies), color='red', linestyle='--', 
                          label=f'平均: {np.mean(focus_efficiencies):.2f}')
        axes[1, 1].set_xlabel('集中効率')
        axes[1, 1].set_ylabel('頻度')
        axes[1, 1].set_title('集中効率分布')
        axes[1, 1].legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"生産性ダッシュボード保存: {save_path}")
            return save_path
        else:
            plt.show()
            return "Dashboard displayed"

# 使用例・デモ
if __name__ == "__main__":
    # ProductivityAnalyzer デモ
    analyzer = ProductivityAnalyzer()
    
    # サンプルデータ作成
    from datetime import datetime, timedelta
    import random
    
    # Sample tasks
    sample_tasks = {}
    for i in range(20):
        task_id = f"task_{i:03d}"
        task = ResearchTask(
            task_id=task_id,
            title=f"Research Task {i+1}",
            description=f"Description for task {i+1}",
            task_type=random.choice(list(TaskType)),
            priority=random.choice(list(TaskPriority)),
            estimated_duration=random.randint(30, 180),
            created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
            completed_duration=random.randint(25, 200),
            completion_ratio=random.uniform(0.6, 1.0)
        )
        sample_tasks[task_id] = task
    
    # Sample focus sessions
    sample_sessions = []
    for i in range(15):
        session = FocusSession(
            session_id=f"session_{i:03d}",
            start_time=datetime.now() - timedelta(days=random.randint(1, 30)),
            end_time=datetime.now() - timedelta(days=random.randint(1, 30)) + timedelta(minutes=random.randint(45, 120)),
            task_id=f"task_{random.randint(0, 19):03d}",
            total_duration=random.randint(2700, 7200),  # 45-120 minutes in seconds
            focused_duration=random.randint(2000, 6000),
            distraction_count=random.randint(0, 5),
            average_focus_level=random.uniform(2.0, 4.0)
        )
        sample_sessions.append(session)
    
    # Add data to analyzer
    analyzer.add_task_data(sample_tasks)
    analyzer.add_focus_data(sample_sessions)
    
    print("=== Productivity Analyzer Demo ===")
    
    # Calculate metrics
    analyzer.calculate_productivity_metrics()
    print(f"Generated productivity metrics: {len(analyzer.productivity_metrics)}")
    
    # Detect patterns
    patterns = analyzer.detect_productivity_patterns()
    print(f"Detected patterns: {len(patterns)}")
    for pattern in patterns:
        print(f"- {pattern.name}: {pattern.description}")
    
    # Analyze trends
    trend = analyzer.analyze_productivity_trends()
    print(f"Productivity trend: {trend.value}")
    
    # Generate insights
    insights = analyzer.generate_insights()
    print(f"Generated insights: {len(insights)}")
    for insight in insights[:3]:  # Show first 3
        print(f"- {insight.title}: {insight.description}")
    
    # Generate comprehensive report
    report = analyzer.generate_comprehensive_report()
    print(f"\n--- Comprehensive Report ---")
    print(f"Period: {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}")
    print(f"Total work hours: {report.total_work_hours:.1f}")
    print(f"Focused work hours: {report.focused_work_hours:.1f}")
    print(f"Average efficiency: {report.average_efficiency:.1%}")
    print(f"Task completion rate: {report.task_completion_rate:.1%}")
    print(f"Productivity trend: {report.productivity_trend.value}")
    
    print(f"\nOptimization opportunities ({len(report.optimization_opportunities)}):")
    for opp in report.optimization_opportunities[:3]:
        print(f"- {opp}")
    
    print(f"\nTime management suggestions ({len(report.time_management_suggestions)}):")
    for suggestion in report.time_management_suggestions[:3]:
        print(f"- {suggestion}")
    
    logger.info("生産性分析システム デモ完了")