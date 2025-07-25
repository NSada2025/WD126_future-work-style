#!/usr/bin/env python3
"""
ハンズフリー開発のための音声入力インターフェース
入浴中・運転中でも安全にweb開発可能なシステム
"""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import speech_recognition as sr
import pyttsx3


class Context(Enum):
    """使用コンテキスト"""
    DESK = "desk"
    WALKING = "walking"
    DRIVING = "driving"
    BATHING = "bathing"
    COOKING = "cooking"
    EXERCISING = "exercising"


class CommandCategory(Enum):
    """コマンドカテゴリ"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    FILE_OPERATION = "file_operation"
    GIT_OPERATION = "git_operation"
    QUERY = "query"
    CONFIRMATION = "confirmation"


@dataclass
class VoiceCommand:
    """音声コマンド"""
    raw_text: str
    category: CommandCategory
    action: str
    parameters: Dict[str, Any]
    context: Context
    timestamp: datetime
    confidence: float


class SafetyValidator:
    """安全性検証システム"""
    
    def __init__(self):
        # コンテキスト別の許可されたコマンド
        self.allowed_commands = {
            Context.DRIVING: [
                CommandCategory.QUERY,
                CommandCategory.DOCUMENTATION,
                CommandCategory.CODE_REVIEW
            ],
            Context.BATHING: [
                CommandCategory.CODE_GENERATION,
                CommandCategory.DOCUMENTATION,
                CommandCategory.QUERY
            ],
            Context.WALKING: [
                CommandCategory.QUERY,
                CommandCategory.DOCUMENTATION,
                CommandCategory.CODE_REVIEW
            ],
            Context.DESK: [  # 全て許可
                cat for cat in CommandCategory
            ]
        }
        
        # 危険な操作の定義
        self.dangerous_operations = {
            "delete": ["削除", "消去", "remove", "rm"],
            "force": ["強制", "force", "-f"],
            "recursive": ["再帰", "recursive", "-r"],
            "overwrite": ["上書き", "overwrite", "replace"]
        }
        
    def validate_command(self, command: VoiceCommand) -> Tuple[bool, str]:
        """コマンドの安全性を検証"""
        # コンテキストチェック
        if command.context not in self.allowed_commands:
            return True, "未知のコンテキスト"
            
        allowed = self.allowed_commands[command.context]
        if command.category not in allowed:
            return False, f"{command.context.value}中は{command.category.value}操作は制限されています"
            
        # 危険操作チェック
        if command.context != Context.DESK:
            for op_type, keywords in self.dangerous_operations.items():
                for keyword in keywords:
                    if keyword in command.raw_text.lower():
                        return False, f"{command.context.value}中は{op_type}操作は許可されていません"
                        
        # 確認が必要な操作
        if self._requires_confirmation(command):
            return True, "confirmation_required"
            
        return True, "safe"
        
    def _requires_confirmation(self, command: VoiceCommand) -> bool:
        """確認が必要かチェック"""
        confirmation_keywords = ["本番", "production", "マスター", "master", "deploy"]
        return any(keyword in command.raw_text.lower() for keyword in confirmation_keywords)


class VoiceParser:
    """音声コマンドパーサー"""
    
    def __init__(self):
        self.command_patterns = {
            CommandCategory.CODE_GENERATION: [
                (r"(.+?)関数を?作成", "create_function"),
                (r"(.+?)クラスを?実装", "create_class"),
                (r"(.+?)のテストを?書いて", "create_test"),
                (r"(.+?)コンポーネントを?作って", "create_component")
            ],
            CommandCategory.CODE_REVIEW: [
                (r"(.+?)をレビュー", "review_code"),
                (r"(.+?)の問題点を?教えて", "find_issues"),
                (r"(.+?)を最適化", "optimize_code")
            ],
            CommandCategory.DEBUGGING: [
                (r"エラーを?修正", "fix_error"),
                (r"バグを?探して", "find_bug"),
                (r"(.+?)が動かない", "debug_issue")
            ],
            CommandCategory.DOCUMENTATION: [
                (r"(.+?)の説明を?書いて", "write_docs"),
                (r"README(?:を)?更新", "update_readme"),
                (r"コメントを?追加", "add_comments")
            ],
            CommandCategory.FILE_OPERATION: [
                (r"(.+?)ファイルを?開いて", "open_file"),
                (r"(.+?)を保存", "save_file"),
                (r"(.+?)に移動", "navigate_to")
            ],
            CommandCategory.GIT_OPERATION: [
                (r"変更を?コミット", "git_commit"),
                (r"(.+?)ブランチに?切り替え", "git_checkout"),
                (r"プッシュして", "git_push")
            ]
        }
        
    def parse(self, text: str, context: Context) -> Optional[VoiceCommand]:
        """テキストをコマンドに変換"""
        text = text.strip()
        
        for category, patterns in self.command_patterns.items():
            for pattern, action in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    parameters = self._extract_parameters(match, text)
                    return VoiceCommand(
                        raw_text=text,
                        category=category,
                        action=action,
                        parameters=parameters,
                        context=context,
                        timestamp=datetime.now(),
                        confidence=0.8  # 仮の値
                    )
                    
        # パターンにマッチしない場合は一般的なクエリとして扱う
        return VoiceCommand(
            raw_text=text,
            category=CommandCategory.QUERY,
            action="general_query",
            parameters={"query": text},
            context=context,
            timestamp=datetime.now(),
            confidence=0.6
        )
        
    def _extract_parameters(self, match: re.Match, text: str) -> Dict[str, Any]:
        """パラメータを抽出"""
        params = {}
        
        # マッチグループから抽出
        groups = match.groups()
        if groups:
            params["target"] = groups[0]
            
        # 追加のコンテキスト情報
        if "TypeScript" in text or "TS" in text:
            params["language"] = "typescript"
        elif "Python" in text:
            params["language"] = "python"
        elif "React" in text:
            params["framework"] = "react"
            
        return params


class CodeGenerator:
    """コード生成エンジン"""
    
    def __init__(self):
        self.templates = {
            "create_function": self._generate_function,
            "create_class": self._generate_class,
            "create_test": self._generate_test,
            "create_component": self._generate_component
        }
        
    async def generate(self, command: VoiceCommand) -> str:
        """コマンドからコードを生成"""
        action = command.action
        if action in self.templates:
            return await self.templates[action](command.parameters)
        return f"// {command.action} is not implemented yet"
        
    async def _generate_function(self, params: Dict[str, Any]) -> str:
        """関数を生成"""
        name = params.get("target", "newFunction")
        language = params.get("language", "javascript")
        
        if language == "python":
            return f"""def {name}():
    \"\"\"
    {name}関数の実装
    \"\"\"
    # TODO: 実装を追加
    pass"""
        else:
            return f"""function {name}() {{
    // {name}関数の実装
    // TODO: 実装を追加
}}"""
        
    async def _generate_class(self, params: Dict[str, Any]) -> str:
        """クラスを生成"""
        name = params.get("target", "NewClass")
        language = params.get("language", "javascript")
        
        if language == "python":
            return f"""class {name}:
    \"\"\"
    {name}クラスの実装
    \"\"\"
    
    def __init__(self):
        # TODO: 初期化処理
        pass"""
        else:
            return f"""class {name} {{
    constructor() {{
        // TODO: 初期化処理
    }}
}}"""
        
    async def _generate_test(self, params: Dict[str, Any]) -> str:
        """テストを生成"""
        target = params.get("target", "function")
        return f"""describe('{target}', () => {{
    it('should work correctly', () => {{
        // TODO: テストを実装
        expect(true).toBe(true);
    }});
}});"""
        
    async def _generate_component(self, params: Dict[str, Any]) -> str:
        """コンポーネントを生成"""
        name = params.get("target", "NewComponent")
        framework = params.get("framework", "react")
        
        if framework == "react":
            return f"""import React from 'react';

const {name} = () => {{
    return (
        <div>
            <h1>{name}</h1>
            {{/* TODO: コンポーネントの実装 */}}
        </div>
    );
}};

export default {name};"""
        return f"// {framework} component generation not implemented"


class VoiceFeedback:
    """音声フィードバックシステム"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # 読み上げ速度
        self.engine.setProperty('volume', 0.8)  # 音量
        
        # コンテキスト別の読み上げ設定
        self.context_settings = {
            Context.DRIVING: {
                "verbose": False,
                "code_reading": False,
                "summary_only": True
            },
            Context.BATHING: {
                "verbose": True,
                "code_reading": False,
                "summary_only": False
            },
            Context.DESK: {
                "verbose": True,
                "code_reading": True,
                "summary_only": False
            }
        }
        
    async def provide_feedback(self, message: str, context: Context, message_type: str = "info"):
        """フィードバックを提供"""
        settings = self.context_settings.get(context, self.context_settings[Context.DESK])
        
        if message_type == "code" and not settings["code_reading"]:
            message = "コードを生成しました"
        elif settings["summary_only"]:
            message = self._summarize(message)
            
        # 非同期で読み上げ
        await self._speak_async(message)
        
    def _summarize(self, message: str) -> str:
        """メッセージを要約"""
        if len(message) > 50:
            return message[:50] + "...以下省略"
        return message
        
    async def _speak_async(self, text: str):
        """非同期で音声出力"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._speak, text)
        
    def _speak(self, text: str):
        """音声出力"""
        self.engine.say(text)
        self.engine.runAndWait()


class VoiceDevelopmentInterface:
    """音声開発インターフェース統合システム"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.parser = VoiceParser()
        self.validator = SafetyValidator()
        self.generator = CodeGenerator()
        self.feedback = VoiceFeedback()
        self.context = Context.DESK
        self.command_history = []
        
    async def start_listening(self):
        """音声認識を開始"""
        print("🎤 音声開発インターフェースを起動しました")
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
        while True:
            try:
                # 音声入力を待機
                audio = await self._listen_async()
                if audio:
                    # 音声をテキストに変換
                    text = await self._recognize_async(audio)
                    if text:
                        # コマンドを処理
                        await self.process_voice_input(text)
                        
            except Exception as e:
                print(f"エラー: {e}")
                await self.feedback.provide_feedback(
                    "エラーが発生しました", 
                    self.context,
                    "error"
                )
                
    async def _listen_async(self) -> Optional[sr.AudioData]:
        """非同期で音声を聞く"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._listen)
        
    def _listen(self) -> Optional[sr.AudioData]:
        """音声を聞く"""
        try:
            with self.microphone as source:
                print("聞いています...")
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                return audio
        except sr.WaitTimeoutError:
            return None
            
    async def _recognize_async(self, audio: sr.AudioData) -> Optional[str]:
        """非同期で音声認識"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._recognize, audio)
        
    def _recognize(self, audio: sr.AudioData) -> Optional[str]:
        """音声認識"""
        try:
            text = self.recognizer.recognize_google(audio, language="ja-JP")
            print(f"認識: {text}")
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"音声認識エラー: {e}")
            return None
            
    async def process_voice_input(self, text: str):
        """音声入力を処理"""
        # コンテキスト更新チェック
        new_context = self._detect_context_change(text)
        if new_context:
            self.context = new_context
            await self.feedback.provide_feedback(
                f"コンテキストを{new_context.value}に変更しました",
                self.context
            )
            return
            
        # コマンドをパース
        command = self.parser.parse(text, self.context)
        if not command:
            await self.feedback.provide_feedback(
                "コマンドを認識できませんでした",
                self.context
            )
            return
            
        # 安全性検証
        is_safe, message = self.validator.validate_command(command)
        if not is_safe:
            await self.feedback.provide_feedback(message, self.context, "warning")
            return
            
        if message == "confirmation_required":
            await self.feedback.provide_feedback(
                "この操作には確認が必要です。続行しますか？",
                self.context,
                "confirmation"
            )
            # TODO: 確認待ち処理
            return
            
        # コマンド実行
        await self.execute_command(command)
        
    def _detect_context_change(self, text: str) -> Optional[Context]:
        """コンテキスト変更を検出"""
        context_keywords = {
            "運転": Context.DRIVING,
            "お風呂": Context.BATHING,
            "歩き": Context.WALKING,
            "デスク": Context.DESK,
            "料理": Context.COOKING,
            "運動": Context.EXERCISING
        }
        
        for keyword, context in context_keywords.items():
            if f"{keyword}モード" in text or f"{keyword}に切り替え" in text:
                return context
                
        return None
        
    async def execute_command(self, command: VoiceCommand):
        """コマンドを実行"""
        self.command_history.append(command)
        
        if command.category == CommandCategory.CODE_GENERATION:
            # コード生成
            code = await self.generator.generate(command)
            await self.feedback.provide_feedback(code, self.context, "code")
            
            # ファイルに保存する場合
            if self.context == Context.DESK:
                # TODO: 実際のファイル保存処理
                pass
                
        elif command.category == CommandCategory.QUERY:
            # 一般的なクエリ
            response = f"{command.parameters.get('query')}について調べています..."
            await self.feedback.provide_feedback(response, self.context)
            
        else:
            # その他のコマンド
            response = f"{command.action}を実行しています"
            await self.feedback.provide_feedback(response, self.context)


async def demo_voice_interface():
    """音声インターフェースのデモ"""
    interface = VoiceDevelopmentInterface()
    
    print("=== 音声開発インターフェース デモ ===")
    print("利用可能なコマンド例:")
    print("- 「Userクラスを作成」")
    print("- 「calculateTotal関数を実装」")
    print("- 「Headerコンポーネントを作って」")
    print("- 「運転モードに切り替え」")
    print("- 「エラーを修正」")
    
    # デモ用のシミュレーション
    demo_commands = [
        ("運転モードに切り替え", Context.DESK),
        ("データ解析関数を作成", Context.DRIVING),
        ("READMEを更新", Context.DRIVING),
        ("デスクモードに切り替え", Context.DRIVING),
        ("Pythonでユーザークラスを実装", Context.DESK)
    ]
    
    for text, current_context in demo_commands:
        print(f"\n入力: {text} (コンテキスト: {current_context.value})")
        interface.context = current_context
        await interface.process_voice_input(text)
        await asyncio.sleep(1)


if __name__ == "__main__":
    # 実際の音声認識を使用する場合
    # interface = VoiceDevelopmentInterface()
    # asyncio.run(interface.start_listening())
    
    # デモ実行
    asyncio.run(demo_voice_interface())