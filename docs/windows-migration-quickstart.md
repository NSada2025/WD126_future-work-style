# Windows移行 クイックスタートガイド

## 現在の環境（確認済み）
✅ VS Code Windows版インストール済み
✅ WSL環境でClaude Code稼働中

## Step 1: 現在の環境診断（5分）

### PowerShellで確認
```powershell
# PowerShellを管理者権限で開いて実行
git --version
node --version
npm --version

# Git Bashのパス確認
where git
```

期待される出力例：
```
git version 2.xx.x
v18.xx.x（またはそれ以上）
```

## Step 2: Claude Code Windows版のテストインストール（5分）

### グローバルインストール
```powershell
# 既存のWSL版と競合しないようにテスト
npm install -g @anthropic-ai/claude-code

# インストール確認
claude --version
claude doctor
```

## Step 3: テストディレクトリでの動作確認（5分）

### 小規模テスト
```powershell
# テスト用ディレクトリ作成
mkdir D:\claude-test
cd D:\claude-test

# Claude起動テスト
claude

# 簡単なタスクで動作確認
echo "# Test Project" > README.md
```

### 確認すべき点
- 起動速度（WSLより速いか）
- ファイルアクセス（D:\直接アクセスできるか）
- VS Codeとの連携（必要に応じて）

## Step 4: 既存プロジェクトでのパフォーマンステスト（10分）

### WD132をWindows環境で開く
```powershell
# プロジェクトディレクトリへ移動
cd D:\WD132_project-vitality-system

# Claude起動
claude

# 簡単なタスクで比較
> このプロジェクトの健康状態を確認して
```

### 比較項目
1. **起動時間** - WSL vs Windows
2. **ファイル読み込み速度** - 体感的な差
3. **メモリ使用量** - タスクマネージャーで確認

## Step 5: 問題がなければ段階的移行開始

### 移行順序（推奨）
1. **WD132** - プロジェクト管理系（テスト最適）
2. **WD126** - メインプロジェクト（慣れてから）
3. **その他WDプロジェクト群** - 段階的に

## VS Code統合の活用

### Claude + VS Code Windowsの連携
```powershell
# VS CodeでプロジェクトFolder開く
code D:\WD132_project-vitality-system

# 同じディレクトリでClaude起動
cd D:\WD132_project-vitality-system
claude
```

### 利点
- ファイル編集とAI支援の同時作業
- Windowsネイティブなファイル監視
- 統合ターミナルでの作業

## トラブルシューティング

### よくある問題と対策

#### 問題1: "claude: command not found"
```powershell
# パスの確認
$env:PATH -split ';' | Select-String npm

# npm global binのパス追加が必要な場合
npm config get prefix
```

#### 問題2: 権限エラー
```powershell
# PowerShell実行ポリシー確認
Get-ExecutionPolicy

# 必要に応じて変更
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 問題3: パフォーマンスが期待より悪い
- Windows Defenderの除外設定
- npm cacheのクリア: `npm cache clean --force`

## 成功の判定基準

### 移行成功のサイン
✅ 起動時間がWSLより短い（目標：5秒以内）
✅ D:\パスで直接アクセス可能
✅ ファイル操作が体感的に高速
✅ VS Codeとの連携がスムーズ

### 移行継続の判断
- 日常作業での使いやすさ
- エラー頻度の低さ
- 全体的な作業効率の向上

## 次のステップ予告

移行テストが成功したら：
1. tmux代替としてWindows Terminal設定
2. PowerShell版マルチエージェントスクリプト作成
3. 全プロジェクトの段階的移行

## 今すぐ開始！

まずはStep 1の環境診断から開始してください。
所要時間：約20分で基本的な移行可能性が判定できます。