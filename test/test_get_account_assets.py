#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试获取账户资产信息API
"""

import os
import time
from dotenv import load_dotenv
from weex_sdk import WeexClient

# 加载环境变量
load_dotenv()

# 从环境变量中获取API凭证
WEEX_API_KEY = os.getenv('WEEX_API_KEY')
WEEX_SECRET = os.getenv('WEEX_SECRET')
WEEX_ACCESS_PASSPHRASE = os.getenv('WEEX_ACCESS_PASSPHRASE')

# 验证环境变量
required_env_vars = [
    ('WEEX_API_KEY', WEEX_API_KEY),
    ('WEEX_SECRET', WEEX_SECRET),
    ('WEEX_ACCESS_PASSPHRASE', WEEX_ACCESS_PASSPHRASE)
]

missing_vars = [var_name for var_name, var_value in required_env_vars if not var_value]
if missing_vars:
    print(f"[错误] 缺少以下环境变量: {', '.join(missing_vars)}")
    print("请检查.env文件中的配置")
    exit(1)

def test_get_account_assets():
    """
    测试获取账户资产信息
    """
    try:
        # 初始化客户端
        client = WeexClient(
            api_key=WEEX_API_KEY,
            api_secret=WEEX_SECRET,
            api_passphrase=WEEX_ACCESS_PASSPHRASE
        )
        print("✅ 客户端初始化成功")
        
        # 调用新方法获取账户资产
        print("\n🔍 开始获取账户资产信息...")
        start_time = time.time()
        assets = client.get_account_assets()
        end_time = time.time()
        
        # 验证结果
        if assets is not None:
            print(f"✅ 成功获取资产信息，耗时: {(end_time - start_time):.2f}秒")
            print(f"📊 获取到 {len(assets)} 个币种的资产信息")
            
            # 打印详细信息
            if assets:
                print("\n📋 资产详情:")
                print("-" * 80)
                print(f"{'币种名称':<10} {'可用余额':<20} {'冻结余额':<20} {'总权益':<20} {'未实现盈亏':<20}")
                print("-" * 80)
                
                for asset in assets:
                    coin_name = asset.get('coinName', 'N/A')
                    available = asset.get('available', '0')
                    frozen = asset.get('frozen', '0')
                    equity = asset.get('equity', '0')
                    unrealize_pnl = asset.get('unrealizePnl', '0')
                    
                    print(f"{coin_name:<10} {available:<20} {frozen:<20} {equity:<20} {unrealize_pnl:<20}")
                print("-" * 80)
            else:
                print("⚠️  未获取到任何资产信息")
        else:
            print("❌ 获取账户资产失败")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")

def main():
    """
    主函数
    """
    print("=" * 60)
    print("     Weex 账户资产信息测试工具     ")
    print("=" * 60)
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行测试
    test_get_account_assets()
    
    print(f"\n结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()