import os
import time
from weex_sdk import WeexClient
from dotenv import load_dotenv

load_dotenv()

# 初始化WEEX客户端
def test_weex_client():
    print("开始测试WEEX SDK...")
    
    # 创建客户端实例
    client = WeexClient(
        api_key=os.getenv('WEEX_API_KEY'),
        api_secret=os.getenv('WEEX_SECRET'),
        api_passphrase=os.getenv('WEEX_ACCESS_PASSPHRASE'),
        testnet=False
    )
    
    try:
        # 测试获取账户余额
        print("\n1. 测试获取USDT余额:")
        balance = client.get_coin_balance('USDT')
        print(f"USDT余额: {balance}")
        
        # 测试获取K线数据
        print("\n2. 测试获取K线数据:")
        symbol = 'cmt_btcusdt'
        timeframe = '15m'
        ohlcv = client.fetch_ohlcv(symbol, timeframe, limit=5)
        print(f"获取到{len(ohlcv)}条K线数据")
        print(f"最新K线: {ohlcv[-1] if ohlcv else '无数据'}")
        
        # 测试获取持仓
        print("\n3. 测试获取持仓:")
        positions = client.fetch_positions(symbol)
        print(f"持仓数量: {len(positions)}")
        for pos in positions:
            print(f"持仓: {pos}")
        
        print("\nWEEX SDK测试完成!")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_weex_client()