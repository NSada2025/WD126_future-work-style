# 📖 使用例とベストプラクティス

## 🚀 基本的な使用例

### 1. シンプルなWebアプリ作成

```python
from claude_integration import vive_create, vive_improve, vive_next_steps

# 基本的なプロトタイプ作成
result = vive_create(
    "タスク管理アプリ",
    technology="web",
    time_limit=10
)

# 成功した場合の改善
if result.get("success"):
    # UI改善
    vive_improve("ui")
    
    # 次のステップを確認
    vive_next_steps()
```

### 2. データ可視化プロトタイプ

```python
# データ分析向けプロトタイプ
result = vive_create(
    "売上データの可視化ダッシュボード",
    technology="data_viz",
    time_limit=12
)

print(f"作成ファイル: {result.get('files_created')}")
print(f"実行方法: {result.get('executable_command')}")
```

### 3. Python自動化スクリプト

```python
# 自動化スクリプトの作成
result = vive_create(
    "ファイル整理とリネーム自動化",
    technology="python",
    time_limit=8,
    complexity="simple"
)

# 機能追加による改善
if result.get("success"):
    vive_improve("feature")
```

### 4. REST API開発

```python
# API サービスのプロトタイプ
result = vive_create(
    "ユーザー管理API",
    technology="api",
    time_limit=15,
    complexity="medium"
)

# APIが作成された場合のテスト
if result.get("success"):
    print("APIテストクライアント: test_client.html")
    print("ドキュメント: http://localhost:8000/docs")
```

## 🎯 学習シナリオ別使用例

### シナリオ1: プログラミング初心者

```python
# ステップ1: 超シンプルなスタート
vive_create("Hello Worldボタン", technology="web", time_limit=5)

# ステップ2: インタラクションを追加
vive_create("クリックカウンター", technology="web", time_limit=7)

# ステップ3: データ管理を体験
vive_create("簡単なメモアプリ", technology="web", time_limit=10)

# 各段階で学習ガイドを確認して理論を習得
```

### シナリオ2: 新技術習得

```python
# 新しい技術スタックを体験
technologies = ["web", "python", "data_viz", "api"]

for tech in technologies:
    idea = f"{tech}の基本機能デモ"
    result = vive_create(idea, technology=tech, time_limit=8)
    
    if result.get("success"):
        print(f"{tech}: 体験完了 ✅")
        # 学習ガイドで理論を補完
```

### シナリオ3: 制約下での開発練習

```python
# 時間制約チャレンジ
quick_ideas = [
    "3分で電卓",
    "5分でタイマー", 
    "7分でクイズアプリ"
]

for idea in quick_ideas:
    time_limit = int(idea.split("分で")[0])
    app_name = idea.split("分で")[1]
    
    print(f"🏃 チャレンジ: {idea}")
    result = vive_create(app_name, technology="web", time_limit=time_limit)
    
    success = "✅" if result.get("success") else "⚠️"
    print(f"結果: {success}")
```

## 💡 プロジェクト別ベストプラクティス

### Webアプリケーション

```python
# 推奨パターン1: UI重視
result = vive_create(
    "フォトギャラリー",
    technology="web",
    time_limit=12
)

# UI改善は最も効果的
vive_improve("ui")

# 推奨パターン2: インタラクション重視  
result = vive_create(
    "ドラッグ&ドロップファイル管理",
    technology="web",
    complexity="medium"
)
```

### Python開発

```python
# 推奨パターン1: CLI重視
result = vive_create(
    "ログファイル解析ツール",
    technology="python",
    complexity="simple"
)

# 機能追加が効果的
vive_improve("feature")

# 推奨パターン2: データ処理重視
result = vive_create(
    "CSV データ変換バッチ",
    technology="python",
    time_limit=10
)
```

### データ可視化

```python
# 推奨パターン1: 基本グラフから開始
result = vive_create(
    "月別売上推移グラフ",
    technology="data_viz",
    complexity="simple"
)

# 推奨パターン2: インタラクティブ要素
result = vive_create(
    "フィルタリング可能なダッシュボード",
    technology="data_viz",
    complexity="medium",
    time_limit=15
)
```

### API開発

```python
# 推奨パターン1: シンプルなCRUD
result = vive_create(
    "ブックマーク管理API",
    technology="api",
    complexity="simple"
)

# 推奨パターン2: 認証機能付き
result = vive_create(
    "ユーザー認証付きタスクAPI",
    technology="api", 
    complexity="medium",
    time_limit=18
)
```

## 🔧 高度な使用テクニック

### 1. カスタム制約での学習

```python
# 複雑さレベル制限
result = vive_create(
    "機能豊富なアプリ",
    complexity="simple",  # 意図的にシンプルに制限
    time_limit=15
)

# 技術制約
result = vive_create(
    "データ処理アプリ",
    technology="python",  # 特定技術に限定
    time_limit=10
)
```

### 2. 連続改善パターン

```python
# 基本版作成
base_result = vive_create("計算機", technology="web", time_limit=5)

if base_result.get("success"):
    # 段階的改善
    vive_improve("ui")         # Step 1: 見た目
    vive_improve("feature")    # Step 2: 機能
    vive_improve("error_handling")  # Step 3: 堅牢性
```

### 3. テーマ別探索

```python
# 「タスク管理」テーマの多角的探索
theme = "タスク管理"

approaches = {
    "web": f"{theme}Webアプリ",
    "python": f"{theme}CLIツール", 
    "data_viz": f"{theme}進捗可視化",
    "api": f"{theme}API"
}

for tech, idea in approaches.items():
    result = vive_create(idea, technology=tech, time_limit=10)
    print(f"{tech}アプローチ: {'✅' if result.get('success') else '⚠️'}")
```

## 📊 セッション管理のベストプラクティス

### 統計の活用

```python
from claude_integration import vive_stats, vive_history

# セッション開始時
print("今日の学習セッション開始")

# 複数のプロトタイプ作成...

# セッション終了時の振り返り
print("\\n今日の成果:")
vive_history()

print("\\n統計情報:")
vive_stats()
```

### 学習進捗の記録

```python
# 学習日記パターン
learning_log = []

def record_learning(idea, result):
    log_entry = {
        "date": "2025-07-25",
        "idea": idea,
        "success": result.get("success"),
        "time": result.get("creation_time_minutes"),
        "learnings": result.get("learning_points", [])
    }
    learning_log.append(log_entry)

# 使用例
result = vive_create("天気アプリ", technology="web")
record_learning("天気アプリ", result)
```

## ⚠️ よくある失敗パターンと対策

### 失敗パターン1: 複雑すぎるアイデア

```python
# ❌ 失敗例
result = vive_create(
    "機械学習による株価予測システム with リアルタイム更新とソーシャル機能",
    time_limit=10  # 明らかに不足
)

# ✅ 改善例
result = vive_create(
    "シンプルな株価グラフ表示",
    technology="data_viz",
    time_limit=10
)
```

### 失敗パターン2: 完璧主義

```python
# ❌ 失敗例: 完璧を求めすぎ
result = vive_create("ToDOアプリ", time_limit=10)
if not result.get("success"):
    print("失敗した、もう一度...")  # これは非生産的

# ✅ 改善例: 部分成功も価値として認識
result = vive_create("ToDOアプリ", time_limit=10)
if result.get("files_created"):
    print("基本機能は実装できた。次のステップへ!")
    vive_next_steps()
```

### 失敗パターン3: 学習ガイドを読まない

```python
# ❌ 失敗例: 作って終わり
result = vive_create("計算機", technology="web")
print("完成!")  # これでは学習効果が薄い

# ✅ 改善例: 体験を学習につなげる
result = vive_create("計算機", technology="web")
if result.get("success"):
    print("完成! 学習ガイドで理論を確認...")
    # learning_guide.md を読む
    vive_next_steps()  # 次の学習ステップを確認
```

## 🎉 成功パターンの例

### パターン1: 段階的スキルアップ

```python
# 週次学習計画
week_1 = [
    ("HTML基礎", "静的ページ", "web", 5),
    ("CSS基礎", "スタイリング", "web", 7),
    ("JS基礎", "インタラクション", "web", 10)
]

for day, (skill, idea, tech, time) in enumerate(week_1, 1):
    print(f"Day {day}: {skill}学習")
    result = vive_create(idea, technology=tech, time_limit=time)
    
    if result.get("success"):
        print(f"✅ {skill} 体験完了")
    else:
        print(f"📚 {skill} 基礎は習得、更なる学習が必要")
```

### パターン2: プロジェクト駆動学習

```python
# 実用的なプロジェクトを段階的に構築
project_phases = [
    ("フェーズ1", "基本UI", "web", 8),
    ("フェーズ2", "データ保存", "web", 12),
    ("フェーズ3", "ユーザー管理", "web", 15),
    ("フェーズ4", "API統合", "api", 20)
]

for phase, description, tech, time in project_phases:
    print(f"\\n{phase}: {description}")
    result = vive_create(f"タスク管理{description}", technology=tech, time_limit=time)
    
    if result.get("success"):
        print("✅ フェーズ完了、次へ進行")
    else:
        print("⚠️ 基本実装完了、理論学習で補完")
        break  # 無理をせず学習に集中
```

## 🌟 まとめ

Vive Paradigm Implementerを効果的に使うコツ：

1. **小さく始める** - 複雑なアイデアは分割
2. **時間を守る** - 制限時間が創造性を促進
3. **失敗を恐れない** - 部分的成功も価値がある
4. **学習ガイドを活用** - 体験を理論につなげる
5. **継続する** - 毎日少しずつでも実践

最も重要なのは、**体験すること**です。まずは簡単なアイデアから始めて、Vive Paradigmの効果を実感してください！