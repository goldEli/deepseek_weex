#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取WEEX交易所历史计划订单脚本

功能：
- 从环境变量加载API配置
- 初始化WeexClient
- 获取历史计划订单列表
- 格式化显示订单数据
- 支持按时间范围、订单类型筛选
- 支持保存订单数据到文件
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


class OrderDisplay:
    """订单信息显示类"""
    
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
    def format_value(cls, value, decimals=4):
        """格式化数值"""
        try:
            return f"{float(value):.{decimals}f}"
        except (ValueError, TypeError):
            return f"{value}"
    
    @classmethod
    def format_timestamp(cls, timestamp):
        """格式化时间戳为可读时间"""
        try:
            if isinstance(timestamp, str):
                timestamp = int(timestamp)
            # 尝试将毫秒时间戳转换为可读时间
            if len(str(timestamp)) > 10:
                timestamp = timestamp / 1000  # 转换为秒
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "N/A"
    
    @classmethod
    def colorize_order_type(cls, order_type):
        """根据订单类型添加颜色"""
        if "开多" in order_type:
            return cls.colorize(order_type, "green")
        elif "开空" in order_type:
            return cls.colorize(order_type, "red")
        elif "平多" in order_type:
            return cls.colorize(order_type, "blue")
        elif "平空" in order_type:
            return cls.colorize(order_type, "yellow")
        return order_type
    
    @classmethod
    def colorize_status(cls, status):
        """根据订单状态添加颜色"""
        status_map = {
            "触发成功": "green",
            "触发失败": "red",
            "已撤销": "yellow",
            "初始": "blue",
            "暂停": "yellow",
            "未触发": "blue"
        }
        color = status_map.get(status, "")
        return cls.colorize(status, color) if color else status
    
    @classmethod
    def print_separator(cls):
        """打印分隔线"""
        print("=" * 150)
    
    @classmethod
    def print_order_header(cls):
        """打印订单信息表头"""
        headers = [
            "订单ID", "交易对", "订单类型", "价格", 
            "数量", "订单价值", "触发价", "状态", 
            "创建时间", "更新时间"
        ]
        
        # 计算列宽
        col_widths = [15, 15, 10, 12, 10, 15, 12, 10, 20, 20]
        
        # 打印表头
        header_line = "|".join(f"{h:<{w}}".format(h, w) for h, w in zip(headers, col_widths))
        print(f"|{header_line}|")
        
        # 打印表头分隔线
        separator_line = "+".join("-" * w for w in col_widths)
        print(f"+{separator_line}+")
    
    @classmethod
    def print_order_row(cls, order):
        """打印订单信息行"""
        # 格式化数据
        order_id = order.get("order_id", "")[:12] + "..." if len(order.get("order_id", "")) > 12 else order.get("order_id", "")
        symbol = order.get("symbol", "").replace("cmt_", "")
        order_type = cls.colorize_order_type(order.get("order_type", "未知"))
        price = cls.format_value(order.get("price", 0))
        volume = cls.format_value(order.get("volume", 0))
        order_value = cls.format_value(order.get("order_value", 0), 2)
        trigger_price = cls.format_value(order.get("trigger_price", 0))
        status = cls.colorize_status(order.get("status", "未知"))
        create_time = cls.format_timestamp(order.get("create_time"))
        update_time = cls.format_timestamp(order.get("update_time"))
        
        # 计算列宽
        col_widths = [15, 15, 10, 12, 10, 15, 12, 10, 20, 20]
        
        # 打印数据行
        data = [order_id, symbol, order_type, price, volume, order_value, trigger_price, 
                status, create_time, update_time]
        
        # 确保颜色标记不会影响宽度计算
        row_line = "|".join(f"{d:<{w}}".format(d, w) for d, w in zip(data, col_widths))
        print(f"|{row_line}|")
    
    @classmethod
    def print_order_summary(cls, orders):
        """打印订单汇总信息"""
        # 计算总订单数
        total_orders = len(orders)
        
        # 按订单类型统计
        order_types = {}
        for order in orders:
            order_type = order.get("order_type", "未知")
            order_types[order_type] = order_types.get(order_type, 0) + 1
        
        # 按状态统计
        order_status = {}
        for order in orders:
            status = order.get("status", "未知")
            order_status[status] = order_status.get(status, 0) + 1
        
        # 打印汇总信息
        print(f"\n订单汇总:")
        print(f"总订单数量: {total_orders}")
        
        print(f"\n订单类型统计:")
        for order_type, count in order_types.items():
            print(f"  {order_type}: {count}")
        
        print(f"\n订单状态统计:")
        for status, count in order_status.items():
            print(f"  {cls.colorize_status(status)}: {count}")
    
    @classmethod
    def print_detailed_order_info(cls, order):
        """打印详细的订单信息"""
        print(f"\n详细订单信息 - {order.get('order_id', 'N/A')}:")
        for key, value in sorted(order.items()):
            # 格式化时间戳
            if key in ['create_time', 'update_time'] and value:
                value = cls.format_timestamp(value)
            # 格式化数值
            elif key in ['price', 'volume', 'order_value', 'trigger_price']:
                value = cls.format_value(value)
            # 格式化订单类型和状态
            elif key == 'order_type':
                value = cls.colorize_order_type(value)
            elif key == 'status':
                value = cls.colorize_status(value)
            
            print(f"  {key}: {value}")
    
    @classmethod
    def display_orders(cls, orders, verbose=False):
        """显示订单列表"""
        if not orders:
            print(cls.colorize("没有找到历史订单。", "yellow"))
            return
        
        # 打印订单表格
        cls.print_order_header()
        for order in orders:
            cls.print_order_row(order)
        
        # 打印表格底部边框
        cls.print_separator()
        
        # 打印汇总信息
        cls.print_order_summary(orders)
        
        # 如果开启详细模式，显示每个订单的详细信息
        if verbose:
            for order in orders:
                cls.print_detailed_order_info(order)


def save_orders_to_file(orders, filename):
    """
    保存订单数据到文件
    
    Args:
        orders (list): 订单列表
        filename (str): 输出文件名
    """
    import json
    
    try:
        # 准备要保存的数据
        export_data = {
            "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_orders": len(orders),
            "orders": orders
        }
        
        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n订单数据已保存到: {filename}")
    except Exception as e:
        print(f"保存订单数据失败: {str(e)}")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='获取WEEX交易所历史计划订单')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='显示详细的订单信息')
    parser.add_argument('-t', '--testnet', action='store_true', 
                        help='使用测试网络')
    parser.add_argument('-s', '--symbol', type=str, required=True, 
                        help='指定交易对（必需，例如：cmt_btcusdt）')
    parser.add_argument('--start-time', type=str, default=None, 
                        help='开始时间（格式：YYYY-MM-DD HH:MM:SS）')
    parser.add_argument('--end-time', type=str, default=None, 
                        help='结束时间（格式：YYYY-MM-DD HH:MM:SS）')
    parser.add_argument('--order-type', type=int, default=None, choices=[1, 2, 3, 4],
                        help='订单类型: 1: 开多, 2: 开空, 3: 平多, 4: 平空')
    parser.add_argument('--page-size', type=int, default=100,
                        help='每页数量（默认100，最大500）')
    parser.add_argument('--output', type=str, default=None,
                        help='将订单数据保存到指定文件（JSON格式）')
    args = parser.parse_args()
    
    # 从环境变量获取API配置
    api_key = os.getenv('WEEX_API_KEY')
    api_secret = os.getenv('WEEX_SECRET')
    api_passphrase = os.getenv('WEEX_ACCESS_PASSPHRASE')
    
    # 检查环境变量是否设置
    if not all([api_key, api_secret, api_passphrase]):
        print(OrderDisplay.colorize("错误: 未找到API配置，请确保.env文件中有正确的环境变量设置。", "red"))
        print("需要设置的环境变量:")
        print("  WEEX_API_KEY")
        print("  WEEX_SECRET")
        print("  WEEX_ACCESS_PASSPHRASE")
        return 1
    
    def parse_timestamp(time_str):
        """解析时间字符串为时间戳（毫秒）"""
        try:
            if time_str:
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                return int(dt.timestamp() * 1000)  # 转换为毫秒
        except ValueError:
            print(OrderDisplay.colorize(f"无效的时间格式: {time_str}，应为 YYYY-MM-DD HH:MM:SS", "red"))
        return None
    
    # 解析时间参数
    start_time_ms = parse_timestamp(args.start_time)
    end_time_ms = parse_timestamp(args.end_time)
    
    # 订单类型映射
    order_type_map = {
        1: "开多",
        2: "开空",
        3: "平多",
        4: "平空"
    }
    
    try:
        # 初始化WeexClient
        client = WeexClient(api_key, api_secret, api_passphrase, testnet=args.testnet)
        print(f"已初始化WeexClient ({'测试网络' if args.testnet else '主网络'})")

        
        # 构建查询参数信息
        query_info = [f"交易对: {args.symbol}"]
        if start_time_ms:
            query_info.append(f"开始时间: {args.start_time}")
        if end_time_ms:
            query_info.append(f"结束时间: {args.end_time}")
        if args.order_type:
            query_info.append(f"订单类型: {order_type_map[args.order_type]}({args.order_type})")
        query_info.append(f"每页数量: {args.page_size}")
        
        print(f"正在获取历史计划订单...")
        print(f"查询条件: {', '.join(query_info)}")
        
        # 获取历史订单
        result = client.get_order_history(
            symbol=args.symbol,
            start_time=start_time_ms,
            end_time=end_time_ms,
            delegate_type=args.order_type,
            page_size=args.page_size
        )

        
        # 检查是否有错误
        if result.get("error"):
            print(OrderDisplay.colorize(f"获取历史订单失败: {result['error']}", "red"))
            if result.get("error_code"):
                print(f"错误代码: {result['error_code']}")
            return 1
        
        # 获取订单列表
        order_list = result.get("orders", [])
        has_more = result.get("has_more", False)
        
        # 订单类型映射
        order_type_map = {
            1: "开多",
            2: "开空",
            3: "平多",
            4: "平空"
        }
        
        # 订单状态映射
        status_map = {
            0: "初始",
            1: "触发成功",
            2: "触发失败",
            3: "已撤销",
            4: "暂停",
            5: "未触发"
        }
        
        # 格式化每个订单
        orders = []
        try:
            for order in order_list:
                if isinstance(order, dict):
                    formatted_order = {
                        "order_id": order.get("orderId", ""),
                        "symbol": order.get("symbol", ""),
                        "order_type": order_type_map.get(order.get("delegateType"), "未知"),
                        "order_type_code": order.get("delegateType"),
                        "price": float(order.get("price", 0.0)),
                        "volume": float(order.get("volume", 0.0)),
                        "status": status_map.get(order.get("status"), "未知"),
                        "status_code": order.get("status"),
                        "create_time": order.get("createTime"),
                        "update_time": order.get("updateTime"),
                        "trigger_price": float(order.get("triggerPrice", 0.0)),
                        "trigger_type": order.get("triggerType"),
                        "order_source": order.get("source"),
                        "reduce_only": bool(order.get("reduceOnly", False)),
                        # 额外字段，根据API文档添加
                        "client_oid": order.get("client_oid", ""),
                        "filled_qty": float(order.get("filled_qty", 0.0)),
                        "fee": float(order.get("fee", 0.0)),
                        "price_avg": float(order.get("price_avg", 0.0)),
                        "total_profits": float(order.get("totalProfits", 0.0)),
                        "trigger_price_type": order.get("triggerPriceType", ""),
                        "trigger_time": order.get("triggerTime"),
                        "preset_take_profit_price": float(order.get("presetTakeProfitPrice", 0.0)) if order.get("presetTakeProfitPrice") is not None else None,
                        "preset_stop_loss_price": float(order.get("presetStopLossPrice", 0.0)) if order.get("presetStopLossPrice") is not None else None
                    }
                    # 计算订单价值
                    formatted_order["order_value"] = formatted_order["price"] * formatted_order["volume"]
                    orders.append(formatted_order)
        except Exception as e:
            print(f"处理订单数据时发生错误: {str(e)}")
            # 如果格式化出错，使用原始订单数据
            orders = order_list
        
        # 显示当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"查询时间: {current_time}")
        OrderDisplay.print_separator()
        
        # 显示订单信息
        OrderDisplay.display_orders(orders, verbose=args.verbose)
        
        # 显示是否有更多数据
        if has_more:
            print(OrderDisplay.colorize("\n注意: 还有更多历史订单未显示，请调整时间范围或增加page_size参数。", "yellow"))
        
        # 保存到文件（如果指定）
        if args.output:
            save_orders_to_file(orders, args.output)
        
        print(f"\n任务完成!")
        print(f"结束时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断操作")
        return 1
    except Exception as e:
        print(OrderDisplay.colorize(f"获取历史订单时发生错误: {str(e)}", "red"))
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
