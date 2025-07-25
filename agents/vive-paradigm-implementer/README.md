# Vive Paradigm Implementer Agent

## 概要

**Vive Paradigm**（体験から理解へ）を実践するエージェント。10分以内にプロトタイプを作成し、体験を通じた学習を促進します。

## 核心理念

> "完璧より速度" - まず動くものを作り、体験を通じて理解を深める

## 主要機能

### 1. 10分間プロトタイプ生成
- 任意のアイデアを10分以内で動作可能な形に実装
- HTML/CSS/JavaScript, Python, 簡易APIなど多様な技術スタック対応
- 最小限の機能で最大の学習効果を実現

### 2. 体験駆動型学習ガイド
- プロトタイプ体験から学習ポイントを自動抽出
- 理論的背景の後追い説明
- 次のステップの具体的提案

### 3. 段階的改善システム
- 5分単位の小さな改善タスク
- 機能追加の優先順位付け
- 失敗からの学習促進

### 4. 視覚的理解促進
- 動作の可視化
- コンセプト図の自動生成
- インタラクティブなデモ

## ディレクトリ構造

```
vive-paradigm-implementer/
├── src/
│   ├── vive_agent.py          # メインエージェント
│   ├── prototype_generator.py  # プロトタイプ生成エンジン
│   ├── learning_guide.py      # 学習ガイド生成
│   └── template_manager.py    # テンプレート管理
├── templates/
│   ├── web_app/              # Webアプリテンプレート
│   ├── python_script/        # Pythonスクリプトテンプレート
│   ├── data_viz/            # データ可視化テンプレート
│   └── api_service/         # API作成テンプレート
├── examples/
│   ├── 10min_todo_app/      # 10分でTodoアプリ
│   ├── simple_chatbot/      # シンプルチャットボット
│   └── data_dashboard/      # データダッシュボード
├── tests/
│   └── test_prototype_speed.py
└── docs/
    ├── vive_paradigm_guide.md
    └── usage_examples.md
```

## 使用方法

### 基本的な使い方

```python
from src.vive_agent import ViveParadigmImplementer

agent = ViveParadigmImplementer()

# アイデアからプロトタイプを生成
prototype = agent.create_prototype(
    idea="タスク管理アプリ",
    time_limit=10,  # 分
    technology="web"
)

# 学習ガイドを生成
guide = agent.generate_learning_guide(prototype)

# 次のステップを提案
next_steps = agent.suggest_next_steps(prototype)
```

### Claude Code統合での使用

```bash
# Claude Codeでエージェントを呼び出し
Use the vive-paradigm-implementer agent to create a quick prototype for [your idea]
```

## 設計原則

1. **速度第一**: 完璧を求めず、まず動くものを
2. **体験重視**: 理論より実践、説明より体験
3. **段階的発展**: 小さな成功の積み重ね
4. **学習促進**: 作る過程での気づきを最大化
5. **実用性保持**: 学習目的でも実用的な価値を提供

## 成功指標

- プロトタイプ生成時間: 10分以内
- 動作成功率: 90%以上
- ユーザー学習満足度: 即座の理解と価値実感
- 改善継続率: プロトタイプの継続的発展

## バージョン情報

- **Version**: 1.0.0
- **作成日**: 2025年7月25日
- **Phase**: 1 (Week 1)
- **Status**: 実装中