"""
Windows通知模块 - 发送系统通知和声音提示

兼容性:
  - 普通命令行运行: 使用 PowerShell Toast 通知 + MessageBox 兜底
  - Task Scheduler (SYSTEM): 使用 msg * 命令弹窗到当前登录用户桌面
"""

import winsound
import ctypes
import subprocess
import os


def send_notification(title, message):
    """
    发送Windows通知（自动适配运行环境）

    Args:
        title: 通知标题
        message: 通知内容
    """
    try:
        playsound()
    except Exception:
        pass

    # 判断是否在 SYSTEM 环境（Task Scheduler）
    is_system = _is_system_context()

    if is_system:
        _notify_via_msg(title, message)
    else:
        _notify_via_toast(title, message)


def _is_system_context():
    """判断当前进程是否以 SYSTEM 用户运行"""
    try:
        import ctypes
        # GetUserName 返回当前用户名
        buf = ctypes.create_unicode_buffer(256)
        size = ctypes.c_uint32(256)
        ctypes.windll.advapi32.GetUserNameW(buf, ctypes.byref(size))
        return buf.value == "SYSTEM"
    except Exception:
        return False


def _notify_via_msg(title, message):
    """
    通过 msg * 命令弹窗（适用于 SYSTEM 环境）。
    在系统托盘中向当前登录用户发送桌面弹窗。
    """
    try:
        # msg * 会向所有活动会话发送消息对话框
        full_msg = f"{title}\n{message}"
        subprocess.run(
            ["msg", "*", "/TIME:60", full_msg],
            capture_output=True, timeout=10
        )
        print(f"通知已发送到桌面: {title}")
    except FileNotFoundError:
        # msg.exe 可能在某些精简版系统上不存在
        print("msg.exe 不可用，跳过桌面通知")
    except Exception as e:
        print(f"msg 通知失败: {e}")


def _notify_via_toast(title, message):
    """
    通过 Windows Toast 通知（适用于普通用户环境）。
    优先使用 PowerShell Toast API，失败时回退到 MessageBox。
    """
    try:
        _show_powershell_toast(title, message)
    except Exception as e:
        print(f"PowerShell Toast 通知失败: {e}")
        try:
            _show_messagebox(title, message)
        except Exception as e2:
            print(f"MessageBox 也失败: {e2}")


def _show_powershell_toast(title, message):
    """
    使用 PowerShell 的 Windows.UI.Notifications API 显示 Toast 通知。
    """
    ps_command = f'''
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $template = @"
    <toast>
        <visual>
            <binding template="ToastGeneric">
                <text>{title}</text>
                <text>{message}</text>
            </binding>
        </visual>
        <audio src="ms-winsound-event:Notification.Default"/>
    </toast>
"@

    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)

    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Buff Price Tracker").Show($toast)
    '''

    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_command],
        capture_output=True, text=True, timeout=10
    )


def _show_messagebox(title, message):
    """
    使用 Win32 MessageBox 显示弹窗。
    MB_ICONINFORMATION | MB_SYSTEMMODAL — 即使在其他窗口之上也能显示。
    """
    ctypes.windll.user32.MessageBoxW(
        0,
        message,
        title,
        0x40 | 0x1000  # MB_ICONINFORMATION | MB_SYSTEMMODAL
    )


def playsound():
    """
    播放系统提示音
    """
    winsound.MessageBeep(winsound.MB_ICONASTERISK)


if __name__ == "__main__":
    send_notification("Buff价格追踪测试",
                       "数据采集完成！\n"
                       "不带计数器的刀: 20 个\n"
                       "带计数器的刀: 20 个\n"
                       "数据已保存到 output/knife_prices.xlsx")
