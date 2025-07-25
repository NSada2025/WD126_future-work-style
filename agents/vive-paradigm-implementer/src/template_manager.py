#!/usr/bin/env python3
"""
Template Manager - テンプレート選択と管理

Author: NSada2025
Date: 2025-07-25
"""

import re
from typing import Dict, List, Optional


class TemplateManager:
    """プロトタイプテンプレートの選択と管理"""
    
    def __init__(self):
        self.templates = {
            # Webアプリケーション系
            "web_basic": {
                "name": "基本Webアプリ",
                "type": "web",
                "complexity": "simple",
                "keywords": ["web", "ウェブ", "サイト", "アプリ", "html", "javascript"],
                "features": ["HTML/CSS/JS", "レスポンシブ", "インタラクティブ"],
                "time_estimate": 8
            },
            "web_dashboard": {
                "name": "ダッシュボード",
                "type": "web", 
                "complexity": "medium",
                "keywords": ["ダッシュボード", "dashboard", "管理", "統計", "グラフ"],
                "features": ["チャート表示", "データ管理", "リアルタイム更新"],
                "time_estimate": 12
            },
            "web_portfolio": {
                "name": "ポートフォリオサイト",
                "type": "web",
                "complexity": "simple", 
                "keywords": ["ポートフォリオ", "portfolio", "プロフィール", "作品", "履歴"],
                "features": ["プロフィール表示", "作品ギャラリー", "問い合わせフォーム"],
                "time_estimate": 10
            },
            
            # Python アプリケーション系
            "python_cli": {
                "name": "CLI アプリケーション",
                "type": "python",
                "complexity": "simple",
                "keywords": ["cli", "コマンド", "ツール", "スクリプト", "自動化"],
                "features": ["コマンドライン引数", "ファイル処理", "ログ出力"],
                "time_estimate": 7
            },
            "python_data": {
                "name": "データ処理スクリプト",
                "type": "python",
                "complexity": "medium",
                "keywords": ["データ", "処理", "分析", "csv", "json", "変換"],
                "features": ["ファイル読み書き", "データ変換", "統計計算"],
                "time_estimate": 9
            },
            "python_automation": {
                "name": "自動化スクリプト",
                "type": "python",
                "complexity": "simple",
                "keywords": ["自動化", "automation", "スケジュール", "タスク", "バッチ"],
                "features": ["定期実行", "ファイル操作", "通知機能"],
                "time_estimate": 8
            },
            
            # データ可視化系
            "dataviz_basic": {
                "name": "基本データ可視化",
                "type": "data_viz",
                "complexity": "simple",
                "keywords": ["グラフ", "chart", "可視化", "visualization", "統計"],
                "features": ["折れ線グラフ", "ヒストグラム", "散布図"],
                "time_estimate": 10
            },
            "dataviz_interactive": {
                "name": "インタラクティブ可視化",
                "type": "data_viz",
                "complexity": "medium",
                "keywords": ["インタラクティブ", "interactive", "動的", "plotly"],
                "features": ["ズーム機能", "フィルタリング", "アニメーション"],
                "time_estimate": 15
            },
            
            # API サービス系
            "api_rest": {
                "name": "REST API",
                "type": "api",
                "complexity": "medium",
                "keywords": ["api", "rest", "サービス", "エンドポイント", "json"],
                "features": ["CRUD操作", "JSON応答", "自動ドキュメント"],
                "time_estimate": 12
            },
            "api_microservice": {
                "name": "マイクロサービス",
                "type": "api",
                "complexity": "advanced",
                "keywords": ["マイクロサービス", "microservice", "分散", "サービス"],
                "features": ["軽量アーキテクチャ", "独立デプロイ", "API ゲートウェイ"],
                "time_estimate": 18
            },
            
            # 特殊用途
            "game_simple": {
                "name": "シンプルゲーム",
                "type": "web",
                "complexity": "medium",
                "keywords": ["ゲーム", "game", "パズル", "クイズ", "シューティング"],
                "features": ["ゲームループ", "スコア管理", "キーボード操作"],
                "time_estimate": 15
            },
            "chatbot_basic": {
                "name": "基本チャットボット",
                "type": "python",
                "complexity": "simple",
                "keywords": ["チャット", "bot", "会話", "ai", "対話"],
                "features": ["パターンマッチング", "応答生成", "学習機能"],
                "time_estimate": 10
            }
        }
        
        # 複雑さレベルの定義
        self.complexity_levels = {
            "simple": {"max_time": 10, "files": 2-4, "features": "基本機能のみ"},
            "medium": {"max_time": 15, "files": 4-6, "features": "実用的な機能セット"},
            "advanced": {"max_time": 20, "files": 6-10, "features": "高度な機能と統合"}
        }
    
    def select_template(self, idea: str, technology: str = "auto", complexity: str = "auto") -> Dict:
        """
        アイデアに最適なテンプレートを選択
        
        Args:
            idea: 実装したいアイデアの説明
            technology: 優先技術 (web, python, data_viz, api, auto)
            complexity: 複雑さレベル (simple, medium, advanced, auto)
            
        Returns:
            選択されたテンプレート情報
        """
        print(f"🔍 テンプレート選択中: '{idea}'")
        
        # キーワードマッチングでスコア計算
        scores = {}
        idea_lower = idea.lower()
        
        for template_id, template in self.templates.items():
            score = 0
            
            # キーワードマッチング
            for keyword in template["keywords"]:
                if keyword in idea_lower:
                    score += 3
                # 部分マッチも考慮
                if any(keyword in word for word in idea_lower.split()):
                    score += 1
            
            # 技術指定がある場合
            if technology != "auto" and template["type"] == technology:
                score += 10
            
            # 複雑さ指定がある場合
            if complexity != "auto" and template["complexity"] == complexity:
                score += 5
                
            scores[template_id] = score
        
        # スコアが最も高いテンプレートを選択
        if not scores or max(scores.values()) == 0:
            # マッチしない場合はデフォルト選択
            selected_id = self._get_default_template(technology, complexity)
        else:
            selected_id = max(scores.keys(), key=lambda k: scores[k])
        
        selected_template = self.templates[selected_id].copy()
        selected_template["id"] = selected_id
        selected_template["match_score"] = scores.get(selected_id, 0)
        
        print(f"✅ テンプレート選択: {selected_template['name']} (スコア: {selected_template['match_score']})")
        
        return selected_template
    
    def _get_default_template(self, technology: str, complexity: str) -> str:
        """デフォルトテンプレートを取得"""
        defaults = {
            "web": "web_basic",
            "python": "python_cli", 
            "data_viz": "dataviz_basic",
            "api": "api_rest"
        }
        
        if technology in defaults:
            return defaults[technology]
        
        # 複雑さベースのデフォルト
        if complexity == "simple":
            return "web_basic"
        elif complexity == "advanced":
            return "api_microservice"
        else:
            return "python_cli"
    
    def get_template_suggestions(self, idea: str, count: int = 3) -> List[Dict]:
        """
        アイデアに対するテンプレート候補を複数提案
        
        Args:
            idea: アイデアの説明
            count: 提案数
            
        Returns:
            テンプレート候補のリスト
        """
        idea_lower = idea.lower()
        suggestions = []
        
        # 全テンプレートをスコア付きで評価
        for template_id, template in self.templates.items():
            score = 0
            
            # キーワードマッチング
            for keyword in template["keywords"]:
                if keyword in idea_lower:
                    score += 3
                elif any(keyword in word for word in idea_lower.split()):
                    score += 1
            
            # テンプレート情報をコピーして追加
            suggestion = template.copy()
            suggestion["id"] = template_id
            suggestion["match_score"] = score
            suggestions.append(suggestion)
        
        # スコア順でソートして上位を返す
        suggestions.sort(key=lambda x: x["match_score"], reverse=True)
        
        return suggestions[:count]
    
    def customize_template(self, template_info: Dict, customizations: Dict) -> Dict:
        """
        テンプレートをカスタマイズ
        
        Args:
            template_info: ベーステンプレート
            customizations: カスタマイズ設定
            
        Returns:
            カスタマイズされたテンプレート
        """
        customized = template_info.copy()
        
        # 機能の追加/削除
        if "add_features" in customizations:
            customized["features"].extend(customizations["add_features"])
        
        if "remove_features" in customizations:
            for feature in customizations["remove_features"]:
                if feature in customized["features"]:
                    customized["features"].remove(feature)
        
        # 複雑さレベルの調整
        if "complexity" in customizations:
            new_complexity = customizations["complexity"]
            if new_complexity in self.complexity_levels:
                customized["complexity"] = new_complexity
                # 時間見積もりも調整
                level_info = self.complexity_levels[new_complexity]
                customized["time_estimate"] = min(
                    customized["time_estimate"],
                    level_info["max_time"]
                )
        
        # 時間制約
        if "max_time" in customizations:
            max_time = customizations["max_time"]
            if customized["time_estimate"] > max_time:
                # 複雑さを下げる
                if customized["complexity"] == "advanced":
                    customized["complexity"] = "medium"
                elif customized["complexity"] == "medium":
                    customized["complexity"] = "simple"
                
                customized["time_estimate"] = max_time
                customized["features"] = customized["features"][:3]  # 機能を削減
        
        return customized
    
    def validate_template(self, template_info: Dict, time_limit: int) -> Dict:
        """
        テンプレートが制約に適合するかチェック
        
        Args:
            template_info: テンプレート情報
            time_limit: 時間制限（分）
            
        Returns:
            バリデーション結果と調整済みテンプレート
        """
        result = {
            "valid": True,
            "warnings": [],
            "adjusted_template": template_info.copy()
        }
        
        # 時間制限チェック
        if template_info["time_estimate"] > time_limit:
            result["warnings"].append(f"推定時間 {template_info['time_estimate']}分 > 制限時間 {time_limit}分")
            
            # 自動調整
            if time_limit <= 5:
                result["adjusted_template"]["complexity"] = "simple"
                result["adjusted_template"]["features"] = result["adjusted_template"]["features"][:2]
            elif time_limit <= 10:
                result["adjusted_template"]["complexity"] = "simple"
                result["adjusted_template"]["features"] = result["adjusted_template"]["features"][:3]
            elif time_limit <= 15:
                result["adjusted_template"]["complexity"] = "medium"
            
            result["adjusted_template"]["time_estimate"] = min(
                result["adjusted_template"]["time_estimate"],
                time_limit
            )
        
        # 複雑さレベルの整合性チェック
        complexity = template_info["complexity"]
        if complexity in self.complexity_levels:
            level_info = self.complexity_levels[complexity]
            if template_info["time_estimate"] > level_info["max_time"]:
                result["warnings"].append(f"複雑さ '{complexity}' に対して時間見積もりが過大")
        
        return result
    
    def get_template_by_type(self, template_type: str) -> List[Dict]:
        """
        指定タイプのテンプレート一覧を取得
        
        Args:
            template_type: テンプレートタイプ (web, python, data_viz, api)
            
        Returns:
            該当するテンプレートのリスト
        """
        matching_templates = []
        
        for template_id, template in self.templates.items():
            if template["type"] == template_type:
                template_copy = template.copy()
                template_copy["id"] = template_id
                matching_templates.append(template_copy)
        
        # 複雑さ順でソート
        complexity_order = {"simple": 1, "medium": 2, "advanced": 3}
        matching_templates.sort(
            key=lambda x: complexity_order.get(x["complexity"], 2)
        )
        
        return matching_templates
    
    def analyze_idea_complexity(self, idea: str) -> str:
        """
        アイデアの複雑さを分析
        
        Args:
            idea: アイデアの説明
            
        Returns:
            推定複雑さレベル (simple, medium, advanced)
        """
        idea_lower = idea.lower()
        
        # 複雑さを示すキーワード
        simple_keywords = ["簡単", "基本", "シンプル", "basic", "simple", "minimal"]
        medium_keywords = ["実用", "機能", "管理", "dashboard", "practical", "functional"]
        advanced_keywords = ["複雑", "高度", "分散", "リアルタイム", "advanced", "complex", "enterprise"]
        
        # キーワードカウント
        simple_count = sum(1 for kw in simple_keywords if kw in idea_lower)
        medium_count = sum(1 for kw in medium_keywords if kw in idea_lower)
        advanced_count = sum(1 for kw in advanced_keywords if kw in idea_lower)
        
        # 文字数も考慮
        if len(idea) > 100:
            advanced_count += 1
        elif len(idea) > 50:
            medium_count += 1
        else:
            simple_count += 1
        
        # 単語数も考慮
        word_count = len(idea.split())
        if word_count > 20:
            advanced_count += 1
        elif word_count > 10:
            medium_count += 1
        
        # 最も高いスコアの複雑さを返す
        if advanced_count >= max(simple_count, medium_count):
            return "advanced"
        elif medium_count >= simple_count:
            return "medium"
        else:
            return "simple"
    
    def get_template_info(self, template_id: str) -> Optional[Dict]:
        """指定IDのテンプレート情報を取得"""
        if template_id in self.templates:
            template = self.templates[template_id].copy()
            template["id"] = template_id
            return template
        return None
    
    def list_all_templates(self) -> Dict[str, List[Dict]]:
        """全テンプレートをタイプ別にグループ化して取得"""
        grouped = {}
        
        for template_id, template in self.templates.items():
            template_type = template["type"]
            if template_type not in grouped:
                grouped[template_type] = []
            
            template_copy = template.copy()
            template_copy["id"] = template_id
            grouped[template_type].append(template_copy)
        
        # 各グループ内で複雑さ順にソート
        complexity_order = {"simple": 1, "medium": 2, "advanced": 3}
        for template_type in grouped:
            grouped[template_type].sort(
                key=lambda x: complexity_order.get(x["complexity"], 2)
            )
        
        return grouped


if __name__ == "__main__":
    # テスト実行
    manager = TemplateManager()
    
    # テストケース
    test_ideas = [
        "タスク管理アプリを作りたい",
        "データの可視化ダッシュボード",
        "REST APIサービス",
        "簡単なゲーム",
        "自動化スクリプト"
    ]
    
    print("🧪 テンプレート選択テスト")
    for idea in test_ideas:
        template = manager.select_template(idea)
        print(f"📋 '{idea}' → {template['name']} ({template['type']})")
    
    print("\n🎯 テンプレート管理システム テスト完了")