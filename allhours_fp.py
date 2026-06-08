import requests
import time
import os
import subprocess
import pandas as pd
import threading
import re
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================== Git 推送配置 ==================
GITHUB_REPO = "Juineii/allhours_fp0610"        # 请替换为您的仓库名
GITHUB_BRANCH = "main"                        # 分支名（main 或 master）
PUSH_INTERVAL = 60                            # 推送检查间隔（秒）

PRODUCTS = [
    {"url": "https://new-prod-ic2.imcatalogue.com/api/v1/product/6a26447b12e012b936c438c5"}
    # 可以继续添加更多商品
]

# 请求头（所有商品共用）
HEADERS = {
    "Host": "new-prod-ic2.imcatalogue.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541939) XWEB/19841",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "ictrace": "[MP 9e33f33482fd243d4d732af5d2dd540e]",
    "ictoken": "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",
    "minippage": "pages/detail/index",
    "Referer": "https://servicewechat.com/wx2932f9da05a48c27/19/page-frame.html",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Priority": "u=1, i"
}

# 存储每个选项的上次库存，key 为 (url, option_key) 或 (url, '整体')
# 存储每个选项是否已初始化
last_stock_dict = {}
initialized_dict = {}

lines_since_last_push = 0          # 自上次推送后新增的CSV总行数
lines_lock = threading.Lock()      # 保护计数器的锁
csv_file_locks = {}                # 每个CSV文件的锁，key为文件名
csv_file_lock = threading.Lock()   # 保护 csv_file_locks 字典的锁


def get_csv_lock(filename):
    """获取指定CSV文件的线程锁"""
    with csv_file_lock:
        if filename not in csv_file_locks:
            csv_file_locks[filename] = threading.Lock()
        return csv_file_locks[filename]


def sanitize_filename(name):
    """清理字符串中的非法字符，使其可作为文件名"""
    # 替换 Windows 文件名中不允许的字符为下划线
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()


def git_push_update():
    """提交并推送所有CSV文件的变更"""
    try:
        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            print("⚠️ 环境变量 GITHUB_TOKEN 未设置，跳过 Git 推送")
            return False

        remote_url = f"https://{token}@github.com/{GITHUB_REPO}.git"

        # 暂存所有变更（包括新增、修改、删除的文件）
        subprocess.run(['git', 'add', '--all'], check=True, capture_output=True, timeout=30)

        # 检查是否有变更可提交
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True, timeout=30)
        if result.returncode != 0:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"自动更新数据 {timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True, timeout=30)
            subprocess.run(
                ['git', 'push', remote_url, f'HEAD:{GITHUB_BRANCH}'],
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"✅ 已推送到 GitHub: {commit_msg}")
            return True
        else:
            print("⏭️ 无文件变更，跳过推送")
            return True
    except subprocess.TimeoutExpired:
        print("❌ Git 操作超时 (30秒)，推送失败")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e.stderr if e.stderr else e}")
        return False
    except Exception as e:
        print(f"❌ 推送过程中发生错误: {e}")
        return False


def append_to_csv(timestamp, product_name_with_option, stock_change_msg, sales_volume, csv_filename):
    """写入指定的CSV文件并累加全局计数器"""
    global lines_since_last_push
    try:
        columns = ["时间", "商品名称", "库存变化", "单笔销量"]
        new_row = pd.DataFrame([[timestamp, product_name_with_option, stock_change_msg, sales_volume]], columns=columns)

        # 获取该文件对应的锁
        file_lock = get_csv_lock(csv_filename)

        with file_lock:
            if os.path.exists(csv_filename):
                df_existing = pd.read_csv(csv_filename, encoding='utf-8-sig')
            else:
                df_existing = pd.DataFrame(columns=columns)

            df_updated = pd.concat([df_existing, new_row], ignore_index=True)
            df_updated.to_csv(csv_filename, index=False, encoding='utf-8-sig')

        # 保留原有打印格式，方便实时查看
        print(f"{timestamp},{product_name_with_option},{stock_change_msg},{sales_volume} -> 写入 {csv_filename}")

        # 增加全局计数器
        with lines_lock:
            lines_since_last_push += 1

    except Exception as e:
        print(f"CSV写入错误 ({csv_filename}): {e}")


def check_single_product(product_info):
    """检查单个商品的库存变化，每个选项独立写入不同CSV文件"""
    url = product_info["url"]

    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        if response.status_code != 200:
            print(f"[{datetime.now()}] 请求失败，URL: {url}，状态码：{response.status_code}")
            return

        data = response.json()
        product_base_name = data.get("data", {}).get("productName", "unknown")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 检查是否存在选项列表 options
        options = data.get("options")
        if options and isinstance(options, list) and len(options) > 0:
            # 处理每个选项
            for opt in options:
                opt_data = opt.get("data", {})
                opt_stock = opt_data.get("stock")
                if opt_stock is None:
                    print(f"[{current_time}] 选项 {opt.get('id')} 无库存字段，跳过")
                    continue

                # 获取选项显示名称
                opt_name = opt_data.get("subProductExposeName")
                if not opt_name:
                    opt_name = opt_data.get("subProductName", opt_data.get("type", "unknown_option"))
                # 清理选项名作为文件名
                safe_opt_name = sanitize_filename(opt_name)
                csv_filename = f"{safe_opt_name}.csv"

                # 构建唯一标识key（用于记录上次库存状态）
                opt_key = opt.get("id", opt_name)
                full_key = (url, opt_key)
                full_product_name = f"{product_base_name} - {opt_name}"

                if not initialized_dict.get(full_key, False):
                    # 首次监控，记录初始库存
                    last_stock_dict[full_key] = opt_stock
                    initialized_dict[full_key] = True
                    append_to_csv(current_time, full_product_name, f"初始库存：{opt_stock}", 0, csv_filename)
                else:
                    last = last_stock_dict.get(full_key)
                    if opt_stock != last:
                        change_msg = f"{last} -> {opt_stock}"
                        sales_volume = last - opt_stock
                        append_to_csv(current_time, full_product_name, change_msg, sales_volume, csv_filename)
                        last_stock_dict[full_key] = opt_stock
        else:
            # 无选项的商品（整体库存），使用商品基础名作为CSV文件名
            safe_name = sanitize_filename(product_base_name)
            csv_filename = f"{safe_name}.csv"
            full_key = (url, "整体")

            # 提取库存（兼容旧格式）
            stock = data.get("data", {}).get("stock", [None])[0]
            if stock is None:
                print(f"[{current_time}] 未找到库存字段，URL: {url}")
                return

            full_product_name = product_base_name

            if not initialized_dict.get(full_key, False):
                last_stock_dict[full_key] = stock
                initialized_dict[full_key] = True
                append_to_csv(current_time, full_product_name, f"初始库存：{stock}", 0, csv_filename)
            else:
                last = last_stock_dict.get(full_key)
                if stock != last:
                    change_msg = f"{last} -> {stock}"
                    sales_volume = last - stock
                    append_to_csv(current_time, full_product_name, change_msg, sales_volume, csv_filename)
                    last_stock_dict[full_key] = stock

    except Exception as e:
        print(f"[{datetime.now()}] 商品检查异常，URL: {url}，错误：{e}")


# ================== 推送工作线程 ==================
def push_worker():
    global lines_since_last_push
    while True:
        time.sleep(PUSH_INTERVAL)
        with lines_lock:
            pending = lines_since_last_push
        if pending > 0:
            print(f"⏰ 定时推送：有 {pending} 条新数据待推送")
            success = git_push_update()
            if success:
                with lines_lock:
                    lines_since_last_push = 0
                print("✅ 推送成功，计数器已归零")
            else:
                print("⚠️ 推送失败，下次再试")


def monitor_products(interval):
    while True:
        for product in PRODUCTS:
            check_single_product(product)
        time.sleep(interval)


if __name__ == "__main__":
    push_thread = threading.Thread(target=push_worker, daemon=True)
    push_thread.start()

    try:
        monitor_products(interval=10)
    except KeyboardInterrupt:
        print("\n监控程序被用户终止")
        # 退出前推送剩余数据
        with lines_lock:
            pending = lines_since_last_push
        if pending > 0:
            print(f"正在推送剩余的 {pending} 条数据...")
            success = git_push_update()
            if success:
                with lines_lock:
                    lines_since_last_push = 0
                print("✅ 剩余数据已推送")
            else:
                print("⚠️ 剩余数据推送失败，请手动检查")
        else:
            print("无待推送数据")