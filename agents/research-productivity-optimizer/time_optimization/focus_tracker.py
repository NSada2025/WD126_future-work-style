#!/usr/bin/env python3
"""
Focus Tracker - 集中度追跡システム

リアルタイム集中度測定・分析・最適化提案を行う
研究効率10倍化を実現するフォーカス管理エンジン
"""

import json
import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import logging

# Optional imports for advanced features
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

logger = logging.getLogger(__name__)

class FocusLevel(Enum):
    """集中レベル"""
    DEEP_FOCUS = 4      # 深い集中状態
    FOCUSED = 3         # 集中状態
    NORMAL = 2          # 普通状態
    DISTRACTED = 1      # 散漫状態
    UNFOCUSED = 0       # 非集中状態

class DistractionType(Enum):
    """妨害タイプ"""
    NOTIFICATION = "notification"       # 通知
    TASK_SWITCHING = "task_switching"   # タスク切り替え
    BREAK = "break"                     # 休憩
    INTERRUPTION = "interruption"       # 外部中断
    MENTAL_FATIGUE = "mental_fatigue"   # 精神的疲労
    PHYSICAL_DISCOMFORT = "physical"    # 身体的不快感

@dataclass
class FocusMetric:
    """集中度指標"""
    timestamp: datetime
    focus_level: FocusLevel
    attention_duration: int     # seconds of continuous attention
    task_id: Optional[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class DistractionEvent:
    """妨害イベント"""
    event_id: str
    timestamp: datetime
    distraction_type: DistractionType
    duration: int               # seconds
    severity: int              # 1-5 scale
    source: str                # Source of distraction
    impact_on_focus: float     # Impact score 0.0-1.0
    recovery_time: int = 0     # seconds to recover focus
    task_id: Optional[str] = None

@dataclass
class FocusSession:
    """集中セッション"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    task_id: Optional[str] = None
    
    # Session metrics
    total_duration: int = 0              # Total session seconds
    focused_duration: int = 0            # Actual focused seconds
    distraction_count: int = 0           # Number of distractions
    average_focus_level: float = 0.0     # Average focus level
    peak_focus_duration: int = 0         # Longest continuous focus
    
    # Flow state indicators
    entered_flow: bool = False
    flow_duration: int = 0               # Time in flow state
    flow_interruptions: int = 0          # Number of flow breaks
    
    @property
    def focus_efficiency(self) -> float:
        """集中効率"""
        if self.total_duration == 0:
            return 0.0
        return self.focused_duration / self.total_duration
    
    @property
    def distraction_rate(self) -> float:
        """妨害率（妨害/時間）"""
        if self.total_duration == 0:
            return 0.0
        return (self.distraction_count * 3600) / self.total_duration  # per hour

@dataclass
class FlowState:
    """フロー状態"""
    is_in_flow: bool = False
    flow_start_time: Optional[datetime] = None
    flow_duration: int = 0
    flow_intensity: float = 0.0         # 0.0-1.0
    challenge_skill_balance: float = 0.5 # Balance indicator
    
    # Flow conditions
    clear_goals: bool = False
    immediate_feedback: bool = False
    concentration_level: float = 0.0
    self_consciousness: float = 1.0     # Lower is better for flow
    time_distortion: bool = False

class FocusTracker:
    """集中度追跡システム"""
    
    def __init__(self, measurement_interval: int = 30):
        self.measurement_interval = measurement_interval  # seconds
        self.is_tracking = False
        self.current_session: Optional[FocusSession] = None
        self.flow_state = FlowState()
        
        # Data storage
        self.focus_metrics: deque = deque(maxlen=10000)  # Last 10k measurements
        self.distraction_events: List[DistractionEvent] = []
        self.completed_sessions: List[FocusSession] = []
        
        # Real-time tracking
        self.tracking_thread: Optional[threading.Thread] = None
        self.last_activity_time = datetime.now()
        self.activity_buffer: deque = deque(maxlen=120)  # 2 minutes buffer
        
        # Configuration
        self.config = {
            "flow_threshold": 3.5,          # Focus level to enter flow
            "flow_maintenance_threshold": 3.0,  # Minimum to maintain flow
            "distraction_recovery_threshold": 2.5,  # Focus level after distraction
            "inactivity_threshold": 300,     # Seconds before considering inactive
            "focus_measurement_window": 60,  # Seconds to average focus
            "notification_threshold": 0.7,  # Threshold for focus alerts
            "deep_work_target": 2700,      # Target deep work seconds per day (45 min)
            "break_recommendation_interval": 5400  # Recommend break every 90 min
        }
        
        # Analytics
        self.daily_stats: Dict[str, Dict] = defaultdict(dict)
        
    def start_tracking_session(self, task_id: str = None) -> str:
        """集中追跡セッション開始"""
        session_id = f"session_{int(datetime.now().timestamp())}"
        
        # End current session if exists
        if self.current_session and not self.current_session.end_time:
            self.end_tracking_session()
        
        # Start new session
        self.current_session = FocusSession(
            session_id=session_id,
            start_time=datetime.now(),
            task_id=task_id
        )
        
        # Reset flow state
        self.flow_state = FlowState()
        
        # Start background tracking
        self.is_tracking = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
        
        logger.info(f"集中追跡開始: {session_id}")
        return session_id
    
    def end_tracking_session(self) -> Optional[FocusSession]:
        """集中追跡セッション終了"""
        if not self.current_session:
            return None
        
        # Stop tracking
        self.is_tracking = False
        if self.tracking_thread:
            self.tracking_thread.join(timeout=1.0)
        
        # Finalize session
        session = self.current_session
        session.end_time = datetime.now()
        session.total_duration = int((session.end_time - session.start_time).total_seconds())
        
        # Calculate session metrics
        self._calculate_session_metrics(session)
        
        # Store completed session
        self.completed_sessions.append(session)
        self.current_session = None
        
        logger.info(f"集中追跡終了: {session.session_id}, 効率: {session.focus_efficiency:.1%}")
        return session
    
    def _tracking_loop(self):
        """バックグラウンド追跡ループ"""
        while self.is_tracking:
            try:
                # Measure current focus
                focus_metric = self._measure_current_focus()
                if focus_metric:
                    self.focus_metrics.append(focus_metric)
                    
                    # Update flow state
                    self._update_flow_state(focus_metric)
                    
                    # Check for alerts
                    self._check_focus_alerts(focus_metric)
                
                # Sleep until next measurement
                time.sleep(self.measurement_interval)
                
            except Exception as e:
                logger.error(f"追跡ループエラー: {e}")
                break
    
    def _measure_current_focus(self) -> Optional[FocusMetric]:
        """現在の集中度測定"""
        # Simulate focus measurement (in real implementation, this would use various inputs)
        
        # Time-based focus simulation
        current_time = datetime.now()
        
        # Check for recent activity
        seconds_since_last_activity = (current_time - self.last_activity_time).total_seconds()
        
        if seconds_since_last_activity > self.config["inactivity_threshold"]:
            focus_level = FocusLevel.UNFOCUSED
        else:
            # Simulate focus level based on session duration and patterns
            if self.current_session:
                session_duration = (current_time - self.current_session.start_time).total_seconds()
                
                # Focus tends to peak after some warmup and decline with fatigue
                if session_duration < 300:  # First 5 minutes - warming up
                    focus_probability = session_duration / 300
                elif session_duration < 2700:  # 5-45 minutes - peak focus possible
                    focus_probability = 0.8 + 0.2 * (1 - (session_duration - 300) / 2400)
                else:  # After 45 minutes - fatigue sets in
                    focus_probability = max(0.3, 0.8 - (session_duration - 2700) / 3600)
                
                # Simulate focus level
                import random
                random_factor = random.random()
                
                if random_factor < focus_probability * 0.1:
                    focus_level = FocusLevel.DEEP_FOCUS
                elif random_factor < focus_probability * 0.4:
                    focus_level = FocusLevel.FOCUSED
                elif random_factor < focus_probability * 0.7:
                    focus_level = FocusLevel.NORMAL
                elif random_factor < focus_probability * 0.9:
                    focus_level = FocusLevel.DISTRACTED
                else:
                    focus_level = FocusLevel.UNFOCUSED
            else:
                focus_level = FocusLevel.NORMAL
        
        # Calculate attention duration
        if len(self.focus_metrics) > 0 and self.focus_metrics[-1].focus_level.value >= 2:
            attention_duration = (current_time - self.focus_metrics[-1].timestamp).total_seconds()
        else:
            attention_duration = 0
        
        return FocusMetric(
            timestamp=current_time,
            focus_level=focus_level,
            attention_duration=int(attention_duration),
            task_id=self.current_session.task_id if self.current_session else None,
            context={
                "session_duration": int((current_time - self.current_session.start_time).total_seconds()) if self.current_session else 0,
                "is_in_flow": self.flow_state.is_in_flow
            }
        )
    
    def _update_flow_state(self, metric: FocusMetric):
        """フロー状態更新"""
        current_focus = metric.focus_level.value
        
        # Check for flow entry
        if not self.flow_state.is_in_flow and current_focus >= self.config["flow_threshold"]:
            self.flow_state.is_in_flow = True
            self.flow_state.flow_start_time = metric.timestamp
            self.flow_state.flow_intensity = (current_focus - 2) / 2  # Normalize to 0-1
            
            if self.current_session:
                self.current_session.entered_flow = True
            
            logger.info("フロー状態に入りました")
        
        # Update flow state while in flow
        elif self.flow_state.is_in_flow:
            if current_focus >= self.config["flow_maintenance_threshold"]:
                # Maintain flow
                self.flow_state.flow_duration = int((metric.timestamp - self.flow_state.flow_start_time).total_seconds())
                self.flow_state.flow_intensity = max(self.flow_state.flow_intensity, (current_focus - 2) / 2)
            else:
                # Exit flow
                self.flow_state.is_in_flow = False
                if self.current_session:
                    self.current_session.flow_duration += self.flow_state.flow_duration
                    self.current_session.flow_interruptions += 1
                
                logger.info(f"フロー状態終了 (継続時間: {self.flow_state.flow_duration}秒)")
    
    def _check_focus_alerts(self, metric: FocusMetric):
        """集中アラート確認"""
        # Check for prolonged low focus
        if metric.focus_level.value <= 1:
            recent_metrics = [m for m in list(self.focus_metrics)[-5:] 
                            if (metric.timestamp - m.timestamp).total_seconds() < 300]
            
            if len(recent_metrics) >= 3 and all(m.focus_level.value <= 1 for m in recent_metrics):
                self._trigger_focus_alert("prolonged_low_focus", 
                                        "Focus has been low for an extended period")
        
        # Check for break recommendation
        if self.current_session:
            session_duration = (metric.timestamp - self.current_session.start_time).total_seconds()
            if session_duration > self.config["break_recommendation_interval"]:
                self._trigger_focus_alert("break_recommendation",
                                        "Consider taking a break to maintain focus")
    
    def _trigger_focus_alert(self, alert_type: str, message: str):
        """集中アラート発火"""
        logger.warning(f"Focus Alert [{alert_type}]: {message}")
        # In real implementation, this could send notifications, play sounds, etc.
    
    def _calculate_session_metrics(self, session: FocusSession):
        """セッションメトリクス計算"""
        if not session or session.total_duration == 0:
            return
        
        # Get metrics for this session
        session_metrics = [m for m in self.focus_metrics 
                          if session.start_time <= m.timestamp <= (session.end_time or datetime.now())]
        
        if not session_metrics:
            return
        
        # Calculate focused duration
        focused_time = sum(self.measurement_interval for m in session_metrics 
                          if m.focus_level.value >= 2)
        session.focused_duration = min(focused_time, session.total_duration)
        
        # Calculate average focus level
        session.average_focus_level = sum(m.focus_level.value for m in session_metrics) / len(session_metrics)
        
        # Calculate peak focus duration
        current_peak = 0
        max_peak = 0
        for metric in session_metrics:
            if metric.focus_level.value >= 3:
                current_peak += self.measurement_interval
                max_peak = max(max_peak, current_peak)
            else:
                current_peak = 0
        session.peak_focus_duration = max_peak
        
        # Count distractions in this session
        session_distractions = [d for d in self.distraction_events
                              if session.start_time <= d.timestamp <= (session.end_time or datetime.now())]
        session.distraction_count = len(session_distractions)
    
    def record_distraction(self, distraction_type: DistractionType, 
                          duration: int, severity: int = 3,
                          source: str = "unknown") -> str:
        """妨害記録"""
        event_id = f"distraction_{int(datetime.now().timestamp())}"
        
        # Calculate impact based on current focus and severity
        impact = min(1.0, (severity / 5.0) * 0.8)
        
        # Estimate recovery time based on distraction type and severity
        recovery_time = {
            DistractionType.NOTIFICATION: duration * 2,
            DistractionType.TASK_SWITCHING: duration * 3,
            DistractionType.INTERRUPTION: duration * 4,
            DistractionType.BREAK: 0,  # Breaks are good
            DistractionType.MENTAL_FATIGUE: duration * 5,
            DistractionType.PHYSICAL_DISCOMFORT: duration * 2
        }.get(distraction_type, duration * 2)
        
        event = DistractionEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            distraction_type=distraction_type,
            duration=duration,
            severity=severity,
            source=source,
            impact_on_focus=impact,
            recovery_time=recovery_time,
            task_id=self.current_session.task_id if self.current_session else None
        )
        
        self.distraction_events.append(event)
        
        # Update flow state if in flow
        if self.flow_state.is_in_flow and severity >= 3:
            self.flow_state.is_in_flow = False
            if self.current_session:
                self.current_session.flow_interruptions += 1
        
        logger.info(f"妨害記録: {distraction_type.value} ({duration}秒, 重要度{severity})")
        return event_id
    
    def simulate_activity(self):
        """活動シミュレート（実装では実際のユーザー活動を検知）"""
        self.last_activity_time = datetime.now()
    
    def get_focus_analysis(self, hours_back: int = 24) -> Dict[str, Any]:
        """集中分析取得"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Filter recent metrics and sessions
        recent_metrics = [m for m in self.focus_metrics if m.timestamp >= cutoff_time]
        recent_sessions = [s for s in self.completed_sessions 
                          if s.start_time >= cutoff_time]
        recent_distractions = [d for d in self.distraction_events 
                             if d.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {"message": "データ不足"}
        
        # Calculate focus statistics
        focus_levels = [m.focus_level.value for m in recent_metrics]
        avg_focus = sum(focus_levels) / len(focus_levels)
        peak_focus_ratio = sum(1 for f in focus_levels if f >= 3) / len(focus_levels)
        
        # Session statistics
        if recent_sessions:
            avg_efficiency = sum(s.focus_efficiency for s in recent_sessions) / len(recent_sessions)
            total_focused_time = sum(s.focused_duration for s in recent_sessions)
            avg_session_length = sum(s.total_duration for s in recent_sessions) / len(recent_sessions)
            flow_sessions = sum(1 for s in recent_sessions if s.entered_flow)
        else:
            avg_efficiency = 0
            total_focused_time = 0
            avg_session_length = 0
            flow_sessions = 0
        
        # Distraction analysis
        distraction_types = defaultdict(int)
        total_distraction_time = 0
        for d in recent_distractions:
            distraction_types[d.distraction_type.value] += 1
            total_distraction_time += d.duration
        
        # Peak performance times
        hourly_focus = defaultdict(list)
        for metric in recent_metrics:
            hour = metric.timestamp.hour
            hourly_focus[hour].append(metric.focus_level.value)
        
        peak_hours = []
        for hour, values in hourly_focus.items():
            if values and sum(values) / len(values) >= 3.0:
                peak_hours.append(hour)
        
        return {
            "analysis_period_hours": hours_back,
            "total_measurements": len(recent_metrics),
            "average_focus_level": avg_focus,
            "peak_focus_ratio": peak_focus_ratio,
            "total_sessions": len(recent_sessions),
            "average_session_efficiency": avg_efficiency,
            "total_focused_minutes": total_focused_time // 60,
            "average_session_minutes": avg_session_length // 60,
            "flow_sessions_count": flow_sessions,
            "total_distractions": len(recent_distractions),
            "distraction_breakdown": dict(distraction_types),
            "total_distraction_minutes": total_distraction_time // 60,
            "peak_performance_hours": sorted(peak_hours),
            "focus_improvement_target": max(0, 3.5 - avg_focus),
            "recommended_session_length": min(90, max(30, avg_session_length // 60)) if recent_sessions else 45
        }
    
    def get_real_time_status(self) -> Dict[str, Any]:
        """リアルタイムステータス取得"""
        current_metric = self.focus_metrics[-1] if self.focus_metrics else None
        
        status = {
            "is_tracking": self.is_tracking,
            "current_session_id": self.current_session.session_id if self.current_session else None,
            "current_focus_level": current_metric.focus_level.name if current_metric else "UNKNOWN",
            "is_in_flow": self.flow_state.is_in_flow,
            "flow_duration_minutes": self.flow_state.flow_duration // 60,
            "session_duration_minutes": 0,
            "session_efficiency": 0.0
        }
        
        if self.current_session:
            session_duration = (datetime.now() - self.current_session.start_time).total_seconds()
            status["session_duration_minutes"] = int(session_duration // 60)
            
            if session_duration > 0:
                # Calculate current efficiency
                session_metrics = [m for m in self.focus_metrics 
                                 if m.timestamp >= self.current_session.start_time]
                if session_metrics:
                    focused_measurements = sum(1 for m in session_metrics if m.focus_level.value >= 2)
                    status["session_efficiency"] = focused_measurements / len(session_metrics)
        
        return status
    
    def generate_focus_report(self, days_back: int = 7) -> Dict[str, Any]:
        """集中レポート生成"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Filter data
        relevant_sessions = [s for s in self.completed_sessions if s.start_time >= cutoff_date]
        relevant_distractions = [d for d in self.distraction_events if d.timestamp >= cutoff_date]
        
        if not relevant_sessions:
            return {"message": "分析期間にセッションデータがありません"}
        
        # Daily breakdown
        daily_stats = defaultdict(lambda: {
            "sessions": 0,
            "total_time": 0,
            "focused_time": 0,
            "efficiency": 0.0,
            "flow_sessions": 0,
            "distractions": 0
        })
        
        for session in relevant_sessions:
            date_key = session.start_time.strftime("%Y-%m-%d")
            stats = daily_stats[date_key]
            
            stats["sessions"] += 1
            stats["total_time"] += session.total_duration
            stats["focused_time"] += session.focused_duration
            stats["efficiency"] = stats["focused_time"] / stats["total_time"] if stats["total_time"] > 0 else 0
            if session.entered_flow:
                stats["flow_sessions"] += 1
        
        for distraction in relevant_distractions:
            date_key = distraction.timestamp.strftime("%Y-%m-%d")
            daily_stats[date_key]["distractions"] += 1
        
        # Overall statistics
        total_sessions = len(relevant_sessions)
        total_time = sum(s.total_duration for s in relevant_sessions)
        total_focused = sum(s.focused_duration for s in relevant_sessions)
        average_efficiency = total_focused / total_time if total_time > 0 else 0
        flow_rate = sum(1 for s in relevant_sessions if s.entered_flow) / total_sessions
        
        # Trends
        daily_efficiencies = []
        for date_key in sorted(daily_stats.keys()):
            daily_efficiencies.append(daily_stats[date_key]["efficiency"])
        
        if len(daily_efficiencies) > 1:
            trend = "improving" if daily_efficiencies[-1] > daily_efficiencies[0] else "declining"
        else:
            trend = "stable"
        
        return {
            "analysis_period": f"{days_back} days",
            "total_sessions": total_sessions,
            "total_hours": total_time / 3600,
            "total_focused_hours": total_focused / 3600,
            "average_efficiency": average_efficiency,
            "flow_achievement_rate": flow_rate,
            "total_distractions": len(relevant_distractions),
            "daily_breakdown": dict(daily_stats),
            "efficiency_trend": trend,
            "recommendations": self._generate_focus_recommendations(relevant_sessions, relevant_distractions)
        }
    
    def _generate_focus_recommendations(self, sessions: List[FocusSession], 
                                      distractions: List[DistractionEvent]) -> List[str]:
        """集中改善提案生成"""
        recommendations = []
        
        if not sessions:
            return ["データ不足のため提案できません"]
        
        # Efficiency recommendations
        avg_efficiency = sum(s.focus_efficiency for s in sessions) / len(sessions)
        if avg_efficiency < 0.6:
            recommendations.append("集中効率が低下しています。より短いセッションから始めることを推奨します")
        
        # Session length recommendations
        avg_session_length = sum(s.total_duration for s in sessions) / len(sessions) / 60
        if avg_session_length > 120:
            recommendations.append("セッションが長すぎます。90分以下に短縮することを推奨します")
        elif avg_session_length < 30:
            recommendations.append("セッションが短すぎます。45-90分の長さを推奨します")
        
        # Flow state recommendations
        flow_rate = sum(1 for s in sessions if s.entered_flow) / len(sessions)
        if flow_rate < 0.3:
            recommendations.append("フロー状態への入りが少ないです。環境の整備と集中技法の練習を推奨します")
        
        # Distraction recommendations
        if distractions:
            distraction_types = defaultdict(int)
            for d in distractions:
                distraction_types[d.distraction_type] += 1
            
            most_common = max(distraction_types.items(), key=lambda x: x[1])
            if most_common[0] == DistractionType.NOTIFICATION:
                recommendations.append("通知による中断が多いです。集中時間中は通知をオフにすることを推奨します")
            elif most_common[0] == DistractionType.TASK_SWITCHING:
                recommendations.append("タスク切り替えが多いです。一つのタスクに集中することを推奨します")
        
        # Peak time recommendations
        hourly_efficiency = defaultdict(list)
        for session in sessions:
            start_hour = session.start_time.hour
            hourly_efficiency[start_hour].append(session.focus_efficiency)
        
        best_hours = []
        for hour, efficiencies in hourly_efficiency.items():
            if efficiencies and sum(efficiencies) / len(efficiencies) > 0.7:
                best_hours.append(hour)
        
        if best_hours:
            recommendations.append(f"最も集中しやすい時間帯: {sorted(best_hours)}時台での作業を推奨します")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def visualize_focus_pattern(self, days_back: int = 7, save_path: str = None) -> str:
        """集中パターン可視化"""
        if not HAS_MATPLOTLIB:
            return "matplotlib not available - visualization skipped"
        
        cutoff_time = datetime.now() - timedelta(days=days_back)
        recent_metrics = [m for m in self.focus_metrics if m.timestamp >= cutoff_time]
        
        if len(recent_metrics) < 10:
            return "データ不足"
        
        # Prepare data
        timestamps = [m.timestamp for m in recent_metrics]
        focus_values = [m.focus_level.value for m in recent_metrics]
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Focus level over time
        ax1.plot(timestamps, focus_values, marker='o', markersize=3, alpha=0.7)
        ax1.set_title('集中レベルの時系列変化')
        ax1.set_ylabel('集中レベル')
        ax1.set_ylim(0, 4)
        ax1.grid(True, alpha=0.3)
        
        # Add flow state regions
        flow_periods = []
        current_flow_start = None
        for i, metric in enumerate(recent_metrics):
            if metric.context.get('is_in_flow') and current_flow_start is None:
                current_flow_start = i
            elif not metric.context.get('is_in_flow') and current_flow_start is not None:
                flow_periods.append((current_flow_start, i))
                current_flow_start = None
        
        for start_idx, end_idx in flow_periods:
            ax1.axvspan(timestamps[start_idx], timestamps[end_idx], 
                       alpha=0.3, color='green', label='Flow State')
        
        # Hourly focus distribution
        hourly_focus = defaultdict(list)
        for metric in recent_metrics:
            hourly_focus[metric.timestamp.hour].append(metric.focus_level.value)
        
        hours = sorted(hourly_focus.keys())
        avg_focus_by_hour = [sum(hourly_focus[h]) / len(hourly_focus[h]) for h in hours]
        
        ax2.bar(hours, avg_focus_by_hour, alpha=0.7, color='skyblue')
        ax2.set_title('時間帯別平均集中レベル')
        ax2.set_xlabel('時間')
        ax2.set_ylabel('平均集中レベル')
        ax2.set_ylim(0, 4)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"集中パターン可視化保存: {save_path}")
            return save_path
        else:
            plt.show()
            return "Graph displayed"
    
    def export_focus_data(self, filepath: str, format: str = "json"):
        """集中データエクスポート"""
        export_data = {
            "export_time": datetime.now().isoformat(),
            "config": self.config,
            "completed_sessions": [asdict(s) for s in self.completed_sessions],
            "distraction_events": [asdict(d) for d in self.distraction_events],
            "focus_metrics": [asdict(m) for m in list(self.focus_metrics)[-1000:]]  # Last 1000
        }
        
        if format.lower() == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"集中データエクスポート: {filepath}")

# 使用例・デモ
if __name__ == "__main__":
    # FocusTracker デモ
    tracker = FocusTracker(measurement_interval=5)  # 5 second intervals for demo
    
    print("=== Focus Tracker Demo ===")
    
    # Start tracking session
    session_id = tracker.start_tracking_session("research_task_001")
    print(f"Tracking session started: {session_id}")
    
    # Simulate focus session
    import random
    for i in range(20):  # 20 measurements
        # Simulate activity
        tracker.simulate_activity()
        
        # Occasionally record distractions
        if random.random() < 0.15:  # 15% chance of distraction
            distraction_types = list(DistractionType)
            selected_type = random.choice(distraction_types)
            duration = random.randint(30, 180)
            severity = random.randint(1, 5)
            
            tracker.record_distraction(selected_type, duration, severity)
        
        # Sleep to simulate real time
        time.sleep(1)
        
        # Show real-time status occasionally
        if i % 5 == 0:
            status = tracker.get_real_time_status()
            print(f"Status: Focus={status['current_focus_level']}, "
                  f"Flow={status['is_in_flow']}, "
                  f"Duration={status['session_duration_minutes']}min, "
                  f"Efficiency={status['session_efficiency']:.1%}")
    
    # End session
    completed_session = tracker.end_tracking_session()
    if completed_session:
        print(f"\nSession completed:")
        print(f"- Duration: {completed_session.total_duration}s")
        print(f"- Focus efficiency: {completed_session.focus_efficiency:.1%}")
        print(f"- Peak focus duration: {completed_session.peak_focus_duration}s")
        print(f"- Distractions: {completed_session.distraction_count}")
        print(f"- Entered flow: {completed_session.entered_flow}")
    
    # Analysis
    analysis = tracker.get_focus_analysis(hours_back=1)
    print(f"\nFocus Analysis:")
    print(f"- Average focus level: {analysis['average_focus_level']:.2f}")
    print(f"- Peak focus ratio: {analysis['peak_focus_ratio']:.1%}")
    print(f"- Total focused minutes: {analysis['total_focused_minutes']}")
    print(f"- Total distractions: {analysis['total_distractions']}")
    
    # Generate report
    report = tracker.generate_focus_report(days_back=1)
    print(f"\nFocus Report:")
    print(f"- Total sessions: {report['total_sessions']}")
    print(f"- Average efficiency: {report['average_efficiency']:.1%}")
    print(f"- Flow achievement rate: {report['flow_achievement_rate']:.1%}")
    
    if report.get('recommendations'):
        print(f"- Recommendations:")
        for rec in report['recommendations'][:3]:
            print(f"  • {rec}")
    
    logger.info("集中追跡システム デモ完了")