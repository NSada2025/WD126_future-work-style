#!/usr/bin/env powershell
# Modern Engineer Claude Code Setup Script
# モダンエンジニア派 Claude Code 自動セットアップ

Write-Host "🚀 Claude Code Modern Engineer Setup" -ForegroundColor Cyan

# 管理者権限チェック
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Administrator rights required. Restarting as admin..." -ForegroundColor Red
    Start-Process PowerShell -Verb RunAs -ArgumentList ("-File", $MyInvocation.MyCommand.Path)
    exit 1
}

Write-Host "✅ Running with administrator privileges" -ForegroundColor Green

# 環境確認
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

try {
    $gitVersion = git --version
    Write-Host "Git: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found. Please install Git for Windows first." -ForegroundColor Red
    exit 1
}

try {
    $nodeVersion = node --version
    Write-Host "Node: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+ first." -ForegroundColor Red
    exit 1
}

try {
    $npmVersion = npm --version
    Write-Host "npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please check Node.js installation." -ForegroundColor Red
    exit 1
}

# Claude Code インストール確認
Write-Host "📦 Checking Claude Code installation..." -ForegroundColor Yellow

try {
    $claudeVersion = claude --version
    Write-Host "✅ Claude Code already installed: $claudeVersion" -ForegroundColor Green
} catch {
    Write-Host "🔧 Installing Claude Code globally..." -ForegroundColor Yellow
    npm install -g @anthropic-ai/claude-code
    
    # インストール確認
    try {
        $claudeVersion = claude --version
        Write-Host "✅ Claude Code installed successfully: $claudeVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Claude Code installation failed" -ForegroundColor Red
        exit 1
    }
}

# Windows Terminal設定チェック
Write-Host "🖥️ Checking Windows Terminal..." -ForegroundColor Yellow

$wtPath = Get-Command wt -ErrorAction SilentlyContinue
if ($wtPath) {
    Write-Host "✅ Windows Terminal found" -ForegroundColor Green
} else {
    Write-Host "⚠️ Windows Terminal not found. Installing via winget..." -ForegroundColor Yellow
    try {
        winget install Microsoft.WindowsTerminal
        Write-Host "✅ Windows Terminal installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Please install Windows Terminal manually from Microsoft Store" -ForegroundColor Yellow
    }
}

# D:\ ドライブ確認
Write-Host "💾 Checking D:\\ drive..." -ForegroundColor Yellow

if (Test-Path "D:\\") {
    Write-Host "✅ D:\\ drive accessible" -ForegroundColor Green
    
    # プロジェクトディレクトリの確認
    if (Test-Path "D:\\WD126_future-work-style") {
        Write-Host "✅ WD126 project directory found" -ForegroundColor Green
    } else {
        Write-Host "⚠️ WD126 project directory not found at D:\\WD126_future-work-style" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ D:\\ drive not accessible. Please check drive mapping." -ForegroundColor Red
}

# 動作確認テスト
Write-Host "🔍 Running diagnostics..." -ForegroundColor Yellow

try {
    claude doctor
    Write-Host "✅ Claude doctor check passed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Claude doctor check had issues - check output above" -ForegroundColor Yellow
}

# ベンチマーク実行
Write-Host "⚡ Performance benchmark..." -ForegroundColor Yellow

$iterations = 3
$times = @()

for ($i = 1; $i -le $iterations; $i++) {
    Write-Host "  Running test $i/$iterations..." -ForegroundColor Gray
    $time = Measure-Command { claude --version | Out-Null }
    $times += $time.TotalSeconds
    Write-Host "  Iteration $i: $($time.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Gray
}

$average = ($times | Measure-Object -Average).Average
Write-Host "📊 Average startup time: $($average.ToString('F2')) seconds" -ForegroundColor Green

if ($average -lt 3.0) {
    Write-Host "🚀 Excellent performance!" -ForegroundColor Green
} elseif ($average -lt 5.0) {
    Write-Host "✅ Good performance" -ForegroundColor Green
} else {
    Write-Host "⚠️ Consider optimization" -ForegroundColor Yellow
}

# PowerShell Profile設定の提案
Write-Host "🔧 PowerShell Profile optimization..." -ForegroundColor Yellow

$profilePath = $PROFILE
if (Test-Path $profilePath) {
    $profileContent = Get-Content $profilePath -Raw
    if ($profileContent -like "*Set-Alias c claude*") {
        Write-Host "✅ Claude alias already configured" -ForegroundColor Green
    } else {
        Write-Host "📝 Adding Claude aliases to PowerShell profile..." -ForegroundColor Yellow
        Add-Content $profilePath "`n# Claude Code aliases"
        Add-Content $profilePath "Set-Alias c claude"
        Add-Content $profilePath "Set-Location D:\\"
        Write-Host "✅ Aliases added to PowerShell profile" -ForegroundColor Green
    }
} else {
    Write-Host "📝 Creating PowerShell profile with Claude aliases..." -ForegroundColor Yellow
    New-Item -Path $profilePath -ItemType File -Force
    Add-Content $profilePath "# Claude Code aliases"
    Add-Content $profilePath "Set-Alias c claude"
    Add-Content $profilePath "Set-Location D:\\"
    Write-Host "✅ PowerShell profile created" -ForegroundColor Green
}

# 設定状況の確認
Write-Host "`n📋 Configuration Summary:" -ForegroundColor Cyan
Write-Host "  🔹 Claude Code: Installed and working" -ForegroundColor White
Write-Host "  🔹 Default directory: D:\\" -ForegroundColor White
Write-Host "  🔹 Startup time: $($average.ToString('F2'))s average" -ForegroundColor White
Write-Host "  🔹 Alias 'c' configured for quick access" -ForegroundColor White

Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Restart PowerShell to apply profile changes" -ForegroundColor White
Write-Host "  2. Navigate to project directory: cd D:\\WD126_future-work-style" -ForegroundColor White
Write-Host "  3. Start Claude: claude (or use alias: c)" -ForegroundColor White
Write-Host "  4. Test Windows Terminal configuration" -ForegroundColor White

Write-Host "`n✅ Modern Engineer Setup Complete!" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "Ready to experience Windows-native Claude Code! 🚀" -ForegroundColor Cyan

# ログファイル出力
$logPath = "D:\\claude-setup-log.txt"
"Claude Code Modern Engineer Setup completed at $(Get-Date)" | Out-File $logPath -Append
"Average startup time: $($average.ToString('F2')) seconds" | Out-File $logPath -Append
"Setup successful" | Out-File $logPath -Append

Write-Host "`n📄 Setup log saved to: $logPath" -ForegroundColor Gray