import re
import time
import os
import json
from weex_sdk import WeexClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取API凭证
api_key = os.getenv('WEEX_API_KEY')
api_secret = os.getenv('WEEX_SECRET')
api_passphrase = os.getenv('WEEX_API_PASSPHRASE') or os.getenv('WEEX_ACCESS_PASSPHRASE')

# 检查环境变量
if not api_key:
    print("错误: WEEX_API_KEY 环境变量未设置")
    exit(1)
if not api_secret:
    print("错误: WEEX_SECRET 环境变量未设置")
    exit(1)
if not api_passphrase:
    print("错误: WEEX_API_PASSPHRASE 或 WEEX_ACCESS_PASSPHRASE 环境变量未设置")
    exit(1)

print("环境变量检查通过，正在初始化客户端...")
client = WeexClient(api_key, api_secret, api_passphrase)

def extract_order_id(error_message):
    """从错误消息中提取订单ID"""
    try:
        match = re.search(r'order\s+(\d+)', error_message)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"提取订单ID时出错: {e}")
    return None

def cancel_conflicting_order(order_id, symbol):
    """尝试取消冲突订单，使用多种API路径"""
    if not order_id:
        return False
    
    print(f"尝试取消冲突订单: {order_id}")
    
    # 尝试不同的取消订单API路径
    paths = [
        ("/capi/v2/order/cancelOrder", {"order_id": order_id, "symbol": symbol}),
        ("/capi/v2/order/cancel-batch", {"order_id": order_id, "symbol": symbol}),
        ("/capi/v2/order/cancel", {"order_id": order_id})
    ]
    
    for path, data in paths:
        try:
            print(f"尝试路径: {path}, 参数: {data}")
            # 使用data参数而不是params，与SDK保持一致
            response = client._request('POST', path, data=data, need_sign=True)
            print(f"成功取消订单: {order_id}")
            return True
        except Exception as e:
            print(f"使用路径 {path} 取消订单失败: {e}")
    
    return False

def parse_error_response(error_response):
    """解析错误响应，提取错误消息"""
    try:
        # 尝试从响应字符串中提取JSON部分
        start = error_response.find('{')
        end = error_response.rfind('}') + 1
        if start >= 0 and end > start:
            error_data = json.loads(error_response[start:end])
            return error_data.get('msg', error_response)
    except Exception as e:
        print(f"解析错误响应时出错: {e}")
    return error_response

def normalize_order_size(amount, step_size=0.0001):
    """
    规范化订单数量，使其符合stepSize要求
    
    Args:
        amount: 原始订单数量
        step_size: 最小步长
        
    Returns:
        float: 规范化后的订单数量
    """
    # 确保是正数
    amount = abs(amount)
    # 四舍五入到step_size的整数倍
    normalized = round(amount / step_size) * step_size
    # 确保数量大于0
    return max(normalized, step_size)

def close_position_with_adaptive_strategy(symbol, position_side, position_size):
    """使用自适应策略平仓"""
    # 确定平仓方向 - 修复持仓方向判断
    close_side = "buy" if position_side == "short" else "sell"
    
    # 规范化持仓数量，使其符合stepSize要求
    normalized_position_size = normalize_order_size(position_size)
    print(f"开始平仓: {symbol}, 持仓方向: {position_side}, 持仓数量: {position_size}, 规范化数量: {normalized_position_size}, 平仓方向: {close_side}")
    
    max_retries = 5
    retry_count = 0
    current_size = normalized_position_size
    
    while retry_count < max_retries:
        retry_count += 1
        print(f"\n尝试第 {retry_count}/{max_retries} 次平仓，数量: {current_size}")
        
        try:
            # 生成客户端订单ID
            client_oid = f"close_{symbol}_{position_side}_{int(time.time() * 1000)}"
            
            # 使用SDK中已定义的create_market_order方法进行平仓
            # 设置reduce_only=True表示平仓操作
            print(f"发送市价{close_side}平仓请求: 交易对={symbol}, 数量={current_size}")
            order = client.create_market_order(symbol, close_side, current_size, client_oid=client_oid, reduce_only=True)
            
            # 检查订单创建结果
            if order and order.get('id'):
                print(f"✓ 平仓成功! 订单ID: {order['id']}")
                return True
            elif order is None:
                # 订单创建失败，尝试提取冲突订单信息
                print("订单创建失败，尝试查找冲突订单")
                
                # 尝试获取并取消未完成的订单
                try:
                    # 获取未完成订单
                    print("尝试获取未完成订单...")
                    open_orders = client._request('GET', '/capi/v2/order/openOrders', need_sign=True)
                    if isinstance(open_orders, list):
                        # 取消相关交易对的未完成订单
                        for open_order in open_orders:
                            if open_order.get('symbol') == symbol:
                                order_id = open_order.get('id') or open_order.get('order_id')
                                if order_id:
                                    print(f"发现相关未完成订单: {order_id}")
                                    if cancel_conflicting_order(order_id, symbol):
                                        print("冲突订单已取消，准备重试")
                                        time.sleep(1)  # 等待订单取消生效
                                        continue
                except Exception as get_orders_error:
                    print(f"获取未完成订单时出错: {get_orders_error}")
                
                print("准备重试")
                time.sleep(1)  # 等待后重试
                continue
            else:
                print(f"未预期的订单格式: {order}")
            
        except Exception as e:
            error_str = str(e)
            print(f"平仓请求出错: {error_str}")
            
            # 尝试解析错误消息
            error_msg = parse_error_response(error_str)
            
            # 检查是否为冲突订单错误
            if any(keyword in error_msg for keyword in ['FAILED_PRECONDITION', 'position side invalid', 'conflict', 'conflicting']):
                # 提取并取消冲突订单
                conflict_order_id = extract_order_id(error_msg)
                if conflict_order_id:
                    if cancel_conflicting_order(conflict_order_id, symbol):
                        print("冲突订单已取消，准备重试")
                        time.sleep(1)  # 等待订单取消生效
                        continue
                else:
                    # 如果无法提取订单ID，尝试获取并取消所有相关未完成订单
                    try:
                        print("无法提取订单ID，尝试获取所有未完成订单...")
                        open_orders = client._request('GET', '/capi/v2/order/openOrders', need_sign=True)
                        if isinstance(open_orders, list):
                            for open_order in open_orders:
                                if open_order.get('symbol') == symbol:
                                    order_id = open_order.get('id') or open_order.get('order_id')
                                    if order_id:
                                        print(f"取消未完成订单: {order_id}")
                                        cancel_conflicting_order(order_id, symbol)
                        print("未完成订单清理完成，准备重试")
                        time.sleep(2)  # 等待订单取消生效
                        continue
                    except Exception as cleanup_error:
                        print(f"清理未完成订单时出错: {cleanup_error}")
        
        # 调整数量并重试，确保符合stepSize要求
        current_size *= 0.97  # 减少3%
        current_size = normalize_order_size(current_size)
        print(f"调整平仓数量为: {current_size}")
        time.sleep(1.5)  # 等待后重试
    
    print(f"❌ 平仓失败，已尝试 {max_retries} 次")
    return False

def close_all_positions():
    """获取所有持仓并全部平仓"""
    try:
        # 获取所有持仓
        print("获取所有持仓...")
        positions = client.fetch_positions()
        
        if not positions:
            print("没有找到持仓")
            return
        
        print(f"获取到 {len(positions)} 个持仓")
        
        success_count = 0
        failed_count = 0
        
        # 遍历持仓进行平仓
        for i, position in enumerate(positions):
            symbol = position.get('symbol')
            side = position.get('side')
            size = float(position.get('size', 0))
            
            if not symbol or not side or size <= 0:
                print(f"无效的持仓数据 ({i+1}/{len(positions)}): {position}")
                failed_count += 1
                continue
            
            print(f"\n处理持仓 {i+1}/{len(positions)}: {symbol} {side} {size}")
            
            if close_position_with_adaptive_strategy(symbol, side, size):
                success_count += 1
            else:
                failed_count += 1
            
            # 持仓间隔处理
            if i < len(positions) - 1:
                print("\n等待2秒后处理下一个持仓...")
                time.sleep(2)
        
        # 输出结果摘要
        print(f"\n{'=' * 50}")
        print("平仓操作完成")
        print(f"总持仓数量: {len(positions)}")
        print(f"成功平仓: {success_count}")
        print(f"平仓失败: {failed_count}")
        print(f"{'=' * 50}")
        
    except Exception as e:
        print(f"执行过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始执行平仓操作...")
    close_all_positions()
    print("平仓操作结束")
