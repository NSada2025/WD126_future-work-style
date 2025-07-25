#!/usr/bin/env python3
"""
Learning Guide Generator - 体験駆動型学習ガイド生成

Author: NSada2025
Date: 2025-07-25
"""

from typing import Dict, List
from datetime import datetime


class LearningGuideGenerator:
    """体験から学習ガイドを生成するエンジン"""
    
    def __init__(self):
        self.learning_patterns = {
            "web": {
                "theory_areas": ["HTML構造", "CSS設計", "JavaScript基礎", "DOM操作"],
                "practice_suggestions": ["要素の追加/削除", "スタイル変更", "イベント処理"],
                "common_questions": [
                    "なぜこの要素構造なのか？",
                    "CSSセレクタの種類と使い分け",
                    "JavaScriptとHTMLの連携方法"
                ]
            },
            "python": {
                "theory_areas": ["データ型", "制御構造", "関数設計", "例外処理"],
                "practice_suggestions": ["関数の追加", "データ処理の改善", "エラー対応"],
                "common_questions": [
                    "Pythonの基本文法の理由",
                    "効率的なデータ処理方法",
                    "保守しやすいコード設計"
                ]
            },
            "data_viz": {
                "theory_areas": ["統計の基礎", "可視化原則", "色彩理論", "認知科学"],
                "practice_suggestions": ["グラフ種類の変更", "色の調整", "レイアウト改善"],
                "common_questions": [
                    "適切なグラフの選び方",
                    "色覚異常への配慮",
                    "データの誤解を防ぐ方法"
                ]
            },
            "api": {
                "theory_areas": ["REST設計", "HTTPメソッド", "データ形式", "認証/認可"],
                "practice_suggestions": ["新エンドポイント追加", "バリデーション強化", "ドキュメント改善"],
                "common_questions": [
                    "RESTful設計の原則",
                    "ステータスコードの使い分け",
                    "セキュリティベストプラクティス"
                ]
            }
        }
    
    def create_guide(self, prototype_result: Dict) -> Dict:
        """
        プロトタイプ結果から学習ガイドを生成
        
        Args:
            prototype_result: create_prototypeの結果
            
        Returns:
            学習ガイドの情報
        """
        prototype_type = prototype_result.get("technology", "generic")
        idea = prototype_result.get("idea", "プロトタイプ")
        creation_time = prototype_result.get("creation_time_minutes", 0)
        success = prototype_result.get("success", False)
        
        # 基本情報
        guide_data = {
            "prototype_info": {
                "idea": idea,
                "type": prototype_type,
                "creation_time": creation_time,
                "success": success,
                "files_created": prototype_result.get("files_created", [])
            },
            "experience_reflection": self._generate_experience_reflection(prototype_result),
            "theory_explanation": self._generate_theory_explanation(prototype_type, prototype_result),
            "learning_path": self._generate_learning_path(prototype_type, success),
            "next_experiments": self._generate_next_experiments(prototype_type, prototype_result),
            "troubleshooting": self._generate_troubleshooting_guide(prototype_type),
            "resources": self._generate_learning_resources(prototype_type)
        }
        
        # Markdown形式のガイドを生成
        markdown_content = self._create_markdown_guide(guide_data)
        
        return {
            "data": guide_data,
            "markdown_content": markdown_content,
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_experience_reflection(self, prototype_result: Dict) -> Dict:
        """体験の振り返りセクションを生成"""
        success = prototype_result.get("success", False)
        creation_time = prototype_result.get("creation_time_minutes", 0)
        files_created = len(prototype_result.get("files_created", []))
        
        reflection = {
            "what_you_built": f"あなたは「{prototype_result.get('idea')}」のプロトタイプを作成しました。",
            "time_analysis": "",
            "achievement": "",
            "key_learnings": []
        }
        
        # 時間分析
        if success:
            if creation_time <= 5:
                reflection["time_analysis"] = f"⚡ 驚異的！{creation_time:.1f}分で完成。効率的な実装ができています。"
            elif creation_time <= 8:
                reflection["time_analysis"] = f"✨ 素晴らしい！{creation_time:.1f}分での完成。良いペースです。"
            else:
                reflection["time_analysis"] = f"👍 {creation_time:.1f}分で完成。制限時間内での達成です。"
        else:
            reflection["time_analysis"] = f"⏰ {creation_time:.1f}分かかりましたが、基本機能は実装できています。"
        
        # 達成感
        if files_created >= 4:
            reflection["achievement"] = f"🎯 {files_created}個のファイルを作成し、本格的なプロトタイプが完成しました。"
        elif files_created >= 2:
            reflection["achievement"] = f"📝 {files_created}個のファイルでシンプルながら機能的なプロトタイプができました。"
        else:
            reflection["achievement"] = "🌱 最小限の構成でアイデアを形にできました。"
        
        # 主要な学習ポイント
        learning_points = prototype_result.get("learning_points", [])
        if learning_points:
            reflection["key_learnings"] = [
                f"✓ {point}" for point in learning_points[:4]
            ]
        else:
            reflection["key_learnings"] = [
                "✓ アイデアを素早く形にする方法",
                "✓ 最小限の機能で価値を提供する重要性",
                "✓ プロトタイピングの基本プロセス"
            ]
        
        return reflection
    
    def _generate_theory_explanation(self, prototype_type: str, prototype_result: Dict) -> Dict:
        """理論的説明セクションを生成"""
        pattern = self.learning_patterns.get(prototype_type, self.learning_patterns["web"])
        
        explanation = {
            "why_it_works": self._explain_why_it_works(prototype_type),
            "key_concepts": pattern["theory_areas"],
            "design_decisions": self._explain_design_decisions(prototype_type, prototype_result),
            "best_practices": self._get_best_practices(prototype_type)
        }
        
        return explanation
    
    def _explain_why_it_works(self, prototype_type: str) -> str:
        """なぜ動作するかの説明"""
        explanations = {
            "web": """
Webアプリケーションが動作する理由：
• HTML: 構造と内容を定義
• CSS: 見た目とレイアウトを制御
• JavaScript: インタラクション（ユーザーの操作への反応）を実現
• ブラウザ: これらを統合して表示・実行
            """.strip(),
            "python": """
Pythonスクリプトが動作する理由：
• インタープリター: コードを1行ずつ実行
• 標準ライブラリ: 豊富な機能をすぐに利用可能
• 動的型付け: 型を意識せず柔軟にコーディング
• オブジェクト指向: データと処理をまとめて管理
            """.strip(),
            "data_viz": """
データ可視化が効果的な理由：
• 視覚情報: 人間は視覚的な情報を素早く理解
• パターン認識: グラフで傾向や異常を発見
• 統計ライブラリ: 複雑な計算を簡単に実行
• インタラクティブ性: 探索的なデータ分析が可能
            """.strip(),
            "api": """
APIが機能する理由：
• HTTP: 標準的な通信プロトコル
• JSON: 軽量で読みやすいデータ形式
• RESTful設計: 直感的で一貫したインターフェース
• フレームワーク: 共通的な処理を自動化
            """.strip()
        }
        
        return explanations.get(prototype_type, "基本的なプログラミング原則に基づいて動作します。")
    
    def _explain_design_decisions(self, prototype_type: str, prototype_result: Dict) -> List[str]:
        """設計判断の説明"""
        decisions = []
        
        files_created = prototype_result.get("files_created", [])
        
        if prototype_type == "web":
            if "index.html" in files_created:
                decisions.append("📄 index.html: エントリーポイントとしてブラウザが最初に読み込む")
            if "style.css" in files_created:
                decisions.append("🎨 style.css: HTMLとCSSを分離してメンテナンス性向上")
            if "script.js" in files_created:
                decisions.append("⚡ script.js: 動的な機能を別ファイルで管理")
        
        elif prototype_type == "python":
            if "main.py" in files_created:
                decisions.append("🐍 main.py: メイン実行ファイルとして明確な命名")
            if "requirements.txt" in files_created:
                decisions.append("📦 requirements.txt: 依存関係を明示して環境構築を簡単に")
        
        elif prototype_type == "api":
            decisions.append("🚀 FastAPI: 高速で直感的なAPI開発フレームワーク")
            decisions.append("📚 自動ドキュメント: /docs で API仕様を自動生成")
            decisions.append("🔧 テストクライアント: API動作を簡単に確認")
        
        if not decisions:
            decisions = [
                "🎯 最小限の構成: 必要な機能のみで複雑さを回避",
                "📝 明確な命名: ファイル名から役割が分かるように",
                "🔄 拡張可能性: 後から機能追加しやすい構造"
            ]
        
        return decisions
    
    def _get_best_practices(self, prototype_type: str) -> List[str]:
        """ベストプラクティス"""
        practices = {
            "web": [
                "セマンティックなHTML要素を使用",
                "CSSでレスポンシブデザインを考慮",
                "JavaScriptでDOM操作を効率的に",
                "アクセシビリティを意識した設計"
            ],
            "python": [
                "PEP 8に従ったコーディングスタイル",
                "適切な例外処理の実装",
                "関数は単一責任の原則を守る",
                "ドキュメントストリングで説明を追加"
            ],
            "data_viz": [
                "適切なグラフタイプの選択",
                "色覚異常に配慮した色選択",
                "軸ラベルと単位を明確に表示",
                "データの出典と更新日を記載"
            ],
            "api": [
                "RESTful な URL設計",
                "適切なHTTPステータスコード",
                "入力データのバリデーション",
                "エラーハンドリングとログ記録"
            ]
        }
        
        return practices.get(prototype_type, [
            "コードの可読性を重視",
            "段階的な機能追加",
            "テストを書いて品質確保",
            "ドキュメントを充実"
        ])
    
    def _generate_learning_path(self, prototype_type: str, success: bool) -> Dict:
        """学習パスを生成"""
        base_path = {
            "current_level": "プロトタイプ作成" if success else "基礎実装",
            "next_steps": [],
            "advanced_topics": [],
            "mastery_indicators": []
        }
        
        if prototype_type == "web":
            base_path["next_steps"] = [
                "レスポンシブデザインの実装",
                "JavaScriptフレームワーク (React/Vue) の学習",
                "バックエンドとの連携 (API呼び出し)",
                "Webアクセシビリティの向上"
            ]
            base_path["advanced_topics"] = [
                "PWA (Progressive Web App) 開発",
                "WebAssembly の活用",
                "パフォーマンス最適化",
                "セキュリティ対策"
            ]
            base_path["mastery_indicators"] = [
                "複雑なUIを直感的に実装できる",
                "ブラウザ間の互換性を考慮できる",
                "SEOとアクセシビリティを両立できる",
                "モダンな開発ツールを使いこなせる"
            ]
        
        elif prototype_type == "python":
            base_path["next_steps"] = [
                "オブジェクト指向プログラミングの深化",
                "外部ライブラリの効果的な活用",
                "ファイル操作とデータ処理の最適化",
                "テスト駆動開発 (TDD) の実践"
            ]
            base_path["advanced_topics"] = [
                "非同期プログラミング (asyncio)",
                "デコレータとメタクラス",
                "C拡張とのインターフェース",
                "分散システムでの Python活用"
            ]
            base_path["mastery_indicators"] = [
                "Pythonic なコードを自然に書ける",
                "適切なデザインパターンを選択できる",
                "パフォーマンス問題を特定・解決できる",
                "大規模プロジェクトを設計できる"
            ]
        
        # 成功度に応じて調整
        if not success:
            base_path["next_steps"].insert(0, "基本機能の完成と動作確認")
            base_path["next_steps"].insert(1, "エラーハンドリングの追加")
        
        return base_path
    
    def _generate_next_experiments(self, prototype_type: str, prototype_result: Dict) -> List[Dict]:
        """次の実験提案"""
        experiments = []
        
        # 共通の実験
        experiments.extend([
            {
                "title": "機能拡張実験",
                "description": "現在のプロトタイプに1つの新機能を追加",
                "time_estimate": "15分",
                "learning_goal": "既存コードの理解と拡張スキル",
                "difficulty": "初級"
            },
            {
                "title": "UI/UX改善実験", 
                "description": "使いやすさと見た目を向上させる",
                "time_estimate": "20分",
                "learning_goal": "ユーザー体験設計の基礎",
                "difficulty": "初級"
            }
        ])
        
        # 技術特化の実験
        if prototype_type == "web":
            experiments.extend([
                {
                    "title": "ローカルストレージ活用",
                    "description": "データをブラウザに保存して永続化",
                    "time_estimate": "25分",
                    "learning_goal": "Webストレージ API の理解",
                    "difficulty": "中級"
                },
                {
                    "title": "外部API連携",
                    "description": "天気APIなど外部サービスと連携",
                    "time_estimate": "30分",
                    "learning_goal": "Ajax/Fetch API の活用",
                    "difficulty": "中級"
                }
            ])
        
        elif prototype_type == "python":
            experiments.extend([
                {
                    "title": "データベース連携",
                    "description": "SQLite を使ってデータを永続化",
                    "time_estimate": "25分",
                    "learning_goal": "データベース操作の基礎",
                    "difficulty": "中級"
                },
                {
                    "title": "コマンドライン拡張",
                    "description": "argparse で柔軟な引数処理",
                    "time_estimate": "20分",
                    "learning_goal": "CLI アプリケーション設計",
                    "difficulty": "初級"
                }
            ])
        
        return experiments[:4]  # 最大4つまで
    
    def _generate_troubleshooting_guide(self, prototype_type: str) -> Dict:
        """トラブルシューティングガイド"""
        common_issues = {
            "web": {
                "ファイルが表示されない": [
                    "ブラウザのキャッシュをクリア",
                    "HTMLファイルのパスを確認",
                    "開発者ツールでエラーを確認"
                ],
                "JavaScriptエラー": [
                    "ブラウザの開発者ツール (F12) を開く",
                    "Consoleタブでエラーメッセージを確認",
                    "構文エラーや変数名のミスをチェック"
                ],
                "CSSが適用されない": [
                    "CSSファイルのリンクタグを確認",
                    "セレクタの書き方をチェック",
                    "ブラウザの開発者ツールでスタイルを確認"
                ]
            },
            "python": {
                "ModuleNotFoundError": [
                    "pip install で必要なライブラリをインストール",
                    "仮想環境が正しく有効化されているか確認",
                    "Python パスの設定を確認"
                ],
                "SyntaxError": [
                    "インデントが正しいかチェック",
                    "括弧やクォートの対応を確認",
                    "Python のバージョンを確認"
                ],
                "プログラムが終了しない": [
                    "無限ループになっていないかチェック",
                    "Ctrl+C で強制終了",
                    "ロジックの見直し"
                ]
            }
        }
        
        return {
            "common_issues": common_issues.get(prototype_type, {}),
            "debugging_steps": [
                "1. エラーメッセージを注意深く読む",
                "2. 最後に変更した部分を確認",
                "3. 段階的にコードを確認 (コメントアウト等)",
                "4. 必要に応じて検索エンジンで調べる",
                "5. 解決できない場合は基本に戻る"
            ],
            "helpful_tools": self._get_debugging_tools(prototype_type)
        }
    
    def _get_debugging_tools(self, prototype_type: str) -> List[str]:
        """デバッグツール一覧"""
        tools = {
            "web": [
                "ブラウザ開発者ツール (F12)",
                "VS Code Live Server 拡張",
                "W3C Markup Validator",
                "Lighthouse (パフォーマンス測定)"
            ],
            "python": [
                "Python デバッガー (pdb)",
                "VS Code Python 拡張",
                "print() デバッグ",
                "Python Tutor (実行の可視化)"
            ]
        }
        
        return tools.get(prototype_type, ["IDE/エディタのデバッグ機能", "ログ出力", "ステップ実行"])
    
    def _generate_learning_resources(self, prototype_type: str) -> Dict:
        """学習リソース"""
        resources = {
            "web": {
                "documentation": [
                    "MDN Web Docs - 信頼できるWeb技術リファレンス",
                    "W3Schools - 初心者向けチュートリアル",
                    "Can I use - ブラウザ対応状況確認"
                ],
                "practice_sites": [
                    "freeCodeCamp - 実践的なプロジェクト",
                    "Codepen - コード共有とインスピレーション",
                    "Frontend Mentor - デザインから実装練習"
                ],
                "communities": [
                    "Stack Overflow - 技術的な質問",
                    "Reddit r/webdev - 開発者コミュニティ",
                    "Dev.to - 技術記事とディスカッション"
                ]
            },
            "python": {
                "documentation": [
                    "Python.org 公式ドキュメント",
                    "Real Python - 実践的なチュートリアル",
                    "Python Module of the Week"
                ],
                "practice_sites": [
                    "LeetCode - アルゴリズム練習",
                    "HackerRank - プログラミング問題",
                    "Project Euler - 数学的問題"
                ],
                "communities": [
                    "r/Python - Reddit コミュニティ",
                    "Python Discord - リアルタイムチャット",
                    "Stack Overflow Python タグ"
                ]
            }
        }
        
        return resources.get(prototype_type, {
            "documentation": ["公式ドキュメント", "技術ブログ"],
            "practice_sites": ["オンライン学習サイト", "コーディング練習"],
            "communities": ["開発者コミュニティ", "質問サイト"]
        })
    
    def _create_markdown_guide(self, guide_data: Dict) -> str:
        """Markdown形式の学習ガイドを生成"""
        prototype_info = guide_data["prototype_info"]
        reflection = guide_data["experience_reflection"]
        theory = guide_data["theory_explanation"]
        learning_path = guide_data["learning_path"]
        experiments = guide_data["next_experiments"]
        troubleshooting = guide_data["troubleshooting"]
        resources = guide_data["resources"]
        
        markdown = f'''# 🎯 Vive Learning Guide: {prototype_info["idea"]}

> **体験から理解へ** - あなたのプロトタイプ体験を学習に変換します

## 📋 プロトタイプ情報

- **アイデア**: {prototype_info["idea"]}
- **技術**: {prototype_info["type"]}
- **作成時間**: {prototype_info["creation_time"]:.1f}分
- **結果**: {"✅ 成功" if prototype_info["success"] else "⚠️ 部分完成"}
- **ファイル数**: {len(prototype_info["files_created"])}個

## 🌟 体験の振り返り

### あなたが成し遂げたこと
{reflection["what_you_built"]}

{reflection["achievement"]}

{reflection["time_analysis"]}

### 主要な学習ポイント
'''
        
        for learning in reflection["key_learnings"]:
            markdown += f"{learning}\n"
        
        markdown += f'''
## 🧠 理論的理解

### なぜ動作するのか？
{theory["why_it_works"]}

### 重要な概念
'''
        
        for i, concept in enumerate(theory["key_concepts"], 1):
            markdown += f"{i}. **{concept}**\n"
        
        markdown += "\n### 設計判断の理由\n"
        for decision in theory["design_decisions"]:
            markdown += f"- {decision}\n"
        
        markdown += "\n### ベストプラクティス\n"
        for practice in theory["best_practices"]:
            markdown += f"- {practice}\n"
        
        markdown += f'''
## 🚀 学習パス

### 現在のレベル: {learning_path["current_level"]}

### 次のステップ
'''
        
        for i, step in enumerate(learning_path["next_steps"], 1):
            markdown += f"{i}. {step}\n"
        
        markdown += "\n### 上級トピック\n"
        for topic in learning_path["advanced_topics"]:
            markdown += f"- {topic}\n"
        
        markdown += "\n### マスタリー指標\n"
        for indicator in learning_path["mastery_indicators"]:
            markdown += f"- {indicator}\n"
        
        markdown += "\n## 🔬 次の実験提案\n"
        
        for i, exp in enumerate(experiments, 1):
            markdown += f'''
### {i}. {exp["title"]} ({exp["difficulty"]})
**時間**: {exp["time_estimate"]}  
**学習目標**: {exp["learning_goal"]}  
**内容**: {exp["description"]}
'''
        
        markdown += "\n## 🛠️ トラブルシューティング\n"
        
        if troubleshooting["common_issues"]:
            markdown += "\n### よくある問題と解決法\n"
            for issue, solutions in troubleshooting["common_issues"].items():
                markdown += f"\n**{issue}**\n"
                for solution in solutions:
                    markdown += f"- {solution}\n"
        
        markdown += "\n### デバッグ手順\n"
        for step in troubleshooting["debugging_steps"]:
            markdown += f"{step}\n"
        
        markdown += "\n### 有用なツール\n"
        for tool in troubleshooting["helpful_tools"]:
            markdown += f"- {tool}\n"
        
        markdown += "\n## 📚 学習リソース\n"
        
        for category, items in resources.items():
            if items:
                markdown += f"\n### {category.title()}\n"
                for item in items:
                    markdown += f"- {item}\n"
        
        markdown += f'''
## 🎯 まとめ

おめでとうございます！あなたは「{prototype_info["idea"]}」のプロトタイプを通じて、貴重な学習体験を積みました。

### 今日学んだこと
- プロトタイピングの力: アイデアを素早く形にする
- 体験駆動学習: まず作って、後から理論を理解する
- 段階的改善: 小さな成功の積み重ね

### 次のアクション
1. **即座に試す**: 提案された実験を1つ選んで実行
2. **理論を深める**: 興味を持った概念について詳しく調べる
3. **共有する**: 作ったものを他の人に見せてフィードバックをもらう

### Vive Paradigm の精神
> "完璧を恐れるな、まず始めよ。体験が最高の先生である。"

---

**作成日**: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}  
**生成エンジン**: Vive Paradigm Implementer Learning Guide Generator  
**次回の改善**: このガイドを読んで実践した結果をもとに、さらに深い学習を
'''
        
        return markdown


if __name__ == "__main__":
    # テスト実行
    generator = LearningGuideGenerator()
    
    test_result = {
        "idea": "タスク管理アプリ",
        "technology": "web",
        "creation_time_minutes": 8.5,
        "success": True,
        "files_created": ["index.html", "style.css", "script.js", "README.md"],
        "learning_points": ["HTMLの基本構造", "CSSによるスタイリング", "JavaScriptイベント処理"]
    }
    
    guide = generator.create_guide(test_result)
    print("🎯 学習ガイド生成テスト完了")
    print(f"📄 Markdown長さ: {len(guide['markdown_content'])}文字")