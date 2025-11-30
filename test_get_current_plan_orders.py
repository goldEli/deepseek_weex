#!/usr/bin/env python3
"""
测试获取当前计划订单的方法
参考文档: GET /capi/v2/order/currentPlan
"""

import os
import sys
from dotenv import load_dotenv

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from weex_sdk import WeexClient

# 加载环境变量
load_dotenv()

def test_get_current_plan_orders():
    """测试获取当前计划订单功能"""
    print("=" * 60)
    print("测试获取当前计划订单")
    print("=" * 60)
    print()

    # 检查环境变量
    required_vars = ['WEEX_API_KEY', 'WEEX_SECRET', 'WEEX_ACCESS_PASSPHRASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("⚠️  警告: 以下环境变量未设置:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("请在.env文件中设置这些变量，或使用测试模式进行调试")
        print()
        return

    try:
        # 初始化WEEX客户端
        exchange = WeexClient(
            api_key=os.getenv('WEEX_API_KEY'),
            api_secret=os.getenv('WEEX_SECRET') or os.getenv('WEEX_API_SECRET'),
            api_passphrase=os.getenv('WEEX_ACCESS_PASSPHRASE'),
            testnet=False
        )

        print("✅ WEEX客户端初始化成功")
        print()

        # 测试场景1: 获取所有当前计划订单
        print("场景1: 获取所有当前计划订单")
        print("-" * 60)
        result = exchange.getCurrentPlanOrders()

        if result['error']:
            print(f"❌ 错误: {result['error']}")
            print(f"   错误代码: {result['error_code']}")
        else:
            print(f"✅ 成功获取 {result['total_count']} 条当前计划订单")

            if result['orders']:
                print()
                for i, order in enumerate(result['orders'][:3], 1):  # 只显示前3条
                    print(f"订单 {i}:")
                    print(f"  交易对: {order['symbol']}")
                    print(f"  订单ID: {order['order_id']}")
                    print(f"  类型: {order['type']}")
                    print(f"  价格: ${order['price']:,.2f}")
                    print(f"  数量: {order['size']}")
                    print(f"  状态: {order['status']}")
                    print(f"  止盈价: {order['presetTakeProfitPrice'] if order['presetTakeProfitPrice'] else 'N/A'}")
                    print(f"  止损价: {order['presetStopLossPrice'] if order['presetStopLossPrice'] else 'N/A'}")
                    print()
            else:
                print("暂无当前计划订单")
        print()

        # 测试场景2: 按交易对查询
        print("场景2: 按交易对查询 (BTC/USDT)")
        print("-" * 60)
        result = exchange.getCurrentPlanOrders(symbol="cmt_btcusdt")

        if result['error']:
            print(f"❌ 错误: {result['error']}")
        else:
            print(f"✅ 成功获取 {result['total_count']} 条 cmt_btcusdt 当前计划订单")
        print()

        # 测试场景3: 指定订单ID查询
        print("场景3: 指定订单ID查询")
        print("-" * 60)
        result = exchange.getCurrentPlanOrders(orderId=123456789)

        if result['error']:
            print(f"❌ 错误: {result['error']}")
        else:
            print(f"✅ 成功查询指定订单")
        print()

        # 测试场景4: 按时间范围查询
        print("场景4: 按时间范围查询")
        print("-" * 60)
        import time
        now = int(time.time() * 1000)  # 毫秒时间戳
        one_hour_ago = now - 3600 * 1000  # 1小时前

        result = exchange.getCurrentPlanOrders(
            startTime=one_hour_ago,
            endTime=now,
            limit=10
        )

        if result['error']:
            print(f"❌ 错误: {result['error']}")
        else:
            print(f"✅ 成功获取 {result['total_count']} 条时间范围内的订单")
        print()

        print("=" * 60)
        print("测试完成!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

def demo_response_format():
    """演示API响应数据格式"""
    print()
    print("=" * 60)
    print("API响应数据格式示例")
    print("=" * 60)
    print()

    sample_response = [
        {
            "symbol": "cmt_btcusdt",
            "size": "1",
            "client_oid": "1234567890",
            "createTime": "1742213506548",
            "filled_qty": "0.5",
            "fee": "0.01",
            "order_id": "461234125",
            "price": "50000.00",
            "price_avg": "49900.00",
            "status": "1",
            "type": "1",
            "order_type": "0",
            "totalProfits": "200.00",
            "triggerPrice": "48000.00",
            "triggerPriceType": "LIMIT",
            "triggerTime": "1742213506548",
            "presetTakeProfitPrice": "52000.00",
            "presetStopLossPrice": "48000.00"
        }
    ]

    print("API原始响应 (list):")
    import json
    print(json.dumps(sample_response, indent=2, ensure_ascii=False))
    print()

    print("格式化后的订单信息:")
    from weex_sdk import WeexClient
    exchange = WeexClient("test", "test", "test")

    # 模拟解析响应
    order = sample_response[0]
    formatted = {
        "symbol": order.get("symbol", ""),
        "size": float(order.get("size", 0.0)),
        "order_id": order.get("order_id", ""),
        "price": float(order.get("price", 0.0)),
        "status": {-1: "已取消", 0: "待成交", 1: "部分成交", 2: "已成交"}.get(order.get("status"), "未知"),
        "type": {1: "开多", 2: "开空", 3: "平多", 4: "平空"}.get(order.get("type"), "未知"),
        "presetTakeProfitPrice": float(order.get("presetTakeProfitPrice", 0.0)) if order.get("presetTakeProfitPrice") else None,
        "presetStopLossPrice": float(order.get("presetStopLossPrice", 0.0)) if order.get("presetStopLossPrice") else None
    }

    for key, value in formatted.items():
        print(f"  {key}: {value}")
    print()

if __name__ == "__main__":
    test_get_current_plan_orders()
    demo_response_format()
