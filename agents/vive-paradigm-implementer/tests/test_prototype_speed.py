#!/usr/bin/env python3
"""
Test suite for Vive Paradigm Implementer - Speed and Quality Tests

Author: NSada2025
Date: 2025-07-25
"""

import unittest
import time
import tempfile
import shutil
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vive_agent import ViveParadigmImplementer
from template_manager import TemplateManager
from learning_guide import LearningGuideGenerator


class TestPrototypeSpeed(unittest.TestCase):
    """プロトタイプ生成速度のテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.agent = ViveParadigmImplementer(self.temp_dir)
        self.test_ideas = [
            "シンプルなタスク管理アプリ",
            "データ可視化ダッシュボード", 
            "基本的なRESTAPI",
            "チャットボットプロトタイプ",
            "ゲームのスコア管理システム"
        ]
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_10_minute_constraint(self):
        """10分制約のテスト"""
        print("\\n🕐 10分制約テスト開始")
        
        for idea in self.test_ideas[:3]:  # 最初の3つをテスト
            with self.subTest(idea=idea):
                start_time = time.time()
                
                result = self.agent.create_prototype(
                    idea=idea,
                    time_limit=10,
                    technology="web"
                )
                
                elapsed = time.time() - start_time
                
                # アサーション
                self.assertIsNotNone(result, "結果が返されること")
                self.assertTrue(result.get("files_created"), "ファイルが作成されること")
                self.assertLessEqual(elapsed, 12*60, "実際の実行時間が12分以内であること")  # 多少のバッファ
                
                print(f"  ✅ '{idea}': {elapsed/60:.1f}分 -> {len(result.get('files_created', []))}ファイル")
    
    def test_different_technologies(self):
        """異なる技術スタックのテスト"""
        print("\\n💻 技術スタック別テスト")
        
        technologies = ["web", "python", "data_viz", "api"]
        
        for tech in technologies:
            with self.subTest(technology=tech):
                start_time = time.time()
                
                result = self.agent.create_prototype(
                    idea=f"{tech}用のプロトタイプ",
                    time_limit=10,
                    technology=tech
                )
                
                elapsed = time.time() - start_time
                
                # アサーション
                self.assertIsNotNone(result)
                self.assertTrue(result.get("files_created"))
                self.assertEqual(result.get("technology"), tech)
                
                print(f"  ✅ {tech}: {elapsed/60:.1f}分 -> {result.get('files_created')}")
    
    def test_complexity_levels(self):
        """複雑さレベル別テスト"""
        print("\\n📊 複雑さレベル別テスト")
        
        complexity_levels = ["simple", "medium"]  # advancedは10分では厳しい
        
        for complexity in complexity_levels:
            with self.subTest(complexity=complexity):
                result = self.agent.create_prototype(
                    idea=f"{complexity}レベルのWebアプリ",
                    time_limit=10,
                    technology="web",
                    complexity=complexity
                )
                
                # アサーション
                self.assertIsNotNone(result)
                self.assertTrue(result.get("files_created"))
                
                # 複雑さに応じたファイル数の期待値
                file_count = len(result.get("files_created", []))
                if complexity == "simple":
                    self.assertGreaterEqual(file_count, 2)
                elif complexity == "medium":
                    self.assertGreaterEqual(file_count, 3)
                
                print(f"  ✅ {complexity}: {file_count}ファイル")


class TestLearningGuide(unittest.TestCase):
    """学習ガイド生成のテスト"""
    
    def setUp(self):
        self.guide_generator = LearningGuideGenerator()
        self.sample_result = {
            "idea": "タスク管理アプリ",
            "technology": "web", 
            "creation_time_minutes": 8.5,
            "success": True,
            "files_created": ["index.html", "style.css", "script.js", "README.md"],
            "learning_points": ["HTML構造", "CSS設計", "JavaScript基礎"]
        }
    
    def test_guide_generation(self):
        """学習ガイド生成テスト"""
        print("\\n📚 学習ガイド生成テスト")
        
        guide = self.guide_generator.create_guide(self.sample_result)
        
        # アサーション
        self.assertIsNotNone(guide)
        self.assertIn("data", guide)
        self.assertIn("markdown_content", guide)
        
        # データ構造の確認
        data = guide["data"]
        self.assertIn("experience_reflection", data)
        self.assertIn("theory_explanation", data)
        self.assertIn("learning_path", data)
        self.assertIn("next_experiments", data)
        
        # Markdownコンテンツの基本確認
        markdown = guide["markdown_content"]
        self.assertIn("# 🎯 Vive Learning Guide", markdown)
        self.assertIn("タスク管理アプリ", markdown)
        self.assertGreater(len(markdown), 1000, "十分な量のガイドが生成されること")
        
        print(f"  ✅ ガイド生成完了: {len(markdown)}文字")
    
    def test_different_technologies_guide(self):
        """異なる技術のガイド生成テスト"""
        print("\\n🔧 技術別ガイドテスト")
        
        tech_results = [
            {"technology": "python", "idea": "Pythonスクリプト"},
            {"technology": "data_viz", "idea": "データ可視化"},
            {"technology": "api", "idea": "REST API"}
        ]
        
        for tech_result in tech_results:
            test_result = self.sample_result.copy()
            test_result.update(tech_result)
            
            with self.subTest(technology=tech_result["technology"]):
                guide = self.guide_generator.create_guide(test_result)
                
                self.assertIsNotNone(guide)
                self.assertIn("data", guide)
                
                # 技術特有の内容が含まれているか確認
                markdown = guide["markdown_content"]
                tech = tech_result["technology"]
                
                if tech == "python":
                    self.assertIn("Python", markdown)
                elif tech == "data_viz":
                    self.assertIn("可視化", markdown)
                elif tech == "api":
                    self.assertIn("API", markdown)
                
                print(f"  ✅ {tech}: ガイド生成成功")


class TestTemplateManager(unittest.TestCase):
    """テンプレート管理のテスト"""
    
    def setUp(self):
        self.template_manager = TemplateManager()
    
    def test_template_selection(self):
        """テンプレート選択テスト"""
        print("\\n📋 テンプレート選択テスト")
        
        test_cases = [
            ("Webアプリを作りたい", "web"),
            ("Pythonスクリプト", "python"),
            ("データ可視化", "data_viz"),
            ("REST API", "api"),
            ("ゲーム", "web"),  # ゲームはWebで実装
        ]
        
        for idea, expected_type in test_cases:
            with self.subTest(idea=idea):
                template = self.template_manager.select_template(idea)
                
                self.assertIsNotNone(template)
                self.assertEqual(template["type"], expected_type)
                self.assertIn("name", template)
                self.assertIn("features", template)
                self.assertIn("time_estimate", template)
                
                print(f"  ✅ '{idea}' -> {template['name']} ({template['type']})")
    
    def test_complexity_analysis(self):
        """複雑さ分析テスト"""
        print("\\n🎯 複雑さ分析テスト")
        
        test_cases = [
            ("簡単なWebアプリ", "simple"),
            ("高度な分散システム", "advanced"),
            ("実用的なダッシュボードアプリケーション", "medium"),
        ]
        
        for idea, expected_complexity in test_cases:
            with self.subTest(idea=idea):
                complexity = self.template_manager.analyze_idea_complexity(idea)
                
                self.assertEqual(complexity, expected_complexity)
                print(f"  ✅ '{idea}' -> {complexity}")
    
    def test_template_validation(self):
        """テンプレート検証テスト"""
        print("\\n✅ テンプレート検証テスト")
        
        # 過大な時間見積もりのテンプレート
        test_template = {
            "name": "テストテンプレート",
            "type": "web",
            "complexity": "advanced",
            "time_estimate": 25,  # 制限時間を超過
            "features": ["機能1", "機能2", "機能3", "機能4"]
        }
        
        validation_result = self.template_manager.validate_template(
            test_template, time_limit=10
        )
        
        self.assertIn("valid", validation_result)
        self.assertIn("warnings", validation_result)
        self.assertIn("adjusted_template", validation_result)
        
        # 調整されたテンプレートの確認
        adjusted = validation_result["adjusted_template"]
        self.assertLessEqual(adjusted["time_estimate"], 10)
        
        print(f"  ✅ 検証完了: 警告数={len(validation_result['warnings'])}")


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.agent = ViveParadigmImplementer(self.temp_dir)
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """完全なワークフローテスト"""
        print("\\n🔄 統合ワークフローテスト")
        
        # 1. プロトタイプ作成
        prototype_result = self.agent.create_prototype(
            idea="シンプルなカウンターアプリ",
            time_limit=10,
            technology="web"
        )
        
        self.assertIsNotNone(prototype_result)
        self.assertTrue(prototype_result.get("files_created"))
        
        # 2. 学習ガイド生成
        guide = self.agent.generate_learning_guide(prototype_result)
        
        self.assertIsNotNone(guide)
        self.assertIn("data", guide)
        
        # 3. 次のステップ提案
        next_steps = self.agent.suggest_next_steps(prototype_result)
        
        self.assertIsInstance(next_steps, list)
        self.assertGreater(len(next_steps), 0)
        
        # 4. 迅速改善（成功した場合のみ）
        if prototype_result.get("success"):
            improvement_result = self.agent.quick_improve(
                prototype_result, "ui"
            )
            
            self.assertIsNotNone(improvement_result)
            self.assertIn("changes", improvement_result)
        
        print("  ✅ 統合ワークフロー完了")
        print(f"     - プロトタイプ: {len(prototype_result.get('files_created', []))}ファイル")
        print(f"     - 学習ガイド: {len(guide['markdown_content'])}文字")
        print(f"     - 次のステップ: {len(next_steps)}個")


def run_performance_benchmark():
    """パフォーマンスベンチマーク"""
    print("\\n🏃 パフォーマンスベンチマーク開始")
    
    temp_dir = tempfile.mkdtemp()
    agent = ViveParadigmImplementer(temp_dir)
    
    benchmark_ideas = [
        "簡単なクイズアプリ",
        "基本的な計算機",
        "シンプルなメモアプリ",
        "タイマーアプリ",
        "色彩パレット生成器"
    ]
    
    total_time = 0
    success_count = 0
    
    try:
        for i, idea in enumerate(benchmark_ideas, 1):
            print(f"  🎯 テスト {i}/{len(benchmark_ideas)}: {idea}")
            
            start_time = time.time()
            result = agent.create_prototype(idea, time_limit=8, technology="web")
            elapsed = time.time() - start_time
            
            total_time += elapsed
            if result.get("success"):
                success_count += 1
            
            print(f"     ⏱️  {elapsed:.1f}秒 -> {'✅' if result.get('success') else '⚠️'}")
        
        # 結果サマリー
        avg_time = total_time / len(benchmark_ideas)
        success_rate = (success_count / len(benchmark_ideas)) * 100
        
        print(f"\\n📊 ベンチマーク結果:")
        print(f"   平均作成時間: {avg_time:.1f}秒")
        print(f"   成功率: {success_rate:.1f}%")
        print(f"   総実行時間: {total_time:.1f}秒")
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("🧪 Vive Paradigm Implementer テストスイート")
    print("=" * 60)
    
    # パフォーマンスベンチマーク実行
    run_performance_benchmark()
    
    print("\\n" + "=" * 60)
    print("🔬 ユニットテスト実行")
    
    # ユニットテスト実行
    unittest.main(verbosity=2, exit=False)
    
    print("\\n🎉 全テスト完了!")
    print("💡 次のステップ: 実際のプロジェクトでエージェントを使用してみてください")