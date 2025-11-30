import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入WeexClient
from weex_sdk import WeexClient

# 从环境变量加载API密钥
from dotenv import load_dotenv
load_dotenv()

# 初始化WeexClient
client = WeexClient(
    api_key=os.getenv('WEEX_API_KEY'),
    api_secret=os.getenv('WEEX_SECRET'),
    api_passphrase=os.getenv('WEEX_ACCESS_PASSPHRASE'),
    testnet=False
)

def test_legacy_amount():
    print("测试获取账户余额（使用legacy_amount字段）...")
    try:
        # 测试获取USDT余额
        usdt_balance = client.get_coin_balance("USDT")
        print(f"USDT余额: {usdt_balance}")
        return usdt_balance
    except Exception as e:
        print(f"获取账户余额时出错: {e}")
        return None

if __name__ == '__main__':
    test_legacy_amount()
