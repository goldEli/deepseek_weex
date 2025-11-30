#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试设置杠杆倍数的功能
"""
import os
import sys
import json

# 导入SDK
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from weex_sdk import WeexClient


def test_set_leverage():
    """测试设置杠杆倍数"""
    # 从环境变量获取API密钥
    api_key = os.getenv('WEEX_API_KEY')
    api_secret = os.getenv('WEEX_API_SECRET')
    api_passphrase = os.getenv('WEEX_API_PASSPHRASE')
    
    # 检查环境变量
    if not all([api_key, api_secret, api_passphrase]):
        print("警告: 环境变量未完全设置")
        print("请检查以下环境变量:")
        print(f"  - WEEX_API_KEY: {'已设置' if api_key else '未设置'}")
        print(f"  - WEEX_API_SECRET: {'已设置' if api_secret else '未设置'}")
        print(f"  - WEEX_API_PASSPHRASE: {'已设置' if api_passphrase else '未设置'}")
        
        # 尝试从其他可能的环境变量获取
        if not api_key:
            api_key = os.getenv('WEEX_APIKEY')
        if not api_secret:
            api_secret = os.getenv('WEEX_APISECRET')
        if not api_passphrase:
            api_passphrase = os.getenv('WEEX_PASSPHRASE')
        
        # 再次检查
        if not all([api_key, api_secret, api_passphrase]):
            print("\n错误: 无法获取完整的API密钥信息")
            return False
        else:
            print("\n提示: 已从替代环境变量获取API密钥")
    
    try:
        # 初始化客户端
        client = WeexClient(api_key, api_secret, api_passphrase)
        print("客户端初始化成功")
        
        # 测试设置杠杆 - 使用合约交易对格式
        symbol = "cmt_btcusdt"
        margin_mode = 1  # 1: 逐仓
        leverage = 10    # 设置10倍杠杆
        
        print(f"\n测试设置{symbol}的杠杆倍数为{leverage}x，保证金模式: {margin_mode}")
        
        # 添加更详细的调试信息
        print(f"即将调用set_leverage方法，参数: symbol={symbol}, margin_mode={margin_mode}, leverage={leverage}")
        
        response = client.set_leverage(symbol, margin_mode, leverage)
        
        # 打印响应结果
        print(f"\nAPI响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        print("\n测试完成!")
        return True
        
    except Exception as e:
        print(f"\n测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("开始测试设置杠杆倍数功能...")
    success = test_set_leverage()
    
    if success:
        print("\n测试成功! 修改后的set_leverage方法工作正常。")
    else:
        print("\n测试失败，请检查错误信息。")
    
    sys.exit(0 if success else 1)
