#!/usr/bin/env python3
"""
获取当前计划订单脚本
使用getCurrentPlanOrders方法查询WEEX交易所的当前计划订单

使用方法:
    python3 get_current_plan_orders.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from weex_sdk import WeexClient

# 加载环境变量
load_dotenv()


def format_timestamp(timestamp_str):
    """格式化时间戳"""
    try:
        if not timestamp_str or timestamp_str == "0":
            return "N/A"

        # 尝试毫秒时间戳
        if len(str(timestamp_str)) >= 13:
            timestamp_ms = int(timestamp_str)
            return datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            # 尝试秒时间戳
            timestamp_s = int(timestamp_str)
            return datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str


def display_order_details(order, index=1):
    """显示订单详细信息"""
    print(f"\n{'='*80}")
    print(f"订单 #{index}")
    print(f"{'='*80}")

    print(f"📋 基本信息:")
    print(f"  订单ID:       {order.get('order_id', 'N/A')}")
    print(f"  交易对:       {order.get('symbol', 'N/A')}")
    print(f"  订单类型:     {order.get('type', 'N/A')} ({order.get('type_code', 'N/A')})")
    print(f"  订单子类型:   {order.get('order_type', 'N/A')} ({order.get('order_type_code', 'N/A')})")
    print(f"  订单状态:     {order.get('status', 'N/A')} ({order.get('status_code', 'N/A')})")

    print(f"\n💰 价格信息:")
    print(f"  委托价格:     ${order.get('price', 0):,.2f}")
    print(f"  委托数量:     {order.get('size', 0)}")
    print(f"  委托金额:     ${order.get('order_value', 0):,.2f}")
    print(f"  平均成交价:   ${order.get('price_avg', 0):,.2f}" if order.get('price_avg') else "  平均成交价:   N/A")
    print(f"  已成交数量:   {order.get('filled_qty', 0)}")
    print(f"  手续费:       ${order.get('fee', 0):,.2f}")
    print(f"  盈亏:         ${order.get('totalProfits', 0):,.2f}")

    print(f"\n🎯 止盈止损:")
    if order.get('presetTakeProfitPrice'):
        print(f"  止盈价格:     ${order.get('presetTakeProfitPrice'):,.2f}")
    else:
        print(f"  止盈价格:     未设置")

    if order.get('presetStopLossPrice'):
        print(f"  止损价格:     ${order.get('presetStopLossPrice'):,.2f}")
    else:
        print(f"  止损价格:     未设置")

    if order.get('triggerPrice'):
        print(f"  触发价格:     ${order.get('triggerPrice'):,.2f}")
        print(f"  触发类型:     {order.get('triggerPriceType', 'N/A')}")
    else:
        print(f"  触发价格:     N/A")

    print(f"\n⏰ 时间信息:")
    print(f"  创建时间:     {format_timestamp(order.get('create_time'))}")
    print(f"  触发时间:     {format_timestamp(order.get('triggerTime'))}")

    print(f"\n📝 其他信息:")
    print(f"  客户端ID:     {order.get('client_oid', 'N/A')}")


def get_all_current_plan_orders():
    """获取所有当前计划订单"""
    print("\n" + "="*80)
    print("📊 获取所有当前计划订单")
    print("="*80)

    try:
        result = exchange.getCurrentPlanOrders()

        if result['error']:
            print(f"\n❌ 错误: {result['error']}")
            print(f"   错误代码: {result['error_code']}")
            return False

        print(f"\n✅ 成功获取 {result['total_count']} 条订单记录")

        if not result['orders']:
            print("\n📝 暂无当前计划订单")
            return True

        # 显示订单列表
        for i, order in enumerate(result['orders'], 1):
            display_order_details(order, i)

        return True

    except Exception as e:
        print(f"\n❌ 获取订单时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def get_orders_by_symbol(symbol):
    """按交易对查询当前计划订单"""
    print(f"\n{'='*80}")
    print(f"🔍 查询交易对: {symbol}")
    print("="*80)

    try:
        result = exchange.getCurrentPlanOrders(symbol=symbol)

        if result['error']:
            print(f"\n❌ 错误: {result['error']}")
            return False

        print(f"\n✅ 成功获取 {result['total_count']} 条 {symbol} 订单")

        if not result['orders']:
            print(f"\n📝 暂无 {symbol} 当前计划订单")
            return True

        for i, order in enumerate(result['orders'], 1):
            display_order_details(order, i)

        return True

    except Exception as e:
        print(f"\n❌ 查询订单时发生错误: {str(e)}")
        return False


def get_orders_with_stop_loss_take_profit():
    """获取设置了止盈止损的订单"""
    print(f"\n{'='*80}")
    print("🎯 获取设置了止盈止损的订单")
    print("="*80)

    try:
        result = exchange.getCurrentPlanOrders()

        if result['error']:
            print(f"\n❌ 错误: {result['error']}")
            return False

        # 筛选有止盈止损的订单
        filtered_orders = []
        for order in result['orders']:
            if order.get('presetTakeProfitPrice') or order.get('presetStopLossPrice'):
                filtered_orders.append(order)

        print(f"\n✅ 找到 {len(filtered_orders)} 条设置了止盈止损的订单")

        if not filtered_orders:
            print("\n📝 暂无设置止盈止损的订单")
            return True

        for i, order in enumerate(filtered_orders, 1):
            display_order_details(order, i)

        return True

    except Exception as e:
        print(f"\n❌ 获取订单时发生错误: {str(e)}")
        return False


def get_pending_orders():
    """获取待成交的订单"""
    print(f"\n{'='*80}")
    print("⏳ 获取待成交的订单")
    print("="*80)

    try:
        result = exchange.getCurrentPlanOrders()

        if result['error']:
            print(f"\n❌ 错误: {result['error']}")
            return False

        # 筛选待成交订单
        pending_orders = []
        for order in result['orders']:
            status = order.get('status_code', '')
            if status in ['UNTRIGGERED', 'PENDING']:
                pending_orders.append(order)

        print(f"\n✅ 找到 {len(pending_orders)} 条待成交订单")

        if not pending_orders:
            print("\n📝 暂无待成交订单")
            return True

        for i, order in enumerate(pending_orders, 1):
            display_order_details(order, i)

        return True

    except Exception as e:
        print(f"\n❌ 获取订单时发生错误: {str(e)}")
        return False


def main():
    """主函数"""
    print("\n" + "="*80)
    print("🚀 WEEX 当前计划订单查询工具")
    print("="*80)
    print()

    # 检查环境变量
    required_vars = ['WEEX_API_KEY', 'WEEX_SECRET', 'WEEX_ACCESS_PASSPHRASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("⚠️  错误: 以下环境变量未设置:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请在.env文件中设置这些变量")
        sys.exit(1)

    global exchange
    try:
        # 初始化WEEX客户端
        exchange = WeexClient(
            api_key=os.getenv('WEEX_API_KEY'),
            api_secret=os.getenv('WEEX_SECRET') or os.getenv('WEEX_API_SECRET'),
            api_passphrase=os.getenv('WEEX_ACCESS_PASSPHRASE'),
            testnet=False
        )
        print("✅ WEEX客户端初始化成功")
    except Exception as e:
        print(f"❌ WEEX客户端初始化失败: {str(e)}")
        sys.exit(1)

    print()

    # 获取所有当前计划订单
    success = get_all_current_plan_orders()

    if success:
        print("\n\n" + "="*80)
        print("📋 可选查询操作:")
        print("="*80)
        print("1. 查询特定交易对 (BTC/USDT)")
        print("2. 查看设置了止盈止损的订单")
        print("3. 查看待成交订单")
        print("4. 退出")
        print()

        while True:
            choice = input("请选择操作 (1-4): ").strip()

            if choice == '1':
                symbol = input("请输入交易对 (例如: cmt_btcusdt): ").strip()
                if symbol:
                    get_orders_by_symbol(symbol)
            elif choice == '2':
                get_orders_with_stop_loss_take_profit()
            elif choice == '3':
                get_pending_orders()
            elif choice == '4':
                print("\n👋 感谢使用!")
                break
            else:
                print("❌ 无效选择，请输入 1-4")

    print("\n" + "="*80)
    print("✨ 程序结束")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
