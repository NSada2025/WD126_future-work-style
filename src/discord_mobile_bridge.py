#!/usr/bin/env python3
"""
Discord APIを介したPC-スマホ連携システム
WD122_discord-multiagent-controlプロジェクトとの統合
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import discord
from discord.ext import commands
import aiohttp
from enum import Enum


class DeviceType(Enum):
    PC = "pc"
    MOBILE = "mobile"
    VOICE_ASSISTANT = "voice_assistant"
    WEARABLE = "wearable"


class CommandType(Enum):
    CODE_EXECUTE = "code_execute"
    FILE_SYNC = "file_sync"
    TASK_CREATE = "task_create"
    STATUS_CHECK = "status_check"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class DeviceCommand:
    """デバイス間コマンド"""
    id: str
    source_device: DeviceType
    target_device: DeviceType
    command_type: CommandType
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 0
    safety_context: Optional[str] = None


class SafetyMonitor:
    """安全性監視システム"""
    
    def __init__(self):
        self.unsafe_contexts = ["driving", "operating_machinery"]
        self.restricted_commands = {
            "driving": [CommandType.CODE_EXECUTE, CommandType.FILE_SYNC],
            "walking": [CommandType.CODE_EXECUTE],
            "bathing": [CommandType.FILE_SYNC]
        }
        
    def is_command_safe(self, command: DeviceCommand) -> tuple[bool, str]:
        """コマンドの安全性を確認"""
        context = command.safety_context
        
        if context in self.unsafe_contexts:
            return False, f"'{context}'中は操作が制限されています"
            
        if context in self.restricted_commands:
            restricted = self.restricted_commands[context]
            if command.command_type in restricted:
                return False, f"'{context}'中は{command.command_type.value}が制限されています"
                
        return True, "安全"


class DiscordMobileBridge(commands.Bot):
    """Discord経由のモバイル連携ブリッジ"""
    
    def __init__(self, command_prefix='!', **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents, **kwargs)
        
        self.safety_monitor = SafetyMonitor()
        self.active_devices = {}
        self.command_queue = asyncio.Queue()
        self.sync_channel_id = None
        
        # WD122プロジェクトとの連携設定
        self.multiagent_channel_id = None
        self.agent_commands = {
            "president": self.handle_president_command,
            "worker": self.handle_worker_command,
            "analyst": self.handle_analyst_command
        }
        
    async def setup_hook(self):
        """起動時の初期設定"""
        # コマンドの登録
        self.add_command(self.mobile_exec)
        self.add_command(self.sync_files)
        self.add_command(self.create_task)
        self.add_command(self.status)
        self.add_command(self.emergency_stop)
        
        # バックグラウンドタスクの開始
        self.loop.create_task(self.process_command_queue())
        
    async def on_ready(self):
        """Bot準備完了"""
        print(f'{self.user} として接続しました')
        print(f'接続先サーバー: {len(self.guilds)}')
        
        # 同期チャンネルの設定
        if self.sync_channel_id:
            channel = self.get_channel(self.sync_channel_id)
            if channel:
                await channel.send("📱 モバイルブリッジが起動しました")
                
    @commands.command(name='mobile_exec')
    async def mobile_exec(self, ctx, *, code: str):
        """モバイルからコード実行"""
        # コンテキストの取得
        safety_context = await self.detect_context(ctx)
        
        command = DeviceCommand(
            id=f"cmd_{datetime.now().timestamp()}",
            source_device=DeviceType.MOBILE,
            target_device=DeviceType.PC,
            command_type=CommandType.CODE_EXECUTE,
            payload={"code": code, "language": "python"},
            timestamp=datetime.now(),
            safety_context=safety_context
        )
        
        # 安全性チェック
        is_safe, message = self.safety_monitor.is_command_safe(command)
        if not is_safe:
            await ctx.send(f"⚠️ {message}")
            return
            
        # コマンドをキューに追加
        await self.command_queue.put(command)
        await ctx.send("📤 コード実行リクエストを送信しました")
        
    @commands.command(name='sync_files')
    async def sync_files(self, ctx, direction: str = "pull"):
        """ファイル同期"""
        command = DeviceCommand(
            id=f"sync_{datetime.now().timestamp()}",
            source_device=DeviceType.MOBILE,
            target_device=DeviceType.PC,
            command_type=CommandType.FILE_SYNC,
            payload={"direction": direction, "files": []},
            timestamp=datetime.now()
        )
        
        await self.command_queue.put(command)
        await ctx.send(f"🔄 ファイル同期を開始しました（{direction}）")
        
    @commands.command(name='create_task')
    async def create_task(self, ctx, *, task_description: str):
        """タスク作成"""
        # 音声入力からの自動解析
        task_data = await self.parse_task_description(task_description)
        
        command = DeviceCommand(
            id=f"task_{datetime.now().timestamp()}",
            source_device=DeviceType.MOBILE,
            target_device=DeviceType.PC,
            command_type=CommandType.TASK_CREATE,
            payload=task_data,
            timestamp=datetime.now()
        )
        
        await self.command_queue.put(command)
        await ctx.send(f"✅ タスクを作成しました: {task_data['title']}")
        
    @commands.command(name='status')
    async def status(self, ctx):
        """ステータス確認"""
        status_info = await self.get_system_status()
        
        embed = discord.Embed(
            title="🖥️ システムステータス",
            color=discord.Color.green()
        )
        
        embed.add_field(name="PC", value=status_info.get("pc", "オフライン"), inline=True)
        embed.add_field(name="エージェント", value=status_info.get("agents", "待機中"), inline=True)
        embed.add_field(name="キュー", value=f"{self.command_queue.qsize()}件", inline=True)
        
        await ctx.send(embed=embed)
        
    @commands.command(name='emergency_stop')
    async def emergency_stop(self, ctx):
        """緊急停止"""
        command = DeviceCommand(
            id=f"stop_{datetime.now().timestamp()}",
            source_device=DeviceType.MOBILE,
            target_device=DeviceType.PC,
            command_type=CommandType.EMERGENCY_STOP,
            payload={"reason": "user_initiated"},
            timestamp=datetime.now(),
            priority=999  # 最高優先度
        )
        
        # キューの先頭に追加
        await self.command_queue.put(command)
        await ctx.send("🛑 緊急停止コマンドを送信しました")
        
    async def detect_context(self, ctx) -> str:
        """使用コンテキストを検出"""
        # 実際の実装では、デバイスのセンサー情報を使用
        # ここではシミュレーション
        hour = datetime.now().hour
        
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            return "commuting"
        elif 22 <= hour or hour <= 6:
            return "sleeping"
        else:
            return "working"
            
    async def parse_task_description(self, description: str) -> Dict[str, Any]:
        """タスク記述を解析"""
        # 簡易的な自然言語処理
        task_data = {
            "title": description[:50],
            "description": description,
            "priority": "medium",
            "tags": []
        }
        
        # キーワード検出
        if "緊急" in description or "至急" in description:
            task_data["priority"] = "high"
        if "会議" in description:
            task_data["tags"].append("meeting")
        if "締切" in description or "期限" in description:
            task_data["tags"].append("deadline")
            
        return task_data
        
    async def get_system_status(self) -> Dict[str, Any]:
        """システムステータスを取得"""
        status = {
            "pc": "オンライン" if self.active_devices.get(DeviceType.PC) else "オフライン",
            "agents": "稼働中" if self.multiagent_channel_id else "待機中",
            "last_sync": datetime.now().strftime("%H:%M:%S")
        }
        return status
        
    async def process_command_queue(self):
        """コマンドキューを処理"""
        while True:
            try:
                command = await self.command_queue.get()
                await self.execute_command(command)
            except Exception as e:
                print(f"コマンド処理エラー: {e}")
            await asyncio.sleep(0.1)
            
    async def execute_command(self, command: DeviceCommand):
        """コマンドを実行"""
        if command.command_type == CommandType.CODE_EXECUTE:
            await self.execute_code(command)
        elif command.command_type == CommandType.FILE_SYNC:
            await self.sync_files_handler(command)
        elif command.command_type == CommandType.TASK_CREATE:
            await self.create_task_handler(command)
        elif command.command_type == CommandType.EMERGENCY_STOP:
            await self.emergency_stop_handler(command)
            
    async def execute_code(self, command: DeviceCommand):
        """コード実行ハンドラー"""
        # PC側のエージェントにコマンドを転送
        if self.sync_channel_id:
            channel = self.get_channel(self.sync_channel_id)
            if channel:
                embed = discord.Embed(
                    title="📱 モバイルからのコード実行",
                    description=f"```python\n{command.payload['code']}\n```",
                    color=discord.Color.blue()
                )
                await channel.send(embed=embed)
                
    async def sync_files_handler(self, command: DeviceCommand):
        """ファイル同期ハンドラー"""
        # 実装省略
        pass
        
    async def create_task_handler(self, command: DeviceCommand):
        """タスク作成ハンドラー"""
        # マルチエージェントシステムと連携
        if self.multiagent_channel_id:
            channel = self.get_channel(self.multiagent_channel_id)
            if channel:
                task_info = command.payload
                message = f"新規タスク: {task_info['title']} (優先度: {task_info['priority']})"
                await channel.send(message)
                
    async def emergency_stop_handler(self, command: DeviceCommand):
        """緊急停止ハンドラー"""
        # 全てのアクティブなプロセスを停止
        for device in self.active_devices:
            await self.send_stop_signal(device)
            
        if self.sync_channel_id:
            channel = self.get_channel(self.sync_channel_id)
            if channel:
                await channel.send("🛑 システムを緊急停止しました")
                
    async def send_stop_signal(self, device: DeviceType):
        """停止信号を送信"""
        # 実装省略
        pass
        
    # WD122プロジェクトとの連携メソッド
    async def handle_president_command(self, command: str):
        """presidentエージェントのコマンド処理"""
        # 実装省略
        pass
        
    async def handle_worker_command(self, command: str):
        """workerエージェントのコマンド処理"""
        # 実装省略
        pass
        
    async def handle_analyst_command(self, command: str):
        """analystエージェントのコマンド処理"""
        # 実装省略
        pass


class VoiceInterface:
    """音声入力インターフェース"""
    
    def __init__(self, discord_bridge: DiscordMobileBridge):
        self.bridge = discord_bridge
        self.voice_commands = {
            "コード実行": self.execute_code_voice,
            "タスク作成": self.create_task_voice,
            "ステータス確認": self.check_status_voice,
            "同期": self.sync_files_voice,
            "停止": self.emergency_stop_voice
        }
        
    async def process_voice_command(self, transcript: str, context: str) -> str:
        """音声コマンドを処理"""
        # コマンドの識別
        for keyword, handler in self.voice_commands.items():
            if keyword in transcript:
                return await handler(transcript, context)
                
        return "コマンドが認識できませんでした"
        
    async def execute_code_voice(self, transcript: str, context: str) -> str:
        """音声でコード実行"""
        if context == "driving":
            return "運転中はコード実行できません"
            
        # コード部分の抽出（簡易実装）
        code = transcript.replace("コード実行", "").strip()
        
        command = DeviceCommand(
            id=f"voice_{datetime.now().timestamp()}",
            source_device=DeviceType.VOICE_ASSISTANT,
            target_device=DeviceType.PC,
            command_type=CommandType.CODE_EXECUTE,
            payload={"code": code, "language": "python"},
            timestamp=datetime.now(),
            safety_context=context
        )
        
        await self.bridge.command_queue.put(command)
        return "コード実行リクエストを送信しました"
        
    async def create_task_voice(self, transcript: str, context: str) -> str:
        """音声でタスク作成"""
        # タスク内容の抽出
        task_description = transcript.replace("タスク作成", "").strip()
        
        command = DeviceCommand(
            id=f"voice_task_{datetime.now().timestamp()}",
            source_device=DeviceType.VOICE_ASSISTANT,
            target_device=DeviceType.PC,
            command_type=CommandType.TASK_CREATE,
            payload=await self.bridge.parse_task_description(task_description),
            timestamp=datetime.now()
        )
        
        await self.bridge.command_queue.put(command)
        return f"タスクを作成しました: {task_description[:30]}..."
        
    async def check_status_voice(self, transcript: str, context: str) -> str:
        """音声でステータス確認"""
        status = await self.bridge.get_system_status()
        return f"PC: {status['pc']}, エージェント: {status['agents']}"
        
    async def sync_files_voice(self, transcript: str, context: str) -> str:
        """音声でファイル同期"""
        if context == "driving":
            return "運転中はファイル同期できません"
            
        direction = "pull" if "取得" in transcript else "push"
        
        command = DeviceCommand(
            id=f"voice_sync_{datetime.now().timestamp()}",
            source_device=DeviceType.VOICE_ASSISTANT,
            target_device=DeviceType.PC,
            command_type=CommandType.FILE_SYNC,
            payload={"direction": direction},
            timestamp=datetime.now(),
            safety_context=context
        )
        
        await self.bridge.command_queue.put(command)
        return f"ファイル同期を開始しました（{direction}）"
        
    async def emergency_stop_voice(self, transcript: str, context: str) -> str:
        """音声で緊急停止"""
        command = DeviceCommand(
            id=f"voice_stop_{datetime.now().timestamp()}",
            source_device=DeviceType.VOICE_ASSISTANT,
            target_device=DeviceType.PC,
            command_type=CommandType.EMERGENCY_STOP,
            payload={"reason": "voice_command"},
            timestamp=datetime.now(),
            priority=999
        )
        
        await self.bridge.command_queue.put(command)
        return "緊急停止を実行しました"


async def main():
    """メイン実行関数"""
    # 環境変数から設定を読み込み
    token = os.getenv("DISCORD_BOT_TOKEN")
    sync_channel_id = int(os.getenv("SYNC_CHANNEL_ID", "0"))
    multiagent_channel_id = int(os.getenv("MULTIAGENT_CHANNEL_ID", "0"))
    
    # Botの初期化
    bot = DiscordMobileBridge()
    bot.sync_channel_id = sync_channel_id
    bot.multiagent_channel_id = multiagent_channel_id
    
    # 音声インターフェースの初期化
    voice_interface = VoiceInterface(bot)
    
    # Bot起動
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())