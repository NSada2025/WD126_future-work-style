#!/usr/bin/env python3
"""
Claude Code Integration for Vive Paradigm Implementer

Claude Code環境での統合使用を実現するメインインターフェース

Author: NSada2025
Date: 2025-07-25
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.vive_agent import ViveParadigmImplementer


class ClaudeCodeViveAgent:
    """Claude Code環境用のViveエージェントラッパー"""
    
    def __init__(self):
        """エージェントを初期化"""
        self.output_dir = "./vive_output"
        self.agent = ViveParadigmImplementer(self.output_dir)
        self.session_history = []
        
        print("🌟 Vive Paradigm Implementer (Claude Code統合版) 起動")
        print("💡 使用方法: vive_create('アイデア', technology='web', time_limit=10)")
    
    def vive_create(self, 
                   idea: str, 
                   technology: str = "auto",
                   time_limit: int = 10,
                   complexity: str = "auto",
                   generate_guide: bool = True) -> Dict:
        """
        プロトタイプを作成（Claude Code用インターフェース）
        
        Args:
            idea: 実装したいアイデア  
            technology: 技術スタック (web, python, data_viz, api, auto)
            time_limit: 制限時間（分）
            complexity: 複雑さ (simple, medium, advanced, auto)
            generate_guide: 学習ガイドを自動生成するか
            
        Returns:
            作成結果とパス情報
        """
        print(f"🚀 Vive プロトタイプ作成: '{idea}'")
        
        try:
            # プロトタイプ作成
            result = self.agent.create_prototype(
                idea=idea,
                time_limit=time_limit,
                technology=technology,
                complexity=complexity
            )
            
            # セッション履歴に記録
            session_entry = {
                "idea": idea,
                "technology": technology,
                "result": result,
                "timestamp": result.get("created_at")
            }
            self.session_history.append(session_entry)
            
            # 学習ガイド生成
            if generate_guide and result.get("success"):
                print("📚 学習ガイドを生成中...")
                guide = self.agent.generate_learning_guide(result)
                result["learning_guide_path"] = os.path.join(
                    result["output_dir"], "learning_guide.md"
                )
            
            # 次のステップ提案
            next_steps = self.agent.suggest_next_steps(result)
            result["suggested_next_steps"] = next_steps
            
            # Claude Code用の簡潔な結果表示
            self._display_claude_result(result)
            
            return result
            
        except Exception as e:
            error_msg = f"❌ エラーが発生しました: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}
    
    def vive_improve(self, improvement_type: str = "ui") -> Dict:
        """
        最後に作成したプロトタイプを改善
        
        Args:
            improvement_type: 改善タイプ (ui, feature, error_handling)
            
        Returns:
            改善結果
        """
        if not self.session_history:
            print("❌ 改善対象のプロトタイプがありません。まずvive_create()を実行してください。")
            return {"success": False, "error": "No prototype to improve"}
        
        last_session = self.session_history[-1]
        last_result = last_session["result"]
        
        if not last_result.get("success"):
            print("❌ 最後のプロトタイプが未完成のため改善できません。")
            return {"success": False, "error": "Last prototype was not successful"}
        
        print(f"⚡ プロトタイプ改善中: {improvement_type}")
        
        try:
            improvement_result = self.agent.quick_improve(last_result, improvement_type)
            
            # 結果表示
            if improvement_result.get("success"):
                print(f"✨ 改善完了! ({improvement_result.get('improvement_time_minutes', 0):.1f}分)")
                for change in improvement_result.get("changes", []):
                    print(f"  • {change}")
            else:
                print("⚠️ 改善に時間がかかりました")
            
            return improvement_result
            
        except Exception as e:
            error_msg = f"❌ 改善エラー: {str(e)}"
            print(error_msg)
            return {"success": False, "error": error_msg}
    
    def vive_next_steps(self) -> None:
        """最後のプロトタイプの次のステップを表示"""
        if not self.session_history:
            print("❌ プロトタイプがありません。まずvive_create()を実行してください。")
            return
        
        last_result = self.session_history[-1]["result"]
        next_steps = last_result.get("suggested_next_steps", [])
        
        if not next_steps:
            next_steps = self.agent.suggest_next_steps(last_result)
        
        print("\\n🔮 次のステップ提案:")
        for i, step in enumerate(next_steps[:5], 1):
            print(f"{i}. **{step['title']}** ({step['estimated_time']}分)")
            print(f"   {step['description']}")
            print(f"   📚 学習価値: {step['learning_value']}")
            print()
    
    def vive_history(self) -> None:
        """セッション履歴を表示"""
        if not self.session_history:
            print("📋 履歴はありません。")
            return
        
        print("\\n📚 Vive セッション履歴:")
        for i, session in enumerate(self.session_history, 1):
            result = session["result"]
            status = "✅ 成功" if result.get("success") else "⚠️ 部分完成"
            print(f"{i}. {session['idea']} - {status}")
            print(f"   技術: {session['technology']}, 時間: {result.get('creation_time_minutes', 0):.1f}分")
            if result.get("output_dir"):
                print(f"   📁 出力: {result['output_dir']}")
    
    def vive_open_last(self) -> Optional[str]:
        """最後に作成したプロトタイプのディレクトリパスを返す"""
        if not self.session_history:
            print("❌ プロトタイプがありません。")
            return None
        
        last_result = self.session_history[-1]["result"]
        output_dir = last_result.get("output_dir")
        
        if output_dir and os.path.exists(output_dir):
            print(f"📁 最新プロトタイプ: {output_dir}")
            
            # ファイル一覧表示
            files = last_result.get("files_created", [])
            print("📄 作成ファイル:")
            for file in files:
                file_path = os.path.join(output_dir, file)
                if os.path.exists(file_path):
                    print(f"  • {file}")
            
            return output_dir
        else:
            print("❌ プロトタイプディレクトリが見つかりません。")
            return None
    
    def vive_stats(self) -> None:
        """統計情報を表示"""
        if not self.session_history:
            print("📊 統計情報がありません。")
            return
        
        total_prototypes = len(self.session_history)
        successful = sum(1 for s in self.session_history if s["result"].get("success"))
        
        total_time = sum(s["result"].get("creation_time_minutes", 0) for s in self.session_history)
        avg_time = total_time / total_prototypes if total_prototypes > 0 else 0
        
        tech_count = {}
        for session in self.session_history:
            tech = session["result"].get("technology", "unknown")
            tech_count[tech] = tech_count.get(tech, 0) + 1
        
        print("\\n📊 Vive統計情報:")
        print(f"  • 総プロトタイプ数: {total_prototypes}")
        print(f"  • 成功率: {(successful/total_prototypes)*100:.1f}% ({successful}/{total_prototypes})")
        print(f"  • 平均作成時間: {avg_time:.1f}分")
        print(f"  • 総作成時間: {total_time:.1f}分")
        
        print("\\n  技術別統計:")
        for tech, count in tech_count.items():
            print(f"    - {tech}: {count}個")
    
    def _display_claude_result(self, result: Dict) -> None:
        """Claude Code用の結果表示"""
        if result.get("success"):
            print(f"\\n✅ プロトタイプ完成! ({result.get('creation_time_minutes', 0):.1f}分)")
        else:
            print(f"\\n⚠️ プロトタイプ部分完成 ({result.get('creation_time_minutes', 0):.1f}分)")
        
        # 作成ファイル
        files = result.get("files_created", [])
        if files:
            print(f"📁 作成ファイル ({len(files)}個):")
            for file in files:
                print(f"  • {file}")
        
        # 実行方法
        run_command = result.get("executable_command")
        if run_command:
            print(f"\\n🏃 実行方法: {run_command}")
        
        # 出力先
        output_dir = result.get("output_dir")
        if output_dir:
            print(f"📂 出力先: {output_dir}")
        
        # 次のステップをさりげなく提案
        next_steps = result.get("suggested_next_steps", [])
        if next_steps:
            print(f"\\n💡 次のステップ: vive_next_steps() で {len(next_steps)}個の改善提案を確認")
        
        print("📚 学習ガイド: learning_guide.md をチェック")


# Claude Code環境での使用を簡単にするためのグローバル変数とヘルパー関数
_vive_agent_instance = None

def vive_init():
    """Viveエージェントを初期化"""
    global _vive_agent_instance
    if _vive_agent_instance is None:
        _vive_agent_instance = ClaudeCodeViveAgent()
    return _vive_agent_instance

def vive_create(idea: str, **kwargs) -> Dict:
    """プロトタイプ作成（グローバル関数）"""
    agent = vive_init()
    return agent.vive_create(idea, **kwargs)

def vive_improve(improvement_type: str = "ui") -> Dict:
    """プロトタイプ改善（グローバル関数）"""
    agent = vive_init()
    return agent.vive_improve(improvement_type)

def vive_next_steps():
    """次のステップ表示（グローバル関数）"""
    agent = vive_init()
    agent.vive_next_steps()

def vive_history():
    """履歴表示（グローバル関数）"""
    agent = vive_init()
    agent.vive_history()

def vive_open_last():
    """最新プロトタイプを開く（グローバル関数）"""
    agent = vive_init()
    return agent.vive_open_last()

def vive_stats():
    """統計表示（グローバル関数）"""
    agent = vive_init()
    agent.vive_stats()

def vive_help():
    """ヘルプ表示"""
    print("""
🌟 Vive Paradigm Implementer - Claude Code統合版

📋 基本コマンド:
  vive_create('アイデア')           - プロトタイプを作成
  vive_improve('ui')               - 最新プロトタイプを改善
  vive_next_steps()               - 次のステップを表示
  vive_open_last()                - 最新プロトタイプを開く

📊 管理コマンド:
  vive_history()                  - 作成履歴を表示
  vive_stats()                    - 統計情報を表示
  vive_help()                     - このヘルプを表示

💡 使用例:
  vive_create('タスク管理アプリ', technology='web', time_limit=8)
  vive_create('データ可視化', technology='data_viz')
  vive_improve('feature')  # ui, feature, error_handling

🎯 技術オプション: web, python, data_viz, api
⏰ デフォルト制限時間: 10分
📚 自動生成: 学習ガイド + 次のステップ提案
""")


if __name__ == "__main__":
    # デモ実行
    print("🎯 Claude Code統合版デモ")
    
    # ヘルプ表示
    vive_help()
    
    # サンプル実行
    print("\\n" + "="*50)
    print("📝 サンプル実行")
    
    result = vive_create("簡単な計算機", technology="web", time_limit=8)
    
    if result.get("success"):
        print("\\n⚡ 改善テスト")
        vive_improve("ui")
        
        print("\\n🔮 次のステップ")
        vive_next_steps()
    
    print("\\n📊 統計")
    vive_stats()
    
    print("\\n✅ デモ完了!")