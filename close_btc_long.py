#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平多BTC脚本 - 使用Weex SDK创建市价平仓订单
"""

import os
import sys
from dotenv import load_dotenv

# 导入Weex SDK
from weex_sdk import WeexClient


def load_environment_variables():
    """
    加载环境变量并验证必要的API密钥
    """
    # 尝试从.env文件加载环境变量
    load_dotenv()
    
    # 读取API密钥
    api_key = os.getenv('WEEX_API_KEY')
    api_secret = os.getenv('WEEX_API_SECRET') or os.getenv('WEEX_SECRET')
    api_passphrase = os.getenv('WEEX_ACCESS_PASSPHRASE')
    
    # 验证必要的API密钥
    if not all([api_key, api_secret, api_passphrase]):
        missing = []
        if not api_key:
            missing.append('WEEX_API_KEY')
        if not api_secret:
            missing.append('WEEX_API_SECRET/WEEX_SECRET')
        if not api_passphrase:
            missing.append('WEEX_ACCESS_PASSPHRASE')
        
        print(f"错误: 缺少必要的环境变量: {', '.join(missing)}")
        print("请确保.env文件中包含这些变量，或者直接设置到系统环境变量中")
        sys.exit(1)
    
    return api_key, api_secret, api_passphrase


def initialize_client(api_key, api_secret, api_passphrase):
    """
    初始化WeexClient
    """
    try:
        client = WeexClient(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
            testnet=False
        )
        print("WeexClient初始化成功")
        return client
    except Exception as e:
        print(f"WeexClient初始化失败: {str(e)}")
        sys.exit(1)


def get_long_position(client, symbol):
    """
    查询指定交易对的多头持仓
    """
    try:
        print(f"正在查询{symbol}的多头持仓情况")
        positions = client.fetch_positions(symbol=symbol)
        
        if not positions:
            print(f"未找到{symbol}的持仓信息")
            return None
        
        # 查找多头持仓
        for pos in positions:
            if pos.get('side') == 'long' and float(pos.get('size', 0)) > 0:
                print(f"找到多头持仓：")
                print(f"持仓数量: {pos.get('size')}")
                print(f"入场价格: {pos.get('entryPrice')}")
                print(f"杠杆倍数: {pos.get('leverage')}")
                print(f"未实现盈亏: {pos.get('unrealizedPnl')}")
                return pos
        
        print(f"未找到{symbol}的多头持仓")
        return None
    except Exception as e:
        print(f"查询持仓时出错: {str(e)}")
        return None


def close_long_position(client, symbol, size):
    """
    卖出平多，使用市价单
    """
    try:
        print(f"正在创建{symbol}市价平仓订单，数量: {size}")
        # 使用create_market_order方法创建空头市价订单
        # side='sell'表示卖出，reduce_only=True表示平仓
        order_result = client.create_market_order(
            symbol=symbol,
            side='sell',
            amount=size,
            reduce_only=True  # 平仓订单
        )
        
        # 验证订单结果
        if not order_result:
            print("错误: 平仓订单创建失败: 未返回有效结果")
            return None
        
        # 检查是否包含订单ID
        if not order_result.get('id'):
            print(f"错误: 订单创建响应中缺少订单ID: {order_result}")
            return None
        
        # 验证订单参数是否正确
        if order_result.get('symbol') != symbol:
            print(f"警告: 订单交易对不匹配: 预期{symbol}, 实际{order_result.get('symbol')}")
        
        if order_result.get('side') != 'sell':
            print(f"警告: 订单方向不匹配: 预期sell, 实际{order_result.get('side')}")
        
        # 输出订单详情
        print(f"平仓订单创建成功！")
        print(f"订单ID: {order_result.get('id')}")
        print(f"客户端订单ID: {order_result.get('clientOrderId')}")
        print(f"交易对: {order_result.get('symbol')}")
        print(f"方向: {order_result.get('side')}")
        print(f"类型: {order_result.get('type')}")
        print(f"数量: {order_result.get('amount')}")
        print(f"状态: {order_result.get('status')}")
        
        # 检查订单状态
        if order_result.get('status') in ['rejected', 'canceled', 'failed']:
            print(f"警告: 订单状态异常: {order_result.get('status')}")
            print(f"错误原因: {order_result.get('reason', '未知')}")
            return None
        
        return order_result
    except ValueError as e:
        print(f"参数错误: {str(e)}")
        return None
    except ConnectionError as e:
        print(f"网络连接错误: {str(e)}")
        return None
    except Exception as e:
        print(f"创建平仓订单时出错: {str(e)}")
        # 尝试获取更多错误信息
        import traceback
        print("详细错误信息:")
        traceback.print_exc()
        return None


def check_positions_after_close(client, symbol):
    """
    平仓后检查持仓情况
    """
    try:
        print(f"\n===== 平仓后持仓情况 =====")
        positions = client.fetch_positions(symbol=symbol)
        
        if positions:
            print(f"找到{len(positions)}个持仓")
            for pos in positions:
                print(f"持仓方向: {pos.get('side')}")
                print(f"持仓数量: {pos.get('size')}")
                print(f"入场价格: {pos.get('entryPrice')}")
                print(f"杠杆倍数: {pos.get('leverage')}")
                print(f"未实现盈亏: {pos.get('unrealizedPnl')}")
                print(f"平仓价格: {pos.get('liquidationPrice')}")
                print(f"保证金模式: {pos.get('marginMode')}")
                print("---")
        else:
            print("未找到持仓信息")
    except Exception as e:
        print(f"查询持仓时出错: {str(e)}")


def main():
    """
    主函数
    """
    # 配置参数
    symbol = "cmt_btcusdt"  # BTC/USDT永续合约
    
    print(f"===== BTC平多脚本开始执行 =====")
    print(f"交易对: {symbol}")
    print("==============================")
    
    try:
        # 步骤1: 加载环境变量
        api_key, api_secret, api_passphrase = load_environment_variables()
        
        # 步骤2: 初始化客户端
        client = initialize_client(api_key, api_secret, api_passphrase)
        
        # 步骤3: 查询多头持仓
        long_position = get_long_position(client, symbol)
        if not long_position:
            print("未找到可平的多头持仓，脚本终止")
            sys.exit(1)
        
        # 验证持仓大小
        position_size = float(long_position.get('size', 0))
        if position_size <= 0:
            print(f"错误: 持仓数量无效: {position_size}")
            sys.exit(1)
        
        # 步骤4: 平仓
        order_result = close_long_position(client, symbol, position_size)
        if not order_result:
            print("平仓失败，脚本终止")
            sys.exit(1)
        
        # 延迟一下再检查持仓，确保订单已经处理完成
        import time
        print("\n等待3秒，确保订单处理完成...")
        time.sleep(3)
        
        # 步骤5: 检查持仓
        check_positions_after_close(client, symbol)
        
        print("\n===== 脚本执行完成 =====")
        return 0
        
    except KeyboardInterrupt:
        print("\n脚本被用户中断")
        return 1
    except Exception as e:
        print(f"\n脚本执行过程中发生未预期错误: {str(e)}")
        import traceback
        print("详细错误堆栈:")
        traceback.print_exc()
        return 1
    finally:
        print("\n脚本已退出")


if __name__ == "__main__":
    sys.exit(main())


if __name__ == "__main__":
    main()
