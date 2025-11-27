#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Weex SDK的历史订单获取功能
"""

import os
import sys
from dotenv import load_dotenv

# 添加当前目录到Python路径，确保能导入weex_sdk
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from weex_sdk import WeexClient


def test_order_history():
    """
    测试获取历史订单功能
    """
    # 加载环境变量
    print("正在加载环境变量...")
    load_dotenv()
    
    # 检查必要的环境变量是否存在
    # 注意：环境变量名称需要与.env文件中的实际名称匹配
    if not os.environ.get("WEEX_API_KEY"):
        print("错误: 环境变量 WEEX_API_KEY 未设置，请检查.env文件")
        return False
    if not os.environ.get("WEEX_SECRET"):
        print("错误: 环境变量 WEEX_SECRET 未设置，请检查.env文件")
        return False
    if not os.environ.get("WEEX_ACCESS_PASSPHRASE"):
        print("错误: 环境变量 WEEX_ACCESS_PASSPHRASE 未设置，请检查.env文件")
        return False
    
    # 可选设置WEEX_API_ENV，如果未设置则使用默认值
    if not os.environ.get("WEEX_API_ENV"):
        print("警告: 环境变量 WEEX_API_ENV 未设置，将使用默认值")
        os.environ["WEEX_API_ENV"] = "prod"  # 设置默认环境
    
    try:
        # 初始化WeexClient，从环境变量中读取凭证
        print("正在初始化WeexClient...")
        api_key = os.environ.get("WEEX_API_KEY")
        api_secret = os.environ.get("WEEX_SECRET")  # 注意：使用正确的环境变量名
        api_passphrase = os.environ.get("WEEX_ACCESS_PASSPHRASE")
        
        client = WeexClient(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase
        )
        
        # 测试1: 获取所有交易对的历史订单（默认10条）
        print("\n测试1: 获取所有交易对的历史订单（默认10条）")
        orders = client.get_order_history()
        
        if not orders:
            print("警告: 未获取到任何历史订单")
        else:
            print(f"成功获取到{len(orders)}条历史订单")
            # 打印前3条订单的详细信息
            print(f"\n前3条订单的详细信息:")
            for i, order in enumerate(orders[:3]):
                print(f"\n订单{i+1}:")
                print(f"交易对: {order.get('symbol', 'N/A')}")
                print(f"订单ID: {order.get('order_id', 'N/A')}")
                print(f"订单状态: {order.get('status', 'N/A')}")
                print(f"订单类型: {order.get('type', 'N/A')}")
                print(f"订单数量: {order.get('size', 'N/A')}")
                print(f"已成交数量: {order.get('filled_qty', 'N/A')}")
                print(f"订单价格: {order.get('price', 'N/A')}")
                print(f"平均成交价格: {order.get('price_avg', 'N/A')}")
                print(f"交易费用: {order.get('fee', 'N/A')}")
                print(f"创建时间: {order.get('createTime', 'N/A')}")
        
        # 测试2: 获取特定交易对的历史订单（例如BTCUSDT）
        # 注意：根据实际情况修改交易对
        test_symbol = "cmt_btcusdt"
        print(f"\n测试2: 获取特定交易对 {test_symbol} 的历史订单")
        symbol_orders = client.get_order_history(symbol=test_symbol)
        
        if not symbol_orders:
            print(f"警告: 未获取到交易对 {test_symbol} 的任何历史订单")
        else:
            print(f"成功获取到交易对 {test_symbol} 的{len(symbol_orders)}条历史订单")
        
        # 测试3: 自定义page_size参数
        custom_page_size = 5
        print(f"\n测试3: 自定义page_size={custom_page_size}")
        custom_orders = client.get_order_history(page_size=custom_page_size)
        print(f"成功获取到{len(custom_orders)}条历史订单（page_size={custom_page_size}）")
        
        # 测试4: 自定义create_date参数（最近7天的订单）
        recent_days = 7
        print(f"\n测试4: 获取最近{recent_days}天的历史订单")
        recent_orders = client.get_order_history(create_date=recent_days)
        print(f"成功获取到最近{recent_days}天的{len(recent_orders)}条历史订单")
        
        # 测试5: 组合参数测试
        print(f"\n测试5: 组合参数测试（交易对={test_symbol}, page_size=3, create_date={recent_days}）")
        combined_orders = client.get_order_history(symbol=test_symbol, page_size=3, create_date=recent_days)
        print(f"成功获取到{len(combined_orders)}条历史订单")
        
        print("\n✅ 历史订单测试完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    print("===== Weex SDK 历史订单获取功能测试 =====")
    success = test_order_history()
    
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n💥 测试失败，请检查错误信息。")
        sys.exit(1)
