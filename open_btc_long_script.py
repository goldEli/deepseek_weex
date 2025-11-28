#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开多BTC脚本 - 使用Weex SDK创建10倍杠杆的BTC多头市价订单
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


def set_leverage(client, symbol, leverage=10):
    """
    设置交易对的杠杆倍数
    使用全仓模式 (margin_mode=1)
    """
    try:
        print(f"正在设置{symbol}的杠杆倍数为{leverage}倍")
        result = client.set_leverage(
            symbol=symbol,
            margin_mode=1,  # 1表示全仓模式
            long_leverage=str(leverage),
            short_leverage=str(leverage)
        )
        
        if result:
            print(f"杠杆设置成功: {result}")
            return True
        else:
            print("杠杆设置失败: 未返回有效结果")
            return False
    except Exception as e:
        print(f"设置杠杆时出错: {str(e)}")
        return False


def open_btc_long(client, symbol, size=0.01):
    """
    创建BTC多头市价订单
    """
    try:
        print(f"正在创建{symbol}多头市价订单，数量: {size}")
        # 使用create_market_order方法创建多头市价订单
        # side='buy'表示买入开多
        order_result = client.create_market_order(
            symbol=symbol,
            side='buy',
            amount=size,
            reduce_only=False  # 开仓订单，不是平仓
        )
        
        if order_result:
            print(f"多头订单创建成功！")
            print(f"订单ID: {order_result.get('id')}")
            print(f"客户端订单ID: {order_result.get('clientOrderId')}")
            print(f"交易对: {order_result.get('symbol')}")
            print(f"方向: {order_result.get('side')}")
            print(f"类型: {order_result.get('type')}")
            print(f"数量: {order_result.get('amount')}")
            return order_result
        else:
            print("多头订单创建失败: 未返回有效结果")
            return None
    except Exception as e:
        print(f"创建多头订单时出错: {str(e)}")
        return None


def check_positions(client, symbol):
    """
    检查当前持仓情况
    """
    try:
        print(f"正在查询{symbol}的持仓情况")
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
            return positions
        else:
            print("未找到持仓信息")
            return []
    except Exception as e:
        print(f"查询持仓时出错: {str(e)}")
        return []


def main():
    """
    主函数
    """
    # 配置参数
    symbol = "cmt_btcusdt"  # BTC/USDT永续合约
    leverage = 10           # 10倍杠杆
    size = 0.01             # 开仓数量
    
    print(f"===== BTC开多脚本开始执行 =====")
    print(f"交易对: {symbol}")
    print(f"杠杆倍数: {leverage}倍")
    print(f"开仓数量: {size} BTC")
    print("==============================")
    
    # 步骤1: 加载环境变量
    api_key, api_secret, api_passphrase = load_environment_variables()
    
    # 步骤2: 初始化客户端
    client = initialize_client(api_key, api_secret, api_passphrase)
    
    # 步骤3: 设置杠杆
    if not set_leverage(client, symbol, leverage):
        print("杠杆设置失败，脚本终止")
        sys.exit(1)
    
    # 步骤4: 开多
    order_result = open_btc_long(client, symbol, size)
    if not order_result:
        print("开多失败，脚本终止")
        sys.exit(1)
    
    # 步骤5: 检查持仓
    print("\n===== 开仓后持仓情况 =====")
    check_positions(client, symbol)
    
    print("\n===== 脚本执行完成 =====")


if __name__ == "__main__":
    main()
