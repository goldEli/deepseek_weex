import os
import time
from dotenv import load_dotenv
from weex_sdk import WeexClient

# 加载环境变量
load_dotenv()

# 从环境变量获取API凭证
api_key = os.getenv('WEEX_API_KEY')
api_secret = os.getenv('WEEX_API_SECRET') or os.getenv('WEEX_SECRET')
api_passphrase = os.getenv('WEEX_ACCESS_PASSPHRASE')

def query_history_orders(symbol=None, page_size=10, create_days=7):
    """
    查询历史订单的简单函数
    
    Args:
        symbol (str, optional): 交易对，例如 "cmt_btcusdt"
        page_size (int, optional): 每页数量
        create_days (int, optional): 查询最近几天的订单（1-90天）
    
    Returns:
        dict: 订单历史信息
    """
    # 将天数转换为时间戳（毫秒）
    # 计算N天前的时间戳
    current_timestamp_ms = int(time.time() * 1000)
    days_in_ms = create_days * 24 * 60 * 60 * 1000
    create_timestamp = current_timestamp_ms - days_in_ms
    # 初始化客户端
    client = WeexClient(api_key, api_secret, api_passphrase)
    
    print(f"开始查询历史订单...")
    print(f"参数: symbol={symbol if symbol else '全部'}, page_size={page_size}, 查询最近{create_days}天的订单")
    print(f"时间戳: {create_timestamp}")
    
    # 调用get_history_orders方法，传入时间戳
    result = client.get_history_orders(symbol=symbol, page_size=page_size, create_date=create_timestamp)
    
    # 处理结果
    orders = result.get('orders', [])
    
    if 'error' in result:
        print(f"\n查询失败!")
        print(f"错误信息: {result['error']}")
        print(f"错误代码: {result['error_code']}")
    else:
        print(f"\n查询成功!")
        print(f"共获取到 {len(orders)} 条历史订单")
        
        # 打印订单详情
        if orders:
            print(f"\n订单详情:")
            print("-" * 100)
            print(f"{'订单ID':<25} {'交易对':<15} {'价格':<12} {'数量':<12} {'状态':<12} {'类型':<15} {'时间'}")
            print("-" * 100)
            
            for order in orders:
                order_id = order.get('order_id', 'N/A')
                symbol = order.get('symbol', 'N/A')
                price = order.get('price', '0')
                size = order.get('size', '0')
                status = order.get('status', 'N/A')
                order_type = order.get('type', 'N/A')
                create_time = order.get('createTime', 'N/A')
                
                print(f"{order_id:<25} {symbol:<15} {price:<12} {size:<12} {status:<12} {order_type:<15} {create_time}")
            print("-" * 100)
    
    return result

if __name__ == "__main__":
    # 默认查询BTC/USDT最近7天的历史订单
    print("===== Weex历史订单查询工具 =====\n")
    
    # 提供几个示例查询选项
    print("1. 查询BTC/USDT最近7天的历史订单")
    print("2. 查询全部交易对最近1天的历史订单")
    print("3. 自定义查询参数")
    
    choice = input("\n请选择查询类型 (1-3): ").strip()
    
    if choice == "1":
        query_history_orders(symbol="cmt_btcusdt", page_size=10, create_days=7)
    elif choice == "2":
        query_history_orders(symbol=None, page_size=20, create_days=1)
    elif choice == "3":
        symbol = input("请输入交易对 (留空表示全部): ").strip() or None
        try:
            page_size = int(input("请输入每页数量 (默认10): ").strip() or "10")
            create_days = int(input("请输入查询天数 (1-90, 默认7): ").strip() or "7")
            # 验证天数范围
            if create_days < 1 or create_days > 90:
                print("天数必须在1-90之间，将使用默认值7")
                create_days = 7
            query_history_orders(symbol=symbol, page_size=page_size, create_days=create_days)
        except ValueError:
            print("输入错误，请输入有效的数字")
    else:
        # 默认查询
        query_history_orders(symbol="cmt_btcusdt", page_size=10, create_days=7)
    
    print("\n查询完成!")
