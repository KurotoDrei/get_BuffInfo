@echo off
REM Buff刀饰品价格追踪工具 - 自动运行脚本
REM 此脚本用于Windows任务计划程序自动运行（每小时）

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 创建日志目录
if not exist "logs" mkdir logs

REM 获取当前时间用于日志文件名
set LOGFILE=logs\run_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOGFILE=%LOGFILE: =0%

REM 记录开始时间
echo ======================================== >> "%LOGFILE%"
echo Buff刀饰品价格追踪 - 自动运行 >> "%LOGFILE%"
echo 开始时间: %date% %time% >> "%LOGFILE%"
echo ======================================== >> "%LOGFILE%"

REM 运行Python脚本（输出同时显示在控制台和日志文件）
python main.py >> "%LOGFILE%" 2>&1

REM 检查运行结果
if %errorlevel% equ 0 (
    echo >> "%LOGFILE%"
    echo 运行成功 >> "%LOGFILE%"
) else (
    echo >> "%LOGFILE%"
    echo 运行失败，错误代码: %errorlevel% >> "%LOGFILE%"
)

echo 完成时间: %date% %time% >> "%LOGFILE%"
echo ======================================== >> "%LOGFILE%"

REM 删除30天前的旧日志
forfiles /p "%~dp0logs" /s /m *.log /d -30 /c "cmd /c del @path" 2>nul

exit /b %errorlevel%
