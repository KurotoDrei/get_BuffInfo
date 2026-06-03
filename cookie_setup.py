"""
Cookie 设置工具 - 获取 Buff Cookie 并更新到 GitHub 仓库 secret

使用方法:
    python cookie_setup.py

功能:
    1. 显示获取 Buff Cookie 的图文步骤
    2. 输入你的 Cookie 值
    3. 自动通过 GitHub API 设置为仓库 secret
    4. 可选触发一次工作流运行
"""

import re
import sys
import webbrowser


def print_step(num, title):
    """打印步骤标题"""
    print(f"\n{'=' * 60}")
    print(f"  步骤 {num}: {title}")
    print(f"{'=' * 60}")


def get_buff_cookie_from_user():
    """交互式获取用户输入的 Buff Cookie"""
    print("\n📋 请按照以下步骤获取你的 Buff Cookie：")
    print()
    print_step(1, "打开 Buff 网站并登录")
    print("  在浏览器中打开 https://buff.163.com/")
    print("  确保你已经登录了你的 Steam 账号")
    input("  按 Enter 键继续...")

    print_step(2, "打开开发者工具")
    print("  Windows: 按 F12 打开开发者工具")
    print("  Mac: 按 Cmd+Option+I 打开开发者工具")
    webbrowser.open("https://buff.163.com/")
    input("  按 Enter 键继续...")

    print_step(3, "找到 Cookie")
    print('  切换到 Network（网络）选项卡')
    print('  刷新页面（F5）')
    print('  在请求列表中点击任意一个 buff.163.com 的请求')
    print('  在右侧找到 Request Headers 中的 Cookie 字段')
    print('  复制完整的 Cookie 值（很长的一段文本）')
    print()
    print('  💡 提示: Cookie 通常以 "session=..." 开头')
    print()

    print_step(4, "粘贴 Cookie")
    print("  请将复制好的完整 Cookie 粘贴到下面：")
    cookie = input("  Cookie > ").strip()

    if not cookie:
        print("  ❌ Cookie 不能为空！")
        return None

    # 验证 cookie 是否包含 session
    if "session" not in cookie.lower() and "Device-Id" not in cookie:
        print("  ⚠️  警告: 你的 Cookie 看起来不完整，应该包含 'session=' 字段")
        confirm = input("  仍然继续使用？(y/n): ").strip().lower()
        if confirm != 'y':
            return None

    return cookie


def get_github_token():
    """获取 GitHub Personal Access Token"""
    print()
    print("需要 GitHub Personal Access Token 来更新仓库 secret。")
    print()
    print("如何创建 Token：")
    print("  1. 打开 https://github.com/settings/tokens")
    print("  2. 点击 Generate new token → Generate new token (classic)")
    print("  3. 名称随便写，比如 'cookie_setup'")
    print("  4. 权限勾选: repo (全部) 和 workflow")
    print("  5. 点击 Generate token 并复制")
    print()
    token = input("  粘贴你的 GitHub Token > ").strip()

    if not token:
        print("  ❌ Token 不能为空！")
        return None

    # 简单验证 token 格式
    if not token.startswith("ghp_") and not token.startswith("github_pat_"):
        print("  ⚠️  Token 格式看起来不太对，应该以 'ghp_' 或 'github_pat_' 开头")
        confirm = input("  仍然继续使用？(y/n): ").strip().lower()
        if confirm != 'y':
            return None

    return token


def update_github_secret(token, repo_full_name, secret_name, secret_value):
    """通过 GitHub API 更新仓库 secret"""
    import requests
    from base64 import b64encode
    from nacl import encoding, public

    print(f"\n  🔄 正在更新 secret: {secret_name} ...")

    # 1. 获取公钥
    pubkey_url = f"https://api.github.com/repos/{repo_full_name}/actions/secrets/public-key"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        resp = requests.get(pubkey_url, headers=headers)
        resp.raise_for_status()
        pubkey_data = resp.json()
        public_key = pubkey_data["key"]
        key_id = pubkey_data["key_id"]
    except Exception as e:
        print(f"  ❌ 获取公钥失败: {e}")
        return False

    # 2. 使用 libsodium 加密 secret
    try:
        pub_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(pub_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        encrypted_value = b64encode(encrypted).decode("utf-8")
    except Exception as e:
        print(f"  ❌ 加密失败: {e}")
        print("  提示: 需要安装 pynacl 库: pip install pynacl")
        return False

    # 3. 更新 secret
    secret_url = f"https://api.github.com/repos/{repo_full_name}/actions/secrets/{secret_name}"
    payload = {"encrypted_value": encrypted_value, "key_id": key_id}

    try:
        resp = requests.put(secret_url, headers=headers, json=payload)
        resp.raise_for_status()
        print(f"  ✅ Secret '{secret_name}' 已成功更新！")
        return True
    except Exception as e:
        print(f"  ❌ 更新 secret 失败: {e}")
        if resp.status_code == 404:
            print("  可能原因: Token 没有 repo 或 workflow 权限")
        return False


def trigger_workflow(token, repo_full_name, workflow_file="hourly.yml"):
    """触发 GitHub Actions 工作流"""
    import requests

    print(f"\n  🔄 正在触发工作流: {workflow_file} ...")

    url = f"https://api.github.com/repos/{repo_full_name}/actions/workflows/{workflow_file}/dispatches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {"ref": "main"}

    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        print("  ✅ 工作流已触发！")
        print(f"  📍 查看运行: https://github.com/{repo_full_name}/actions")
        return True
    except Exception as e:
        print(f"  ❌ 触发工作流失败: {e}")
        return False


def main():
    print()
    print("=" * 60)
    print("       🍪 Buff Cookie 设置工具")
    print("=" * 60)
    print()

    # 仓库信息
    repo_full_name = "KurotoDrei/get_BuffInfo"

    # 步骤1: 获取 Cookie
    cookie = get_buff_cookie_from_user()
    if not cookie:
        print("\n❌ 已取消")
        sys.exit(1)

    # 步骤2: 获取 GitHub Token
    token = get_github_token()
    if not token:
        print("\n❌ 已取消")
        sys.exit(1)

    # 步骤3: 更新 secret
    print(f"\n{'=' * 60}")
    print("   正在配置仓库: KurotoDrei/get_BuffInfo")
    print(f"{'=' * 60}")

    success = update_github_secret(token, repo_full_name, "BUFF_COOKIE", cookie)

    if not success:
        print("\n❌ Secret 更新失败")
        print("请检查: 1. Token 权限 2. 网络连接 3. 仓库名称是否正确")
        sys.exit(1)

    # 步骤4: 触发工作流
    print()
    trigger = input("  是否立即触发一次价格追踪运行？(Y/n): ").strip().lower()
    if trigger != 'n':
        trigger_workflow(token, repo_full_name)

    print()
    print("=" * 60)
    print("   ✅ 全部完成！")
    print()
    print(f"   下次 Cookie 过期时，再次运行:")
    print(f"     python cookie_setup.py")
    print()
    print(f"   访问仪表盘:")
    print(f"     https://kurotodrei.github.io/get_BuffInfo/")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 已取消")
        sys.exit(1)
    except ImportError as e:
        if "nacl" in str(e) or "pynacl" in str(e):
            print("\n❌ 缺少依赖: pynacl")
            print("   请运行: pip install pynacl requests")
        else:
            print(f"\n❌ 导入错误: {e}")
        sys.exit(1)
