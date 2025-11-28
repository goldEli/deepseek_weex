#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开多BTC脚本
用途：使用WEEX API开多BTC，数量为0.01
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 添加当前目录到Python路径，确保能导入weex_sdk
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入Weex SDK
from weex_sdk import WeexClient

def main():
    """主函数，执行BTC开多操作"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行BTC开多操作...")
    
    # 加载环境变量
    load_dotenv()
    
    # 从环境变量获取API密钥
    api_key = os.getenv('WEEX_API_KEY')
    # 优先使用WEEX_API_SECRET，如果不存在则使用WEEX_SECRET作为备选
    api_secret = os.getenv('WEEX_API_SECRET') or os.getenv('WEEX_SECRET')
    api_passphrase = os.getenv('WEEX_ACCESS_PASSPHRASE')
    
    # 验证API密钥
    if not api_key or not api_secret or not api_passphrase:
        print("错误: 请在.env文件中设置WEEX_API_KEY、WEEX_API_SECRET或WEEX_SECRET、以及WEEX_ACCESS_PASSPHRASE环境变量")
        print("示例: cp .env.example .env && 编辑.env文件")
        return 1
    
    try:
        # 初始化Weex客户端
        client = WeexClient(api_key=api_key, api_secret=api_secret, api_passphrase=api_passphrase)
        
        # 设置交易参数
        symbol = "cmt_btcusdt"  # BTC永续合约交易对
        amount = 0.01  # 开多数量
        match_price = "1"  # 1表示市价单，0表示限价单
        
        print(f"交易参数:")
        print(f"  交易对: {symbol}")
        print(f"  数量: {amount}")
        print(f"  价格类型: {'市价单' if match_price == '1' else '限价单'}")
        
        # 设置杠杆倍数（可选，根据需要调整）
        print("\n设置杠杆倍数...")
        leverage_response = client.set_leverage(
            symbol=symbol,
            margin_mode=1,  # 1表示全仓模式，3表示逐仓模式
            long_leverage="10",  # 多头杠杆倍数 - 设置为10倍
            short_leverage="10"  # 空头杠杆倍数 - 设置为10倍（API要求必须同时提供）
        )
        
        if leverage_response:
            print(f"杠杆设置成功: {leverage_response}")
        else:
            print("警告: 杠杆设置可能失败，但继续执行开多操作")
        
        # 执行开多操作
        print("\n执行开多操作...")
        order_result = client.open_long(
            symbol=symbol,
            amount=amount,
            match_price=match_price
        )
        
        # 处理开多结果
        if order_result:
            print("\n✅ 开多成功!")
            print(f"  订单ID: {order_result.get('id', 'N/A')}")
            print(f"  客户端订单ID: {order_result.get('clientOrderId', 'N/A')}")
            print(f"  交易对: {order_result.get('symbol', 'N/A')}")
            print(f"  方向: {order_result.get('side', 'N/A')}")
            print(f"  类型: {order_result.get('type', 'N/A')}")
            print(f"  数量: {order_result.get('amount', 'N/A')}")
            print(f"  价格: {order_result.get('price', 'N/A')}")
            
            # 获取当前持仓
            print("\n获取当前持仓情况...")
            positions = client.fetch_positions()
            if positions:
                btc_position = None
                for pos in positions:
                    if pos.get('symbol') == symbol:
                        btc_position = pos
                        break
                
                if btc_position:
                    print(f"BTC持仓信息:")
                    print(f"  交易对: {btc_position.get('symbol', 'N/A')}")
                    print(f"  持仓方向: {'多头' if btc_position.get('side') == 'long' else '空头'}")
                    print(f"  持仓数量: {btc_position.get('size', 'N/A')}")
                    print(f"  开仓均价: {btc_position.get('avgEntryPrice', 'N/A')}")
                    print(f"  未实现盈亏: {btc_position.get('unrealizedPnl', 'N/A')}")
                else:
                    print("未找到BTC持仓信息")
            else:
                print("无法获取持仓信息")
            
            return 0
        else:
            print("❌ 开多失败!")
            return 1
            
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {str(e)}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return 1
    
if __name__ == "__main__":
    sys.exit(main())
