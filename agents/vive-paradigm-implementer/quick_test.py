#!/usr/bin/env python3
"""
Quick test script for Vive Paradigm Implementer
基本機能の動作確認用

Author: NSada2025
Date: 2025-07-25
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_basic_imports():
    """基本的なインポートテスト"""
    print("🧪 インポートテスト開始")
    
    try:
        from vive_agent import ViveParadigmImplementer
        print("✅ ViveParadigmImplementer インポート成功")
        
        from template_manager import TemplateManager
        print("✅ TemplateManager インポート成功")
        
        from learning_guide import LearningGuideGenerator
        print("✅ LearningGuideGenerator インポート成功")
        
        from prototype_generator import PrototypeGenerator
        print("✅ PrototypeGenerator インポート成功")
        
        return True
        
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_template_manager():
    """テンプレートマネージャーのテスト"""
    print("\n🧪 TemplateManager テスト")
    
    try:
        from template_manager import TemplateManager
        
        manager = TemplateManager()
        
        # テンプレート選択テスト
        template = manager.select_template("Webアプリを作りたい")
        print(f"✅ テンプレート選択: {template['name']} ({template['type']})")
        
        # 複雑さ分析テスト
        complexity = manager.analyze_idea_complexity("簡単なアプリ")
        print(f"✅ 複雑さ分析: {complexity}")
        
        return True
        
    except Exception as e:
        print(f"❌ TemplateManager テストエラー: {e}")
        return False

def test_learning_guide():
    """学習ガイドジェネレーターのテスト"""
    print("\n🧪 LearningGuideGenerator テスト")
    
    try:
        from learning_guide import LearningGuideGenerator
        
        generator = LearningGuideGenerator()
        
        # サンプル結果
        sample_result = {
            "idea": "テスト用アプリ",
            "technology": "web",
            "creation_time_minutes": 8.5,
            "success": True,
            "files_created": ["index.html", "style.css", "script.js"],
            "learning_points": ["HTML基礎", "CSS設計"]
        }
        
        guide = generator.create_guide(sample_result)
        print(f"✅ 学習ガイド生成: {len(guide['markdown_content'])}文字")
        
        return True
        
    except Exception as e:
        print(f"❌ LearningGuideGenerator テストエラー: {e}")
        return False

def test_vive_agent_creation():
    """ViveAgentの作成テスト"""
    print("\n🧪 ViveParadigmImplementer 作成テスト")
    
    try:
        from vive_agent import ViveParadigmImplementer
        
        # 一時出力ディレクトリ
        output_dir = "./test_output"
        
        agent = ViveParadigmImplementer(output_dir)
        print("✅ ViveParadigmImplementer インスタンス作成成功")
        
        # 出力ディレクトリが作成されているか確認
        if os.path.exists(output_dir):
            print("✅ 出力ディレクトリ作成成功")
            
            # クリーンアップ
            import shutil
            shutil.rmtree(output_dir)
            print("✅ テストディレクトリクリーンアップ完了")
        
        return True
        
    except Exception as e:
        print(f"❌ ViveParadigmImplementer 作成テストエラー: {e}")
        return False

def test_claude_integration():
    """Claude統合のテスト"""
    print("\n🧪 Claude統合テスト")
    
    try:
        # パスを追加
        sys.path.insert(0, str(project_root))
        
        from claude_integration import ClaudeCodeViveAgent
        
        agent = ClaudeCodeViveAgent()
        print("✅ ClaudeCodeViveAgent インスタンス作成成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Claude統合テストエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🌟 Vive Paradigm Implementer - 基本動作確認")
    print("=" * 50)
    
    tests = [
        ("基本インポート", test_basic_imports),
        ("TemplateManager", test_template_manager),
        ("LearningGuideGenerator", test_learning_guide),
        ("ViveAgent作成", test_vive_agent_creation),
        ("Claude統合", test_claude_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}テスト実行中...")
        if test_func():
            passed += 1
            print(f"✅ {test_name}テスト: PASS")
        else:
            print(f"❌ {test_name}テスト: FAIL")
    
    print("\n" + "=" * 50)
    print(f"📊 テスト結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 全テスト通過! システムは正常に動作しています。")
        print("\n💡 次のステップ:")
        print("  1. python3 examples/demo_run.py でフルデモを実行")
        print("  2. python3 tests/test_prototype_speed.py でパフォーマンステスト")
        print("  3. 実際のプロジェクトでvive_create()を試用")
    else:
        print("⚠️ 一部テストが失敗しました。実装を確認してください。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)