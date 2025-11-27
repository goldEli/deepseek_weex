#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取账户资产信息脚本
基于WEEX SDK的get_account_assets方法
"""

import os
import sys
from datetime import datetime
from weex_sdk import WeexClient
# 尝试从.env文件加载环境变量
from dotenv import load_dotenv
load_dotenv()


def format_assets_data(assets):
    """
    格式化资产数据，使其更易读
    
    Args:
        assets (list): 资产列表
    
    Returns:
        list: 格式化后的资产列表
    """
    formatted_assets = []
    
    for asset in assets:
        # 确保资产是字典类型
        if not isinstance(asset, dict):
            continue
        
        # 提取必要字段，提供默认值
        formatted_asset = {
            '币种名称': asset.get('coinName', '未知'),
            '币种ID': asset.get('coinId', 'N/A'),
            '可用余额': float(asset.get('available', 0)),
            '冻结余额': float(asset.get('frozen', 0)),
            '总权益': float(asset.get('equity', 0)),
            '未实现盈亏': float(asset.get('unrealizePnl', 0))
        }
        
        formatted_assets.append(formatted_asset)
    
    return formatted_assets


def display_assets(assets, verbose=False):
    """
    显示资产信息
    
    Args:
        assets (list): 格式化后的资产列表
        verbose (bool): 是否显示详细信息
    """
    if not assets:
        print("未获取到资产信息")
        return
    
    print(f"\n{'=' * 80}")
    print(f"账户资产信息 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}")
    
    # 显示表头
    print(f"{'币种名称':<10}{'可用余额':>15}{'冻结余额':>15}{'总权益':>15}{'未实现盈亏':>15}")
    print(f"{'-' * 80}")
    
    # 显示每个资产的信息
    for asset in assets:
        # 计算盈亏颜色标记
        pnl = asset['未实现盈亏']
        pnl_str = f"{pnl:>15.8f}"
        if pnl > 0:
            pnl_str = f"\033[92m{pnl_str}\033[0m"  # 绿色表示盈利
        elif pnl < 0:
            pnl_str = f"\033[91m{pnl_str}\033[0m"  # 红色表示亏损
        
        print(f"{asset['币种名称']:<10}"\
              f"{asset['可用余额']:>15.8f}"\
              f"{asset['冻结余额']:>15.8f}"\
              f"{asset['总权益']:>15.8f}"\
              f"{pnl_str}")
    
    print(f"{'=' * 80}")
    
    # 如果是详细模式，显示更多信息
    if verbose:
        print("\n详细资产信息:")
        print(f"{'-' * 80}")
        for asset in assets:
            print(f"币种: {asset['币种名称']} ({asset['币种ID']})")
            print(f"  可用余额: {asset['可用余额']}")
            print(f"  冻结余额: {asset['冻结余额']}")
            print(f"  总权益: {asset['总权益']}")
            print(f"  未实现盈亏: {asset['未实现盈亏']}")
            print(f"{'-' * 80}")


def get_account_assets(client, verbose=False):
    """
    获取并显示账户资产信息
    
    Args:
        client: WeexClient实例
        verbose (bool): 是否显示详细信息
    """
    try:
        print("正在获取账户资产信息...")
        # 调用SDK的get_account_assets方法
        assets = client.get_account_assets()
        
        if not assets:
            print("未获取到任何资产信息")
            return False
        
        # 格式化资产数据
        formatted_assets = format_assets_data(assets)
        
        # 按币种名称排序
        formatted_assets.sort(key=lambda x: x['币种名称'])
        
        # 显示资产信息
        display_assets(formatted_assets, verbose)
        
        return True
        
    except Exception as e:
        print(f"获取账户资产时发生错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return False


def main():
    """
    主函数
    """
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='获取WEEX交易所账户资产信息')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细资产信息')
    parser.add_argument('--testnet', action='store_true', help='使用测试网络')
    args = parser.parse_args()
    
    # 获取环境变量
    api_key = os.getenv('WEEX_API_KEY')
    api_secret = os.getenv('WEEX_SECRET')
    api_passphrase = os.getenv('WEEX_ACCESS_PASSPHRASE')
    
    # 检查环境变量是否存在
    if not all([api_key, api_secret, api_passphrase]):
        print("错误: 未找到必要的环境变量")
        print("请确保在.env文件中设置了以下环境变量:")
        print("  WEEX_API_KEY")
        print("  WEEX_SECRET")
        print("  WEEX_ACCESS_PASSPHRASE")
        return 1
    
    try:
        # 初始化WeexClient
        print(f"正在初始化WeexClient...{'(测试网络)' if args.testnet else ''}")
        client = WeexClient(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
            testnet=args.testnet
        )
        
        # 获取账户资产
        success = get_account_assets(client, args.verbose)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 130
    except Exception as e:
        print(f"发生未预期的错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
