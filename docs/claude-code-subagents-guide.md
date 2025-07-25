# Claude Code サブエージェント機能ガイド

## 概要
Claude Codeのサブエージェント機能は、特定のタスクに特化したAIアシスタントを作成・管理できる機能です。

## 利用可能なコマンド

### /agents
カスタムAIサブエージェントの管理コマンド。特殊化されたタスクのためのエージェントを作成・管理します。

## サブエージェントとTaskツールの関係

### Taskツール（現在利用可能）
```python
# 現在のサブエージェント実行方法
Task(
    description="短い説明",
    prompt="詳細なタスク指示",
    subagent_type="general-purpose"
)
```

### 特徴
1. **並列実行**: 最大10個まで同時実行可能
2. **独立コンテキスト**: 各エージェントが独自のメモリを持つ
3. **一時的実行**: タスク完了で自動終了

## 実践的な使用例

### 1. マルチファイル並列探索
```python
# 4つのサブエージェントで異なるディレクトリを探索
tasks = [
    {"dir": "src/", "pattern": "*.py"},
    {"dir": "docs/", "pattern": "*.md"},
    {"dir": "tests/", "pattern": "test_*.py"},
    {"dir": "examples/", "pattern": "*.js"}
]

for task in tasks:
    Task(
        description=f"{task['dir']}の探索",
        prompt=f"{task['dir']}ディレクトリ内の{task['pattern']}ファイルを分析し、主要な機能をリストアップしてください",
        subagent_type="general-purpose"
    )
```

### 2. 多視点コード分析
```python
# 異なる専門性を持つエージェントによる分析
perspectives = [
    {"role": "セキュリティ専門家", "focus": "脆弱性とセキュリティリスク"},
    {"role": "パフォーマンス専門家", "focus": "最適化可能な箇所"},
    {"role": "可読性専門家", "focus": "コードの明瞭性と保守性"},
    {"role": "テスト専門家", "focus": "テストカバレッジと品質"}
]

for p in perspectives:
    Task(
        description=f"{p['role']}による分析",
        prompt=f"あなたは{p['role']}です。以下のコードを{p['focus']}の観点から分析してください：[コード内容]",
        subagent_type="general-purpose"
    )
```

### 3. プロジェクト健康診断
```python
# WD132_project-vitality-systemとの統合例
projects = ["WD126", "WD127", "WD128", "WD129", "WD130"]

for project in projects:
    Task(
        description=f"{project}の健康診断",
        prompt=f"""
        {project}プロジェクトの健康状態を診断してください：
        1. 最終更新日を確認
        2. README.mdの完成度を評価
        3. 未完了タスクをリストアップ
        4. 5分でできる改善提案を3つ
        """,
        subagent_type="general-purpose"
    )
```

## tmuxマルチエージェントとの統合案

### ハイブリッドアーキテクチャ
```
tmux永続エージェント（専門化）
├── PRESIDENT（戦略）
├── boss1（管理）
│   └── Claude Codeサブエージェント×10（並列タスク）
├── worker1（実装）
│   └── Claude Codeサブエージェント×10（コード生成）
├── worker2（テスト）
│   └── Claude Codeサブエージェント×10（テスト実行）
└── worker3（ドキュメント）
    └── Claude Codeサブエージェント×10（文書作成）
```

### 実装例
```bash
# boss1からサブエージェントを起動
./send.sh boss1 "10個のWDプロジェクトの健康診断を並列実行してください。各プロジェクトに1つのサブエージェントを割り当て、結果をまとめて報告してください。"
```

## ベストプラクティス

### 1. タスクの粒度
- 各サブエージェントには明確で独立したタスクを割り当てる
- 依存関係のあるタスクは避ける

### 2. 結果の統合
- メインエージェントが結果を統合・分析
- 矛盾する結果の調整

### 3. エラーハンドリング
- タイムアウトの設定
- フォールバック戦略

## 今後の展望

### /agentsコマンドの可能性
- カスタムエージェントの永続化
- 特定ドメインに特化したエージェントテンプレート
- エージェント間の直接通信

### 統合アイデア
1. **GitHub Actions連携**: 定期実行でサブエージェントを起動
2. **Discord通知**: サブエージェントの結果をDiscordに送信
3. **自動レポート生成**: 複数エージェントの結果を統合したレポート

## 実験的な使用法

### Vive Paradigmでの活用
```python
# 知らない技術を学ぶ際に複数の視点から同時学習
technologies = ["Rust", "WebAssembly", "GraphQL", "Kubernetes"]

for tech in technologies:
    Task(
        description=f"{tech}のVive Learning",
        prompt=f"""
        {tech}について：
        1. 簡単なHello Worldを作成
        2. 主要な概念を3つ説明
        3. 実用的な使用例を1つ実装
        4. 他の技術との比較
        """,
        subagent_type="general-purpose"
    )
```

この方法により、4つの技術を同時に「体験しながら学ぶ」ことが可能になります。