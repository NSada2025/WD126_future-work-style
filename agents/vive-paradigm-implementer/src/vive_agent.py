#!/usr/bin/env python3
"""
Vive Paradigm Implementer Agent
体験駆動型学習を実現するメインエージェント

Author: NSada2025
Date: 2025-07-25
Version: 1.0.0
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
try:
    from .prototype_generator import PrototypeGenerator
    from .learning_guide import LearningGuideGenerator
    from .template_manager import TemplateManager
except ImportError:
    from prototype_generator import PrototypeGenerator
    from learning_guide import LearningGuideGenerator
    from template_manager import TemplateManager


class ViveParadigmImplementer:
    """
    Vive Paradigm (体験から理解へ) を実践するエージェント
    10分以内でプロトタイプを作成し、体験を通じた学習を促進
    """
    
    def __init__(self, output_dir: str = "./output"):
        """
        エージェントを初期化
        
        Args:
            output_dir: 出力ディレクトリのパス
        """
        self.output_dir = output_dir
        self.prototype_generator = PrototypeGenerator()
        self.learning_guide = LearningGuideGenerator()
        self.template_manager = TemplateManager()
        
        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        
        print("🌟 Vive Paradigm Implementer が起動しました")
        print("📝 理念: 完璧より速度、理論より体験")
        
    def create_prototype(self, 
                        idea: str, 
                        time_limit: int = 10,
                        technology: str = "web",
                        complexity: str = "simple") -> Dict:
        """
        アイデアから10分以内でプロトタイプを作成
        
        Args:
            idea: 実装したいアイデアの説明
            time_limit: 制限時間（分）
            technology: 使用技術 (web, python, data_viz, api)
            complexity: 複雑さレベル (simple, medium, advanced)
            
        Returns:
            プロトタイプの情報を含む辞書
        """
        start_time = time.time()
        
        print(f"🚀 プロトタイプ作成開始: '{idea}'")
        print(f"⏰ 制限時間: {time_limit}分")
        print(f"💻 技術スタック: {technology}")
        
        try:
            # テンプレートを選択
            template_info = self.template_manager.select_template(
                idea, technology, complexity
            )
            
            # プロトタイプを生成
            prototype = self.prototype_generator.generate(
                idea=idea,
                template_info=template_info,
                time_limit=time_limit
            )
            
            # 実行時間を計算
            elapsed_time = (time.time() - start_time) / 60
            
            # 結果をまとめる
            result = {
                "idea": idea,
                "technology": technology,
                "complexity": complexity,
                "template_used": template_info["name"],
                "files_created": prototype["files"],
                "executable_command": prototype.get("run_command"),
                "creation_time_minutes": round(elapsed_time, 2),
                "success": elapsed_time <= time_limit,
                "output_dir": prototype["output_path"],
                "created_at": datetime.now().isoformat(),
                "learning_points": prototype.get("learning_points", [])
            }
            
            # 結果を保存
            self._save_prototype_result(result)
            
            if result["success"]:
                print(f"✅ プロトタイプ完成! ({elapsed_time:.1f}分)")
                print(f"📁 出力先: {result['output_dir']}")
                if result["executable_command"]:
                    print(f"🏃 実行コマンド: {result['executable_command']}")
            else:
                print(f"⚠️  制限時間オーバー ({elapsed_time:.1f}分 > {time_limit}分)")
                print("🔧 基本機能は実装済み、改善余地があります")
                
            return result
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {str(e)}")
            return {
                "idea": idea,
                "success": False,
                "error": str(e),
                "creation_time_minutes": (time.time() - start_time) / 60
            }
    
    def generate_learning_guide(self, prototype_result: Dict) -> Dict:
        """
        プロトタイプから学習ガイドを生成
        
        Args:
            prototype_result: create_prototypeの結果
            
        Returns:
            学習ガイドの情報
        """
        print("📚 学習ガイドを生成中...")
        
        guide = self.learning_guide.create_guide(prototype_result)
        
        # ガイドを保存
        guide_path = os.path.join(
            prototype_result.get("output_dir", self.output_dir),
            "learning_guide.md"
        )
        
        with open(guide_path, "w", encoding="utf-8") as f:
            f.write(guide["markdown_content"])
        
        print(f"📖 学習ガイド作成完了: {guide_path}")
        
        return guide
    
    def suggest_next_steps(self, prototype_result: Dict) -> List[Dict]:
        """
        次のステップを5分単位で提案
        
        Args:
            prototype_result: create_prototypeの結果
            
        Returns:
            次のステップのリスト
        """
        print("🔄 次のステップを提案中...")
        
        steps = []
        
        # 基本的な改善提案
        if prototype_result.get("success"):
            steps.extend([
                {
                    "title": "UIの改善",
                    "description": "見た目をより魅力的にする",
                    "estimated_time": 5,
                    "difficulty": "easy",
                    "learning_value": "CSS/デザインの基礎"
                },
                {
                    "title": "機能追加",
                    "description": "実用性を高める新機能を追加",
                    "estimated_time": 10,
                    "difficulty": "medium", 
                    "learning_value": "機能設計・実装スキル"
                },
                {
                    "title": "データ永続化",
                    "description": "データを保存・読み込みできるようにする",
                    "estimated_time": 15,
                    "difficulty": "medium",
                    "learning_value": "データベース・ストレージの理解"
                }
            ])
        else:
            steps.extend([
                {
                    "title": "基本機能の完成",
                    "description": "最低限の動作を確実にする",
                    "estimated_time": 5,
                    "difficulty": "easy",
                    "learning_value": "デバッグ・問題解決スキル"
                },
                {
                    "title": "エラー処理の追加",
                    "description": "予期しない入力への対応",
                    "estimated_time": 10,
                    "difficulty": "medium",
                    "learning_value": "例外処理・堅牢性"
                }
            ])
        
        # テクノロジー固有の提案
        tech = prototype_result.get("technology", "web")
        if tech == "web":
            steps.append({
                "title": "レスポンシブデザイン",
                "description": "モバイル対応を追加",
                "estimated_time": 10,
                "difficulty": "medium",
                "learning_value": "モバイルファースト設計"
            })
        elif tech == "python":
            steps.append({
                "title": "コマンドライン引数",
                "description": "パラメータを外部から指定可能にする",
                "estimated_time": 5,
                "difficulty": "easy",
                "learning_value": "CLI設計・argparse"
            })
        
        print(f"💡 {len(steps)}個の改善提案を生成しました")
        
        return steps
    
    def quick_improve(self, prototype_result: Dict, improvement_type: str) -> Dict:
        """
        5分以内での迅速な改善を実行
        
        Args:
            prototype_result: 元のプロトタイプ結果
            improvement_type: 改善の種類 (ui, feature, error_handling)
            
        Returns:
            改善結果
        """
        print(f"⚡ 迅速改善実行: {improvement_type}")
        
        start_time = time.time()
        
        try:
            improved = self.prototype_generator.quick_improve(
                prototype_result, improvement_type
            )
            
            elapsed_time = (time.time() - start_time) / 60
            
            result = {
                "original_prototype": prototype_result["idea"],
                "improvement_type": improvement_type,
                "files_modified": improved.get("modified_files", []),
                "improvement_time_minutes": round(elapsed_time, 2),
                "success": elapsed_time <= 5,
                "changes_made": improved.get("changes", []),
                "improved_at": datetime.now().isoformat()
            }
            
            if result["success"]:
                print(f"✨ 改善完了! ({elapsed_time:.1f}分)")
            else:
                print(f"⏰ 改善に時間がかかりました ({elapsed_time:.1f}分)")
            
            return result
            
        except Exception as e:
            print(f"❌ 改善中にエラー: {str(e)}")
            return {
                "improvement_type": improvement_type,
                "success": False,
                "error": str(e)
            }
    
    def _save_prototype_result(self, result: Dict):
        """プロトタイプ結果をJSONファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prototype_result_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 結果を保存: {filepath}")


def main():
    """デモ実行"""
    print("🎯 Vive Paradigm Implementer デモ")
    
    agent = ViveParadigmImplementer("./demo_output")
    
    # デモプロトタイプを作成
    result = agent.create_prototype(
        idea="シンプルなタスク管理アプリ",
        time_limit=10,
        technology="web"
    )
    
    if result.get("success"):
        # 学習ガイドを生成
        guide = agent.generate_learning_guide(result)
        
        # 次のステップを提案
        next_steps = agent.suggest_next_steps(result)
        
        print("\n🔮 次のステップ提案:")
        for i, step in enumerate(next_steps[:3], 1):
            print(f"{i}. {step['title']} ({step['estimated_time']}分)")
            print(f"   {step['description']}")
    
    print("\n✅ デモ完了!")


if __name__ == "__main__":
    main()