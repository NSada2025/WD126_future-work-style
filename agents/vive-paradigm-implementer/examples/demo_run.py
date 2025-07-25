#!/usr/bin/env python3
"""
Vive Paradigm Implementer - Demo Script
実際の使用例とデモンストレーション

Author: NSada2025
Date: 2025-07-25
"""

import os
import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from claude_integration import (
    vive_create, vive_improve, vive_next_steps, 
    vive_history, vive_stats, vive_help
)


def demo_basic_usage():
    """基本的な使用方法のデモ"""
    print("🎯 デモ1: 基本的なプロトタイプ作成")
    print("=" * 50)
    
    # シンプルなWebアプリ作成
    result1 = vive_create(
        "タスク管理アプリ",
        technology="web",
        time_limit=8
    )
    
    if result1.get("success"):
        print("\\n⚡ 改善デモ: UI向上")
        vive_improve("ui")
        
        print("\\n🔮 次のステップ提案")
        vive_next_steps()
    
    time.sleep(2)  # デモ用の待機


def demo_different_technologies():
    """異なる技術スタックのデモ"""
    print("\\n\\n💻 デモ2: 異なる技術スタック")
    print("=" * 50)
    
    demos = [
        ("データ可視化ダッシュボード", "data_viz", 10),
        ("自動化スクリプト", "python", 7),
        ("シンプルなREST API", "api", 12)
    ]
    
    for idea, tech, time_limit in demos:
        print(f"\\n🔧 {tech} プロトタイプ: {idea}")
        result = vive_create(idea, technology=tech, time_limit=time_limit)
        
        if result.get("success"):
            print(f"  ✅ 成功: {len(result.get('files_created', []))}ファイル作成")
        else:
            print(f"  ⚠️ 部分完成: 基本機能は実装済み")
        
        time.sleep(1)


def demo_rapid_prototyping():
    """高速プロトタイピングのデモ"""
    print("\\n\\n⚡ デモ3: 高速プロトタイピング（5分制限）")
    print("=" * 50)
    
    rapid_ideas = [
        "シンプルな計算機",
        "色彩パレット生成器",
        "基本的なタイマー"
    ]
    
    for idea in rapid_ideas:
        print(f"\\n🏃 高速作成: {idea}")
        start_time = time.time()
        
        result = vive_create(idea, technology="web", time_limit=5)
        
        actual_time = time.time() - start_time
        
        status = "✅" if result.get("success") else "⚠️"
        print(f"  {status} 実際の時間: {actual_time:.1f}秒")


def demo_learning_workflow():
    """学習ワークフローのデモ"""
    print("\\n\\n📚 デモ4: 学習ワークフロー")
    print("=" * 50)
    
    print("🎯 学習目標: JavaScript基礎の習得")
    
    # 段階的な学習プロトタイプ
    learning_sequence = [
        ("Hello World ボタン", "web", 3),
        ("カウンターアプリ", "web", 5), 
        ("簡単なクイズアプリ", "web", 8)
    ]
    
    for i, (idea, tech, time_limit) in enumerate(learning_sequence, 1):
        print(f"\\n📖 学習ステップ {i}: {idea}")
        
        result = vive_create(idea, technology=tech, time_limit=time_limit)
        
        if result.get("success"):
            print(f"  ✨ 完成! 次のレベルへ")
            
            # 最後のプロトタイプのみ次のステップを表示
            if i == len(learning_sequence):
                print("\\n🔮 継続学習の提案:")
                vive_next_steps()
        else:
            print(f"  📝 基本機能完成。学習ガイドで理解を深化")


def demo_failure_handling():
    """失敗ケースとリカバリのデモ"""
    print("\\n\\n🛠️ デモ5: 制約下での実装")
    print("=" * 50)
    
    # 意図的に厳しい制約
    challenging_ideas = [
        ("複雑な機械学習アプリ", "python", 3),  # 時間が足りない
        ("高度な3Dゲーム", "web", 5)  # 複雑すぎる
    ]
    
    for idea, tech, time_limit in challenging_ideas:
        print(f"\\n🎯 チャレンジ: {idea} ({time_limit}分制限)")
        
        result = vive_create(idea, technology=tech, time_limit=time_limit)
        
        if not result.get("success"):
            print("  ⚠️ 制限時間内で完全実装は困難でしたが...")
            print("  💡 基本機能は実装されており、段階的改善が可能です")
            print("  📚 学習ガイドで理論を補完し、継続開発しましょう")


def demo_session_management():
    """セッション管理のデモ"""
    print("\\n\\n📊 デモ6: セッション管理と統計")
    print("=" * 50)
    
    print("📚 今回のセッション履歴:")
    vive_history()
    
    print("\\n📈 統計情報:")
    vive_stats()


def main():
    """メインデモ実行"""
    print("🌟 Vive Paradigm Implementer - 総合デモ")
    print("🎯 体験駆動型学習の実践例")
    print("⏰ 推定実行時間: 5-8分")
    print("=" * 60)
    
    # ヘルプ表示
    print("\\n📖 まずは使用方法を確認:")
    vive_help()
    
    # 各デモを順次実行
    try:
        demo_basic_usage()
        demo_different_technologies()
        demo_rapid_prototyping()
        demo_learning_workflow()
        demo_failure_handling()
        demo_session_management()
        
    except KeyboardInterrupt:
        print("\\n\\n⚠️ デモが中断されました")
    except Exception as e:
        print(f"\\n\\n❌ デモ実行エラー: {e}")
    
    # 最終サマリー
    print("\\n\\n🎉 総合デモ完了!")
    print("✨ Vive Paradigm のポイント:")
    print("  • 完璧より速度 - まず動くものを作る")
    print("  • 体験から理解 - 理論は後追いで学習")
    print("  • 段階的改善 - 小さな成功を積み重ねる")
    print("  • 学習促進 - 作る過程での気づきを重視")
    
    print("\\n💡 次のアクション:")
    print("  1. 実際のプロジェクトでvive_create()を試す")
    print("  2. 学習ガイドを読んで理論を深める")
    print("  3. 改善提案を実行して機能を拡張")
    print("  4. 他の人と作成物を共有してフィードバック収集")
    
    print("\\n📚 詳細情報:")
    print("  • README.md - 基本的な使用方法")
    print("  • docs/vive_paradigm_guide.md - 理論と実践")
    print("  • examples/ - より多くの実例")


if __name__ == "__main__":
    main()