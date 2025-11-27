#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取Weex历史订单脚本
基于client.get_order_history()方法
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 添加当前目录到Python路径，确保能导入weex_sdk
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from weex_sdk import WeexClient


def initialize_client():
    """
    初始化WeexClient客户端
    
    Returns:
        WeexClient: 初始化后的客户端实例，如果失败则返回None
    """
    try:
        # 加载环境变量
        print("[INFO] 正在加载环境变量...")
        load_dotenv()
        
        # 检查必要的环境变量
        api_key = os.environ.get("WEEX_API_KEY")
        api_secret = os.environ.get("WEEX_SECRET")
        api_passphrase = os.environ.get("WEEX_ACCESS_PASSPHRASE")
        
        if not all([api_key, api_secret, api_passphrase]):
            print("[ERROR] 缺少必要的API凭证环境变量！")
            print("[ERROR] 请确保.env文件中设置了以下环境变量：")
            print("[ERROR] - WEEX_API_KEY")
            print("[ERROR] - WEEX_SECRET")
            print("[ERROR] - WEEX_ACCESS_PASSPHRASE")
            return None
        
        # 初始化客户端
        print("[INFO] 正在初始化WeexClient...")
        client = WeexClient(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase
        )
        
        print("[INFO] 客户端初始化成功")
        return client
        
    except Exception as e:
        print(f"[ERROR] 初始化客户端时出错: {str(e)}")
        return None


def format_order_data(order):
    """
    格式化订单数据，使其更易读
    
    Args:
        order (dict): 原始订单数据
        
    Returns:
        dict: 格式化后的订单数据
    """
    try:
        # 尝试获取并格式化时间
        create_time = order.get('createTime', '')
        if create_time:
            try:
                # 假设时间戳是毫秒级
                timestamp = int(create_time) / 1000 if len(create_time) > 10 else int(create_time)
                create_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        # 订单状态映射
        status_map = {
            '0': '待成交',
            '1': '部分成交',
            '2': '已成交',
            '3': '已取消',
            '4': '部分成交已取消'
        }
        
        # 订单类型映射
        type_map = {
            '1': '开多',
            '2': '开空',
            '3': '平多',
            '4': '平空'
        }
        
        formatted = {
            '订单ID': order.get('order_id', 'N/A'),
            '交易对': order.get('symbol', 'N/A'),
            '创建时间': create_time,
            '订单类型': type_map.get(order.get('type', ''), order.get('type', 'N/A')),
            '订单状态': status_map.get(order.get('status', ''), order.get('status', 'N/A')),
            '订单数量': order.get('size', 'N/A'),
            '已成交数量': order.get('filled_qty', 'N/A'),
            '订单价格': order.get('price', 'N/A'),
            '平均成交价': order.get('price_avg', 'N/A'),
            '交易费用': order.get('fee', 'N/A'),
            '总盈亏': order.get('totalProfits', 'N/A')
        }
        
        return formatted
    except Exception as e:
        print(f"[ERROR] 格式化订单数据时出错: {str(e)}")
        return order


def display_orders(orders, verbose=False):
    """
    展示订单数据
    
    Args:
        orders (list): 订单列表
        verbose (bool): 是否显示详细信息
    """
    if not orders:
        print("[INFO] 未获取到任何历史订单")
        return
    
    print(f"\n[INFO] 成功获取到 {len(orders)} 条历史订单")
    
    # 显示摘要信息
    print("\n[INFO] 订单摘要:")
    print("-" * 100)
    print(f"{'订单ID':<20} {'交易对':<15} {'类型':<8} {'状态':<10} {'数量':<10} {'价格':<15} {'创建时间':<20}")
    print("-" * 100)
    
    for order in orders[:10]:  # 只显示前10条的摘要
        formatted = format_order_data(order)
        print(f"{formatted['订单ID'][:18]:<20} {formatted['交易对']:<15} {formatted['订单类型']:<8} "
              f"{formatted['订单状态']:<10} {formatted['订单数量']:<10} {formatted['订单价格']:<15} "
              f"{formatted['创建时间']:<20}")
    
    if len(orders) > 10:
        print(f"... 还有 {len(orders) - 10} 条订单未显示")
    
    print("-" * 100)
    
    # 如果需要详细信息，显示前3条订单的详细信息
    if verbose and orders:
        print("\n[INFO] 前3条订单的详细信息:")
        for i, order in enumerate(orders[:3], 1):
            print(f"\n订单 {i}:")
            formatted = format_order_data(order)
            for key, value in formatted.items():
                print(f"  {key}: {value}")


def fetch_order_history(client, symbol=None, page_size=10, create_date=None):
    """
    获取历史订单
    
    Args:
        client (WeexClient): WeexClient实例
        symbol (str): 交易对
        page_size (int): 每页数量
        create_date (int): 天数
        
    Returns:
        list: 订单列表
    """
    try:
        print(f"\n[INFO] 正在获取历史订单...")
        print(f"[INFO] 参数: symbol={symbol}, page_size={page_size}, create_date={create_date}")
        
        # 调用API获取订单
        orders = client.get_order_history(
            symbol=symbol,
            page_size=page_size,
            create_date=create_date
        )
        
        return orders
    except Exception as e:
        print(f"[ERROR] 获取历史订单时出错: {str(e)}")
        return []


def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description='获取Weex交易所历史订单')
    
    parser.add_argument('-s', '--symbol', type=str, help='交易对，例如 cmt_btcusdt')
    parser.add_argument('-p', '--page-size', type=int, default=10, help='每页数量，默认为10')
    parser.add_argument('-d', '--days', type=int, help='获取最近多少天的订单，最大90天')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('-o', '--output', type=str, help='输出文件路径，将订单保存为JSON文件')
    
    return parser.parse_args()


def save_orders_to_file(orders, file_path):
    """
    保存订单到文件
    
    Args:
        orders (list): 订单列表
        file_path (str): 文件路径
    """
    try:
        import json
        
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 订单数据已保存到: {file_path}")
        return True
    except Exception as e:
        print(f"[ERROR] 保存订单到文件时出错: {str(e)}")
        return False


def main():
    """
    主函数
    """
    print("===== Weex历史订单获取工具 =====")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 验证参数
        if args.days is not None:
            if args.days < 0:
                print("[ERROR] 天数不能为负数")
                return 1
            if args.days > 90:
                print("[ERROR] 天数不能超过90天")
                return 1
        
        # 初始化客户端
        client = initialize_client()
        if not client:
            return 1
        
        # 获取历史订单
        orders = fetch_order_history(
            client=client,
            symbol=args.symbol,
            page_size=args.page_size,
            create_date=args.days
        )
        
        # 显示订单信息
        display_orders(orders, verbose=args.verbose)
        
        # 保存到文件（如果指定）
        if args.output:
            save_orders_to_file(orders, args.output)
        
        print(f"\n[INFO] 任务完成!")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return 0
        
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断操作")
        return 1
    except Exception as e:
        print(f"\n[ERROR] 程序运行时出错: {str(e)}")
        import traceback
        print(f"[ERROR] 错误堆栈: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
