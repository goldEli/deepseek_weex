import os
from dotenv import load_dotenv
from weex_sdk import WeexClient
from deepseek_weex1 import setup_exchange, TRADE_CONFIG

# 加载环境变量
load_dotenv()

# 初始化WEEX交易所客户端
exchange = WeexClient(
    api_key=os.getenv('WEEX_API_KEY'),
    api_secret=os.getenv('WEEX_SECRET'),
    api_passphrase=os.getenv('WEEX_ACCESS_PASSPHRASE'),
    testnet=False  # 使用主网API
)

# 测试设置杠杆
def test_leverage_setting():
    print("测试设置杠杆功能...")
    print(f"交易对: {TRADE_CONFIG['symbol']}")
    print(f"杠杆倍数: {TRADE_CONFIG['leverage']}")
    print(f"保证金模式: 全仓模式 (margin_mode=1)")
    
    try:
        # 直接调用setup_exchange函数测试
        success = setup_exchange()
        if success:
            print("✅ 杠杆设置成功!")
            return True
        else:
            print("❌ 杠杆设置失败")
            return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 测试deepseek_weex1.py中的杠杆设置功能 ===")
    
    # 确保环境变量已设置
    if not all([os.getenv('WEEX_API_KEY'), os.getenv('WEEX_SECRET'), os.getenv('WEEX_ACCESS_PASSPHRASE')]):
        print("❌ 错误: 请在.env文件中设置WEEX_API_KEY, WEEX_SECRET和WEEX_ACCESS_PASSPHRASE")
        exit(1)
    
    # 运行测试
    test_leverage_setting()