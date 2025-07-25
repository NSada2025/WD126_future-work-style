# 🚀 モダンエンジニア派 Claude Code セットアップ

## 採用構成
```
✅ npm グローバルインストール
✅ Windows Terminal
✅ PowerShell
✅ D:\直下構造維持
✅ VS Code中程度統合
```

## Phase 1: 基盤環境構築（10分）

### Step 1.1: Windows Terminal インストール
```powershell
# Microsoft Store から Windows Terminal インストール
# または winget 使用
winget install Microsoft.WindowsTerminal
```

### Step 1.2: Claude Code グローバルインストール
```powershell
# 管理者権限 PowerShell で実行
npm install -g @anthropic-ai/claude-code

# インストール確認
claude --version
claude doctor
```

### Step 1.3: パフォーマンステスト（エンジニア必須）
```powershell
# ベンチマーク実行
Measure-Command { claude --version }

# 詳細診断
claude doctor --verbose
```

## Phase 2: Windows Terminal カスタマイズ（15分）

### Step 2.1: settings.json 設定
Windows Terminal → Settings → Open JSON file

```json
{
  "defaultProfile": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
  "profiles": {
    "defaults": {
      "fontFace": "Cascadia Code",
      "fontSize": 12,
      "startingDirectory": "D:\\"
    },
    "list": [
      {
        "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
        "name": "PowerShell",
        "commandline": "powershell.exe",
        "startingDirectory": "D:\\",
        "colorScheme": "Campbell"
      },
      {
        "guid": "{claude-president}",
        "name": "Claude President",
        "commandline": "powershell.exe",
        "startingDirectory": "D:\\WD126_future-work-style",
        "tabTitle": "President",
        "colorScheme": "One Half Dark"
      },
      {
        "guid": "{claude-multiagent}",
        "name": "MultiAgent Hub",
        "commandline": "powershell.exe",
        "startingDirectory": "D:\\",
        "tabTitle": "MultiAgent",
        "colorScheme": "Tango Dark"
      }
    ]
  },
  "schemes": [
    {
      "name": "Claude Theme",
      "foreground": "#CCCCCC",
      "background": "#1E1E1E",
      "cursorColor": "#FFFFFF"
    }
  ],
  "keybindings": [
    {
      "command": "newTab",
      "keys": "ctrl+t"
    },
    {
      "command": "splitPane",
      "keys": "ctrl+shift+d"
    }
  ]
}
```

### Step 2.2: マルチエージェント用レイアウト
```powershell
# 4ペイン構成でtmux代替
# Ctrl+Shift+D で分割
# President | Boss1
# Worker1   | Worker2
```

## Phase 3: パフォーマンス最適化（エンジニア的）

### Step 3.1: ベンチマークスクリプト作成
```powershell
# D:\scripts\claude-benchmark.ps1
$iterations = 10
$times = @()

for ($i = 1; $i -le $iterations; $i++) {
    $time = Measure-Command { claude --version }
    $times += $time.TotalSeconds
    Write-Host "Iteration $i: $($time.TotalSeconds) seconds"
}

$average = ($times | Measure-Object -Average).Average
Write-Host "Average startup time: $average seconds"
```

### Step 3.2: 環境変数最適化
```powershell
# PowerShell Profile 設定
notepad $PROFILE

# 以下を追加
Set-Alias c claude
Set-Location D:\
function Quick-Claude { claude --help }
Set-Alias qc Quick-Claude
```

## Phase 4: VS Code統合（中程度）

### Step 4.1: VS Code設定
```json
// .vscode/settings.json (global)
{
  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "terminal.integrated.profiles.windows": {
    "PowerShell": {
      "source": "PowerShell",
      "args": ["-NoLogo", "-WorkingDirectory", "D:\\"]
    }
  },
  "terminal.integrated.cwd": "${workspaceFolder}",
  "files.watcherExclude": {
    "**/node_modules/**": true
  }
}
```

### Step 4.2: プロジェクト別ワークスペース
```json
// WD126.code-workspace
{
  "folders": [
    {
      "name": "WD126 Main",
      "path": "D:\\WD126_future-work-style"
    }
  ],
  "settings": {
    "terminal.integrated.cwd": "D:\\WD126_future-work-style"
  }
}
```

## Phase 5: 比較検証（エンジニア魂）

### Step 5.1: WSL vs Windows パフォーマンス比較
```powershell
# Windows環境でのテスト
cd D:\WD126_future-work-style
Measure-Command {
  claude
  # 簡単なタスクを実行
  exit
}
```

```bash
# WSL環境での同じテスト（比較用）
cd /mnt/d/WD126_future-work-style
time claude
```

### Step 5.2: メモリ使用量モニタリング
```powershell
# プロセス監視
Get-Process | Where-Object {$_.ProcessName -like "*node*" -or $_.ProcessName -like "*claude*"}
```

## Phase 6: 自動セットアップスクリプト（配布用）

### setup-claude-modern.ps1
```powershell
#!/usr/bin/env powershell
# Modern Engineer Claude Code Setup Script

Write-Host "🚀 Claude Code Modern Engineer Setup" -ForegroundColor Cyan

# 管理者権限チェック
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Administrator rights required" -ForegroundColor Red
    exit 1
}

# 環境確認
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
$gitVersion = git --version
$nodeVersion = node --version
Write-Host "Git: $gitVersion" -ForegroundColor Green
Write-Host "Node: $nodeVersion" -ForegroundColor Green

# Claude Code インストール
Write-Host "📦 Installing Claude Code globally..." -ForegroundColor Yellow
npm install -g @anthropic-ai/claude-code

# 動作確認
Write-Host "🔍 Running diagnostics..." -ForegroundColor Yellow
claude doctor

# ベンチマーク実行
Write-Host "⚡ Performance benchmark..." -ForegroundColor Yellow
$time = Measure-Command { claude --version }
Write-Host "Startup time: $($time.TotalSeconds) seconds" -ForegroundColor Green

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "Next: Configure Windows Terminal settings" -ForegroundColor Cyan
```

## 使用開始

### 今すぐテスト
1. Windows Terminal 起動
2. PowerShell タブを開く
3. `cd D:\WD126_future-work-style`
4. `claude`

### 期待される体験
- ⚡ 3-5秒で起動
- 🎯 D:\直接アクセス
- 🔧 VS Codeとシームレス連携
- 📊 定量的パフォーマンス把握

### エンジニアとしての次の楽しみ
- Windows Terminal のカスタマイズ探求
- PowerShell スクリプト作成
- パフォーマンス最適化
- 他の開発者への共有・布教

**準備完了！** モダンエンジニア構成でClaude Codeライフを始めましょう🚀