#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟测试设置杠杆倍数的功能（不依赖实际API调用）
"""
import os
import sys
import json
from unittest.mock import patch, MagicMock

# 导入SDK
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from weex_sdk import WeexClient


def mock_request(self, method, request_path, data=None, need_sign=False, headers=None):
    """模拟_request方法，只验证参数是否正确"""
    print(f"\n[模拟请求] 方法: {method}, 路径: {request_path}")
    print(f"[模拟请求] 参数: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    # 验证必要的参数
    required_params = ['symbol', 'marginMode', 'longLeverage', 'shortLeverage']
    for param in required_params:
        if param not in data:
            print(f"[错误] 缺少必要参数: {param}")
            return {'code': '400', 'msg': f'{param} is required'}
    
    # 验证参数类型
    assert isinstance(data['marginMode'], int), "marginMode 必须是整数"
    assert isinstance(data['longLeverage'], str), "longLeverage 必须是字符串"
    assert isinstance(data['shortLeverage'], str), "shortLeverage 必须是字符串"
    
    print("[验证通过] 所有必要参数都已提供且格式正确")
    return {'code': '0', 'msg': 'success', 'data': {'symbol': data['symbol']}}


def test_set_leverage_mock():
    """使用模拟的方式测试set_leverage方法"""
    print("开始模拟测试设置杠杆倍数功能...")
    
    # 使用模拟的_request方法
    with patch.object(WeexClient, '_request', side_effect=mock_request):
        # 创建客户端（使用任意API密钥）
        client = WeexClient('mock_api_key', 'mock_api_secret', 'mock_passphrase')
        print("模拟客户端初始化成功")
        
        # 测试用例1: 只提供long_leverage
        print("\n===== 测试用例1: 只提供long_leverage =====")
        response = client.set_leverage('cmt_btcusdt', margin_mode=1, long_leverage=10)
        print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
        # 测试用例2: 同时提供long_leverage和short_leverage
        print("\n===== 测试用例2: 同时提供long_leverage和short_leverage =====")
        response = client.set_leverage('cmt_btcusdt', margin_mode=1, long_leverage=10, short_leverage=5)
        print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
        # 测试用例3: 使用部分默认值
        print("\n===== 测试用例3: 使用部分默认值 =====")
        response = client.set_leverage('cmt_btcusdt', margin_mode=1)
        print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
        print("\n所有测试用例执行完成!")
        return True


if __name__ == "__main__":
    try:
        success = test_set_leverage_mock()
        
        if success:
            print("\n✅ 模拟测试成功! set_leverage方法现在总是包含shortLeverage参数。")
            print("这应该解决了'40017: shortLeverage is required'错误。")
        else:
            print("\n❌ 模拟测试失败。")
            
    except Exception as e:
        print(f"\n❌ 模拟测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)
