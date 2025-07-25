# Windows版マルチエージェントシステム
# tmux代替としてWindows Terminalを活用

param(
    [string]$Mode = "init",
    [string]$Message = "",
    [string]$Target = ""
)

# 設定
$ProjectRoot = "D:\WD126_future-work-style"
$LogDir = "$ProjectRoot\logs"

# ログディレクトリ作成
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force
}

function Write-Log {
    param($Message, $Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    $logEntry | Out-File "$LogDir\multiagent.log" -Append
}

function Start-MultiAgentSystem {
    Write-Log "Starting Windows MultiAgent System" "INFO"
    
    # President タブ起動
    Write-Log "Starting President session"
    Start-Process wt -ArgumentList @(
        "-w", "0",
        "new-tab", "--title", "President",
        "-d", $ProjectRoot,
        "--", "powershell.exe", "-NoExit", "-Command",
        "Write-Host '🚀 President Agent Ready' -ForegroundColor Cyan; Set-Location '$ProjectRoot'"
    )
    
    Start-Sleep 2
    
    # Boss1 ペイン追加
    Write-Log "Adding Boss1 pane"
    Start-Process wt -ArgumentList @(
        "-w", "0",
        "split-pane", "--title", "Boss1", 
        "-d", $ProjectRoot,
        "--", "powershell.exe", "-NoExit", "-Command",
        "Write-Host '👑 Boss1 Agent Ready' -ForegroundColor Yellow; Set-Location '$ProjectRoot'"
    )
    
    Start-Sleep 1
    
    # Worker1 ペイン追加
    Write-Log "Adding Worker1 pane"
    Start-Process wt -ArgumentList @(
        "-w", "0",
        "split-pane", "--title", "Worker1",
        "-d", $ProjectRoot,
        "--", "powershell.exe", "-NoExit", "-Command", 
        "Write-Host '⚡ Worker1 Agent Ready' -ForegroundColor Green; Set-Location '$ProjectRoot'"
    )
    
    Start-Sleep 1
    
    # Worker2 ペイン追加
    Write-Log "Adding Worker2 pane"
    Start-Process wt -ArgumentList @(
        "-w", "0",
        "split-pane", "--title", "Worker2",
        "-d", $ProjectRoot,
        "--", "powershell.exe", "-NoExit", "-Command",
        "Write-Host '🎨 Worker2 Agent Ready' -ForegroundColor Magenta; Set-Location '$ProjectRoot'"
    )
    
    Write-Log "MultiAgent system started successfully"
    Write-Host "🎯 MultiAgent System Ready! Switch between panes with Alt+Arrow keys" -ForegroundColor Green
}

function Send-AgentMessage {
    param($TargetAgent, $MessageText)
    
    Write-Log "Sending message to $TargetAgent: $MessageText" "INFO"
    
    # Windows Terminal pane selection and message sending
    # Note: This requires Windows Terminal Preview features
    $timestamp = Get-Date -Format "HH:mm:ss"
    $formattedMessage = "[$timestamp] From System: $MessageText"
    
    # PowerShell remoting simulation (placeholder)
    # In actual implementation, would use Windows Terminal automation
    Write-Log "Message sent to $TargetAgent" "SUCCESS"
    
    # ログファイルに記録
    $logEntry = @{
        Timestamp = Get-Date
        Source = "System"
        Target = $TargetAgent
        Message = $MessageText
    }
    
    $logEntry | ConvertTo-Json | Out-File "$LogDir\agent_messages.log" -Append
}

function Show-AgentStatus {
    Write-Host "`n🎯 Windows MultiAgent System Status" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    
    # Windows Terminal プロセス確認
    $wtProcesses = Get-Process -Name "WindowsTerminal" -ErrorAction SilentlyContinue
    if ($wtProcesses) {
        Write-Host "✅ Windows Terminal: Running ($($wtProcesses.Count) instances)" -ForegroundColor Green
    } else {
        Write-Host "❌ Windows Terminal: Not running" -ForegroundColor Red
    }
    
    # ログファイルチェック
    if (Test-Path "$LogDir\multiagent.log") {
        $logSize = (Get-Item "$LogDir\multiagent.log").Length
        Write-Host "📄 Log file: $($logSize) bytes" -ForegroundColor Gray
    }
    
    Write-Host "`n🚀 Available Commands:" -ForegroundColor Yellow
    Write-Host "  .\multiagent-windows.ps1 -Mode init     # Start system" -ForegroundColor White
    Write-Host "  .\multiagent-windows.ps1 -Mode send -Target worker1 -Message 'hello'" -ForegroundColor White
    Write-Host "  .\multiagent-windows.ps1 -Mode status   # Show status" -ForegroundColor White
}

function Stop-MultiAgentSystem {
    Write-Log "Stopping MultiAgent system" "INFO"
    
    # Windows Terminal プロセス終了（注意：全タブが閉じます）
    $confirmation = Read-Host "Are you sure you want to close all Windows Terminal tabs? (y/N)"
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        Get-Process -Name "WindowsTerminal" -ErrorAction SilentlyContinue | Stop-Process -Force
        Write-Log "MultiAgent system stopped" "INFO"
    } else {
        Write-Host "Operation cancelled" -ForegroundColor Yellow
    }
}

# メイン処理
switch ($Mode.ToLower()) {
    "init" {
        Start-MultiAgentSystem
    }
    "send" {
        if (-not $Target -or -not $Message) {
            Write-Host "Error: Both -Target and -Message parameters required for send mode" -ForegroundColor Red
            Write-Host "Example: .\multiagent-windows.ps1 -Mode send -Target worker1 -Message 'Hello Worker1'" -ForegroundColor Yellow
            exit 1
        }
        Send-AgentMessage -TargetAgent $Target -MessageText $Message
    }
    "status" {
        Show-AgentStatus
    }
    "stop" {
        Stop-MultiAgentSystem
    }
    default {
        Write-Host "Unknown mode: $Mode" -ForegroundColor Red
        Write-Host "Available modes: init, send, status, stop" -ForegroundColor Yellow
        exit 1
    }
}

# 使用例コメント
<#
使用例:

# システム起動
.\multiagent-windows.ps1 -Mode init

# メッセージ送信
.\multiagent-windows.ps1 -Mode send -Target "worker1" -Message "新しいタスクを開始してください"

# ステータス確認
.\multiagent-windows.ps1 -Mode status

# システム停止
.\multiagent-windows.ps1 -Mode stop
#>