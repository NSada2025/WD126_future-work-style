# Windows移行 クイックスタート

## 即座実行（5分セットアップ）

### Step 1: 自動セットアップ実行
```powershell
# PowerShellを管理者権限で起動
# D:\WD126_future-work-style フォルダで実行
.\setup-claude-modern.ps1
```

### Step 2: Windows Terminal設定適用
```powershell
# 設定ファイルをコピー（Windows Terminalが閉じた状態で）
copy .\windows-terminal-settings.json "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
```

### Step 3: 動作確認
```powershell
# Windows Terminal再起動後
wt -p "Claude President"
# または
wt -p "MultiAgent Hub"
```

## 5分後の体験

### ✅ 期待される結果
- PowerShellで `c` → Claude Code起動
- D:\直接アクセス（/mnt/d 不要）
- 起動時間 < 5秒
- Windows Terminal 4ペイン構成

### 🎯 新しいワークフロー例
```powershell
# 従来（WSL）
wsl
cd /mnt/d/WD126_future-work-style  
claude

# 新方式（Windows）
wt -p "Claude President"  # 自動でD:\WD126_future-work-styleに移動
c                         # aliasで claude 起動
```

## トラブルシューティング

### 問題: セットアップスクリプトが実行できない
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 問題: Windows Terminal設定が反映されない
1. Windows Terminalを完全終了
2. タスクマネージャーでプロセス確認
3. 設定ファイル再コピー

### 問題: Claude起動が遅い
```powershell
# npm cache クリア
npm cache clean --force

# Windows Defender除外設定追加
# D:\フォルダ を除外対象に追加
```

## 次のステップ

移行テストが成功したら：
1. マルチエージェントシステムのWindows対応
2. 全WDプロジェクトの段階的移行
3. Windows専用機能の活用

**所要時間**: 5分でテスト → 1時間で本格移行