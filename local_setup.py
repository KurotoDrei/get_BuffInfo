"""
本地自动化配置工具 - 图形界面

功能:
1. 设置 BUFF_COOKIE 到 .env 文件
2. 创建 Windows 任务计划程序（每小时自动运行）
3. 立即测试运行
4. 查看运行日志
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import os
import sys
import threading
from pathlib import Path
from datetime import datetime


PROJECT_DIR = Path(__file__).parent.resolve()
ENV_FILE = PROJECT_DIR / ".env"
TASK_NAME = "BuffPriceTracker"
PYTHON_EXE = sys.executable or "python"
MAIN_SCRIPT = PROJECT_DIR / "main.py"


class LocalSetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Buff 刀饰品价格追踪 - 本地配置工具")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        self.root.resizable(True, True)

        # 尝试设置图标
        try:
            self.root.iconbitmap(default=PROJECT_DIR / "icon.ico")
        except Exception:
            pass

        style = ttk.Style()
        style.theme_use("vista")

        main_frame = ttk.Frame(root, padding=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === 标题 ===
        title = ttk.Label(main_frame, text="Buff 刀饰品价格追踪", font=("微软雅黑", 16, "bold"))
        title.pack(pady=(0, 4))

        subtitle = ttk.Label(main_frame, text="本地每小时自动运行配置工具", font=("微软雅黑", 10))
        subtitle.pack(pady=(0, 16))

        # === 状态卡片 ===
        status_frame = ttk.LabelFrame(main_frame, text="当前状态", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 12))

        self.status_env = ttk.Label(status_frame, text="❌ .env 文件: 未配置")
        self.status_env.pack(anchor=tk.W, pady=2)

        self.status_task = ttk.Label(status_frame, text="❌ 定时任务: 未配置")
        self.status_task.pack(anchor=tk.W, pady=2)

        ttk.Button(status_frame, text="刷新状态", command=self.refresh_status).pack(anchor=tk.W, pady=(6, 0))

        # === Cookie 设置 ===
        cookie_frame = ttk.LabelFrame(main_frame, text="① Cookie 设置", padding=10)
        cookie_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(cookie_frame, text="将你的 Buff Cookie 粘贴到下面：").pack(anchor=tk.W)
        
        cookie_entry_frame = ttk.Frame(cookie_frame)
        cookie_entry_frame.pack(fill=tk.X, pady=(6, 0))
        
        self.cookie_var = tk.StringVar()
        self.cookie_entry = ttk.Entry(cookie_entry_frame, textvariable=self.cookie_var, font=("Consolas", 10))
        self.cookie_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(cookie_entry_frame, text="获取指南", command=self.show_cookie_guide).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(cookie_entry_frame, text="保存 Cookie", command=self.save_cookie).pack(side=tk.RIGHT, padx=(6, 0))

        ttk.Label(cookie_frame, text="提示: 在浏览器登录 buff.163.com → F12 → Network → 复制 Cookie 字段", font=("", 9), foreground="gray").pack(anchor=tk.W, pady=(4, 0))

        # === 定时任务 ===
        task_frame = ttk.LabelFrame(main_frame, text="② 定时任务配置", padding=10)
        task_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(task_frame, text="配置 Windows 任务计划程序，每小时自动运行一次：").pack(anchor=tk.W)

        btn_frame = ttk.Frame(task_frame)
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Button(btn_frame, text="创建定时任务", command=self.create_task).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="删除定时任务", command=self.delete_task).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(task_frame, text="任务名称: BuffPriceTracker  |  触发: 每小时重复  |  系统托盘静默运行", font=("", 9), foreground="gray").pack(anchor=tk.W, pady=(4, 0))

        # === 操作按钮 ===
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Button(action_frame, text="▶ 立即测试运行", command=self.test_run).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_frame, text="📂 打开输出目录", command=self.open_output).pack(side=tk.LEFT, padx=(0, 8))

        # === 日志 ===
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding=6)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, font=("Consolas", 9), bg="#1e1e2f", fg="#cdd6f4", wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 初始状态刷新
        self.refresh_status()
        self.log("启动配置工具 v1.0")
        self.log(f"项目目录: {PROJECT_DIR}")
        self.log(f"Python: {PYTHON_EXE}")
        self.log("")

    # ==================== Methods ====================

    def log(self, msg):
        """追加日志"""
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def log_run(self, msg):
        """带时间戳的日志"""
        ts = datetime.now().strftime("%H:%M:%S")
        self.log(f"[{ts}] {msg}")

    def refresh_status(self):
        """刷新状态显示"""
        # .env 状态
        if ENV_FILE.exists():
            content = ENV_FILE.read_text(encoding="utf-8")
            if "BUFF_COOKIE" in content and "session" in content:
                self.status_env.config(text="✅ .env 文件: 已配置 Cookie")
            else:
                self.status_env.config(text="⚠️ .env 文件: 存在但 Cookie 不完整")
        else:
            self.status_env.config(text="❌ .env 文件: 未配置")

        # 预填 Cookie（如果已有）
        if ENV_FILE.exists():
            for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
                if line.startswith("BUFF_COOKIE="):
                    val = line.split("=", 1)[1].strip().strip("\"'")
                    if val:
                        self.cookie_var.set(val[:60] + "..." if len(val) > 60 else val)
                    break

        # 任务计划程序状态
        try:
            result = subprocess.run(
                ["schtasks", "/query", "/tn", TASK_NAME, "/fo", "LIST", "/v"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                status = "已启用" if "Ready" in result.stdout or "Running" in result.stdout else "存在"
                schedule_info = ""
                for line in result.stdout.splitlines():
                    if "Schedule" in line or "触发" in line:
                        schedule_info = f"  |  {line.split(':')[-1].strip()}"
                        break
                self.status_task.config(text=f"✅ 定时任务: {status}{schedule_info}")
            else:
                self.status_task.config(text="❌ 定时任务: 未配置")
        except Exception:
            self.status_task.config(text="❌ 定时任务: 无法查询（请以管理员身份运行）")

    def show_cookie_guide(self):
        """显示 Cookie 获取指南"""
        guide = (
            "如何获取 Buff Cookie：\n\n"
            "1. 打开浏览器，访问 https://buff.163.com/\n"
            "2. 登录你的 Steam 账号\n"
            "3. 按 F12 打开开发者工具\n"
            "4. 切换到 Network（网络）选项卡\n"
            "5. 刷新页面（F5）\n"
            "6. 点击任意 buff.163.com 的请求\n"
            "7. 在 Request Headers 中找到 Cookie 字段\n"
            "8. 复制完整的 Cookie 值（以 session= 开头）\n\n"
            "提示: Cookie 很长，请完整复制。"
        )
        messagebox.showinfo("Cookie 获取指南", guide)

    def save_cookie(self):
        """保存 Cookie 到 .env 文件"""
        cookie = self.cookie_var.get().strip()
        if not cookie:
            messagebox.showerror("错误", "Cookie 不能为空！")
            return
        
        if "session" not in cookie.lower():
            if not messagebox.askyesno("警告", "Cookie 中未发现 'session' 字段，确定要保存吗？"):
                return

        try:
            ENV_FILE.write_text(f'BUFF_COOKIE="{cookie}"\n', encoding="utf-8")
            self.log_run(f"Cookie 已保存到 .env 文件（{len(cookie)} 字符）")
            self.refresh_status()
            messagebox.showinfo("成功", "Cookie 已保存到 .env 文件")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def create_task(self):
        """创建 Windows 定时任务"""
        # 检查 .env
        if not ENV_FILE.exists():
            if not messagebox.askyesno("提示", ".env 文件未配置，是否继续创建任务？（运行时会因缺少 Cookie 而失败）"):
                return

        # 检查 python-dotenv
        try:
            import dotenv
        except ImportError:
            if not messagebox.askyesno("缺少依赖", "缺少 python-dotenv 库，是否自动安装？"):
                return
            self.log_run("正在安装 python-dotenv...")
            try:
                subprocess.run([PYTHON_EXE, "-m", "pip", "install", "python-dotenv"], check=True, capture_output=True, timeout=30)
                self.log_run("python-dotenv 安装成功")
            except Exception as e:
                messagebox.showerror("错误", f"安装失败: {e}\n请手动运行: pip install python-dotenv")
                return

        self.log_run("正在创建定时任务...")
        self.log(f"  执行: {PYTHON_EXE} main.py")
        self.log(f"  工作目录: {PROJECT_DIR}")
        self.log(f"  计划: 每小时第5分钟运行")

        LocalSetupApp.run_elevated("create-task")

    def delete_task(self):
        """删除定时任务"""
        if not messagebox.askyesno("确认", f"确定要删除定时任务 '{TASK_NAME}' 吗？"):
            return

        self.log_run("正在删除定时任务...")
        LocalSetupApp.run_elevated("delete-task")

    def test_run(self):
        """立即运行一次测试"""
        self.log_run("正在运行测试...")
        self.log_run("=" * 40)
        
        # 在子线程中运行，防止界面卡死
        def run_test():
            try:
                result = subprocess.run(
                    [PYTHON_EXE, str(MAIN_SCRIPT)],
                    capture_output=True, text=True, timeout=300,  # 5分钟超时
                    cwd=str(PROJECT_DIR)
                )
                # 输出到日志
                for line in (result.stdout + result.stderr).splitlines():
                    if line.strip():
                        self.log(f"  {line}")
                
                if result.returncode == 0:
                    self.log_run("✅ 测试运行成功！")
                    messagebox.showinfo("成功", "测试运行完成！\n查看 output/ 目录获取结果。")
                else:
                    self.log_run(f"❌ 运行失败 (exit code: {result.returncode})")
                    messagebox.showerror("失败", f"运行失败，请查看日志。")
            except subprocess.TimeoutExpired:
                self.log_run("❌ 运行超时（超过5分钟）")
            except Exception as e:
                self.log_run(f"❌ 出错: {e}")

        threading.Thread(target=run_test, daemon=True).start()

    def open_output(self):
        """打开输出目录"""
        output_dir = PROJECT_DIR / "output"
        if output_dir.exists():
            os.startfile(str(output_dir))
            self.log_run(f"已打开输出目录: {output_dir}")
        else:
            messagebox.showinfo("提示", "输出目录不存在，请先运行一次程序")

    @staticmethod
    def _is_admin():
        """检查是否以管理员权限运行"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    @staticmethod
    def run_elevated(action):
        """以管理员身份执行指定操作"""
        import ctypes
        import time

        if not LocalSetupApp._is_admin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{__file__}" --elevated {action}', None, 1
            )
            return

        # 已提权，执行操作
        project_dir = Path(__file__).parent.resolve()
        python_exe = sys.executable or "python"
        task_name = "BuffPriceTracker"

        if action == "create-task":
            # 用 cmd /c cd /d + && 设置工作目录，避免 schtasks 没有 -WorkingDirectory
            full_cmd = f'cmd /c cd /d "{project_dir}" && "{python_exe}" main.py'
            result = subprocess.run(
                ["schtasks", "/create", "/tn", task_name,
                 "/tr", full_cmd,
                 "/sc", "hourly", "/st", "00:05",
                 "/du", "23:59", "/f",
                 "/rl", "highest", "/ru", "SYSTEM", "/np"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # 启用任务
                subprocess.run(
                    ["schtasks", "/change", "/tn", task_name, "/enable"],
                    capture_output=True, timeout=5
                )
                messagebox.showinfo("成功",
                    f"定时任务已创建！\n"
                    f"  命令: {full_cmd}\n"
                    f"  工作目录: {project_dir}\n"
                    f"  计划: 每小时第5分钟运行\n"
                    f"  cmd /c cd 确保运行在项目目录")
            else:
                messagebox.showerror("失败",
                    f"创建定时任务失败:\n{result.stderr or result.stdout}")

        elif action == "delete-task":
            result = subprocess.run(
                ["schtasks", "/delete", "/tn", task_name, "/f"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                messagebox.showinfo("成功", "定时任务已删除")
            else:
                messagebox.showerror("失败", f"删除失败:\n{result.stderr or result.stdout}")

        time.sleep(2)


def main():
    # 处理提权后的操作
    if len(sys.argv) > 2 and sys.argv[1] == "--elevated":
        action = sys.argv[2]
        LocalSetupApp.run_elevated(action)
        return

    root = tk.Tk()
    app = LocalSetupApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
