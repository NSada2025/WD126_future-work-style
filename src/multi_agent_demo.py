#!/usr/bin/env python3
"""
マルチエージェント協調システムのデモ実装
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """エージェント間メッセージ"""
    id: str
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: datetime
    message_type: str


class Agent:
    """基本エージェントクラス"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.message_queue = asyncio.Queue()
        self.knowledge_base = {}
        self.active = True
        
    async def receive_message(self, message: Message):
        """メッセージ受信"""
        await self.message_queue.put(message)
        
    async def send_message(self, receiver: 'Agent', content: Dict[str, Any], message_type: str):
        """メッセージ送信"""
        message = Message(
            id=str(uuid.uuid4()),
            sender=self.name,
            receiver=receiver.name,
            content=content,
            timestamp=datetime.now(),
            message_type=message_type
        )
        await receiver.receive_message(message)
        logger.info(f"{self.name} -> {receiver.name}: {message_type}")
        
    async def process_messages(self):
        """メッセージ処理ループ"""
        while self.active:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self.handle_message(message)
            except asyncio.TimeoutError:
                continue
                
    async def handle_message(self, message: Message):
        """メッセージハンドラー（サブクラスでオーバーライド）"""
        pass


class PresidentAgent(Agent):
    """統括エージェント"""
    
    def __init__(self):
        super().__init__("President", "Project Manager")
        self.project_status = {
            "active_tasks": [],
            "completed_tasks": [],
            "agents": {}
        }
        
    async def handle_message(self, message: Message):
        """プロジェクト管理メッセージ処理"""
        if message.message_type == "task_completion":
            self.project_status["completed_tasks"].append(message.content)
            logger.info(f"Task completed: {message.content['task_id']}")
            
        elif message.message_type == "status_update":
            self.project_status["agents"][message.sender] = message.content
            
        elif message.message_type == "request_approval":
            # 承認プロセス
            approved = await self.evaluate_request(message.content)
            await self.send_message(
                message.sender,
                {"approved": approved, "request_id": message.content["id"]},
                "approval_response"
            )
            
    async def evaluate_request(self, request: Dict[str, Any]) -> bool:
        """リクエスト評価"""
        # シンプルな承認ロジック
        if request.get("priority") == "high":
            return True
        return request.get("cost", 0) < 1000


class ResearchAgent(Agent):
    """研究エージェント"""
    
    def __init__(self):
        super().__init__("Researcher", "Literature Review")
        self.papers_database = []
        
    async def handle_message(self, message: Message):
        """研究タスク処理"""
        if message.message_type == "research_request":
            topic = message.content["topic"]
            papers = await self.search_papers(topic)
            
            await self.send_message(
                message.sender,
                {
                    "topic": topic,
                    "papers": papers,
                    "summary": self.summarize_papers(papers)
                },
                "research_result"
            )
            
    async def search_papers(self, topic: str) -> List[Dict[str, str]]:
        """論文検索シミュレーション"""
        # 実際にはAPIを使用
        await asyncio.sleep(0.5)  # 検索時間のシミュレーション
        return [
            {"title": f"Paper on {topic} - Study 1", "year": "2024", "relevance": 0.95},
            {"title": f"Review of {topic}", "year": "2023", "relevance": 0.90},
            {"title": f"Novel approach to {topic}", "year": "2025", "relevance": 0.88}
        ]
        
    def summarize_papers(self, papers: List[Dict[str, str]]) -> str:
        """論文要約"""
        return f"Found {len(papers)} relevant papers with average relevance of 0.91"


class AnalystAgent(Agent):
    """分析エージェント"""
    
    def __init__(self):
        super().__init__("Analyst", "Data Analysis")
        
    async def handle_message(self, message: Message):
        """分析タスク処理"""
        if message.message_type == "analysis_request":
            data = message.content["data"]
            analysis_type = message.content["type"]
            
            result = await self.analyze_data(data, analysis_type)
            
            await self.send_message(
                message.sender,
                {
                    "analysis_type": analysis_type,
                    "results": result,
                    "confidence": 0.87
                },
                "analysis_result"
            )
            
    async def analyze_data(self, data: Any, analysis_type: str) -> Dict[str, Any]:
        """データ分析シミュレーション"""
        await asyncio.sleep(1.0)  # 分析時間のシミュレーション
        
        if analysis_type == "statistical":
            return {
                "mean": 42.5,
                "std": 5.2,
                "correlation": 0.73,
                "p_value": 0.001
            }
        elif analysis_type == "pattern":
            return {
                "patterns_found": 3,
                "anomalies": 2,
                "trend": "increasing"
            }
        return {}


class WriterAgent(Agent):
    """執筆支援エージェント"""
    
    def __init__(self):
        super().__init__("Writer", "Documentation")
        
    async def handle_message(self, message: Message):
        """執筆タスク処理"""
        if message.message_type == "write_request":
            doc_type = message.content["type"]
            data = message.content["data"]
            
            document = await self.generate_document(doc_type, data)
            
            await self.send_message(
                message.sender,
                {
                    "document": document,
                    "word_count": len(document.split())
                },
                "document_ready"
            )
            
    async def generate_document(self, doc_type: str, data: Dict[str, Any]) -> str:
        """ドキュメント生成"""
        await asyncio.sleep(0.8)
        
        if doc_type == "report":
            return f"""
# Analysis Report
## Summary
Based on the provided data, we found significant patterns...
## Methodology
Statistical analysis was performed using...
## Results
The analysis revealed {data.get('key_finding', 'important insights')}...
## Conclusion
Further investigation is recommended.
"""
        return "Document generated"


class MultiAgentSystem:
    """マルチエージェントシステム"""
    
    def __init__(self):
        self.agents = {
            "president": PresidentAgent(),
            "researcher": ResearchAgent(),
            "analyst": AnalystAgent(),
            "writer": WriterAgent()
        }
        self.running = False
        
    async def start(self):
        """システム起動"""
        self.running = True
        tasks = []
        
        for agent in self.agents.values():
            tasks.append(asyncio.create_task(agent.process_messages()))
            
        logger.info("Multi-agent system started")
        return tasks
        
    async def stop(self):
        """システム停止"""
        self.running = False
        for agent in self.agents.values():
            agent.active = False
        logger.info("Multi-agent system stopped")
        
    async def execute_research_workflow(self, topic: str):
        """研究ワークフロー実行"""
        president = self.agents["president"]
        researcher = self.agents["researcher"]
        analyst = self.agents["analyst"]
        writer = self.agents["writer"]
        
        # 1. 文献調査
        await president.send_message(
            researcher,
            {"topic": topic, "priority": "high"},
            "research_request"
        )
        
        # 2. データ分析リクエスト
        await asyncio.sleep(1.0)  # 研究完了待ち
        await president.send_message(
            analyst,
            {
                "data": {"sample_size": 1000, "variables": 5},
                "type": "statistical"
            },
            "analysis_request"
        )
        
        # 3. レポート作成
        await asyncio.sleep(2.0)  # 分析完了待ち
        await president.send_message(
            writer,
            {
                "type": "report",
                "data": {"key_finding": "significant correlation found"}
            },
            "write_request"
        )


async def demo():
    """デモ実行"""
    system = MultiAgentSystem()
    
    # システム起動
    tasks = await system.start()
    
    # 研究ワークフロー実行
    await system.execute_research_workflow("AI in Healthcare")
    
    # 5秒間実行
    await asyncio.sleep(5)
    
    # システム停止
    await system.stop()
    
    # タスクのクリーンアップ
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(demo())