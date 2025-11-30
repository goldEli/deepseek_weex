import os
import time
from dotenv import load_dotenv
from weex_sdk import WeexClient

# 加载环境变量
load_dotenv()

# 从环境变量获取API凭证
api_key = os.getenv('WEEX_API_KEY')
api_secret = os.getenv('WEEX_API_SECRET') or os.getenv('WEEX_SECRET')
api_passphrase = os.getenv('WEEX_ACCESS_PASSPHRASE')

def test_get_history_orders():
    """
    测试获取历史订单功能
    """
    print("开始测试WeexClient.get_history_orders方法...\n")
    
    # 初始化客户端
    client = WeexClient(api_key, api_secret, api_passphrase)
    
    # 测试1: 默认参数调用（无参数）
    print("测试1: 默认参数调用（无参数）")
    try:
        result = client.get_history_orders()
        orders = result.get('orders', [])
        print(f"响应状态: {'成功' if 'error' not in result else '失败'}")
        print(f"获取到的订单数量: {len(orders)}")
        if orders:
            # 打印前3个订单的简要信息
            for i, order in enumerate(orders[:3]):
                print(f"订单{i+1}: 交易对={order.get('symbol')}, 订单ID={order.get('order_id')}, 状态={order.get('status')}")
        if 'error' in result:
            print(f"错误信息: {result['error']}, 错误代码: {result['error_code']}")
    except Exception as e:
        print(f"测试1执行失败: {str(e)}")
    print("\n" + "-"*60 + "\n")
    
    # 测试2: 指定交易对参数（BTC/USDT）
    print("测试2: 指定交易对参数（BTC/USDT）")
    try:
        result = client.get_history_orders(symbol="cmt_btcusdt")
        orders = result.get('orders', [])
        print(f"响应状态: {'成功' if 'error' not in result else '失败'}")
        print(f"获取到的BTC订单数量: {len(orders)}")
        if orders:
            # 打印前3个订单的简要信息
            for i, order in enumerate(orders[:3]):
                print(f"订单{i+1}: 交易对={order.get('symbol')}, 订单ID={order.get('order_id')}, 状态={order.get('status')}")
        if 'error' in result:
            print(f"错误信息: {result['error']}, 错误代码: {result['error_code']}")
    except Exception as e:
        print(f"测试2执行失败: {str(e)}")
    print("\n" + "-"*60 + "\n")
    
    # 测试3: 自定义page_size参数
    print("测试3: 自定义page_size参数")
    try:
        result = client.get_history_orders(symbol="cmt_btcusdt", page_size=20)
        orders = result.get('orders', [])
        print(f"响应状态: {'成功' if 'error' not in result else '失败'}")
        print(f"获取到的订单数量: {len(orders)}")
        if orders:
            # 打印前3个订单的简要信息
            for i, order in enumerate(orders[:3]):
                print(f"订单{i+1}: 交易对={order.get('symbol')}, 订单ID={order.get('order_id')}, 状态={order.get('status')}")
        if 'error' in result:
            print(f"错误信息: {result['error']}, 错误代码: {result['error_code']}")
    except Exception as e:
        print(f"测试3执行失败: {str(e)}")
    print("\n" + "-"*60 + "\n")
    
    # 测试4: 自定义create_date参数（获取最近7天的订单）
    print("测试4: 自定义create_date参数（获取最近7天的订单）")
    try:
        # 根据API文档，create_date应该是天数（而不是时间戳）
        result = client.get_history_orders(symbol="cmt_btcusdt", create_date=7)
        orders = result.get('orders', [])
        print(f"响应状态: {'成功' if 'error' not in result else '失败'}")
        print(f"获取到的最近7天订单数量: {len(orders)}")
        if orders:
            # 打印前3个订单的简要信息
            for i, order in enumerate(orders[:3]):
                print(f"订单{i+1}: 交易对={order.get('symbol')}, 订单ID={order.get('order_id')}, 状态={order.get('status')}")
        if 'error' in result:
            print(f"错误信息: {result['error']}, 错误代码: {result['error_code']}")
    except Exception as e:
        print(f"测试4执行失败: {str(e)}")
    print("\n" + "-"*60 + "\n")
    
    # 测试5: 组合参数测试
    print("测试5: 组合参数测试")
    try:
        # 使用组合参数
        result = client.get_history_orders(symbol="cmt_btcusdt", page_size=10, create_date=7)
        orders = result.get('orders', [])
        print(f"响应状态: {'成功' if 'error' not in result else '失败'}")
        print(f"组合参数下获取到的订单数量: {len(orders)}")
        if orders:
            # 打印前3个订单的简要信息
            for i, order in enumerate(orders[:3]):
                print(f"订单{i+1}: 交易对={order.get('symbol')}, 订单ID={order.get('order_id')}, 状态={order.get('status')}")
        if 'error' in result:
            print(f"错误信息: {result['error']}, 错误代码: {result['error_code']}")
    except Exception as e:
        print(f"测试5执行失败: {str(e)}")
    print("\n" + "-"*60 + "\n")
    
    # 测试6: 参数验证 - 无效的page_size
    print("测试6: 参数验证 - 无效的page_size")
    try:
        result = client.get_history_orders(symbol="cmt_btcusdt", page_size="invalid")
        orders = result.get('orders', [])
        print(f"响应状态: {'成功' if 'error' not in result else '失败'}")
        print(f"获取到的订单数量: {len(orders)}")
        if 'error' in result:
            print(f"错误信息: {result['error']}, 错误代码: {result['error_code']}")
    except Exception as e:
        print(f"测试6执行失败: {str(e)}")
    print("\n" + "-"*60 + "\n")
    
    # 测试7: 参数验证 - 无效的create_date范围
    print("测试7: 参数验证 - 无效的create_date范围")
    try:
        result = client.get_history_orders(symbol="cmt_btcusdt", create_date=100)
        orders = result.get('orders', [])
        print(f"响应状态: {'成功' if 'error' not in result else '失败'}")
        print(f"获取到的订单数量: {len(orders)}")
        if 'error' in result:
            print(f"错误信息: {result['error']}, 错误代码: {result['error_code']}")
    except Exception as e:
        print(f"测试7执行失败: {str(e)}")
    print("\n" + "-"*60 + "\n")
    
    print("所有测试完成!")

if __name__ == "__main__":
    test_get_history_orders()
