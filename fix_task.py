"""
修复定时任务配置：
1. 将执行命令改为 run.bat（带日志输出）
2. 启用"错过计划后立即运行"（StartWhenAvailable）
3. 禁用"仅在交流电时启动"等限制条件
"""

import sys
import os
import subprocess
import ctypes
import json

TASK_NAME = "BuffPriceTracker"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def fix_task():
    """以管理员身份修复定时任务"""
    ps_script = f'''
$taskName = "{TASK_NAME}"
$projectDir = "{PROJECT_DIR}"

$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if (-not $task) {{
    Write-Host "创建新任务..."
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c cd /d `"$projectDir`" && run.bat"
    $trigger = New-ScheduledTaskTrigger -Hourly -At 00:05
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "任务已创建"
}} else {{
    Write-Host ("修复现有任务...")
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c cd /d `"$projectDir`" && run.bat"
    Set-ScheduledTask -TaskName $taskName -Action $action | Out-Null

    $task.Settings.StartWhenAvailable = $true
    $task.Settings.AllowStartIfOnBatteries = $true
    $task.Settings.DisallowStartIfOnBatteries = $false
    $task.Settings.StopIfGoingOnBatteries = $false
    $task.Settings.RunOnlyIfIdle = $false
    $task.Settings.RunOnlyIfNetworkAvailable = $false
    $task.Settings.IdleSettings.StopOnIdleEnd = $false
    $task.Settings.IdleSettings.RestartOnIdle = $false
    Set-ScheduledTask -TaskName $taskName -Settings $task.Settings | Out-Null
    Write-Host "任务已修复"
}}

$t = Get-ScheduledTask -TaskName $taskName
Write-Host ("状态: " + $t.State)
Write-Host ("StartWhenAvailable: " + $t.Settings.StartWhenAvailable)
Write-Host ("允许电池运行: " + (-not $t.Settings.DisallowStartIfOnBatteries))
Write-Host ("执行命令: " + $t.Actions.Execute + " " + $t.Actions.Arguments)
'''

    ps_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'fix_task_temp.ps1')
    with open(ps_file, 'w', encoding='utf-8') as f:
        f.write(ps_script)

    try:
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', ps_file],
            capture_output=True, text=True, timeout=30
        )
        print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
    finally:
        if os.path.exists(ps_file):
            os.remove(ps_file)

    print("\n[OK] 修复完成！下次开机后定时任务会自动补跑错过的计划。")

    # 弹出消息框通知用户
    ctypes.windll.user32.MessageBoxW(
        0,
        "定时任务已修复！\n"
        "• 执行命令: run.bat（带日志输出）\n"
        "• 关机后重启: 错过的计划会自动补跑\n"
        "• 可在 logs/ 目录查看运行日志",
        "BuffPriceTracker 修复成功",
        0x40 | 0x1000
    )


if __name__ == "__main__":
    if not is_admin():
        # 提权运行
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{__file__}" --elevated', None, 1
        )
    else:
        fix_task()
