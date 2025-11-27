import sys
import os
import json

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入WeexClient
from weex_sdk import WeexClient

# 从环境变量加载API密钥
from dotenv import load_dotenv
load_dotenv()

# 初始化WeexClient，使用测试网络
client = WeexClient(
    api_key=os.getenv('WEEX_API_KEY'),
    api_secret=os.getenv('WEEX_SECRET'),
    api_passphrase=os.getenv('WEEX_ACCESS_PASSPHRASE'),
    testnet=True
)

def test_create_market_order():
    print("测试创建市价单...")
    try:
        # 按照官方示例格式设置参数
        symbol = 'cmt_btcusdt'
        size = '0.01'  # 使用字符串格式
        order_type = '0'  # 0表示限价单，1表示市价单
        match_price = '1'  # 1表示市价单
        side = '1'  # 1表示买入，2表示卖出
        
        # 使用官方示例中的参数格式
        result = client.create_market_order(
            symbol=symbol,
            side='BUY',
            amount=float(size),
            client_oid=str(int(time.time() * 1000)),
            order_type='0',
            match_price='1'
        )
        print(f"创建市价单成功: {result}")
        return True
    except Exception as e:
        print(f"创建市价单失败: {e}")
        return False

if __name__ == '__main__':
    import time
    test_create_market_order()
