import os
import time
from datetime import datetime
from dotenv import load_dotenv

# 导入WEEX SDK
from weex_sdk import WeexClient

# 加载环境变量
load_dotenv()

# 初始化WEEX交易所客户端
def init_client():
    """初始化WEEX交易所客户端"""
    WEEX_API_KEY = os.getenv('WEEX_API_KEY')
    WEEX_SECRET = os.getenv('WEEX_SECRET')
    WEEX_ACCESS_PASSPHRASE = os.getenv('WEEX_ACCESS_PASSPHRASE')
    
    if not all([WEEX_API_KEY, WEEX_SECRET, WEEX_ACCESS_PASSPHRASE]):
        raise ValueError("请确保环境变量中包含正确的WEEX API凭证")
    
    client = WeexClient(
        api_key=WEEX_API_KEY,
        api_secret=WEEX_SECRET,
        api_passphrase=WEEX_ACCESS_PASSPHRASE,
        testnet=False  # 使用主网API
    )
    
    return client

# 交易参数配置
TRADE_CONFIG = {
    'symbol': 'cmt_btcusdt',  # WEEX的合约符号格式
    'amount': 0.01,  # 交易数量 (BTC)
    'leverage': 10,  # 杠杆倍数
    'test_mode': True  # 测试模式
}

def setup_exchange(client):
    """设置交易所参数"""
    try:
        # WEEX设置杠杆 - 使用set_leverage方法
        # 1表示逐仓模式，0表示全仓模式
        margin_mode = 0  # 全仓模式
        client.set_leverage(
            symbol=TRADE_CONFIG['symbol'],
            margin_mode=margin_mode,
            long_leverage=str(TRADE_CONFIG['leverage']),
            short_leverage=str(TRADE_CONFIG['leverage'])
        )
        print(f"设置杠杆倍数: {TRADE_CONFIG['leverage']}x")

        # 获取USDT余额
        usdt_balance = client.get_coin_balance('USDT')
        print(f"当前USDT余额: {usdt_balance:.2f}")

        return True
    except Exception as e:
        print(f"交易所设置失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_current_position(client):
    """获取当前持仓情况"""
    try:
        # 获取持仓
        positions = client.fetch_positions(TRADE_CONFIG['symbol'])

        for pos in positions:
            if pos['symbol'] == TRADE_CONFIG['symbol'] and pos['size'] > 0:
                return {
                    'side': pos['side'],  # 'long' or 'short'
                    'size': pos['size'],
                    'entry_price': pos['entryPrice'],
                    'unrealized_pnl': pos['unrealizedPnl'],
                    'leverage': pos['leverage'],
                    'symbol': pos['symbol']
                }

        return None

    except Exception as e:
        print(f"获取持仓失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def open_long_position(client):
    """执行开多操作"""
    print(f"\n{'=' * 60}")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")
    
    print(f"交易对: {TRADE_CONFIG['symbol']}")
    print(f"开多数量: {TRADE_CONFIG['amount']} BTC")
    print(f"杠杆倍数: {TRADE_CONFIG['leverage']}x")
    
    if TRADE_CONFIG['test_mode']:
        print("测试模式 - 仅模拟交易")
    else:
        print("实盘交易模式，请谨慎操作！")
    
    # 获取当前持仓
    current_position = get_current_position(client)
    print(f"当前持仓: {current_position}")
    
    try:
        # 检查是否已持有多仓
        if current_position and current_position['side'] == 'long':
            print(f"已持有多仓，数量: {current_position['size']}，无需再次开多")
            return
        
        # 如果持有空仓，先平空再开多
        elif current_position and current_position['side'] == 'short':
            print("检测到空仓，正在平空...")
            
            if TRADE_CONFIG['test_mode']:
                print(f"[模拟] 平空数量: {current_position['size']}")
            else:
                # 平空仓
                client.create_market_order(
                    TRADE_CONFIG['symbol'],
                    'buy',
                    current_position['size'],
                    reduce_only=True  # 使用reduce_only参数表示平仓
                )
                print(f"平空成功，数量: {current_position['size']}")
                time.sleep(2)  # 等待平仓完成
        
        # 开多仓
        print(f"正在开多...")
        
        if TRADE_CONFIG['test_mode']:
            print(f"[模拟] 开多数量: {TRADE_CONFIG['amount']}")
        else:
            # 开多仓
            client.create_market_order(
                TRADE_CONFIG['symbol'],
                'buy',
                TRADE_CONFIG['amount']
            )
            print(f"开多成功，数量: {TRADE_CONFIG['amount']}")
        
        # 更新持仓信息
        time.sleep(3)
        new_position = get_current_position(client)
        print(f"\n更新后持仓:")
        if new_position:
            print(f"方向: {new_position['side']}")
            print(f"数量: {new_position['size']}")
            print(f"入场价格: {new_position['entry_price']:.2f}")
            print(f"未实现盈亏: {new_position['unrealized_pnl']:.2f} USDT")
        else:
            print("无持仓")
            
    except Exception as e:
        print(f"开多操作失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("BTC/USDT WEEX 开多操作工具")
    
    try:
        # 初始化客户端
        client = init_client()
        print("客户端初始化成功")
        
        # 设置交易所
        if not setup_exchange(client):
            print("交易所初始化失败，程序退出")
            return
        
        # 执行开多操作
        open_long_position(client)
        
    except Exception as e:
        print(f"程序异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()