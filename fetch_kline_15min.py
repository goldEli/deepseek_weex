#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取15分钟K线数据脚本 - 使用Weex SDK获取BTC/USDT的15分钟K线数据
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# 导入Weex SDK
from weex_sdk import WeexClient


def load_environment_variables():
    """
    加载环境变量并验证必要的API密钥
    注意：获取K线数据是公开API，理论上不需要API密钥
    但为了保持与SDK初始化一致，我们仍然读取环境变量
    """
    # 尝试从.env文件加载环境变量
    load_dotenv()
    
    # 读取API密钥（即使不需要，也保持SDK初始化的一致性）
    api_key = os.getenv('WEEX_API_KEY') or 'dummy_key'
    api_secret = os.getenv('WEEX_API_SECRET') or os.getenv('WEEX_SECRET') or 'dummy_secret'
    api_passphrase = os.getenv('WEEX_ACCESS_PASSPHRASE') or 'dummy_passphrase'
    
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


def fetch_15min_kline(client, symbol, limit=10):
    """
    获取指定交易对的15分钟K线数据
    """
    try:
        print(f"正在获取{symbol}的15分钟K线数据，限制{limit}条")
        # 使用fetch_ohlcv方法，timeframe设置为'15m'表示15分钟
        ohlcv_data = client.fetch_ohlcv(
            symbol=symbol,
            timeframe='15m',  # 15分钟K线
            limit=limit       # 限制返回10条数据
        )
        
        return ohlcv_data
    except Exception as e:
        print(f"获取K线数据时出错: {str(e)}")
        return []


def format_kline_data(ohlcv_data):
    """
    格式化K线数据，使其更易于阅读，并添加涨跌标识
    """
    if not ohlcv_data:
        print("没有获取到K线数据")
        return
    
    print(f"\n===== 共获取到{len(ohlcv_data)}条15分钟K线数据 =====")
    print("=" * 120)
    print(f"{'时间':<20} {'开盘价':>10} {'最高价':>10} {'最低价':>10} {'收盘价':>10} {'涨跌':>8} {'成交量':>15}")
    print("=" * 120)
    
    # 按时间戳降序排序（最新的数据在前）
    sorted_data = sorted(ohlcv_data, key=lambda x: x[0], reverse=True)
    
    for candle in sorted_data:
        timestamp, open_price, high_price, low_price, close_price, volume = candle
        # 转换时间戳为可读格式
        dt = datetime.fromtimestamp(timestamp / 1000)  # 转换为秒级时间戳
        time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 计算涨跌标识
        if close_price > open_price:
            trend = "涨"
        elif close_price < open_price:
            trend = "跌"
        else:
            trend = "平"
        
        # 打印格式化的数据行
        print(f"{time_str:<20} {open_price:>10.2f} {high_price:>10.2f} {low_price:>10.2f} {close_price:>10.2f} {trend:>8} {volume:>15.2f}")
    
    print("=" * 120)
    
    # 计算简单统计信息
    if len(ohlcv_data) > 0:
        # 获取最新的K线
        latest_candle = sorted_data[0]
        timestamp, open_price, high_price, low_price, close_price, volume = latest_candle
        
        # 计算K线内涨跌标识
        if close_price > open_price:
            candle_trend = "涨"
        elif close_price < open_price:
            candle_trend = "跌"
        else:
            candle_trend = "平"
        
        # 计算涨跌幅
        if len(sorted_data) > 1:
            prev_close = sorted_data[1][4]  # 上一根K线的收盘价
            change = close_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
        else:
            change = 0
            change_percent = 0
        
        print(f"\n最新K线信息:")
        print(f"时间: {datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"开盘价: {open_price:.2f}")
        print(f"最高价: {high_price:.2f}")
        print(f"最低价: {low_price:.2f}")
        print(f"收盘价: {close_price:.2f}")
        print(f"K线涨跌: {candle_trend}")
        print(f"涨跌幅: {change:.2f} ({change_percent:.2f}%)")
        print(f"成交量: {volume:.2f}")





def main():
    """
    主函数
    """
    # 配置参数
    symbol = "cmt_btcusdt"  # BTC/USDT永续合约
    limit = 10              # 获取10条数据
    
    print(f"===== 获取{symbol} 15分钟K线数据脚本开始执行 =====")
    print(f"交易对: {symbol}")
    print(f"K线周期: 15分钟")
    print(f"数据条数: {limit}")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==============================")
    
    try:
        # 步骤1: 加载环境变量
        api_key, api_secret, api_passphrase = load_environment_variables()
        
        # 步骤2: 初始化客户端
        client = initialize_client(api_key, api_secret, api_passphrase)
        
        # 步骤3: 获取K线数据
        ohlcv_data = fetch_15min_kline(client, symbol, limit)
        
        # 步骤4: 格式化输出
        if ohlcv_data:
            format_kline_data(ohlcv_data)
            

        else:
            print("未获取到K线数据，脚本终止")
            return 1
        
        print("\n===== 脚本执行完成 =====")
        return 0
        
    except KeyboardInterrupt:
        print("\n脚本被用户中断")
        return 1
    except Exception as e:
        print(f"\n脚本执行过程中发生错误: {str(e)}")
        import traceback
        print("详细错误信息:")
        traceback.print_exc()
        return 1
    finally:
        print("\n脚本已退出")


if __name__ == "__main__":
    sys.exit(main())
