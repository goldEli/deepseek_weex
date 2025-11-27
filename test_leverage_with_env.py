#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试设置杠杆倍数的功能（从.env文件加载API密钥）
"""
import os
import sys
import json
from dotenv import load_dotenv

# 导入SDK
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from weex_sdk import WeexClient


def load_api_keys():
    """从.env文件加载API密钥，尝试多种可能的环境变量名称"""
    # 尝试加载.env文件
    load_dotenv()
    
    # 尝试多种可能的环境变量名称，特别注意.env文件中实际存在的变量名
    api_key = os.getenv('WEEX_API_KEY')
    
    # 注意.env文件中使用的是WEEX_SECRET而非WEEX_API_SECRET
    api_secret = os.getenv('WEEX_SECRET')
    if not api_secret:
        api_secret = os.getenv('WEEX_API_SECRET')
    
    # 注意.env文件中使用的是WEEX_ACCESS_PASSPHRASE而非WEEX_API_PASSPHRASE
    api_passphrase = os.getenv('WEEX_ACCESS_PASSPHRASE')
    if not api_passphrase:
        api_passphrase = os.getenv('WEEX_API_PASSPHRASE')
    
    # 其他可能的名称
    if not api_key:
        api_key = os.getenv('WEEX_APIKEY')
    if not api_key:
        api_key = os.getenv('API_KEY')
    
    if not api_secret:
        api_secret = os.getenv('WEEX_APISECRET')
    if not api_secret:
        api_secret = os.getenv('API_SECRET')
    
    if not api_passphrase:
        api_passphrase = os.getenv('WEEX_PASSPHRASE')
    if not api_passphrase:
        api_passphrase = os.getenv('API_PASSPHRASE')
    
    # 测试环境名称
    if not api_key:
        api_key = os.getenv('WEEX_TEST_API_KEY')
    if not api_secret:
        api_secret = os.getenv('WEEX_TEST_API_SECRET')
    if not api_passphrase:
        api_passphrase = os.getenv('WEEX_TEST_API_PASSPHRASE')
    
    # 检查是否获取到了密钥
    if not all([api_key, api_secret, api_passphrase]):
        print("警告: 无法从环境变量获取完整的API密钥")
        print(f"检查了以下环境变量:")
        print(f"  - WEEX_API_KEY: {'已设置' if os.getenv('WEEX_API_KEY') else '未设置'}")
        print(f"  - WEEX_SECRET: {'已设置' if os.getenv('WEEX_SECRET') else '未设置'}")
        print(f"  - WEEX_ACCESS_PASSPHRASE: {'已设置' if os.getenv('WEEX_ACCESS_PASSPHRASE') else '未设置'}")
        print(f"  - 其他可能的替代名称...")
        print("\n注意: .env文件中的环境变量名称可能与脚本预期的不同。请确保使用正确的变量名。")
        return None
    
    return api_key, api_secret, api_passphrase


def test_set_leverage():
    """测试设置杠杆倍数"""
    print("开始测试设置杠杆倍数功能...")
    
    # 加载API密钥
    api_credentials = load_api_keys()
    if not api_credentials:
        print("\n错误: 无法获取API密钥，测试终止")
        return False
    
    api_key, api_secret, api_passphrase = api_credentials
    print("成功加载API密钥")
    
    try:
        # 初始化客户端
        client = WeexClient(api_key, api_secret, api_passphrase)
        print("客户端初始化成功")
        
        # 测试设置杠杆 - 使用合约交易对格式
        symbol = "cmt_btcusdt"
        margin_mode = 1  # 整数类型，1: Cross Mode(全仓)
        # margin_mode = 3  # 如果需要使用Isolated Mode(逐仓)，取消此行注释
        leverage = 10      # 设置10倍杠杆
        
        print(f"\n测试设置{symbol}的杠杆倍数为{leverage}x，保证金模式: {margin_mode}")
        print(f"参数格式验证:")
        print(f"  - symbol类型: {type(symbol).__name__}")
        print(f"  - marginMode类型: {type(margin_mode).__name__}")
        print(f"  - longLeverage类型: {type(str(leverage)).__name__}")
        
        # 调用set_leverage方法
        response = client.set_leverage(symbol, margin_mode, leverage)
        
        # 打印响应结果
        print(f"\nAPI响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
        if response and 'code' in response:
            if response['code'] == '200' or response['code'] == '0':
                print("\n✅ 杠杆设置成功!")
                return True
            else:
                print(f"\n❌ 杠杆设置失败: {response.get('msg', '未知错误')}")
                return False
        else:
            print("\n❌ 杠杆设置失败: 未收到有效响应")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 检查是否安装了dotenv
    try:
        import dotenv
    except ImportError:
        print("未安装python-dotenv，尝试安装...")
        os.system(f"{sys.executable} -m pip install python-dotenv")
        try:
            import dotenv
        except ImportError:
            print("安装失败，请手动运行: pip install python-dotenv")
            sys.exit(1)
    
    success = test_set_leverage()
    
    if success:
        print("\n🎉 测试成功! set_leverage方法现在能够正确处理marginMode参数。")
    else:
        print("\n测试失败，请检查错误信息并进行修复。")
    
    sys.exit(0 if success else 1)
