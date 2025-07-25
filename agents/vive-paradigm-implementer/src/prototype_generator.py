#!/usr/bin/env python3
"""
Prototype Generator - 10分間プロトタイプ生成エンジン

Author: NSada2025
Date: 2025-07-25
"""

import os
import json
import shutil
from typing import Dict, List, Optional
from datetime import datetime


class PrototypeGenerator:
    """10分以内でプロトタイプを生成するエンジン"""
    
    def __init__(self):
        self.templates_dir = os.path.join(
            os.path.dirname(__file__), "..", "templates"
        )
        
    def generate(self, idea: str, template_info: Dict, time_limit: int) -> Dict:
        """
        アイデアからプロトタイプを生成
        
        Args:
            idea: 実装したいアイデア
            template_info: 使用するテンプレート情報
            time_limit: 制限時間（分）
            
        Returns:
            生成されたプロトタイプの情報
        """
        print(f"🔨 プロトタイプ生成開始: {template_info['name']}")
        
        # 出力ディレクトリを作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_idea = "".join(c for c in idea if c.isalnum() or c in (' ', '-', '_'))[:20]
        output_name = f"{safe_idea.replace(' ', '_')}_{timestamp}"
        output_path = os.path.join("./output", output_name)
        os.makedirs(output_path, exist_ok=True)
        
        # テンプレートタイプに応じて生成
        if template_info["type"] == "web":
            result = self._generate_web_app(idea, output_path, template_info)
        elif template_info["type"] == "python":
            result = self._generate_python_script(idea, output_path, template_info)
        elif template_info["type"] == "data_viz":
            result = self._generate_data_visualization(idea, output_path, template_info)
        elif template_info["type"] == "api":
            result = self._generate_api_service(idea, output_path, template_info)
        else:
            result = self._generate_generic_prototype(idea, output_path, template_info)
        
        result["output_path"] = output_path
        result["template_info"] = template_info
        
        print(f"📦 ファイル生成完了: {len(result['files'])}個")
        
        return result
    
    def _generate_web_app(self, idea: str, output_path: str, template_info: Dict) -> Dict:
        """Webアプリケーションプロトタイプを生成"""
        files_created = []
        
        # HTML生成
        html_content = self._create_html_template(idea, template_info)
        html_path = os.path.join(output_path, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        files_created.append("index.html")
        
        # CSS生成
        css_content = self._create_css_template(template_info)
        css_path = os.path.join(output_path, "style.css")
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)
        files_created.append("style.css")
        
        # JavaScript生成
        js_content = self._create_js_template(idea, template_info)
        js_path = os.path.join(output_path, "script.js")
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(js_content)
        files_created.append("script.js")
        
        # README生成
        readme_content = self._create_readme(idea, "web", files_created)
        readme_path = os.path.join(output_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        files_created.append("README.md")
        
        return {
            "type": "web",
            "files": files_created,
            "run_command": f"open {html_path}",
            "learning_points": [
                "HTMLの基本構造",
                "CSSによるスタイリング",
                "JavaScriptによるインタラクション",
                "DOM操作の基礎"
            ]
        }
    
    def _generate_python_script(self, idea: str, output_path: str, template_info: Dict) -> Dict:
        """Pythonスクリプトプロトタイプを生成"""
        files_created = []
        
        # メインスクリプト生成
        python_content = self._create_python_template(idea, template_info)
        python_path = os.path.join(output_path, "main.py")
        with open(python_path, "w", encoding="utf-8") as f:
            f.write(python_content)
        files_created.append("main.py")
        
        # requirements.txt生成
        requirements = self._get_python_requirements(template_info)
        if requirements:
            req_path = os.path.join(output_path, "requirements.txt")
            with open(req_path, "w", encoding="utf-8") as f:
                f.write("\n".join(requirements))
            files_created.append("requirements.txt")
        
        # README生成
        readme_content = self._create_readme(idea, "python", files_created)
        readme_path = os.path.join(output_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        files_created.append("README.md")
        
        return {
            "type": "python",
            "files": files_created,
            "run_command": f"python {python_path}",
            "learning_points": [
                "Pythonの基本構文",
                "ファイル操作",
                "エラーハンドリング",
                "モジュールの使用"
            ]
        }
    
    def _generate_data_visualization(self, idea: str, output_path: str, template_info: Dict) -> Dict:
        """データ可視化プロトタイプを生成"""
        files_created = []
        
        # Pythonスクリプト（matplotlib/plotly使用）
        viz_content = self._create_data_viz_template(idea, template_info)
        viz_path = os.path.join(output_path, "visualize.py")
        with open(viz_path, "w", encoding="utf-8") as f:
            f.write(viz_content)
        files_created.append("visualize.py")
        
        # サンプルデータ生成
        data_content = self._create_sample_data(template_info)
        data_path = os.path.join(output_path, "sample_data.csv")
        with open(data_path, "w", encoding="utf-8") as f:
            f.write(data_content)
        files_created.append("sample_data.csv")
        
        # requirements.txt
        req_path = os.path.join(output_path, "requirements.txt")
        with open(req_path, "w", encoding="utf-8") as f:
            f.write("matplotlib>=3.5.0\npandas>=1.3.0\nplotly>=5.0.0\n")
        files_created.append("requirements.txt")
        
        # README生成
        readme_content = self._create_readme(idea, "data_viz", files_created)
        readme_path = os.path.join(output_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        files_created.append("README.md")
        
        return {
            "type": "data_viz",
            "files": files_created,
            "run_command": f"python {viz_path}",
            "learning_points": [
                "データ可視化の基礎",
                "matplotlib/plotlyの使用法",
                "CSVデータの読み込み",
                "グラフの種類と用途"
            ]
        }
    
    def _generate_api_service(self, idea: str, output_path: str, template_info: Dict) -> Dict:
        """API サービスプロトタイプを生成"""
        files_created = []
        
        # FastAPI サーバー
        api_content = self._create_api_template(idea, template_info)
        api_path = os.path.join(output_path, "main.py")
        with open(api_path, "w", encoding="utf-8") as f:
            f.write(api_content)
        files_created.append("main.py")
        
        # requirements.txt
        req_path = os.path.join(output_path, "requirements.txt")
        with open(req_path, "w", encoding="utf-8") as f:
            f.write("fastapi>=0.68.0\nuvicorn>=0.15.0\npydantic>=1.8.0\n")
        files_created.append("requirements.txt")
        
        # テスト用HTMLクライアント
        client_content = self._create_api_client_template(idea)
        client_path = os.path.join(output_path, "test_client.html")
        with open(client_path, "w", encoding="utf-8") as f:
            f.write(client_content)
        files_created.append("test_client.html")
        
        # README生成
        readme_content = self._create_readme(idea, "api", files_created)
        readme_path = os.path.join(output_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        files_created.append("README.md")
        
        return {
            "type": "api",
            "files": files_created,
            "run_command": f"uvicorn main:app --reload --port 8000",
            "learning_points": [
                "REST API の基礎",
                "FastAPI フレームワーク",
                "HTTP メソッド (GET, POST)",
                "JSON データ形式"
            ]
        }
    
    def _generate_generic_prototype(self, idea: str, output_path: str, template_info: Dict) -> Dict:
        """汎用プロトタイプを生成"""
        files_created = []
        
        # 基本スクリプト
        script_content = f'''#!/usr/bin/env python3
"""
{idea} - プロトタイプ

Created by Vive Paradigm Implementer
Date: {datetime.now().strftime("%Y-%m-%d")}
"""

def main():
    print("🚀 {idea} プロトタイプが起動しました!")
    print("📝 このプロトタイプを改良して理想の形に近づけましょう")
    
    # TODO: ここに具体的な機能を実装
    
    print("✅ プロトタイプ実行完了")

if __name__ == "__main__":
    main()
'''
        
        script_path = os.path.join(output_path, "prototype.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        files_created.append("prototype.py")
        
        # README
        readme_content = self._create_readme(idea, "generic", files_created)
        readme_path = os.path.join(output_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        files_created.append("README.md")
        
        return {
            "type": "generic",
            "files": files_created,
            "run_command": f"python {script_path}",
            "learning_points": [
                "プロトタイピングの基礎",
                "アイデアの具体化",
                "段階的な機能実装"
            ]
        }
    
    def _create_html_template(self, idea: str, template_info: Dict) -> str:
        """HTML テンプレートを生成"""
        app_name = idea.split(' ')[0] + " App"
        
        return f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>📱 {app_name}</h1>
            <p class="subtitle">Vive Paradigm プロトタイプ</p>
        </header>
        
        <main id="app">
            <div class="card">
                <h2>💡 アイデア: {idea}</h2>
                <p>このプロトタイプを体験して、改善点や新機能を考えてみましょう！</p>
                
                <div class="action-area">
                    <input type="text" id="userInput" placeholder="何か入力してみてください">
                    <button onclick="handleAction()">実行</button>
                </div>
                
                <div id="output" class="output-area">
                    <p>📋 出力がここに表示されます</p>
                </div>
            </div>
            
            <div class="card">
                <h3>🔄 次のステップ提案</h3>
                <ul>
                    <li>UIをより魅力的にする</li>
                    <li>データの保存機能を追加</li>
                    <li>ユーザビリティを向上</li>
                </ul>
            </div>
        </main>
    </div>
    
    <script src="script.js"></script>
</body>
</html>'''
    
    def _create_css_template(self, template_info: Dict) -> str:
        """CSS テンプレートを生成"""
        return '''/* Vive Paradigm プロトタイプ スタイル */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
    color: white;
}

header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
    font-size: 1.1em;
    opacity: 0.9;
}

.card {
    background: white;
    border-radius: 10px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    backdrop-filter: blur(10px);
}

.card h2 {
    color: #4a5568;
    margin-bottom: 15px;
}

.card h3 {
    color: #667eea;
    margin-bottom: 15px;
}

.action-area {
    display: flex;
    gap: 10px;
    margin: 20px 0;
}

#userInput {
    flex: 1;
    padding: 12px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1em;
    transition: border-color 0.3s;
}

#userInput:focus {
    outline: none;
    border-color: #667eea;
}

button {
    padding: 12px 24px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1em;
    cursor: pointer;
    transition: background 0.3s, transform 0.1s;
}

button:hover {
    background: #5a6fd8;
    transform: translateY(-1px);
}

button:active {
    transform: translateY(0);
}

.output-area {
    background: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 15px;
    margin-top: 15px;
    min-height: 100px;
}

ul {
    list-style: none;
    padding-left: 0;
}

li {
    padding: 8px 0;
    border-bottom: 1px solid #e2e8f0;
}

li:before {
    content: "✨ ";
    margin-right: 8px;
}

li:last-child {
    border-bottom: none;
}

/* アニメーション */
.card {
    animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
    from {
        transform: translateY(30px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

/* レスポンシブ対応 */
@media (max-width: 600px) {
    .container {
        padding: 10px;
    }
    
    header h1 {
        font-size: 2em;
    }
    
    .action-area {
        flex-direction: column;
    }
    
    .card {
        padding: 20px;
    }
}'''
    
    def _create_js_template(self, idea: str, template_info: Dict) -> str:
        """JavaScript テンプレートを生成"""
        return f'''// Vive Paradigm プロトタイプ JavaScript

// アプリケーション状態
let appState = {{
    items: [],
    currentInput: '',
    initialized: false
}};

// 初期化
document.addEventListener('DOMContentLoaded', function() {{
    console.log('🚀 {idea} プロトタイプが初期化されました');
    initializeApp();
}});

function initializeApp() {{
    appState.initialized = true;
    updateOutput('📱 アプリケーションが準備完了しました！');
    
    // Enter キーでも実行できるように
    document.getElementById('userInput').addEventListener('keypress', function(e) {{
        if (e.key === 'Enter') {{
            handleAction();
        }}
    }});
}}

function handleAction() {{
    const input = document.getElementById('userInput');
    const value = input.value.trim();
    
    if (!value) {{
        updateOutput('⚠️ 何か入力してください');
        return;
    }}
    
    // 入力をアプリ状態に保存
    appState.currentInput = value;
    appState.items.push({{
        text: value,
        timestamp: new Date().toLocaleTimeString(),
        id: Date.now()
    }});
    
    // 処理を実行（ここに具体的なロジックを追加）
    processInput(value);
    
    // 入力フィールドをクリア
    input.value = '';
    input.focus();
}}

function processInput(input) {{
    // デモ用の処理ロジック
    let response = '';
    
    if (input.toLowerCase().includes('hello') || input.toLowerCase().includes('こんにちは')) {{
        response = `👋 こんにちは！ "{input}" と入力されました。`;
    }} else if (input.toLowerCase().includes('help') || input.toLowerCase().includes('ヘルプ')) {{
        response = `❓ ヘルプ: このプロトタイプは {idea} を実現します。<br>
                   • 何でも入力してみてください<br>
                   • 次のステップを確認してください<br>
                   • 改善アイデアを考えてみてください`;
    }} else if (input.match(/\\d+/)) {{
        const numbers = input.match(/\\d+/g);
        const sum = numbers.reduce((acc, num) => acc + parseInt(num), 0);
        response = `🔢 数字を検出: {{numbers.join(', ')}} (合計: {{sum}})`;
    }} else {{
        response = `💭 "{input}" を処理しました。<br>
                   📝 処理時刻: {{new Date().toLocaleTimeString()}}<br>
                   📊 アイテム数: {{appState.items.length}}`;
    }}
    
    updateOutput(response);
    
    // ローカルストレージに保存（永続化のデモ）
    localStorage.setItem('vivePrototypeData', JSON.stringify(appState.items));
}}

function updateOutput(message) {{
    const output = document.getElementById('output');
    const timestamp = new Date().toLocaleTimeString();
    
    output.innerHTML = `
        <div style="animation: fadeIn 0.5s ease-in;">
            <strong>[{{timestamp}}]</strong><br>
            {{message}}
        </div>
    `;
    
    // スクロール効果
    output.scrollTop = output.scrollHeight;
}}

// ユーティリティ関数
function clearData() {{
    appState.items = [];
    localStorage.removeItem('vivePrototypeData');
    updateOutput('🗑️ データをクリアしました');
}}

function showStats() {{
    const stats = `
        📊 統計情報:<br>
        • 総アイテム数: {{appState.items.length}}<br>
        • 初期化状態: {{appState.initialized ? '✅' : '❌'}}<br>
        • 最後の入力: {{appState.currentInput || 'なし'}}<br>
        • 起動時刻: {{new Date().toLocaleString()}}
    `;
    updateOutput(stats);
}}

// CSS アニメーション用のスタイルを動的に追加
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
`;
document.head.appendChild(style);

// デバッグ用（開発者コンソールで使用可能）
window.viveDebug = {{
    showState: () => console.log('App State:', appState),
    clearData,
    showStats,
    version: '1.0.0'
}};

console.log('💡 デバッグ機能: viveDebug オブジェクトが利用可能です');'''
    
    def _create_python_template(self, idea: str, template_info: Dict) -> str:
        """Python テンプレートを生成"""
        return f'''#!/usr/bin/env python3
"""
{idea} - Python プロトタイプ

Vive Paradigm Implementer によって生成
作成日: {datetime.now().strftime("%Y-%m-%d %H:%M")}

このプロトタイプを体験し、改善点を見つけて発展させましょう！
"""

import os
import json
import sys
from datetime import datetime
from typing import List, Dict, Optional


class {idea.replace(' ', '').title()}Prototype:
    """
    {idea} のプロトタイプクラス
    """
    
    def __init__(self):
        self.data = []
        self.config = {{
            "version": "1.0.0",
            "created": datetime.now().isoformat()
        }}
        print(f"🚀 {{self.__class__.__name__}} が初期化されました")
    
    def run(self):
        """メイン実行ループ"""
        print(f"\\n📱 {idea} プロトタイプ開始")
        print("=" * 50)
        
        while True:
            try:
                print("\\n💡 コマンド:")
                print("1. add - アイテムを追加")
                print("2. list - アイテム一覧表示") 
                print("3. search - アイテム検索")
                print("4. stats - 統計情報表示")
                print("5. save - データ保存")
                print("6. load - データ読み込み")
                print("7. quit - 終了")
                
                choice = input("\\n選択してください (1-7): ").strip()
                
                if choice == '1':
                    self.add_item()
                elif choice == '2':
                    self.list_items()
                elif choice == '3':
                    self.search_items()  
                elif choice == '4':
                    self.show_stats()
                elif choice == '5':
                    self.save_data()
                elif choice == '6':
                    self.load_data()
                elif choice == '7' or choice.lower() == 'quit':
                    print("👋 プロトタイプを終了します")
                    break
                else:
                    print("❌ 無効な選択です")
                    
            except KeyboardInterrupt:
                print("\\n\\n⚠️ Ctrl+C が押されました")
                break
            except Exception as e:
                print(f"❌ エラーが発生しました: {{e}}")
    
    def add_item(self):
        """アイテムを追加"""
        item_text = input("📝 追加するアイテム: ").strip()
        if item_text:
            item = {{
                "id": len(self.data) + 1,
                "text": item_text,
                "created": datetime.now().isoformat(),
                "type": "user_input"
            }}
            self.data.append(item)
            print(f"✅ アイテムを追加しました: {{item_text}}")
        else:
            print("❌ 空のアイテムは追加できません")
    
    def list_items(self):
        """アイテム一覧を表示"""
        if not self.data:
            print("📋 アイテムがありません")
            return
        
        print(f"\\n📋 アイテム一覧 ({{len(self.data)}}個):")
        print("-" * 40)
        for item in self.data:
            created_time = datetime.fromisoformat(item["created"]).strftime("%H:%M:%S")
            print(f"{{item['id']:2}}. {{item['text']}} ({{created_time}})")
    
    def search_items(self):
        """アイテムを検索"""
        if not self.data:
            print("📋 検索対象のアイテムがありません")
            return
            
        query = input("🔍 検索キーワード: ").strip().lower()
        if not query:
            return
        
        matches = [item for item in self.data 
                  if query in item["text"].lower()]
        
        if matches:
            print(f"\\n🎯 検索結果 ({{len(matches)}}個):")
            for item in matches:
                print(f"- {{item['text']}}")
        else:
            print("❌ 該当するアイテムが見つかりませんでした")
    
    def show_stats(self):
        """統計情報を表示"""
        print("\\n📊 統計情報:")
        print(f"• 総アイテム数: {{len(self.data)}}")
        print(f"• バージョン: {{self.config['version']}}")
        print(f"• 作成日時: {{self.config['created']}}")
        
        if self.data:
            latest = max(self.data, key=lambda x: x["created"])
            latest_time = datetime.fromisoformat(latest["created"])
            print(f"• 最新アイテム: {{latest['text'][:30]}}...")
            print(f"• 最終更新: {{latest_time.strftime('%Y-%m-%d %H:%M:%S')}}")
    
    def save_data(self):
        """データをファイルに保存"""
        filename = f"{idea.replace(' ', '_').lower()}_data.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({{
                    "config": self.config,
                    "data": self.data
                }}, f, ensure_ascii=False, indent=2)
            print(f"💾 データを保存しました: {{filename}}")
        except Exception as e:
            print(f"❌ 保存エラー: {{e}}")
    
    def load_data(self):
        """ファイルからデータを読み込み"""
        filename = f"{idea.replace(' ', '_').lower()}_data.json"
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                self.data = saved_data.get("data", [])
                self.config.update(saved_data.get("config", {{}}))
                print(f"📂 データを読み込みました: {{len(self.data)}}個のアイテム")
            else:
                print(f"❌ ファイルが見つかりません: {{filename}}")
        except Exception as e:
            print(f"❌ 読み込みエラー: {{e}}")


def main():
    """メイン関数"""
    print("🌟 Vive Paradigm プロトタイプ")
    print(f"💡 アイデア: {idea}")
    print("📚 体験から学習し、改善点を見つけましょう！")
    
    # プロトタイプを作成・実行
    prototype = {idea.replace(' ', '').title()}Prototype()
    prototype.run()
    
    print("\\n🎯 プロトタイプ体験完了！")
    print("🔄 次のステップ:")
    print("• UIの改善")
    print("• 新機能の追加") 
    print("• エラーハンドリングの強化")
    print("• データベース連携")


if __name__ == "__main__":
    main()'''
    
    def _create_readme(self, idea: str, prototype_type: str, files: List[str]) -> str:
        """README ファイルを生成"""
        return f'''# {idea} - プロトタイプ

🌟 **Vive Paradigm Implementer** によって生成されたプロトタイプです

## 💡 アイデア
{idea}

## 📋 概要
このプロトタイプは「体験から理解へ」のVive Paradigmに基づいて、10分間で作成されました。
まず動作を体験し、その後で理論や改善点を学習することを目的としています。

## 📁 ファイル構成
{chr(10).join(f"- `{file}`" for file in files)}

## 🚀 実行方法

### 前提条件
- Python 3.7+ (Pythonプロトタイプの場合)
- モダンなWebブラウザ (Webアプリの場合)

### 実行手順
{'1. 依存関係をインストール: `pip install -r requirements.txt`' if 'requirements.txt' in files else ''}
{'2. サーバーを起動: `uvicorn main:app --reload`' if prototype_type == 'api' else ''}
{'2. Webブラウザで `index.html` を開く' if prototype_type == 'web' else ''}
{'2. `python main.py` を実行' if prototype_type in ['python', 'data_viz'] else ''}

## 🎯 学習ポイント

### 体験すべきこと
1. **基本機能の動作確認**
   - プロトタイプを実際に使ってみる
   - どんな操作ができるかを探る
   - 期待通りに動作するかを確認

2. **改善点の発見**
   - 使いにくい部分はないか？
   - 欠けている機能はないか？
   - エラーが発生する場合はないか？

3. **拡張アイデアの着想**
   - どんな機能があったら便利か？
   - 他のシステムとの連携可能性
   - スケールアップの方法

## 🔄 次のステップ提案

### 5分でできる改善
- [ ] UIの見た目を改善
- [ ] エラーメッセージの追加
- [ ] 基本的な入力検証

### 10分でできる機能追加
- [ ] データの永続化
- [ ] 検索・フィルタ機能
- [ ] 設定画面の追加

### 15分でできる高度な改善
- [ ] レスポンシブデザイン対応
- [ ] API連携
- [ ] テストケースの作成

## ⚡ Vive Paradigm の実践

このプロトタイプは以下の原則で作成されています：

1. **完璧より速度**: まず動くものを作る
2. **体験重視**: 理論より実践、説明より体験
3. **段階的発展**: 小さな成功の積み重ね
4. **学習促進**: 作る過程での気づきを最大化

## 📚 参考資料

- [Vive Paradigm Guide](../docs/vive_paradigm_guide.md)
- [プロトタイプ改善チェックリスト](../docs/improvement_checklist.md)

## 🤝 貢献・改善

このプロトタイプを改善したアイデアがあれば、ぜひ実装してみてください！
小さな変更から始めて、段階的に理想の形に近づけていきましょう。

---

**作成日**: {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**プロトタイプタイプ**: {prototype_type}  
**生成エンジン**: Vive Paradigm Implementer v1.0'''
    
    def quick_improve(self, prototype_result: Dict, improvement_type: str) -> Dict:
        """5分以内での迅速な改善を実行"""
        print(f"⚡ 迅速改善: {improvement_type}")
        
        output_path = prototype_result.get("output_path")
        if not output_path or not os.path.exists(output_path):
            raise Exception("プロトタイプの出力パスが見つかりません")
        
        changes_made = []
        modified_files = []
        
        if improvement_type == "ui":
            changes_made, modified_files = self._improve_ui(output_path)
        elif improvement_type == "feature":
            changes_made, modified_files = self._add_feature(output_path)
        elif improvement_type == "error_handling":
            changes_made, modified_files = self._add_error_handling(output_path)
        else:
            raise Exception(f"未対応の改善タイプ: {improvement_type}")
        
        return {
            "changes": changes_made,
            "modified_files": modified_files
        }
    
    def _improve_ui(self, output_path: str) -> Tuple[List[str], List[str]]:
        """UI改善を実行"""
        changes = []
        modified = []
        
        css_path = os.path.join(output_path, "style.css")
        if os.path.exists(css_path):
            # CSS に改善を追加
            with open(css_path, "a", encoding="utf-8") as f:
                f.write("""
/* UI改善 - 迅速改善により追加 */
.improved-animation {
    transition: all 0.3s ease;
}

.improved-animation:hover {
    transform: scale(1.02);
    box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}

.success-message {
    background: linear-gradient(45deg, #48bb78, #38a169);
    color: white;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}
""")
            changes.append("CSS: アニメーション効果と成功メッセージスタイルを追加")
            modified.append("style.css")
        
        return changes, modified
    
    def _add_feature(self, output_path: str) -> Tuple[List[str], List[str]]:
        """新機能を追加"""
        changes = []
        modified = []
        
        js_path = os.path.join(output_path, "script.js")
        if os.path.exists(js_path):
            # JavaScript に新機能を追加
            with open(js_path, "a", encoding="utf-8") as f:
                f.write("""
// 新機能 - エクスポート機能
function exportData() {
    const dataStr = JSON.stringify(appState.items, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'prototype_data.json';
    link.click();
    updateOutput('📥 データをエクスポートしました');
}
""")
            changes.append("JavaScript: データエクスポート機能を追加")
            modified.append("script.js")
        
        return changes, modified
    
    def _add_error_handling(self, output_path: str) -> Tuple[List[str], List[str]]:
        """エラーハンドリングを追加"""
        changes = []
        modified = []
        
        # Python ファイルがある場合
        py_files = [f for f in os.listdir(output_path) if f.endswith('.py')]
        if py_files:
            py_path = os.path.join(output_path, py_files[0])
            with open(py_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # エラーハンドリングを追加（簡易版）
            if "try:" not in content:
                improved_content = content.replace(
                    "def main():",
                    """def main():
    try:"""
                ).replace(
                    'if __name__ == "__main__":',
                    '''    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")
        print("🔧 プロトタイプを改善して再試行してください")

if __name__ == "__main__":'''
                )
                
                with open(py_path, "w", encoding="utf-8") as f:
                    f.write(improved_content)
                
                changes.append("Python: 基本的なエラーハンドリングを追加")
                modified.append(py_files[0])
        
        return changes, modified
    
    def _get_python_requirements(self, template_info: Dict) -> List[str]:
        """Python プロジェクトの requirements を取得"""
        requirements = []
        
        if template_info.get("complexity") == "advanced":
            requirements.extend(["requests>=2.25.0", "click>=8.0.0"])
        
        return requirements
    
    def _create_data_viz_template(self, idea: str, template_info: Dict) -> str:
        """データ可視化テンプレートを作成"""
        return f'''#!/usr/bin/env python3
"""
{idea} - データ可視化プロトタイプ
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_sample_visualization():
    """サンプルデータの可視化を作成"""
    
    # データ読み込み
    if os.path.exists('sample_data.csv'):
        df = pd.read_csv('sample_data.csv')
        print("📊 sample_data.csv からデータを読み込みました")
    else:
        # サンプルデータを生成
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        values = np.random.randint(10, 100, 30)
        df = pd.DataFrame({{'date': dates, 'value': values}})
        print("📊 サンプルデータを生成しました")
    
    # 可視化を作成
    plt.figure(figsize=(12, 8))
    
    # サブプロット1: 線グラフ
    plt.subplot(2, 2, 1)
    plt.plot(df.index, df.iloc[:, -1], marker='o', linewidth=2, markersize=4)
    plt.title(f'📈 {{idea}} - 時系列データ', fontsize=14, pad=20)
    plt.xlabel('時間')
    plt.ylabel('値')
    plt.grid(True, alpha=0.3)
    
    # サブプロット2: ヒストグラム
    plt.subplot(2, 2, 2)
    plt.hist(df.iloc[:, -1], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
    plt.title('📊 値の分布', fontsize=14, pad=20)
    plt.xlabel('値')
    plt.ylabel('頻度')
    
    # サブプロット3: 散布図
    plt.subplot(2, 2, 3)
    x = np.arange(len(df))
    y = df.iloc[:, -1]
    colors = plt.cm.viridis(np.linspace(0, 1, len(df)))
    plt.scatter(x, y, c=colors, alpha=0.7, s=50)
    plt.title('🎯 散布図', fontsize=14, pad=20)
    plt.xlabel('インデックス')
    plt.ylabel('値')
    
    # サブプロット4: 統計サマリー（テキスト）
    plt.subplot(2, 2, 4)
    plt.axis('off')
    stats_text = f'''
📋 統計サマリー

データ数: {{len(df)}}
平均値: {{df.iloc[:, -1].mean():.2f}}
最大値: {{df.iloc[:, -1].max()}}
最小値: {{df.iloc[:, -1].min()}}
標準偏差: {{df.iloc[:, -1].std():.2f}}

🎯 {idea}
Vive Paradigm プロトタイプ
    '''
    plt.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
    
    plt.tight_layout()
    
    # 保存
    output_file = f'{idea.replace(" ", "_").lower()}_visualization.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"💾 可視化を保存しました: {{output_file}}")
    
    # 表示
    plt.show()
    
    return output_file

def main():
    print(f"🎨 {{idea}} - データ可視化プロトタイプ")
    print("=" * 50)
    
    try:
        output_file = create_sample_visualization()
        print(f"\\n✅ 可視化完成: {{output_file}}")
        print("\\n🔄 次のステップ:")
        print("• 実際のデータを使用")
        print("• インタラクティブな可視化 (plotly)")
        print("• 複数のグラフタイプを試す")
        print("• カスタムカラーパレット")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {{e}}")
        print("🔧 requirements.txt の依存関係を確認してください")

if __name__ == "__main__":
    main()'''
    
    def _create_sample_data(self, template_info: Dict) -> str:
        """サンプルデータCSVを生成"""
        return '''date,category,value,status
2025-01-01,A,45,active
2025-01-02,B,67,active
2025-01-03,A,23,inactive
2025-01-04,C,89,active
2025-01-05,B,34,active
2025-01-06,A,56,active
2025-01-07,C,78,inactive
2025-01-08,B,45,active
2025-01-09,A,67,active
2025-01-10,C,34,active'''

    def _create_api_template(self, idea: str, template_info: Dict) -> str:
        """API テンプレートを作成"""
        return f'''#!/usr/bin/env python3
"""
{idea} - API プロトタイプ
FastAPI を使用したシンプルなREST API
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import os

# データモデル
class Item(BaseModel):
    id: Optional[int] = None
    text: str
    category: Optional[str] = "general"
    created: Optional[str] = None

class ItemResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    message: str

# FastAPI アプリ作成
app = FastAPI(
    title="{idea} API",
    description="Vive Paradigm プロトタイプ API",
    version="1.0.0"
)

# メモリ内データストレージ（プロトタイプ用）
items_db = []
next_id = 1

# データファイルパス
DATA_FILE = "api_data.json"

def load_data():
    """データをファイルから読み込み"""
    global items_db, next_id
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            items_db = data.get('items', [])
            next_id = data.get('next_id', 1)

def save_data():
    """データをファイルに保存"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({{
            'items': items_db,
            'next_id': next_id
        }}, f, ensure_ascii=False, indent=2)

# 起動時にデータを読み込み
load_data()

# API エンドポイント

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {{
        "message": f"🚀 {{idea}} API プロトタイプ",
        "version": "1.0.0",
        "endpoints": ["/items", "/items/{{id}}", "/health"],
        "docs": "/docs"
    }}

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {{
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "items_count": len(items_db)
    }}

@app.get("/items", response_model=List[Dict])
async def get_items(category: Optional[str] = None, limit: Optional[int] = 100):
    """全アイテムを取得"""
    filtered_items = items_db
    
    if category:
        filtered_items = [item for item in items_db if item.get('category') == category]
    
    return filtered_items[:limit]

@app.get("/items/{{item_id}}")
async def get_item(item_id: int):
    """指定IDのアイテムを取得"""
    item = next((item for item in items_db if item['id'] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="アイテムが見つかりません")
    return item

@app.post("/items", response_model=ItemResponse)
async def create_item(item: Item):
    """新しいアイテムを作成"""
    global next_id
    
    if not item.text.strip():
        raise HTTPException(status_code=400, detail="テキストは必須です")
    
    new_item = {{
        "id": next_id,
        "text": item.text,
        "category": item.category,
        "created": datetime.now().isoformat()
    }}
    
    items_db.append(new_item)
    next_id += 1
    save_data()
    
    return ItemResponse(
        success=True,
        data=new_item,
        message="アイテムを作成しました"
    )

@app.put("/items/{{item_id}}", response_model=ItemResponse)
async def update_item(item_id: int, item: Item):
    """アイテムを更新"""
    existing_item = next((item for item in items_db if item['id'] == item_id), None)
    if not existing_item:
        raise HTTPException(status_code=404, detail="アイテムが見つかりません")
    
    existing_item['text'] = item.text
    existing_item['category'] = item.category
    existing_item['updated'] = datetime.now().isoformat()
    
    save_data()
    
    return ItemResponse(
        success=True,
        data=existing_item,
        message="アイテムを更新しました"
    )

@app.delete("/items/{{item_id}}", response_model=ItemResponse)
async def delete_item(item_id: int):
    """アイテムを削除"""
    global items_db
    original_count = len(items_db)
    items_db = [item for item in items_db if item['id'] != item_id]
    
    if len(items_db) == original_count:
        raise HTTPException(status_code=404, detail="アイテムが見つかりません")
    
    save_data()
    
    return ItemResponse(
        success=True,
        message="アイテムを削除しました"
    )

@app.get("/stats")
async def get_stats():
    """統計情報を取得"""
    categories = {{}}
    for item in items_db:
        cat = item.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    return {{
        "total_items": len(items_db),
        "categories": categories,
        "api_info": {{
            "name": "{idea} API",
            "version": "1.0.0",
            "created_by": "Vive Paradigm Implementer"
        }}
    }}

# CORS対応（プロトタイプ用）
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # プロダクションでは適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 {{idea}} API を起動中...")
    print("📖 API ドキュメント: http://localhost:8000/docs")
    print("🧪 テストクライアント: test_client.html")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)'''

    def _create_api_client_template(self, idea: str) -> str:
        """API テストクライアントを作成"""
        return f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{idea} API テストクライアント</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #4a5568;
            text-align: center;
            margin-bottom: 30px;
        }}
        .api-section {{
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
        }}
        .method {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            margin-right: 10px;
        }}
        .get {{ background: #38a169; }}
        .post {{ background: #3182ce; }}
        .put {{ background: #d69e2e; }}
        .delete {{ background: #e53e3e; }}
        input, textarea {{
            width: 100%;
            padding: 10px;
            margin: 5px 0 15px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }}
        button {{
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }}
        button:hover {{
            background: #5a6fd8;
        }}
        .response {{
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 15px;
            margin-top: 15px;
            white-space: pre-wrap;
            font-family: monospace;
            max-height: 300px;
            overflow-y: auto;
        }}
        .error {{
            background: #fed7d7;
            border-color: #feb2b2;
            color: #c53030;
        }}
        .success {{
            background: #c6f6d5;
            border-color: #9ae6b4;
            color: #276749;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 {idea} API テストクライアント</h1>
        <p>📡 API ベースURL: <code id="baseUrl">http://localhost:8000</code></p>
        
        <!-- GET /items -->
        <div class="api-section">
            <h3><span class="method get">GET</span>/items - アイテム一覧取得</h3>
            <label>カテゴリ (オプション):</label>
            <input type="text" id="getCategory" placeholder="general, work, personal など">
            <label>件数制限 (オプション):</label>
            <input type="number" id="getLimit" placeholder="10" value="10">
            <button onclick="getItems()">取得</button>
            <div id="getItemsResponse" class="response"></div>
        </div>
        
        <!-- POST /items -->
        <div class="api-section">
            <h3><span class="method post">POST</span>/items - アイテム作成</h3>
            <label>テキスト:</label>
            <input type="text" id="postText" placeholder="新しいアイテムのテキスト" required>
            <label>カテゴリ:</label>
            <input type="text" id="postCategory" placeholder="general" value="general">
            <button onclick="createItem()">作成</button>
            <div id="createItemResponse" class="response"></div>
        </div>
        
        <!-- GET /items/id -->
        <div class="api-section">
            <h3><span class="method get">GET</span>/items/{{id}} - 特定アイテム取得</h3>
            <label>アイテムID:</label>
            <input type="number" id="getItemId" placeholder="1" required>
            <button onclick="getItem()">取得</button>
            <div id="getItemResponse" class="response"></div>
        </div>
        
        <!-- PUT /items/id -->
        <div class="api-section">
            <h3><span class="method put">PUT</span>/items/{{id}} - アイテム更新</h3>
            <label>アイテムID:</label>
            <input type="number" id="putItemId" placeholder="1" required>
            <label>新しいテキスト:</label>
            <input type="text" id="putText" placeholder="更新されたテキスト" required>
            <label>新しいカテゴリ:</label>
            <input type="text" id="putCategory" placeholder="general" value="general">
            <button onclick="updateItem()">更新</button>
            <div id="updateItemResponse" class="response"></div>
        </div>
        
        <!-- DELETE /items/id -->
        <div class="api-section">
            <h3><span class="method delete">DELETE</span>/items/{{id}} - アイテム削除</h3>
            <label>アイテムID:</label>
            <input type="number" id="deleteItemId" placeholder="1" required>
            <button onclick="deleteItem()">削除</button>
            <div id="deleteItemResponse" class="response"></div>
        </div>
        
        <!-- Stats -->
        <div class="api-section">
            <h3><span class="method get">GET</span>/stats - 統計情報</h3>
            <button onclick="getStats()">統計取得</button>
            <div id="statsResponse" class="response"></div>
        </div>
    </div>

    <script>
        const baseUrl = 'http://localhost:8000';
        
        async function makeRequest(url, options = {{}}) {{
            try {{
                const response = await fetch(url, {{
                    headers: {{
                        'Content-Type': 'application/json',
                        ...options.headers
                    }},
                    ...options
                }});
                
                const data = await response.json();
                return {{ data, status: response.status, ok: response.ok }};
            }} catch (error) {{
                return {{ error: error.message, status: 0, ok: false }};
            }}
        }}
        
        function displayResponse(elementId, result) {{
            const element = document.getElementById(elementId);
            element.className = 'response ' + (result.ok ? 'success' : 'error');
            
            if (result.error) {{
                element.textContent = `エラー: ${{result.error}}`;
            }} else {{
                element.textContent = `Status: ${{result.status}}\\n\\n${{JSON.stringify(result.data, null, 2)}}`;
            }}
        }}
        
        async function getItems() {{
            const category = document.getElementById('getCategory').value;
            const limit = document.getElementById('getLimit').value;
            
            let url = `${{baseUrl}}/items`;
            const params = new URLSearchParams();
            if (category) params.append('category', category);
            if (limit) params.append('limit', limit);
            if (params.toString()) url += '?' + params.toString();
            
            const result = await makeRequest(url);
            displayResponse('getItemsResponse', result);
        }}
        
        async function createItem() {{
            const text = document.getElementById('postText').value;
            const category = document.getElementById('postCategory').value;
            
            if (!text) {{
                alert('テキストを入力してください');
                return;
            }}
            
            const result = await makeRequest(`${{baseUrl}}/items`, {{
                method: 'POST',
                body: JSON.stringify({{ text, category }})
            }});
            
            displayResponse('createItemResponse', result);
        }}
        
        async function getItem() {{
            const id = document.getElementById('getItemId').value;
            if (!id) {{
                alert('アイテムIDを入力してください');
                return;
            }}
            
            const result = await makeRequest(`${{baseUrl}}/items/${{id}}`);
            displayResponse('getItemResponse', result);
        }}
        
        async function updateItem() {{
            const id = document.getElementById('putItemId').value;
            const text = document.getElementById('putText').value;
            const category = document.getElementById('putCategory').value;
            
            if (!id || !text) {{
                alert('IDとテキストを入力してください');
                return;
            }}
            
            const result = await makeRequest(`${{baseUrl}}/items/${{id}}`, {{
                method: 'PUT',
                body: JSON.stringify({{ text, category }})
            }});
            
            displayResponse('updateItemResponse', result);
        }}
        
        async function deleteItem() {{
            const id = document.getElementById('deleteItemId').value;
            if (!id) {{
                alert('アイテムIDを入力してください');
                return;
            }}
            
            if (!confirm(`アイテム ${{id}} を削除しますか？`)) {{
                return;
            }}
            
            const result = await makeRequest(`${{baseUrl}}/items/${{id}}`, {{
                method: 'DELETE'
            }});
            
            displayResponse('deleteItemResponse', result);
        }}
        
        async function getStats() {{
            const result = await makeRequest(`${{baseUrl}}/stats`);
            displayResponse('statsResponse', result);
        }}
        
        // 初期化時にヘルスチェック
        window.onload = async function() {{
            const result = await makeRequest(`${{baseUrl}}/health`);
            if (result.ok) {{
                console.log('✅ API サーバーが正常に動作しています');
            }} else {{
                console.warn('⚠️ API サーバーに接続できません。サーバーが起動しているか確認してください。');
            }}
        }};
    </script>
</body>
</html>'''


if __name__ == "__main__":
    # テスト実行
    generator = PrototypeGenerator()
    
    test_template = {
        "name": "web_app_basic",
        "type": "web",
        "complexity": "simple"
    }
    
    result = generator.generate(
        idea="テストアプリ",
        template_info=test_template,
        time_limit=10
    )
    
    print("🎯 テスト完了:", result)