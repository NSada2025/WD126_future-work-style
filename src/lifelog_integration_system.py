#!/usr/bin/env python3
"""
ライフログ統合システム
Limitless AIペンダントからの音声データを活用した
自動タスク管理・スケジュール最適化システム
"""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np


class TaskPriority(Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EnergyLevel(Enum):
    PEAK = "peak"        # 90-100%
    HIGH = "high"        # 70-90%
    MODERATE = "moderate" # 50-70%
    LOW = "low"          # 30-50%
    MINIMAL = "minimal"  # <30%


@dataclass
class Task:
    """タスククラス"""
    id: str
    title: str
    description: str
    deadline: Optional[datetime]
    priority: TaskPriority
    estimated_duration: timedelta
    required_energy: EnergyLevel
    tags: List[str]
    source: str  # "voice", "manual", "ai_suggested"
    created_at: datetime
    completed: bool = False
    
    
@dataclass
class Meeting:
    """会議情報"""
    id: str
    title: str
    participants: List[str]
    start_time: datetime
    duration: timedelta
    transcript: str
    summary: str
    action_items: List[Task]
    

@dataclass
class DailyLog:
    """日次ログ"""
    date: datetime
    energy_levels: List[Tuple[datetime, float]]  # 時刻とエネルギーレベル
    completed_tasks: List[Task]
    meetings: List[Meeting]
    voice_notes: List[Dict[str, Any]]
    productivity_score: float


class VoiceTranscriptionParser:
    """音声転写テキストからタスクを抽出"""
    
    def __init__(self):
        self.task_patterns = [
            # 明確な期限付きタスク
            r"(.+?)を?(.+?)まで(?:に|で)(.+?)(?:する|します|完了|提出|送る)",
            # 期限なしタスク
            r"(.+?)を(.+?)(?:する|します|やる|やります)(?:必要|こと|予定)",
            # TODO形式
            r"(?:TODO|やること|タスク)[:：\s]*(.+)",
            # 依頼形式
            r"(.+?)を?お願い(?:します|できますか)",
        ]
        
        self.deadline_patterns = {
            "今日": timedelta(days=0),
            "明日": timedelta(days=1),
            "明後日": timedelta(days=2),
            "今週": timedelta(days=7),
            "来週": timedelta(days=14),
            "今月": timedelta(days=30),
            "来月": timedelta(days=60),
        }
        
    async def extract_tasks(self, transcript: str) -> List[Task]:
        """転写テキストからタスクを抽出"""
        tasks = []
        
        # センテンスに分割
        sentences = re.split(r'[。！？\n]', transcript)
        
        for sentence in sentences:
            task = await self._parse_sentence(sentence)
            if task:
                tasks.append(task)
                
        return tasks
        
    async def _parse_sentence(self, sentence: str) -> Optional[Task]:
        """文からタスクを抽出"""
        for pattern in self.task_patterns:
            match = re.search(pattern, sentence)
            if match:
                return await self._create_task_from_match(match, sentence)
        return None
        
    async def _create_task_from_match(self, match: re.Match, sentence: str) -> Task:
        """マッチからタスクを作成"""
        # タスクタイトルの抽出
        groups = match.groups()
        title = groups[0] if groups else sentence[:50]
        
        # 期限の抽出
        deadline = self._extract_deadline(sentence)
        
        # 優先度の推定
        priority = self._estimate_priority(sentence, deadline)
        
        # 必要エネルギーの推定
        required_energy = self._estimate_required_energy(sentence)
        
        # タグの抽出
        tags = self._extract_tags(sentence)
        
        return Task(
            id=f"task_{datetime.now().timestamp()}",
            title=title.strip(),
            description=sentence,
            deadline=deadline,
            priority=priority,
            estimated_duration=timedelta(hours=1),  # デフォルト
            required_energy=required_energy,
            tags=tags,
            source="voice",
            created_at=datetime.now()
        )
        
    def _extract_deadline(self, text: str) -> Optional[datetime]:
        """期限を抽出"""
        now = datetime.now()
        
        # 相対的な期限
        for keyword, delta in self.deadline_patterns.items():
            if keyword in text:
                return now + delta
                
        # 具体的な日付（簡易パース）
        date_match = re.search(r'(\d{1,2})月(\d{1,2})日', text)
        if date_match:
            month = int(date_match.group(1))
            day = int(date_match.group(2))
            year = now.year
            if month < now.month:
                year += 1
            try:
                return datetime(year, month, day)
            except ValueError:
                pass
                
        return None
        
    def _estimate_priority(self, text: str, deadline: Optional[datetime]) -> TaskPriority:
        """優先度を推定"""
        urgent_keywords = ["緊急", "至急", "すぐ", "今すぐ", "ASAP"]
        high_keywords = ["重要", "必須", "必ず", "絶対"]
        
        for keyword in urgent_keywords:
            if keyword in text:
                return TaskPriority.URGENT
                
        for keyword in high_keywords:
            if keyword in text:
                return TaskPriority.HIGH
                
        # 期限による判定
        if deadline:
            days_until = (deadline - datetime.now()).days
            if days_until <= 1:
                return TaskPriority.URGENT
            elif days_until <= 3:
                return TaskPriority.HIGH
            elif days_until <= 7:
                return TaskPriority.MEDIUM
                
        return TaskPriority.LOW
        
    def _estimate_required_energy(self, text: str) -> EnergyLevel:
        """必要エネルギーレベルを推定"""
        high_energy_keywords = ["分析", "研究", "執筆", "設計", "開発", "実験"]
        low_energy_keywords = ["確認", "メール", "連絡", "整理", "レビュー"]
        
        for keyword in high_energy_keywords:
            if keyword in text:
                return EnergyLevel.HIGH
                
        for keyword in low_energy_keywords:
            if keyword in text:
                return EnergyLevel.LOW
                
        return EnergyLevel.MODERATE
        
    def _extract_tags(self, text: str) -> List[str]:
        """タグを抽出"""
        tags = []
        
        # プロジェクト関連
        project_keywords = ["研究", "論文", "実験", "開発", "プロジェクト"]
        for keyword in project_keywords:
            if keyword in text:
                tags.append(keyword)
                
        # 人物関連
        if "さん" in text or "先生" in text:
            tags.append("collaboration")
            
        return tags


class EnergyManager:
    """エネルギーレベル管理"""
    
    def __init__(self):
        self.base_decay_rate = 0.05  # 1時間あたり5%減少
        self.task_energy_cost = {
            EnergyLevel.PEAK: 0.15,
            EnergyLevel.HIGH: 0.10,
            EnergyLevel.MODERATE: 0.05,
            EnergyLevel.LOW: 0.02,
            EnergyLevel.MINIMAL: 0.01
        }
        
    def calculate_energy_at_time(self, wake_time: datetime, current_time: datetime) -> float:
        """指定時刻のエネルギーレベルを計算"""
        hours_awake = (current_time - wake_time).total_seconds() / 3600
        
        # 基本的な減衰
        base_energy = 1.0 - (self.base_decay_rate * hours_awake)
        
        # 昼食後の回復
        if 12 <= current_time.hour <= 13:
            base_energy += 0.05
            
        # 夕方の落ち込み
        if 15 <= current_time.hour <= 17:
            base_energy -= 0.05
            
        return max(0.2, min(1.0, base_energy))
        
    def estimate_task_completion_time(self, task: Task, current_energy: float) -> timedelta:
        """タスク完了時間を推定"""
        base_duration = task.estimated_duration
        
        # エネルギーレベルによる効率調整
        if current_energy >= 0.8:
            efficiency = 1.0
        elif current_energy >= 0.6:
            efficiency = 0.9
        elif current_energy >= 0.4:
            efficiency = 0.75
        else:
            efficiency = 0.5
            
        return base_duration / efficiency
        
    def get_energy_level_category(self, energy_value: float) -> EnergyLevel:
        """エネルギー値をカテゴリに変換"""
        if energy_value >= 0.9:
            return EnergyLevel.PEAK
        elif energy_value >= 0.7:
            return EnergyLevel.HIGH
        elif energy_value >= 0.5:
            return EnergyLevel.MODERATE
        elif energy_value >= 0.3:
            return EnergyLevel.LOW
        else:
            return EnergyLevel.MINIMAL


class ScheduleOptimizer:
    """スケジュール最適化"""
    
    def __init__(self, energy_manager: EnergyManager):
        self.energy_manager = energy_manager
        self.work_hours = {
            "start": 7,
            "end": 22,
            "break_times": [(12, 13), (15, 15.5), (19, 20)]
        }
        
    async def optimize_daily_schedule(self, 
                                    tasks: List[Task], 
                                    meetings: List[Meeting],
                                    current_date: datetime) -> Dict[str, Any]:
        """一日のスケジュールを最適化"""
        # タスクを優先度とエネルギー要求でソート
        sorted_tasks = self._sort_tasks_by_priority(tasks)
        
        # 利用可能な時間スロットを計算
        time_slots = self._calculate_available_slots(meetings, current_date)
        
        # エネルギーレベルを考慮してタスクを配置
        schedule = await self._assign_tasks_to_slots(sorted_tasks, time_slots, current_date)
        
        return {
            "date": current_date,
            "scheduled_tasks": schedule,
            "unscheduled_tasks": [t for t in tasks if t.id not in [s["task"].id for s in schedule]],
            "productivity_estimate": self._estimate_productivity(schedule),
            "energy_usage": self._calculate_energy_usage(schedule)
        }
        
    def _sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """タスクを優先度でソート"""
        priority_order = {
            TaskPriority.URGENT: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        return sorted(tasks, key=lambda t: (
            priority_order[t.priority],
            t.deadline or datetime.max
        ))
        
    def _calculate_available_slots(self, meetings: List[Meeting], date: datetime) -> List[Dict[str, Any]]:
        """利用可能な時間スロットを計算"""
        slots = []
        current_time = date.replace(hour=self.work_hours["start"], minute=0)
        end_time = date.replace(hour=self.work_hours["end"], minute=0)
        
        # 会議時間を除外
        meeting_times = [(m.start_time, m.start_time + m.duration) for m in meetings]
        
        while current_time < end_time:
            slot_end = current_time + timedelta(hours=1)
            
            # 休憩時間チェック
            is_break = False
            for break_start, break_end in self.work_hours["break_times"]:
                break_start_time = date.replace(hour=int(break_start), minute=int((break_start % 1) * 60))
                break_end_time = date.replace(hour=int(break_end), minute=int((break_end % 1) * 60))
                
                if current_time < break_end_time and slot_end > break_start_time:
                    is_break = True
                    break
                    
            # 会議時間チェック
            is_meeting = False
            for meeting_start, meeting_end in meeting_times:
                if current_time < meeting_end and slot_end > meeting_start:
                    is_meeting = True
                    break
                    
            if not is_break and not is_meeting:
                energy = self.energy_manager.calculate_energy_at_time(
                    date.replace(hour=6, minute=0),
                    current_time
                )
                slots.append({
                    "start": current_time,
                    "end": slot_end,
                    "energy_level": energy
                })
                
            current_time = slot_end
            
        return slots
        
    async def _assign_tasks_to_slots(self, 
                                   tasks: List[Task], 
                                   slots: List[Dict[str, Any]],
                                   date: datetime) -> List[Dict[str, Any]]:
        """タスクをスロットに割り当て"""
        schedule = []
        used_slots = set()
        
        for task in tasks:
            best_slot = None
            best_score = -1
            
            for i, slot in enumerate(slots):
                if i in used_slots:
                    continue
                    
                # スロットのエネルギーレベルとタスクの要求を比較
                slot_energy_category = self.energy_manager.get_energy_level_category(slot["energy_level"])
                
                # スコア計算
                score = self._calculate_slot_task_compatibility(
                    task,
                    slot,
                    slot_energy_category
                )
                
                if score > best_score:
                    best_score = score
                    best_slot = (i, slot)
                    
            if best_slot:
                slot_index, slot = best_slot
                used_slots.add(slot_index)
                
                schedule.append({
                    "task": task,
                    "start_time": slot["start"],
                    "end_time": slot["start"] + task.estimated_duration,
                    "energy_level": slot["energy_level"],
                    "efficiency_score": best_score
                })
                
        return schedule
        
    def _calculate_slot_task_compatibility(self, 
                                         task: Task, 
                                         slot: Dict[str, Any],
                                         slot_energy: EnergyLevel) -> float:
        """スロットとタスクの適合性スコアを計算"""
        score = 0.0
        
        # エネルギーレベルの適合性
        energy_match = {
            (EnergyLevel.PEAK, EnergyLevel.PEAK): 1.0,
            (EnergyLevel.PEAK, EnergyLevel.HIGH): 0.9,
            (EnergyLevel.HIGH, EnergyLevel.HIGH): 1.0,
            (EnergyLevel.HIGH, EnergyLevel.MODERATE): 0.8,
            (EnergyLevel.MODERATE, EnergyLevel.MODERATE): 1.0,
            (EnergyLevel.MODERATE, EnergyLevel.LOW): 0.9,
            (EnergyLevel.LOW, EnergyLevel.LOW): 1.0,
            (EnergyLevel.LOW, EnergyLevel.MINIMAL): 0.9,
        }
        
        key = (slot_energy, task.required_energy)
        score += energy_match.get(key, 0.5)
        
        # 期限の緊急性
        if task.deadline:
            hours_until_deadline = (task.deadline - slot["start"]).total_seconds() / 3600
            if hours_until_deadline < 24:
                score += 0.5
            elif hours_until_deadline < 72:
                score += 0.3
                
        # 優先度
        priority_scores = {
            TaskPriority.URGENT: 0.4,
            TaskPriority.HIGH: 0.3,
            TaskPriority.MEDIUM: 0.2,
            TaskPriority.LOW: 0.1
        }
        score += priority_scores[task.priority]
        
        return score
        
    def _estimate_productivity(self, schedule: List[Dict[str, Any]]) -> float:
        """生産性を推定"""
        if not schedule:
            return 0.0
            
        total_efficiency = sum(item["efficiency_score"] for item in schedule)
        return total_efficiency / len(schedule)
        
    def _calculate_energy_usage(self, schedule: List[Dict[str, Any]]) -> Dict[str, float]:
        """エネルギー使用量を計算"""
        total_cost = 0.0
        
        for item in schedule:
            task = item["task"]
            cost = self.energy_manager.task_energy_cost[task.required_energy]
            total_cost += cost
            
        return {
            "total_energy_cost": total_cost,
            "remaining_energy": max(0, 1.0 - total_cost),
            "efficiency_ratio": len(schedule) / max(total_cost, 0.1)
        }


class LifelogIntegrationSystem:
    """統合ライフログシステム"""
    
    def __init__(self):
        self.voice_parser = VoiceTranscriptionParser()
        self.energy_manager = EnergyManager()
        self.schedule_optimizer = ScheduleOptimizer(self.energy_manager)
        self.tasks: List[Task] = []
        self.meetings: List[Meeting] = []
        self.daily_logs: Dict[str, DailyLog] = {}
        
    async def process_voice_input(self, transcript: str, timestamp: datetime) -> List[Task]:
        """音声入力を処理してタスクを抽出"""
        # タスク抽出
        new_tasks = await self.voice_parser.extract_tasks(transcript)
        
        # タスクリストに追加
        self.tasks.extend(new_tasks)
        
        # 通知生成
        if new_tasks:
            await self._send_task_notifications(new_tasks)
            
        return new_tasks
        
    async def process_meeting_transcript(self, meeting: Meeting) -> List[Task]:
        """会議の文字起こしからアクションアイテムを抽出"""
        # 会議録からタスク抽出
        action_items = await self.voice_parser.extract_tasks(meeting.transcript)
        
        # 会議コンテキストの追加
        for task in action_items:
            task.tags.append("meeting")
            task.tags.append(f"meeting_{meeting.id}")
            
        meeting.action_items = action_items
        self.meetings.append(meeting)
        self.tasks.extend(action_items)
        
        return action_items
        
    async def generate_daily_schedule(self, date: datetime) -> Dict[str, Any]:
        """日次スケジュールを生成"""
        # 未完了タスクをフィルタ
        pending_tasks = [t for t in self.tasks if not t.completed]
        
        # 今日の会議をフィルタ
        todays_meetings = [
            m for m in self.meetings 
            if m.start_time.date() == date.date()
        ]
        
        # スケジュール最適化
        schedule = await self.schedule_optimizer.optimize_daily_schedule(
            pending_tasks,
            todays_meetings,
            date
        )
        
        return schedule
        
    async def update_task_status(self, task_id: str, completed: bool) -> None:
        """タスクのステータスを更新"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = completed
                break
                
    async def get_productivity_insights(self, date: datetime) -> Dict[str, Any]:
        """生産性インサイトを生成"""
        # 完了タスクの集計
        completed_today = [
            t for t in self.tasks 
            if t.completed and t.created_at.date() == date.date()
        ]
        
        # タスクカテゴリ別の分析
        task_by_priority = {}
        for priority in TaskPriority:
            count = len([t for t in completed_today if t.priority == priority])
            task_by_priority[priority.value] = count
            
        # エネルギー効率の分析
        energy_efficiency = self._calculate_energy_efficiency(completed_today)
        
        # 改善提案
        suggestions = self._generate_improvement_suggestions(completed_today)
        
        return {
            "date": date,
            "completed_tasks": len(completed_today),
            "task_by_priority": task_by_priority,
            "energy_efficiency": energy_efficiency,
            "suggestions": suggestions
        }
        
    def _calculate_energy_efficiency(self, tasks: List[Task]) -> float:
        """エネルギー効率を計算"""
        if not tasks:
            return 0.0
            
        total_cost = sum(
            self.energy_manager.task_energy_cost[t.required_energy] 
            for t in tasks
        )
        
        return len(tasks) / max(total_cost, 0.1)
        
    def _generate_improvement_suggestions(self, completed_tasks: List[Task]) -> List[str]:
        """改善提案を生成"""
        suggestions = []
        
        # 高エネルギータスクの時間帯分析
        high_energy_tasks = [t for t in completed_tasks if t.required_energy in [EnergyLevel.PEAK, EnergyLevel.HIGH]]
        if high_energy_tasks:
            avg_hour = sum(t.created_at.hour for t in high_energy_tasks) / len(high_energy_tasks)
            if avg_hour > 14:
                suggestions.append("高エネルギータスクを午前中に移動することで効率が向上します")
                
        # タスクの分散
        task_hours = [t.created_at.hour for t in completed_tasks]
        if len(set(task_hours)) < 4:
            suggestions.append("タスクをより均等に分散させることで疲労を軽減できます")
            
        return suggestions
        
    async def _send_task_notifications(self, tasks: List[Task]) -> None:
        """タスク通知を送信"""
        for task in tasks:
            if task.priority in [TaskPriority.URGENT, TaskPriority.HIGH]:
                print(f"🔴 緊急タスク追加: {task.title}")
                if task.deadline:
                    print(f"   期限: {task.deadline.strftime('%Y-%m-%d %H:%M')}")


async def demo_lifelog_system():
    """ライフログシステムのデモ"""
    system = LifelogIntegrationSystem()
    
    print("=== ライフログ統合システム デモ ===\n")
    
    # 朝の音声メモ
    morning_transcript = """
    今日は実験データの解析を完了する必要がある。
    明日までに共同研究者の田中先生にレポートを送る。
    来週の学会発表の準備も始めないと。
    あと、メールの返信も忘れずに。
    """
    
    print("1. 朝の音声メモを処理中...")
    morning_tasks = await system.process_voice_input(
        morning_transcript,
        datetime.now().replace(hour=7, minute=30)
    )
    
    print(f"抽出されたタスク: {len(morning_tasks)}件")
    for task in morning_tasks:
        print(f"  - {task.title} (優先度: {task.priority.value})")
        
    # 会議の文字起こし
    print("\n2. 会議の文字起こしを処理中...")
    meeting = Meeting(
        id="meeting_001",
        title="研究進捗会議",
        participants=["自分", "教授", "共同研究者"],
        start_time=datetime.now().replace(hour=10, minute=0),
        duration=timedelta(hours=1),
        transcript="""
        教授: 次回の論文投稿について、来月15日までにドラフトを完成させてください。
        共同研究者: データの追加解析が必要ですね。今週中に解析方法を相談しましょう。
        自分: 了解しました。明日までに解析プランを作成します。
        """,
        summary="論文投稿に向けた進捗確認",
        action_items=[]
    )
    
    meeting_tasks = await system.process_meeting_transcript(meeting)
    print(f"会議から抽出されたアクションアイテム: {len(meeting_tasks)}件")
    
    # スケジュール生成
    print("\n3. 最適化されたスケジュールを生成中...")
    schedule = await system.generate_daily_schedule(datetime.now())
    
    print("\n=== 本日のスケジュール ===")
    for item in schedule["scheduled_tasks"]:
        task = item["task"]
        print(f"{item['start_time'].strftime('%H:%M')} - {item['end_time'].strftime('%H:%M')}: "
              f"{task.title} (エネルギー: {item['energy_level']:.0%})")
        
    print(f"\n未スケジュールタスク: {len(schedule['unscheduled_tasks'])}件")
    print(f"予測生産性スコア: {schedule['productivity_estimate']:.2f}")
    print(f"エネルギー使用効率: {schedule['energy_usage']['efficiency_ratio']:.2f}")
    
    # 夕方の音声メモ
    print("\n4. 夕方の進捗更新...")
    evening_transcript = """
    実験データの解析は完了した。
    レポートも田中先生に送信済み。
    明日は論文の執筆に集中する予定。
    """
    
    # いくつかのタスクを完了としてマーク
    for task in morning_tasks[:2]:
        await system.update_task_status(task.id, True)
        
    # 生産性インサイト
    print("\n5. 本日の生産性インサイトを生成中...")
    insights = await system.get_productivity_insights(datetime.now())
    
    print("\n=== 生産性レポート ===")
    print(f"完了タスク数: {insights['completed_tasks']}")
    print("優先度別完了数:")
    for priority, count in insights['task_by_priority'].items():
        print(f"  {priority}: {count}")
    print(f"エネルギー効率: {insights['energy_efficiency']:.2f}")
    
    if insights['suggestions']:
        print("\n改善提案:")
        for suggestion in insights['suggestions']:
            print(f"  • {suggestion}")


if __name__ == "__main__":
    asyncio.run(demo_lifelog_system())