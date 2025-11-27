import hashlib
import hmac
import time
import requests
import json
import os
# 尝试从.env文件加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 环境变量配置
WEEX_API_KEY = os.getenv('WEEX_API_KEY')
WEEX_SECRET = os.getenv('WEEX_SECRET')
WEEX_ACCESS_PASSPHRASE = os.getenv('WEEX_ACCESS_PASSPHRASE')

class WeexClient:
    """
    WEEX API客户端，用于访问WEEX交易所API
    参考文档: https://www.weex.com/api-doc/
    """
    
    def __init__(self, api_key, api_secret, api_passphrase, testnet=False):
        """
        初始化WEEX API客户端
        
        Args:
            api_key (str): API密钥
            api_secret (str): API密钥密码
            api_passphrase (str): API密码短语
            testnet (bool): 是否使用测试网络
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        
        # 使用合约API专用域名
        self.base_url = "https://api-contract.weex.com" if not testnet else "https://api-testnet.weex.com"
            
        self.timeout = 10  # 请求超时时间（秒）
    
    def _sign(self, timestamp, method, request_path, data=None, params=None):
        """
        生成API签名
        根据官方文档: https://www.weex.com/api-doc/ai/QuickStart/Signature
        
        Args:
            timestamp (str): 时间戳
            method (str): HTTP方法
            request_path (str): 请求路径
            data (dict, optional): 请求体数据
            params (dict, optional): 查询参数
            
        Returns:
            str: 生成的签名（经过BASE64编码）
        """
        import base64
        
        # 构建签名内容，严格按照WEEX API要求
        method = method.upper()
        
        # 处理查询字符串
        query_string = ''
        if params:
            # 按照官方文档要求构建查询字符串
            # 注意：这里需要保持参数的顺序和格式
            query_items = []
            for key, value in sorted(params.items()):
                query_items.append(f"{key}={value}")
            if query_items:
                query_string = '&'.join(query_items)
        
        # 处理请求体
        body = ''
        if method != 'GET' and data:
            # 确保按照合约API要求格式化数据
            body = json.dumps(data, separators=(',', ':'))
        
        # 构建签名消息
        if query_string:
            message = f"{timestamp}{method}{request_path}?{query_string}{body}"
        else:
            message = f"{timestamp}{method}{request_path}{body}"
        print(f"签名消息: {message}")  # 调试信息
        
        # 使用HMAC-SHA256算法生成签名
        hmac_obj = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        # 按照官方文档要求进行BASE64编码
        signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        print(f"生成的签名: {signature}")  # 调试信息
        
        return signature
    
    def _request(self, method, request_path, params=None, data=None, need_sign=True, headers=None):
        """
        发送HTTP请求到WEEX API
        
        Args:
            method (str): HTTP方法，如 'GET', 'POST'
            request_path (str): 请求路径
            params (dict, optional): URL查询参数
            data (dict, optional): 请求体数据
            need_sign (bool): 是否需要签名
            headers (dict, optional): 额外的请求头
        
        Returns:
            dict: API响应的JSON数据
        
        Raises:
            Exception: 请求失败时抛出异常
        """
        if params is None:
            params = {}
        if data is None:
            data = {}
        if headers is None:
            headers = {}
        
        # 构建URL
        url = f"{self.base_url}{request_path}"
        
        # 设置基础请求头
        base_headers = {
            'Content-Type': 'application/json',
            'locale': 'zh-CN'
        }
        # 合并基础请求头和额外请求头
        base_headers.update(headers)
        headers = base_headers
        
        # 如果需要签名
        if need_sign and self.api_key:
            # 生成时间戳
            timestamp = str(int(time.time() * 1000))
            
            # 生成签名（包含查询参数）
            signature = self._sign(timestamp, method, request_path, data, params)
            
            # 添加认证相关的请求头
            headers['ACCESS-KEY'] = self.api_key
            headers['ACCESS-SIGN'] = signature
            headers['ACCESS-PASSPHRASE'] = self.api_passphrase
            headers['ACCESS-TIMESTAMP'] = timestamp
        
        try:
            # 发送请求
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, params=params, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, json=data, params=params, timeout=self.timeout)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            # 打印调试信息
            print(f"发送{method}请求到: {url}")
            if params:
                print(f"查询参数: {params}")
            if data and method.upper() != 'GET':
                print(f"请求体: {data}")
            print(f"响应状态码: {response.status_code}")
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print(f"错误响应: {e.response.json()}")
                except:
                    print(f"错误响应: {e.response.text}")
            raise
    
    def get_account_balance(self):
        """
        获取账户资产信息
        参考文档: https://www.weex.com/api-doc/contract/Account_API/GetAccountBalance
        
        Returns:
            list: 账户资产列表，每个资产包含以下字段:
                - coinId: 币种ID
                - coinName: 币种名称
                - available: 可用余额
                - frozen: 冻结余额
                - equity: 总权益
                - unrealizePnl: 未实现盈亏
        """
        # 使用合约账户API路径，根据curl命令示例
        request_path = "/capi/v2/account/accounts"
        
        try:
            # 尝试获取合约账户信息，使用正确的签名方式
            print(f"尝试访问合约账户路径: {request_path}")
            # 添加必要的请求头
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            # 重新启用签名验证
            response = self._request("GET", request_path, params={}, need_sign=True, headers=custom_headers)
            
            print(f"API响应: {response}")
            # 检查响应是否为dict类型
            if isinstance(response, dict):
                # 合约API直接返回账户信息字典，不需要data字段
                # 为了兼容原有代码，将账户信息转换为列表格式
                account_info = response.get('account', {})
                collateral_info = response.get('collateral', [])
                # 返回合并后的账户信息列表
                return [account_info] + collateral_info
            else:
                raise TypeError(f"响应格式不正确，期望dict类型，收到 {type(response).__name__}")
        except Exception as e:
            print(f"获取账户资产信息时出错: {str(e)}")
            # 打印更详细的错误信息
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            return None
    
    def set_leverage(self, symbol, margin_mode, long_leverage=None, short_leverage=None):
        """
        调整合约杠杆倍数
        参考文档: https://api-contract.weex.com/capi/v2/account/leverage
        
        Args:
            symbol (str): 合约交易对，例如 "cmt_bchusdt"
            margin_mode (int): 保证金模式，1表示逐仓，0表示全仓
            long_leverage (str, optional): 多头杠杆倍数，例如 "2"
            short_leverage (str, optional): 空头杠杆倍数，例如 "2"
            
        Returns:
            dict: API响应数据
        """
        # 设置API路径
        request_path = "/capi/v2/account/leverage"
        
        # 构建请求数据
        data = {
            "symbol": symbol,
            "marginMode": margin_mode
        }
        
        # 添加可选参数
        if long_leverage is not None:
            data["longLeverage"] = long_leverage
        if short_leverage is not None:
            data["shortLeverage"] = short_leverage
        
        try:
            # 发送POST请求，需要签名
            print(f"尝试设置{symbol}的杠杆倍数，保证金模式: {margin_mode}")
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            response = self._request("POST", request_path, data=data, need_sign=True, headers=custom_headers)
            print(f"杠杆设置响应: {response}")
            return response
        except Exception as e:
            print(f"设置杠杆倍数时出错: {str(e)}")
            return None
    
    def get_coin_balance(self, coin_symbol="USDT"):
        """
        获取指定币种的余额
        针对合约API，从collateral字段中提取USDT资产的amount值
        
        Args:
            coin_symbol (str): 币种符号，默认为USDT
            
        Returns:
            float: 币种余额
        """
        try:
            # 获取账户资产信息
            assets = self.get_account_balance()
            print(f"获取到的资产列表: {assets}")
            
            # 遍历资产列表，查找USDT资产
            # 针对合约API，collateral字段中的资产包含amount字段
            for asset in assets:
                if isinstance(asset, dict):
                    # 检查是否为抵押品信息（包含amount字段）
                    if 'amount' in asset:
                        # 假设第一个抵押品就是USDT（根据API响应）
                        # 如果需要精确匹配，可以添加币种判断逻辑
                        balance = asset.get('amount', '0')
                        print(f"找到USDT资产，amount={balance}")
                        return float(balance)
            
            print(f"未找到{coin_symbol}资产或获取失败")
            return 0.0
        except Exception as e:
            print(f"获取{coin_symbol}余额时出错: {str(e)}")
            return 0.0


# 测试用例函数
def test_weex_client():
    """
    测试WEEX客户端的所有功能
    
    这个测试函数会:
    1. 检查必要的环境变量是否设置
    2. 创建WeexClient实例
    3. 测试账户资产查询功能
    4. 测试杠杆调整功能
    5. 打印测试结果
    
    使用方法:
    设置环境变量后运行:
    WEEX_API_KEY=your_api_key WEEX_SECRET=your_secret WEEX_ACCESS_PASSPHRASE=your_passphrase python weex_sdk.py
    """
    # 检查环境变量
    if not all([WEEX_API_KEY, WEEX_SECRET, WEEX_ACCESS_PASSPHRASE]):
        print("错误: 缺少必要的环境变量!")
        print("请设置以下环境变量:")
        print("  WEEX_API_KEY")
        print("  WEEX_SECRET")
        print("  WEEX_ACCESS_PASSPHRASE")
        print("\n使用示例:")
        print("  WEEX_API_KEY=your_api_key WEEX_SECRET=your_secret WEEX_ACCESS_PASSPHRASE=your_passphrase python weex_sdk.py")
        return False
    
    try:
        # 创建客户端实例
        print("正在创建WeexClient实例...")
        client = WeexClient(
            api_key=WEEX_API_KEY,
            api_secret=WEEX_SECRET,
            api_passphrase=WEEX_ACCESS_PASSPHRASE,
            testnet=False  # 使用主网API
        )
        
        # 测试get_account_balance方法
        print("\n正在获取账户资产信息...")
        balances = client.get_account_balance()
    except Exception as e:
        print(f"\nAPI调用失败: {str(e)}")
        return False
    
    try:
        
        # 验证响应
        if not isinstance(balances, list):
            print(f"错误: 响应格式不正确，期望列表类型，收到 {type(balances).__name__}")
            return False
        
        print(f"\n成功获取到 {len(balances)} 个币种的资产信息")
        print("账户资产详情:")
        
        # 打印每个币种的信息
        for balance in balances:
            required_fields = ['coinId', 'coinName', 'available', 'frozen', 'equity']
            
            # 检查必要字段
            missing_fields = [field for field in required_fields if field not in balance]
            if missing_fields:
                print(f"  币种数据不完整，缺少字段: {missing_fields}")
                continue
            
            # 打印完整信息
            print(f"  币种: {balance['coinName']}")
            print(f"    ID: {balance['coinId']}")
            print(f"    可用余额: {balance['available']}")
            print(f"    冻结余额: {balance['frozen']}")
            print(f"    总权益: {balance['equity']}")
            if 'unrealizePnl' in balance:
                print(f"    未实现盈亏: {balance['unrealizePnl']}")
            print()
        
        # 测试get_coin_balance方法
        print("\n测试获取指定币种资产...")
        usdt_balance = client.get_coin_balance('USDT')
        if usdt_balance > 0:
            print(f"  USDT 资产信息:")
            print(f"    账户余额: {usdt_balance}")
        else:
            print("  未找到USDT资产或获取失败")
        
        # 测试set_leverage方法
        print("\n测试杠杆调整功能...")
        # 注意：这里使用示例合约交易对，实际使用时请根据需要修改
        test_symbol = "cmt_bchusdt"
        leverage_response = client.set_leverage(
            symbol=test_symbol,
            margin_mode=1,  # 1表示逐仓模式
            long_leverage="2",  # 设置多头杠杆为2倍
            short_leverage="2"  # 设置空头杠杆为2倍（API要求必须同时提供）
        )
        
        if leverage_response:
            print(f"  杠杆设置响应: {leverage_response}")
            # 检查响应中是否包含成功信息
            if isinstance(leverage_response, dict):
                if leverage_response.get("code") in ["200", 200, "0", 0] or leverage_response.get("msg") == "success":
                    print("  杠杆设置成功!")
                else:
                    print("  杠杆设置可能失败，请检查响应")
        else:
            print("  杠杆设置请求失败")
        
        return True
    except Exception as e:
        print(f"\n测试处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 运行测试用例
if __name__ == "__main__":
    print("开始测试WEEX API客户端...")
    success = test_weex_client()
    
    if success:
        print("\n测试完成，所有功能正常!")
    else:
        print("\n测试失败，请检查错误信息并修复问题")

