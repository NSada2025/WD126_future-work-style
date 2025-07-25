# Claude Code サブエージェント公式ガイド（日本語版）

## サブエージェントとは

### 定義
サブエージェントは「特定の目的を持つ専門化されたAIアシスタント」です。

### 各サブエージェントが持つもの
- **独自のコンテキストウィンドウ** - メインスレッドから独立
- **カスタマイズされたシステムプロンプト** - 専門性を定義
- **特定のツールアクセス** - 必要なツールのみ
- **専門分野** - 明確な責任範囲

## 使用方法

### 1. サブエージェントの作成
```bash
/agents
```

### 2. 明示的な呼び出し
```
> Use the code-reviewer sub agent to check my recent changes
> code-reviewerサブエージェントを使って最近の変更をチェックして
```

### 3. 自動委譲
タスクの説明に基づいて、Claudeが自動的に適切なサブエージェントに委譲することも可能。

## プロジェクトでの実装例

### code-reviewer エージェント
```yaml
name: code-reviewer
description: コードの品質、セキュリティ、保守性をチェック
prompt: |
  あなたは経験豊富なコードレビュアーです。
  以下の観点でコードを分析してください：
  - セキュリティの脆弱性
  - パフォーマンスの問題
  - 可読性と保守性
  - ベストプラクティスの遵守
tools:
  - read
  - grep
  - bash
```

### debugger エージェント
```yaml
name: debugger
description: エラーの根本原因分析を実行
prompt: |
  あなたはデバッグの専門家です。
  エラーメッセージとコードを分析し、
  根本原因を特定して解決策を提案してください。
tools:
  - read
  - grep
  - bash
  - edit
```

### data-scientist エージェント
```yaml
name: data-scientist
description: SQLクエリとデータ分析タスクを処理
prompt: |
  あなたはデータサイエンティストです。
  効率的なSQLクエリを作成し、
  データの洞察を提供してください。
tools:
  - read
  - write
  - bash
```

## WDプロジェクトへの適用

### project-health-checker エージェント
```yaml
name: project-health-checker
description: use PROACTIVELY - プロジェクトの健康状態を診断
prompt: |
  プロジェクトの健康状態を以下の基準で評価してください：
  1. 最終更新日（7日以内: 🟢, 30日以内: 🟡, それ以上: 🔴）
  2. README.mdの完成度
  3. 未解決のIssue数
  4. テストカバレッジ
  
  5分でできる改善提案を3つ提供してください。
```

### vive-learning-assistant エージェント
```yaml
name: vive-learning-assistant
description: use PROACTIVELY - 新技術の実装を通じた学習支援
prompt: |
  Vive Paradigmに基づいて学習を支援します：
  1. まず動くコードを作成
  2. 実行結果から概念を説明
  3. 段階的に理解を深める
  4. 実践的な応用例を提示
```

## ベストプラクティス

### 1. 単一責任の原則
```
❌ 悪い例: "コードレビューとデバッグとドキュメント作成を行う"
✅ 良い例: "コードのセキュリティレビューに特化"
```

### 2. 詳細なプロンプト
```yaml
# 具体的な指示を含める
prompt: |
  セキュリティレビューの際は：
  - OWASP Top 10を基準に
  - 環境変数の露出をチェック
  - SQLインジェクションの可能性を検証
```

### 3. 必要最小限のツール
```yaml
# 読み取り専用のレビュアー
tools:
  - read
  - grep
  
# 修正も行うフィクサー
tools:
  - read
  - grep
  - edit
  - write
```

### 4. プロアクティブな使用促進
```yaml
description: use PROACTIVELY - セキュリティチェックを自動実行
```

## 制限事項と注意点

### 1. レイテンシ
- 毎回クリーンな状態から開始するため、初期化に時間がかかる
- 大量の並列実行は避ける

### 2. コンテキスト
- メインスレッドのコンテキストは引き継がない
- 必要な情報は明示的に渡す

### 3. 優先順位
- プロジェクトレベルのサブエージェント > ユーザーレベル
- 同名の場合はプロジェクトレベルが優先

## tmuxマルチエージェントとの統合

### アーキテクチャ
```
tmux永続エージェント
├── PRESIDENT
├── boss1
│   └─→ project-health-checker (自動起動)
│   └─→ code-reviewer (必要時)
├── worker1
│   └─→ vive-learning-assistant
└── worker2
    └─→ debugger
```

### 実装例
```bash
# boss1がサブエージェントを活用
./send.sh boss1 "全WDプロジェクトの健康診断を実行。project-health-checkerサブエージェントを使用してください。"

# worker1がVive Learning実践
./send.sh worker1 "Rustを学びたい。vive-learning-assistantを使って実装しながら学習を進めてください。"
```

## 推奨：最初のステップ

1. Claudeに依頼してサブエージェントを生成
```
> Create a sub agent for checking project health across multiple repositories
```

2. 生成されたエージェントをカスタマイズ

3. プロジェクトに保存してバージョン管理

これにより、チーム全体で同じサブエージェントを共有できます。