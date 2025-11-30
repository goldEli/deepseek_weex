from weex_sdk import WeexClient

# 直接使用硬编码的API密钥进行测试
def test_create_market_order_direct():
    try:
        # 创建WeexClient实例，直接使用密钥值
        client = WeexClient(
            api_key="weex_966bcf59f10c0cf7e8db9e8b94b0fc6e",
            api_secret="f1deb634e970dcde8453e405e0f37d7d79d36d14f9a037efe0685c7acbc2dd90",
            api_passphrase="weex1234",
            testnet=True  # 使用测试网络API
        )
        
        print("开始测试创建市价买单...")
        
        # 测试创建市价买单
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
    print("===== WEEX 创建市价单测试 (直接使用密钥) =====")
    success = test_create_market_order_direct()
    print("\n测试结果:", "成功" if success else "失败")
