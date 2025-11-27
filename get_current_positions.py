#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取WEEX交易所当前持仓信息脚本

功能：
- 从环境变量加载API配置
- 初始化WeexClient
- 获取当前持仓信息
- 格式化显示持仓数据
- 支持彩色标记盈亏
- 支持详细模式和测试网络
"""

import os
import sys
import argparse
from datetime import datetime

# 尝试从.env文件加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入WeexClient类
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from weex_sdk import WeexClient


class PositionDisplay:
    """持仓信息显示类"""
    
    # ANSI颜色代码
    COLORS = {
        'reset': '\033[0m',
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'bold': '\033[1m',
    }
    
    @classmethod
    def colorize(cls, text, color):
        """给文本添加颜色"""
        if not sys.stdout.isatty():
            return text  # 非终端环境不使用颜色
        return f"{cls.COLORS.get(color, '')}{text}{cls.COLORS['reset']}"
    
    @classmethod
    def format_position_value(cls, value, decimals=4):
        """格式化数值"""
        try:
            return f"{float(value):.{decimals}f}"
        except (ValueError, TypeError):
            return f"{value}"
    
    @classmethod
    def format_pnl(cls, pnl):
        """格式化盈亏并添加颜色"""
        try:
            pnl_float = float(pnl)
            if pnl_float > 0:
                return cls.colorize(f"+{pnl_float:.4f}", 'green')
            elif pnl_float < 0:
                return cls.colorize(f"{pnl_float:.4f}", 'red')
            else:
                return "0.0000"
        except (ValueError, TypeError):
            return f"{pnl}"
    
    @classmethod
    def format_pnl_percentage(cls, pnl, entry_price, size):
        """计算并格式化盈亏百分比"""
        try:
            pnl_float = float(pnl)
            entry_price_float = float(entry_price)
            size_float = float(size)
            
            if entry_price_float > 0 and size_float > 0:
                # 计算成本
                cost = entry_price_float * size_float
                if cost > 0:
                    percentage = (pnl_float / cost) * 100
                    if percentage > 0:
                        return cls.colorize(f"+{percentage:.2f}%", 'green')
                    elif percentage < 0:
                        return cls.colorize(f"{percentage:.2f}%", 'red')
                    else:
                        return "0.00%"
        except (ValueError, TypeError, ZeroDivisionError):
            pass
        return "0.00%"
    
    @classmethod
    def print_separator(cls):
        """打印分隔线"""
        print("=" * 120)
    
    @classmethod
    def print_position_header(cls):
        """打印持仓信息表头"""
        headers = [
            "交易对", "方向", "持仓量", "入场价", 
            "杠杆倍数", "未实现盈亏", "盈亏百分比", 
            "强平价格", "保证金模式", "更新时间"
        ]
        
        # 计算列宽
        col_widths = [len(h) for h in headers]
        col_widths[0] = max(col_widths[0], 15)  # 交易对列宽
        col_widths[1] = max(col_widths[1], 8)   # 方向列宽
        col_widths[2] = max(col_widths[2], 10)  # 持仓量列宽
        col_widths[3] = max(col_widths[3], 12)  # 入场价列宽
        col_widths[4] = max(col_widths[4], 8)   # 杠杆倍数列宽
        col_widths[5] = max(col_widths[5], 12)  # 未实现盈亏列宽
        col_widths[6] = max(col_widths[6], 12)  # 盈亏百分比列宽
        col_widths[7] = max(col_widths[7], 12)  # 强平价格列宽
        col_widths[8] = max(col_widths[8], 12)  # 保证金模式列宽
        col_widths[9] = max(col_widths[9], 16)  # 更新时间列宽
        
        # 打印表头
        header_line = "|".join(f"{h:<{w}}".format(h, w) for h, w in zip(headers, col_widths))
        print(f"|{header_line}|")
        
        # 打印表头分隔线
        separator_line = "+".join("-" * w for w in col_widths)
        print(f"+{separator_line}+")
    
    @classmethod
    def print_position_row(cls, position):
        """打印持仓信息行"""
        # 格式化数据
        symbol = position.get("symbol", "").replace("cmt_", "")
        side = cls.colorize("做多" if position.get("side") == "long" else "做空", 
                          "green" if position.get("side") == "long" else "red")
        size = cls.format_position_value(position.get("size", 0))
        entry_price = cls.format_position_value(position.get("entryPrice", 0))
        leverage = cls.format_position_value(position.get("leverage", 1), 2)
        unrealized_pnl = position.get("unrealizedPnl", 0)
        pnl_formatted = cls.format_pnl(unrealized_pnl)
        pnl_percentage = cls.format_pnl_percentage(
            unrealized_pnl, 
            position.get("entryPrice", 0), 
            position.get("size", 0)
        )
        liquidation_price = cls.format_position_value(position.get("liquidationPrice", 0))
        margin_mode = "逐仓" if position.get("marginMode") == "isolated" else "全仓"
        
        # 格式化时间戳
        timestamp = position.get("timestamp", 0)
        try:
            # 尝试将毫秒时间戳转换为可读时间
            if len(str(timestamp)) > 10:
                timestamp = timestamp / 1000  # 转换为秒
            update_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except:
            update_time = "N/A"
        
        # 计算列宽
        col_widths = [15, 8, 10, 12, 8, 12, 12, 12, 12, 16]
        
        # 打印数据行
        data = [symbol, side, size, entry_price, leverage, pnl_formatted, pnl_percentage, 
                liquidation_price, margin_mode, update_time]
        
        # 确保颜色标记不会影响宽度计算
        row_line = "|".join(f"{d:<{w}}".format(d, w) for d, w in zip(data, col_widths))
        print(f"|{row_line}|")
    
    @classmethod
    def print_position_summary(cls, positions):
        """打印持仓汇总信息"""
        # 计算总持仓数和总盈亏
        total_positions = len(positions)
        total_pnl = sum(float(p.get("unrealizedPnl", 0)) for p in positions)
        
        # 计算多头和空头持仓数
        long_positions = sum(1 for p in positions if p.get("side") == "long")
        short_positions = sum(1 for p in positions if p.get("side") == "short")
        
        # 打印汇总信息
        print(f"\n持仓汇总:")
        print(f"总持仓数量: {total_positions}")
        print(f"多头持仓: {long_positions}")
        print(f"空头持仓: {short_positions}")
        print(f"总未实现盈亏: {cls.format_pnl(total_pnl)}")
    
    @classmethod
    def print_detailed_position_info(cls, position):
        """打印详细的持仓信息"""
        print(f"\n详细持仓信息 - {position.get('symbol', '').replace('cmt_', '')}:")
        for key, value in position.items():
            if key != 'info':  # 跳过原始信息，单独显示
                print(f"  {key}: {value}")
        
        # 显示原始信息
        if 'info' in position:
            print(f"  原始API数据:")
            for k, v in position['info'].items():
                print(f"    {k}: {v}")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='获取WEEX交易所当前持仓信息')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='显示详细的持仓信息')
    parser.add_argument('-t', '--testnet', action='store_true', 
                        help='使用测试网络')
    parser.add_argument('-s', '--symbol', type=str, default=None, 
                        help='指定交易对，不指定则获取所有持仓')
    args = parser.parse_args()
    
    # 从环境变量获取API配置
    api_key = os.getenv('WEEX_API_KEY')
    api_secret = os.getenv('WEEX_SECRET')
    api_passphrase = os.getenv('WEEX_ACCESS_PASSPHRASE')
    
    # 检查环境变量是否设置
    if not all([api_key, api_secret, api_passphrase]):
        print(PositionDisplay.colorize("错误: 未找到API配置，请确保.env文件中有正确的环境变量设置。", "red"))
        print("需要设置的环境变量:")
        print("  WEEX_API_KEY")
        print("  WEEX_SECRET")
        print("  WEEX_ACCESS_PASSPHRASE")
        return 1
    
    try:
        # 初始化WeexClient
        client = WeexClient(api_key, api_secret, api_passphrase, testnet=args.testnet)
        print(f"已初始化WeexClient ({'测试网络' if args.testnet else '主网络'})")
        
        # 获取持仓信息
        print(f"正在获取持仓信息{'' if args.symbol is None else f'，交易对: {args.symbol}'}...")
        positions = client.fetch_positions(symbol=args.symbol)
        
        # 显示当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"查询时间: {current_time}")
        PositionDisplay.print_separator()
        
        if not positions:
            print(PositionDisplay.colorize("当前没有持仓。", "yellow"))
            return 0
        
        # 打印持仓信息表格
        PositionDisplay.print_position_header()
        for position in positions:
            PositionDisplay.print_position_row(position)
        
        # 打印表格底部边框
        PositionDisplay.print_separator()
        
        # 打印汇总信息
        PositionDisplay.print_position_summary(positions)
        
        # 如果开启详细模式，显示每个持仓的详细信息
        if args.verbose:
            for position in positions:
                PositionDisplay.print_detailed_position_info(position)
        
        return 0
        
    except Exception as e:
        print(PositionDisplay.colorize(f"获取持仓信息时发生错误: {str(e)}", "red"))
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
