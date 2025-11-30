import os
import sys
from weex_sdk import WeexClient

# 测试创建市价单功能
def test_create_market_order():
    # 从环境变量获取API密钥
    api_key = os.getenv('WEEX_API_KEY')
    api_secret = os.getenv('WEEX_SECRET')
    api_passphrase = os.getenv('WEEX_ACCESS_PASSPHRASE')
    
    if not all([api_key, api_secret, api_passphrase]):
        print("错误: 缺少必要的环境变量!")
        print("请设置以下环境变量:")
        print("  WEEX_API_KEY")
        print("  WEEX_SECRET")
        print("  WEEX_ACCESS_PASSPHRASE")
        return False
    
    try:
        # 创建WeexClient实例
        client = WeexClient(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
            testnet=False  # 使用主网API
        )
        
        print("开始测试创建市价买单...")
        
        # 测试创建市价买单
        # 参数设置：
        # - symbol: 交易对，使用cmt_btcusdt
        # - side: 交易方向，使用buy
        # - amount: 交易数量，使用0.01
        order = client.create_market_order(
            symbol="cmt_btcusdt",
            side="buy",
            amount=0.01
        )
        
        if order:
            print(f"市价单创建成功!")
            print(f"订单ID: {order.get('id', 'N/A')}")
            print(f"客户端订单ID: {order.get('clientOrderId', 'N/A')}")
            print(f"订单详情: {order.get('info', {})}")
            return True
        else:
            print("市价单创建失败!")
            return False
            
    except Exception as e:
        print(f"测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("===== WEEX 创建市价单测试 =====")
    success = test_create_market_order()
    print("\n测试结果:", "成功" if success else "失败")
