#!/usr/bin/env python3
"""
Schedule Optimizer - 研究スケジュール最適化システム

個人の生産性パターン・タスク特性・締切を考慮した
最適な研究スケジュールを自動生成・動的調整する
"""

import json
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, time
from enum import Enum
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """タスク優先度"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    OPTIONAL = 1

class TaskType(Enum):
    """タスクタイプ"""
    RESEARCH = "research"           # 研究・調査
    WRITING = "writing"             # 論文執筆
    ANALYSIS = "analysis"           # データ分析
    CODING = "coding"               # プログラミング
    READING = "reading"             # 文献読解
    MEETING = "meeting"             # 会議・打ち合わせ
    REVIEW = "review"               # レビュー・査読
    ADMIN = "admin"                 # 事務作業

class EnergyLevel(Enum):
    """エネルギーレベル"""
    PEAK = 4        # 最高集中状態
    HIGH = 3        # 高集中状態
    MEDIUM = 2      # 普通状態
    LOW = 1         # 低集中状態

@dataclass
class TimeSlot:
    """時間スロット"""
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    energy_level: EnergyLevel
    availability: float = 1.0  # 0.0-1.0 available ratio
    
    def __post_init__(self):
        if self.duration_minutes == 0:
            self.duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)

@dataclass
class ResearchTask:
    """研究タスク"""
    task_id: str
    title: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    estimated_duration: int      # minutes
    deadline: Optional[datetime] = None
    
    # Task characteristics
    requires_deep_focus: bool = True
    can_be_interrupted: bool = False
    preferred_time_of_day: Optional[str] = None  # "morning", "afternoon", "evening"
    dependencies: List[str] = None
    
    # Progress tracking
    completed_duration: int = 0
    completion_ratio: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def remaining_duration(self) -> int:
        return max(0, self.estimated_duration - self.completed_duration)
    
    @property
    def is_completed(self) -> bool:
        return self.completion_ratio >= 1.0
    
    @property
    def urgency_score(self) -> float:
        """緊急度スコア計算"""
        if not self.deadline:
            return self.priority.value
        
        days_until_deadline = (self.deadline - datetime.now()).days
        if days_until_deadline <= 0:
            return 10.0  # 過期
        elif days_until_deadline <= 1:
            return 8.0   # 明日まで
        elif days_until_deadline <= 3:
            return 6.0   # 3日以内
        elif days_until_deadline <= 7:
            return 4.0   # 1週間以内
        else:
            return self.priority.value

@dataclass
class ProductivityPattern:
    """生産性パターン"""
    user_id: str
    
    # Daily energy patterns (hour -> energy_level)
    daily_energy: Dict[int, EnergyLevel]
    
    # Task type preferences (task_type -> efficiency_multiplier)
    task_preferences: Dict[TaskType, float]
    
    # Time preferences
    peak_hours: List[int]           # Most productive hours
    low_hours: List[int]            # Least productive hours
    preferred_work_start: time      # Preferred work start time
    preferred_work_end: time        # Preferred work end time
    
    # Break patterns
    focus_duration: int = 90        # Minutes of focused work
    break_duration: int = 15        # Minutes of break
    long_break_interval: int = 4    # Work blocks before long break
    long_break_duration: int = 30   # Long break duration
    
    # Efficiency factors
    task_switching_penalty: float = 0.2    # Efficiency loss when switching
    context_building_time: int = 10        # Minutes to get into flow
    fatigue_factor: float = 0.05           # Hourly efficiency decay
    
    def __post_init__(self):
        if not self.daily_energy:
            # Default energy pattern
            self.daily_energy = {
                9: EnergyLevel.HIGH, 10: EnergyLevel.PEAK, 11: EnergyLevel.PEAK,
                12: EnergyLevel.MEDIUM, 13: EnergyLevel.LOW, 14: EnergyLevel.MEDIUM,
                15: EnergyLevel.HIGH, 16: EnergyLevel.HIGH, 17: EnergyLevel.MEDIUM,
                18: EnergyLevel.LOW, 19: EnergyLevel.LOW, 20: EnergyLevel.MEDIUM
            }
        
        if not self.task_preferences:
            # Default task preferences
            self.task_preferences = {
                TaskType.RESEARCH: 1.0,
                TaskType.WRITING: 0.9,
                TaskType.ANALYSIS: 1.1,
                TaskType.CODING: 1.0,
                TaskType.READING: 0.8,
                TaskType.MEETING: 0.7,
                TaskType.REVIEW: 0.9,
                TaskType.ADMIN: 0.6
            }

@dataclass
class ScheduleBlock:
    """スケジュールブロック"""
    block_id: str
    task: ResearchTask
    time_slot: TimeSlot
    estimated_efficiency: float
    break_before: int = 0           # Break minutes before this block
    break_after: int = 0            # Break minutes after this block
    
    @property
    def effective_duration(self) -> int:
        """実効作業時間"""
        return int(self.time_slot.duration_minutes * self.estimated_efficiency)

@dataclass
class DailySchedule:
    """日別スケジュール"""
    date: datetime
    schedule_blocks: List[ScheduleBlock]
    total_work_time: int           # Total minutes scheduled
    total_break_time: int          # Total break minutes
    efficiency_score: float        # Overall efficiency score
    flexibility_score: float      # Schedule flexibility score

class ScheduleOptimizer:
    """研究スケジュール最適化システム"""
    
    def __init__(self):
        self.productivity_patterns: Dict[str, ProductivityPattern] = {}
        self.tasks: Dict[str, ResearchTask] = {}
        self.schedules: Dict[str, DailySchedule] = {}  # date_string -> schedule
        
        # Optimization parameters
        self.config = {
            "optimization_horizon_days": 7,    # Days to optimize ahead
            "min_task_block_minutes": 30,      # Minimum task block size
            "max_task_block_minutes": 180,     # Maximum task block size
            "context_switch_penalty": 0.15,    # Penalty for switching tasks
            "deadline_urgency_weight": 2.0,    # Weight for deadline urgency
            "energy_match_weight": 1.5,        # Weight for energy-task matching
            "efficiency_threshold": 0.7,       # Minimum acceptable efficiency
            "buffer_time_ratio": 0.1           # Buffer time as ratio of task time
        }
    
    def create_productivity_pattern(self, user_id: str, **kwargs) -> ProductivityPattern:
        """生産性パターン作成"""
        pattern = ProductivityPattern(user_id=user_id, **kwargs)
        self.productivity_patterns[user_id] = pattern
        
        logger.info(f"生産性パターン作成: {user_id}")
        return pattern
    
    def add_task(self, task: ResearchTask) -> str:
        """タスク追加"""
        self.tasks[task.task_id] = task
        logger.info(f"タスク追加: {task.task_id} - {task.title}")
        return task.task_id
    
    def update_task_progress(self, task_id: str, completed_minutes: int = None,
                           completion_ratio: float = None):
        """タスク進捗更新"""
        if task_id not in self.tasks:
            logger.error(f"タスク未発見: {task_id}")
            return
        
        task = self.tasks[task_id]
        
        if completed_minutes is not None:
            task.completed_duration += completed_minutes
        
        if completion_ratio is not None:
            task.completion_ratio = completion_ratio
        
        logger.info(f"タスク進捗更新: {task_id} - {task.completion_ratio:.1%}")
    
    def generate_optimal_schedule(self, user_id: str, start_date: datetime,
                                days: int = 7) -> Dict[str, DailySchedule]:
        """最適スケジュール生成"""
        if user_id not in self.productivity_patterns:
            logger.error(f"生産性パターン未発見: {user_id}")
            return {}
        
        pattern = self.productivity_patterns[user_id]
        
        # Get pending tasks
        pending_tasks = [task for task in self.tasks.values() 
                        if not task.is_completed]
        
        if not pending_tasks:
            logger.info("保留タスクなし")
            return {}
        
        # Sort tasks by priority and urgency
        sorted_tasks = self._sort_tasks_by_priority(pending_tasks)
        
        # Generate schedules for each day
        schedules = {}
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day in range(days):
            day_date = current_date + timedelta(days=day)
            
            # Generate available time slots for the day
            time_slots = self._generate_time_slots(day_date, pattern)
            
            # Allocate tasks to time slots
            daily_schedule = self._allocate_tasks_to_slots(
                day_date, time_slots, sorted_tasks, pattern
            )
            
            if daily_schedule:
                date_str = day_date.strftime("%Y-%m-%d")
                schedules[date_str] = daily_schedule
                self.schedules[date_str] = daily_schedule
        
        logger.info(f"最適スケジュール生成: {len(schedules)}日分")
        return schedules
    
    def _sort_tasks_by_priority(self, tasks: List[ResearchTask]) -> List[ResearchTask]:
        """タスク優先度ソート"""
        def task_score(task):
            urgency = task.urgency_score
            remaining_work = task.remaining_duration / 60  # hours
            
            # Deadline pressure
            if task.deadline:
                days_left = (task.deadline - datetime.now()).days
                deadline_pressure = max(0, 10 - days_left)
            else:
                deadline_pressure = 0
            
            return urgency * 2 + deadline_pressure + remaining_work * 0.1
        
        return sorted(tasks, key=task_score, reverse=True)
    
    def _generate_time_slots(self, date: datetime, 
                           pattern: ProductivityPattern) -> List[TimeSlot]:
        """時間スロット生成"""
        slots = []
        
        # Define work hours
        work_start = datetime.combine(date.date(), pattern.preferred_work_start)
        work_end = datetime.combine(date.date(), pattern.preferred_work_end)
        
        current_time = work_start
        
        while current_time < work_end:
            # Determine slot duration (align with focus/break pattern)
            remaining_minutes = int((work_end - current_time).total_seconds() / 60)
            slot_duration = min(pattern.focus_duration, remaining_minutes)
            
            if slot_duration < self.config["min_task_block_minutes"]:
                break
            
            slot_end = current_time + timedelta(minutes=slot_duration)
            
            # Get energy level for this time
            hour = current_time.hour
            energy_level = pattern.daily_energy.get(hour, EnergyLevel.MEDIUM)
            
            slot = TimeSlot(
                start_time=current_time,
                end_time=slot_end,
                duration_minutes=slot_duration,
                energy_level=energy_level
            )
            slots.append(slot)
            
            # Add break time
            current_time = slot_end + timedelta(minutes=pattern.break_duration)
        
        return slots
    
    def _allocate_tasks_to_slots(self, date: datetime, time_slots: List[TimeSlot],
                               tasks: List[ResearchTask], 
                               pattern: ProductivityPattern) -> Optional[DailySchedule]:
        """タスクをスロットに割り当て"""
        if not time_slots:
            return None
        
        schedule_blocks = []
        allocated_tasks = set()
        
        for slot in time_slots:
            # Find best task for this slot
            best_task = self._find_best_task_for_slot(
                slot, tasks, allocated_tasks, pattern
            )
            
            if best_task:
                # Calculate efficiency for this allocation
                efficiency = self._calculate_task_efficiency(
                    best_task, slot, pattern
                )
                
                # Create schedule block
                block = ScheduleBlock(
                    block_id=f"block_{len(schedule_blocks):03d}_{int(slot.start_time.timestamp())}",
                    task=best_task,
                    time_slot=slot,
                    estimated_efficiency=efficiency,
                    break_before=pattern.break_duration if schedule_blocks else 0
                )
                
                schedule_blocks.append(block)
                
                # Update task progress (estimated)
                work_done = int(slot.duration_minutes * efficiency)
                if work_done >= best_task.remaining_duration:
                    allocated_tasks.add(best_task.task_id)
        
        if not schedule_blocks:
            return None
        
        # Calculate schedule metrics
        total_work = sum(block.time_slot.duration_minutes for block in schedule_blocks)
        total_breaks = sum(block.break_before + block.break_after for block in schedule_blocks)
        avg_efficiency = sum(block.estimated_efficiency for block in schedule_blocks) / len(schedule_blocks)
        
        # Calculate flexibility score
        flexibility = self._calculate_schedule_flexibility(schedule_blocks)
        
        return DailySchedule(
            date=date,
            schedule_blocks=schedule_blocks,
            total_work_time=total_work,
            total_break_time=total_breaks,
            efficiency_score=avg_efficiency,
            flexibility_score=flexibility
        )
    
    def _find_best_task_for_slot(self, slot: TimeSlot, tasks: List[ResearchTask],
                               allocated_tasks: Set[str], 
                               pattern: ProductivityPattern) -> Optional[ResearchTask]:
        """スロットに最適なタスク選択"""
        available_tasks = [t for t in tasks 
                          if t.task_id not in allocated_tasks and not t.is_completed]
        
        if not available_tasks:
            return None
        
        best_task = None
        best_score = -1
        
        for task in available_tasks:
            # Check if task can fit in slot
            if task.remaining_duration < self.config["min_task_block_minutes"]:
                continue
            
            # Calculate matching score
            score = self._calculate_task_slot_match_score(task, slot, pattern)
            
            if score > best_score:
                best_score = score
                best_task = task
        
        return best_task
    
    def _calculate_task_slot_match_score(self, task: ResearchTask, slot: TimeSlot,
                                       pattern: ProductivityPattern) -> float:
        """タスク-スロット適合度スコア"""
        score = 0.0
        
        # Energy level matching
        if task.requires_deep_focus:
            energy_bonus = {
                EnergyLevel.PEAK: 2.0,
                EnergyLevel.HIGH: 1.5,
                EnergyLevel.MEDIUM: 1.0,
                EnergyLevel.LOW: 0.3
            }
            score += energy_bonus[slot.energy_level]
        else:
            # Less demanding tasks can use any energy level
            score += 1.0
        
        # Task type preference
        task_pref = pattern.task_preferences.get(task.task_type, 1.0)
        score += task_pref
        
        # Time preference matching
        hour = slot.start_time.hour
        if task.preferred_time_of_day:
            if (task.preferred_time_of_day == "morning" and hour < 12) or \
               (task.preferred_time_of_day == "afternoon" and 12 <= hour < 18) or \
               (task.preferred_time_of_day == "evening" and hour >= 18):
                score += 1.0
        
        # Urgency factor
        score += task.urgency_score * 0.3
        
        # Duration matching (prefer tasks that fit well in slot)
        duration_ratio = min(task.remaining_duration, slot.duration_minutes) / slot.duration_minutes
        score += duration_ratio * 0.5
        
        return score
    
    def _calculate_task_efficiency(self, task: ResearchTask, slot: TimeSlot,
                                 pattern: ProductivityPattern) -> float:
        """タスク実行効率計算"""
        base_efficiency = 1.0
        
        # Energy level factor
        energy_multiplier = {
            EnergyLevel.PEAK: 1.2,
            EnergyLevel.HIGH: 1.0,
            EnergyLevel.MEDIUM: 0.8,
            EnergyLevel.LOW: 0.6
        }
        base_efficiency *= energy_multiplier[slot.energy_level]
        
        # Task type preference
        type_multiplier = pattern.task_preferences.get(task.task_type, 1.0)
        base_efficiency *= type_multiplier
        
        # Context building penalty for short slots
        if slot.duration_minutes < pattern.context_building_time * 2:
            context_penalty = pattern.context_building_time / slot.duration_minutes
            base_efficiency *= max(0.5, 1.0 - context_penalty)
        
        # Deep focus bonus/penalty
        if task.requires_deep_focus and slot.energy_level in [EnergyLevel.PEAK, EnergyLevel.HIGH]:
            base_efficiency *= 1.1
        elif task.requires_deep_focus and slot.energy_level == EnergyLevel.LOW:
            base_efficiency *= 0.7
        
        return min(1.0, max(0.3, base_efficiency))
    
    def _calculate_schedule_flexibility(self, blocks: List[ScheduleBlock]) -> float:
        """スケジュール柔軟性計算"""
        if not blocks:
            return 0.0
        
        flexibility_factors = []
        
        for block in blocks:
            # Tasks that can be interrupted are more flexible
            if block.task.can_be_interrupted:
                flexibility_factors.append(1.0)
            else:
                flexibility_factors.append(0.5)
            
            # Shorter blocks are more flexible
            duration_factor = max(0.5, 1.0 - block.time_slot.duration_minutes / 180)
            flexibility_factors.append(duration_factor)
        
        return sum(flexibility_factors) / len(flexibility_factors)
    
    def suggest_schedule_adjustments(self, date_str: str) -> List[Dict[str, Any]]:
        """スケジュール調整提案"""
        if date_str not in self.schedules:
            return []
        
        schedule = self.schedules[date_str]
        suggestions = []
        
        # Low efficiency blocks
        for block in schedule.schedule_blocks:
            if block.estimated_efficiency < self.config["efficiency_threshold"]:
                suggestions.append({
                    "type": "efficiency_improvement",
                    "block_id": block.block_id,
                    "current_efficiency": block.estimated_efficiency,
                    "suggestion": f"Consider moving {block.task.title} to a higher-energy time slot",
                    "priority": "medium"
                })
        
        # Overloaded schedule
        if schedule.total_work_time > 480:  # More than 8 hours
            suggestions.append({
                "type": "workload_reduction",
                "total_work_time": schedule.total_work_time,
                "suggestion": "Consider reducing workload or splitting tasks across multiple days",
                "priority": "high"
            })
        
        # Insufficient breaks
        if schedule.total_break_time < schedule.total_work_time * 0.15:
            suggestions.append({
                "type": "break_improvement",
                "current_break_ratio": schedule.total_break_time / schedule.total_work_time,
                "suggestion": "Add more breaks to maintain productivity",
                "priority": "medium"
            })
        
        # Low flexibility
        if schedule.flexibility_score < 0.5:
            suggestions.append({
                "type": "flexibility_improvement",
                "flexibility_score": schedule.flexibility_score,
                "suggestion": "Consider breaking down large tasks or rearranging schedule",
                "priority": "low"
            })
        
        return suggestions
    
    def get_productivity_insights(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """生産性インサイト取得"""
        if user_id not in self.productivity_patterns:
            return {}
        
        pattern = self.productivity_patterns[user_id]
        
        # Analyze completed tasks
        completed_tasks = [t for t in self.tasks.values() if t.is_completed]
        
        if not completed_tasks:
            return {"message": "No completed tasks for analysis"}
        
        # Task type analysis
        task_type_performance = defaultdict(list)
        for task in completed_tasks:
            if task.estimated_duration > 0:
                efficiency = task.completed_duration / task.estimated_duration
                task_type_performance[task.task_type].append(efficiency)
        
        type_averages = {
            task_type.value: sum(effs) / len(effs) if effs else 0
            for task_type, effs in task_type_performance.items()
        }
        
        # Peak performance times
        peak_hours = pattern.peak_hours if pattern.peak_hours else [10, 11, 15, 16]
        
        insights = {
            "most_efficient_task_type": max(type_averages.items(), key=lambda x: x[1]) if type_averages else None,
            "least_efficient_task_type": min(type_averages.items(), key=lambda x: x[1]) if type_averages else None,
            "task_type_performance": type_averages,
            "recommended_peak_hours": peak_hours,
            "average_focus_duration": pattern.focus_duration,
            "optimal_break_duration": pattern.break_duration,
            "total_completed_tasks": len(completed_tasks),
            "average_task_completion_ratio": sum(t.completion_ratio for t in completed_tasks) / len(completed_tasks)
        }
        
        return insights
    
    def export_schedule(self, date_str: str, format: str = "json") -> str:
        """スケジュールエクスポート"""
        if date_str not in self.schedules:
            return ""
        
        schedule = self.schedules[date_str]
        
        if format.lower() == "json":
            export_data = asdict(schedule)
            return json.dumps(export_data, indent=2, default=str, ensure_ascii=False)
        
        elif format.lower() == "text":
            output = [f"Schedule for {schedule.date.strftime('%Y-%m-%d')}"]
            output.append("=" * 50)
            
            for block in schedule.schedule_blocks:
                start_time = block.time_slot.start_time.strftime("%H:%M")
                end_time = block.time_slot.end_time.strftime("%H:%M")
                efficiency = block.estimated_efficiency
                
                output.append(f"{start_time}-{end_time}: {block.task.title}")
                output.append(f"  Type: {block.task.task_type.value}")
                output.append(f"  Efficiency: {efficiency:.1%}")
                output.append(f"  Duration: {block.time_slot.duration_minutes}min")
                output.append("")
            
            output.append(f"Total work time: {schedule.total_work_time}min")
            output.append(f"Total break time: {schedule.total_break_time}min")
            output.append(f"Average efficiency: {schedule.efficiency_score:.1%}")
            
            return "\n".join(output)
        
        else:
            raise ValueError(f"Unsupported format: {format}")

# 使用例・デモ
if __name__ == "__main__":
    # ScheduleOptimizer デモ
    optimizer = ScheduleOptimizer()
    
    # ユーザーの生産性パターン作成
    pattern = optimizer.create_productivity_pattern(
        user_id="researcher_001",
        daily_energy={
            9: EnergyLevel.MEDIUM, 10: EnergyLevel.HIGH, 11: EnergyLevel.PEAK,
            12: EnergyLevel.HIGH, 14: EnergyLevel.MEDIUM, 15: EnergyLevel.HIGH,
            16: EnergyLevel.HIGH, 17: EnergyLevel.MEDIUM, 18: EnergyLevel.LOW
        },
        peak_hours=[10, 11, 15, 16],
        low_hours=[13, 18, 19],
        preferred_work_start=time(9, 0),
        preferred_work_end=time(18, 0),
        focus_duration=90,
        break_duration=15
    )
    
    # サンプルタスク追加
    tasks = [
        ResearchTask(
            task_id="task_001",
            title="Literature Review on AI Ethics",
            description="Comprehensive review of recent papers",
            task_type=TaskType.READING,
            priority=TaskPriority.HIGH,
            estimated_duration=180,
            deadline=datetime.now() + timedelta(days=3),
            requires_deep_focus=True
        ),
        ResearchTask(
            task_id="task_002", 
            title="Data Analysis - Experiment Results",
            description="Statistical analysis of experimental data",
            task_type=TaskType.ANALYSIS,
            priority=TaskPriority.CRITICAL,
            estimated_duration=240,
            deadline=datetime.now() + timedelta(days=2),
            requires_deep_focus=True
        ),
        ResearchTask(
            task_id="task_003",
            title="Write Introduction Section",
            description="Draft introduction for research paper",
            task_type=TaskType.WRITING,
            priority=TaskPriority.MEDIUM,
            estimated_duration=120,
            requires_deep_focus=True,
            preferred_time_of_day="morning"
        ),
        ResearchTask(
            task_id="task_004",
            title="Code Review and Testing",
            description="Review analysis scripts and run tests",
            task_type=TaskType.CODING,
            priority=TaskPriority.MEDIUM,
            estimated_duration=90,
            can_be_interrupted=True
        )
    ]
    
    # タスクを追加
    for task in tasks:
        optimizer.add_task(task)
    
    print("=== Schedule Optimizer Demo ===")
    
    # 最適スケジュール生成
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    schedules = optimizer.generate_optimal_schedule("researcher_001", start_date, days=3)
    
    print(f"Generated schedules for {len(schedules)} days")
    
    # 最初の日のスケジュール表示
    if schedules:
        first_date = list(schedules.keys())[0]
        first_schedule = schedules[first_date]
        
        print(f"\n--- Schedule for {first_date} ---")
        print(f"Total work time: {first_schedule.total_work_time} minutes")
        print(f"Efficiency score: {first_schedule.efficiency_score:.1%}")
        print(f"Flexibility score: {first_schedule.flexibility_score:.1%}\n")
        
        for block in first_schedule.schedule_blocks:
            start_time = block.time_slot.start_time.strftime("%H:%M")
            end_time = block.time_slot.end_time.strftime("%H:%M")
            print(f"{start_time}-{end_time}: {block.task.title}")
            print(f"  Efficiency: {block.estimated_efficiency:.1%}, "
                  f"Energy: {block.time_slot.energy_level.name}")
        
        # 調整提案
        suggestions = optimizer.suggest_schedule_adjustments(first_date)
        if suggestions:
            print(f"\n--- Schedule Adjustment Suggestions ---")
            for suggestion in suggestions:
                print(f"- {suggestion['suggestion']} (Priority: {suggestion['priority']})")
    
    # 生産性インサイト
    # タスク完了をシミュレート
    optimizer.update_task_progress("task_004", completion_ratio=1.0)
    
    insights = optimizer.get_productivity_insights("researcher_001")
    print(f"\n--- Productivity Insights ---")
    print(f"Completed tasks: {insights.get('total_completed_tasks', 0)}")
    print(f"Peak hours: {insights.get('recommended_peak_hours', [])}")
    
    if insights.get('most_efficient_task_type'):
        task_type, efficiency = insights['most_efficient_task_type']
        print(f"Most efficient task type: {task_type} ({efficiency:.1%})")
    
    # スケジュールエクスポート
    if schedules:
        first_date = list(schedules.keys())[0]
        text_schedule = optimizer.export_schedule(first_date, "text")
        print(f"\n--- Text Export Preview ---")
        print(text_schedule[:300] + "..." if len(text_schedule) > 300 else text_schedule)
    
    logger.info("スケジュール最適化システム デモ完了")