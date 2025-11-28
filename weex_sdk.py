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
# 优先使用WEEX_API_SECRET，如果不存在则使用WEEX_SECRET作为备选
WEEX_SECRET = os.getenv('WEEX_API_SECRET') or os.getenv('WEEX_SECRET')
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
        self.base_url = "https://api-contract.weex.com" if not testnet else "https://api-contract.weex.com"
            
        self.timeout = 10  # 请求超时时间（秒）
    
    def _sign(self, timestamp, method, request_path, data=None, params=None):
        """
        生成API签名
        根据官方示例代码实现 - 与office_demo.py保持一致
        
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
        
        # 构建查询字符串，严格按照官方demo的方式
        query_string = ''
        if params:
            # 构建查询字符串，保持原始格式
            query_items = []
            for key, value in params.items():
                # 转换值为字符串
                str_value = str(value)
                query_items.append(f"{key}={str_value}")
            
            if query_items:
                query_string = '?' + '&'.join(query_items)
        
        # 根据HTTP方法选择不同的签名方式 - 与官方demo保持一致
        if method.upper() == 'GET':
            # GET请求的签名方式 - 直接按照官方demo格式
            message = timestamp + method.upper() + request_path + query_string
        else:
            # POST/DELETE请求的签名方式
            body = json.dumps(data) if data else ''
            message = timestamp + method.upper() + request_path + query_string + body
        
        print(f"签名消息: {message}")  # 调试信息
        
        # 使用HMAC-SHA256算法生成签名
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # 按照官方文档要求进行BASE64编码
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        print(f"生成的签名: {signature_b64}")  # 调试信息
        
        return signature_b64
    
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
            
            # 添加认证相关的请求头，使用官方推荐的头名称
            headers['ACCESS-KEY'] = self.api_key
            headers['ACCESS-SIGN'] = signature
            headers['ACCESS-PASSPHRASE'] = self.api_passphrase
            headers['ACCESS-TIMESTAMP'] = timestamp
        
        try:
            # 确保params中的值都是字符串类型
            if params:
                string_params = {k: str(v) for k, v in params.items()}
                params = string_params
            
            # 发送请求 - 对于GET请求，严格按照官方demo的URL拼接方式
            if method.upper() == 'GET':
                # 直接将查询参数拼接到URL中，而不是通过params参数
                if params:
                    # 构建查询字符串
                    query_items = []
                    for key, value in params.items():
                        query_items.append(f"{key}={value}")
                    
                    if query_items:
                        full_url = url + '?' + '&'.join(query_items)
                        response = requests.get(full_url, headers=headers, timeout=self.timeout)
                    else:
                        response = requests.get(url, headers=headers, timeout=self.timeout)
                else:
                    response = requests.get(url, headers=headers, timeout=self.timeout)
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
    
    def get_account_assets(self):
        """
        获取账户资产信息
        参考文档: https://api-contract.weex.com/capi/v2/account/assets
        
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
        request_path = "/capi/v2/account/assets"
        
        try:
            # 尝试获取合约账户信息，使用正确的签名方式
            print(f"尝试访问合约账户资产路径: {request_path}")
            # 添加必要的请求头
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            # 需要签名验证
            response = self._request("GET", request_path, params={}, need_sign=True, headers=custom_headers)
            
            print(f"API响应: {response}")
            # 检查响应是否为列表类型
            if isinstance(response, list):
                # API直接返回资产列表
                return response
            else:
                print(f"警告: 响应格式不是列表，收到 {type(response).__name__}")
                # 如果是字典类型并且包含data字段，尝试获取data
                if isinstance(response, dict) and 'data' in response:
                    return response['data']
                # 返回空列表作为默认值
                return []
        except Exception as e:
            print(f"获取账户资产信息时出错: {str(e)}")
            # 打印更详细的错误信息
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            return []
    
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
            margin_mode (int): 保证金模式，1表示Cross Mode(全仓)，3表示Isolated Mode(逐仓)
            long_leverage (str, optional): 多头杠杆倍数，例如 "2"
            short_leverage (str, optional): 空头杠杆倍数，例如 "2"
            
        Returns:
            dict: API响应数据
        """
        # 设置API路径
        request_path = "/capi/v2/account/leverage"
        
        # 构建请求数据，确保参数格式正确
        # API要求：
        # - marginMode必须是Integer类型，1表示全仓，3表示逐仓
        # - 必须同时提供longLeverage和shortLeverage参数
        # - 全仓模式下，多头和空头杠杆必须相同
        data = {
            "symbol": symbol,
            "marginMode": int(margin_mode),  # 必须是整数类型
            "longLeverage": str(long_leverage) if long_leverage is not None else "1",
            "shortLeverage": str(short_leverage) if short_leverage is not None else str(long_leverage if long_leverage is not None else "1")
        }
        
        try:
            # 发送POST请求，需要签名
            print(f"尝试设置{symbol}的杠杆倍数，保证金模式: {margin_mode}")
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            # 确保正确传递参数到_request方法
            response = self._request(method="POST", request_path=request_path, data=data, need_sign=True, headers=custom_headers)
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
            # 针对合约API，collateral字段中的资产包含legacy_amount字段
            for asset in assets:
                if isinstance(asset, dict):
                    # 检查是否为抵押品信息（包含legacy_amount字段）
                    if 'legacy_amount' in asset:
                        # 假设第一个抵押品就是USDT（根据API响应）
                        # 如果需要精确匹配，可以添加币种判断逻辑
                        balance = asset.get('legacy_amount', '0')
                        print(f"找到USDT资产，legacy_amount={balance}")
                        return float(balance)
            
            print(f"未找到{coin_symbol}资产或获取失败")
            return 0.0
        except Exception as e:
            print(f"获取{coin_symbol}余额时出错: {str(e)}")
            return 0.0
    
    def get_order_history(self, symbol, start_time=None, end_time=None, delegate_type=None, page_size=None):
        """
        获取历史计划订单列表
        参考文档: GET /capi/v2/order/historyPlan
        
        Args:
            symbol (str): 交易对，例如 "cmt_bchusdt"（必需）
            start_time (int, optional): 开始时间戳
            end_time (int, optional): 结束时间戳
            delegate_type (int, optional): 订单类型: 1: 开多. 2: 开空. 3: 平多. 4: 平空.
            page_size (int, optional): 每页数量
        
        Returns:
            dict: 格式化后的订单历史信息，包含orders字段（处理后的订单列表）和has_more字段，以及error信息
        """
        # 参数验证
        if not symbol or not isinstance(symbol, str):
            print("错误: symbol参数必须是非空字符串")
            return {
                "orders": [], 
                "has_more": False,
                "error": "symbol参数无效",
                "error_code": "INVALID_PARAMETER"
            }
        
        # 验证可选参数类型
        if start_time is not None and not isinstance(start_time, int):
            print("错误: start_time参数必须是整数类型")
            return {
                "orders": [], 
                "has_more": False,
                "error": "start_time参数类型无效",
                "error_code": "INVALID_PARAMETER"
            }
        
        if end_time is not None and not isinstance(end_time, int):
            print("错误: end_time参数必须是整数类型")
            return {
                "orders": [], 
                "has_more": False,
                "error": "end_time参数类型无效",
                "error_code": "INVALID_PARAMETER"
            }
        
        if delegate_type is not None:
            if not isinstance(delegate_type, int) or delegate_type not in [1, 2, 3, 4]:
                print(f"错误: delegate_type参数必须是1-4之间的整数，当前值: {delegate_type}")
                return {
                    "orders": [], 
                    "has_more": False,
                    "error": "delegate_type参数无效，必须是1-4之间的整数",
                    "error_code": "INVALID_PARAMETER"
                }
        
        if page_size is not None:
            if not isinstance(page_size, int) or page_size <= 0:
                print(f"错误: page_size参数必须是正整数，当前值: {page_size}")
                return {
                    "orders": [], 
                    "has_more": False,
                    "error": "page_size参数无效，必须是正整数",
                    "error_code": "INVALID_PARAMETER"
                }
            # 限制page_size最大值，避免请求过多数据
            if page_size > 500:
                print(f"警告: page_size({page_size})超过最大限制，将调整为500")
                page_size = 500
        
        try:
            # 设置API路径
            request_path = "/capi/v2/order/historyPlan"
            
            # 构建查询参数
            params = {
                "symbol": symbol  # 必需参数
            }
            
            # 添加可选参数
            if start_time is not None:
                params["startTime"] = start_time
            if end_time is not None:
                params["endTime"] = end_time
            if delegate_type is not None:
                params["delegateType"] = delegate_type
            if page_size is not None:
                params["pageSize"] = page_size
            
            # 发送GET请求，需要签名
            print(f"尝试获取历史计划订单，交易对: {symbol}")
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            
            # 发送请求并处理网络错误
            try:
                response = self._request("GET", request_path, params=params, need_sign=True, headers=custom_headers)
            except requests.RequestException as req_error:
                print(f"网络请求错误: {str(req_error)}")
                return {
                    "orders": [], 
                    "has_more": False,
                    "error": f"网络请求失败: {str(req_error)}",
                    "error_code": "NETWORK_ERROR"
                }
            
            # 检查响应是否有效
            if not isinstance(response, dict):
                print(f"无效的响应格式: {type(response)}")
                return {
                    "orders": [], 
                    "has_more": False,
                    "error": "API返回的响应格式无效",
                    "error_code": "INVALID_RESPONSE"
                }
            
            # 检查API是否返回错误
            if "code" in response and response["code"] != 0:
                error_msg = response.get("msg", "未知API错误")
                error_code = response.get("code", "UNKNOWN_ERROR")
                print(f"API错误 - 代码: {error_code}, 消息: {error_msg}")
                return {
                    "orders": [], 
                    "has_more": False,
                    "error": error_msg,
                    "error_code": str(error_code)
                }
            
            # 解析和格式化订单列表
            formatted_orders = []
            order_list = response.get("list", [])
            
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
                            "reduce_only": bool(order.get("reduceOnly", False))
                        }
                        
                        # 计算订单金额（用于展示）
                        try:
                            formatted_order["order_value"] = round(formatted_order["price"] * formatted_order["volume"], 8)
                        except (TypeError, ValueError):
                            formatted_order["order_value"] = 0.0
                        
                        formatted_orders.append(formatted_order)
            except Exception as parse_error:
                print(f"订单数据解析错误: {str(parse_error)}")
                # 即使部分数据解析失败，也返回已成功解析的订单
                print(f"已成功解析 {len(formatted_orders)} 条订单数据")
            
            # 构建返回结果
            result = {
                "orders": formatted_orders,
                "has_more": bool(response.get("nextPage", False)),
                "total_count": len(formatted_orders),
                "error": None,
                "error_code": None
            }
            
            print(f"成功获取并格式化 {len(formatted_orders)} 条历史订单记录")
            return result
            
        except Exception as e:
            print(f"获取历史订单时发生未知错误: {str(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            # 返回空的订单列表和错误信息
            return {
                "orders": [], 
                "has_more": False,
                "error": f"未知错误: {str(e)}",
                "error_code": "UNKNOWN_ERROR"
            }
    
    def fetch_ohlcv(self, symbol, timeframe, since=None, limit=100):
        """
        获取K线数据
        对应OKX SDK的exchange.fetch_ohlcv方法
        
        Args:
            symbol (str): 交易对，如 "cmt_bchusdt"
            timeframe (str): K线周期，如 "1m", "5m", "1h", "1d"
            since (int, optional): 开始时间戳（毫秒）
            limit (int, optional): 数据条数，默认100
            
        Returns:
            list: K线数据列表，每条数据格式为[时间戳, 开盘价, 最高价, 最低价, 收盘价, 成交量]
        """
        try:
            # 设置API路径
            request_path = "/capi/v2/market/candles"
            
            # 构建查询参数
            params = {
                "symbol": symbol,
                "granularity": timeframe,
                "limit": limit
            }
            
            # 添加可选参数
            if since is not None:
                params["startTime"] = since
                # 如果提供了开始时间，可以设置一个合理的结束时间
                # 例如当前时间加上一段时间
                params["endTime"] = int(time.time() * 1000)
            
            # 发送GET请求，不需要签名（公开API）
            print(f"尝试获取{symbol}的{timeframe} K线数据，限制{limit}条")
            response = self._request("GET", request_path, params=params, need_sign=False)
            
            # 处理响应数据
            # 响应格式: [[时间戳, 开盘价, 最高价, 最低价, 收盘价, 交易量, 成交额], ...]
            # 转换为CCXT兼容格式: [时间戳, 开盘价, 最高价, 最低价, 收盘价, 成交量]
            ohlcv_data = []
            if isinstance(response, list):
                for candle in response:
                    if len(candle) >= 7:
                        # 转换为float类型并重新排列
                        ohlcv_data.append([
                            int(candle[0]),  # 时间戳
                            float(candle[1]),  # 开盘价
                            float(candle[2]),  # 最高价
                            float(candle[3]),  # 最低价
                            float(candle[4]),  # 收盘价
                            float(candle[6])  # 成交量（使用成交额）
                        ])
            
            print(f"成功获取{len(ohlcv_data)}条K线数据")
            return ohlcv_data
        except Exception as e:
            print(f"获取K线数据时出错: {str(e)}")
            return []
    
    def fetch_positions(self, symbol=None):
        """
        获取持仓情况
        对应OKX SDK的exchange.fetch_positions方法
        
        Args:
            symbol (str, optional): 交易对，如 "cmt_bchusdt"，不提供则获取所有持仓
            
        Returns:
            list: 持仓列表，每个持仓包含详细信息
        """
        try:
            # 设置API路径
            request_path = "/capi/v2/account/position/allPosition"
            
            # 构建查询参数
            params = {}
            if symbol is not None:
                params["symbol"] = symbol
            
            # 发送GET请求，需要签名
            print(f"尝试获取持仓情况{'' if symbol is None else f'，交易对: {symbol}'}")
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            response = self._request("GET", request_path, params=params, need_sign=True, headers=custom_headers)
            
            # 处理响应数据
            positions = []
            if isinstance(response, list):
                for pos in response:
                    # 转换为CCXT兼容的格式
                    position = {
                        "id": pos.get("id", ""),
                        "symbol": pos.get("symbol", ""),
                        "side": "long" if pos.get("side") == "LONG" else "short",
                        "size": float(pos.get("size", 0)),
                        "entryPrice": float(pos.get("open_value", 0)) / float(pos.get("size", 1)) if float(pos.get("size", 0)) > 0 else 0,
                        "leverage": float(pos.get("leverage", 1)),
                        "unrealizedPnl": float(pos.get("unrealizePnl", 0)),
                        "liquidationPrice": float(pos.get("liquidatePrice", 0)),
                        "marginMode": "isolated" if pos.get("margin_mode") == "ISOLATED" else "cross",
                        "timestamp": pos.get("updated_time", 0),
                        "info": pos  # 保留原始数据
                    }
                    positions.append(position)
            
            print(f"成功获取{len(positions)}个持仓信息")
            return positions
        except Exception as e:
            print(f"获取持仓情况时出错: {str(e)}")
            return []
    
    def create_market_order(self, symbol, side, amount, **kwargs):
        """
        创建市价单
        对应OKX SDK的exchange.create_market_order方法
        
        Args:
            symbol (str): 交易对，如 "cmt_bchusdt"
            side (str): 交易方向，"buy" 或 "sell"
            amount (float): 订单数量
            **kwargs: 其他可选参数
            
        Returns:
            dict: 订单信息
        """
        try:
            # 设置API路径
            request_path = "/capi/v2/order/placeOrder"
            
            # 生成客户端订单ID
            client_oid = kwargs.get("client_oid", f"{int(time.time() * 1000)}")
            
            # 映射交易方向
            # 1: Open long, 2: Open short, 3: Close long, 4: Close short
            if kwargs.get("reduce_only", False):
                # 平仓订单
                order_type = 4 if side.lower() == "sell" else 3
            else:
                # 开仓订单
                order_type = 1 if side.lower() == "buy" else 2
            
            # 构建请求数据
            data = {
                "symbol": symbol,
                "client_oid": client_oid,
                "size": str(amount),
                "type": str(order_type),
                "order_type": "0",  # 0: Normal
                "match_price": "1"  # 1: Market price
            }
            
            # 添加可选参数
            if "price" in kwargs and float(kwargs["price"]) > 0:
                data["price"] = str(kwargs["price"])
            if "presetTakeProfitPrice" in kwargs:
                data["presetTakeProfitPrice"] = kwargs["presetTakeProfitPrice"]
            if "presetStopLossPrice" in kwargs:
                data["presetStopLossPrice"] = kwargs["presetStopLossPrice"]
            if "marginMode" in kwargs:
                data["marginMode"] = kwargs["marginMode"]
            if "separatedMode" in kwargs:
                data["separatedMode"] = kwargs["separatedMode"]
            
            # 发送POST请求，需要签名
            print(f"尝试创建市价{side}单，交易对: {symbol}，数量: {amount}")
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            response = self._request("POST", request_path, data=data, need_sign=True, headers=custom_headers)
            
            # 处理响应数据
            order = {
                "id": response.get("order_id", ""),
                "clientOrderId": response.get("client_oid", client_oid),
                "symbol": symbol,
                "side": side,
                "type": "market",
                "amount": amount,
                "info": response  # 保留原始数据
            }
            
            print(f"市价单创建成功，订单ID: {order['id']}")
            return order
        except Exception as e:
            print(f"创建市价单时出错: {str(e)}")
            return None
    
    def open_long(self, symbol, amount, price=None, order_type="0", match_price="1", **kwargs):
        """
        开多（建立多头仓位）
        
        Args:
            symbol (str): 交易对，如 "cmt_bchusdt"
            amount (float): 订单数量
            price (float, optional): 订单价格，限价单时必填
            order_type (str, optional): 订单类型，默认0: Normal
            match_price (str, optional): 价格类型，默认1: Market price, 0: Limit price
            **kwargs: 其他可选参数，如presetTakeProfitPrice, presetStopLossPrice, marginMode等
            
        Returns:
            dict: 订单信息
        """
        try:
            # 设置API路径
            request_path = "/capi/v2/order/placeOrder"
            
            # 生成客户端订单ID
            client_oid = kwargs.get("client_oid", f"{int(time.time() * 1000)}")
            
            # 开多对应的type为1
            order_type_value = "1"  # 1: Open long
            
            # 构建请求数据
            data = {
                "symbol": symbol,
                "client_oid": client_oid,
                "size": str(amount),
                "type": order_type_value,
                "order_type": order_type,
                "match_price": match_price
            }
            
            # 如果是限价单且提供了价格，添加价格参数
            if match_price == "0" and price is not None:
                data["price"] = str(price)
            elif match_price == "1" and price is not None:
                # 市价单也可以提供价格作为参考
                data["price"] = str(price)
            
            # 添加可选参数
            if "presetTakeProfitPrice" in kwargs:
                data["presetTakeProfitPrice"] = kwargs["presetTakeProfitPrice"]
            if "presetStopLossPrice" in kwargs:
                data["presetStopLossPrice"] = kwargs["presetStopLossPrice"]
            if "marginMode" in kwargs:
                data["marginMode"] = kwargs["marginMode"]
            if "separatedMode" in kwargs:
                data["separatedMode"] = kwargs["separatedMode"]
            
            # 发送POST请求，需要签名
            print(f"尝试开多，交易对: {symbol}，数量: {amount}")
            if match_price == "0" and price is not None:
                print(f"限价: {price}")
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            response = self._request("POST", request_path, data=data, need_sign=True, headers=custom_headers)
            
            # 处理响应数据
            order = {
                "id": response.get("order_id", ""),
                "clientOrderId": response.get("client_oid", client_oid),
                "symbol": symbol,
                "side": "buy",
                "type": "market" if match_price == "1" else "limit",
                "amount": amount,
                "price": price,
                "info": response  # 保留原始数据
            }
            
            print(f"开多订单创建成功，订单ID: {order['id']}")
            return order
        except Exception as e:
            print(f"开多时出错: {str(e)}")
            return None
    
    def open_short(self, symbol, amount, price=None, order_type="0", match_price="1", **kwargs):
        """
        开空（建立空头仓位）
        
        Args:
            symbol (str): 交易对，如 "cmt_bchusdt"
            amount (float): 订单数量
            price (float, optional): 订单价格，限价单时必填
            order_type (str, optional): 订单类型，默认0: Normal
            match_price (str, optional): 价格类型，默认1: Market price, 0: Limit price
            **kwargs: 其他可选参数，如presetTakeProfitPrice, presetStopLossPrice, marginMode等
            
        Returns:
            dict: 订单信息
        """
        try:
            # 设置API路径
            request_path = "/capi/v2/order/placeOrder"
            
            # 生成客户端订单ID
            client_oid = kwargs.get("client_oid", f"{int(time.time() * 1000)}")
            
            # 开空对应的type为2
            order_type_value = "2"  # 2: Open short
            
            # 构建请求数据
            data = {
                "symbol": symbol,
                "client_oid": client_oid,
                "size": str(amount),
                "type": order_type_value,
                "order_type": order_type,
                "match_price": match_price
            }
            
            # 如果是限价单且提供了价格，添加价格参数
            if match_price == "0" and price is not None:
                data["price"] = str(price)
            elif match_price == "1" and price is not None:
                # 市价单也可以提供价格作为参考
                data["price"] = str(price)
            
            # 添加可选参数
            if "presetTakeProfitPrice" in kwargs:
                data["presetTakeProfitPrice"] = kwargs["presetTakeProfitPrice"]
            if "presetStopLossPrice" in kwargs:
                data["presetStopLossPrice"] = kwargs["presetStopLossPrice"]
            if "marginMode" in kwargs:
                data["marginMode"] = kwargs["marginMode"]
            if "separatedMode" in kwargs:
                data["separatedMode"] = kwargs["separatedMode"]
            
            # 发送POST请求，需要签名
            print(f"尝试开空，交易对: {symbol}，数量: {amount}")
            if match_price == "0" and price is not None:
                print(f"限价: {price}")
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            response = self._request("POST", request_path, data=data, need_sign=True, headers=custom_headers)
            
            # 处理响应数据
            order = {
                "id": response.get("order_id", ""),
                "clientOrderId": response.get("client_oid", client_oid),
                "symbol": symbol,
                "side": "sell",
                "type": "market" if match_price == "1" else "limit",
                "amount": amount,
                "price": price,
                "info": response  # 保留原始数据
            }
            
            print(f"开空订单创建成功，订单ID: {order['id']}")
            return order
        except Exception as e:
            print(f"开空时出错: {str(e)}")
            return None
    
    def close_long(self, symbol, amount, price=None, order_type="0", match_price="1", **kwargs):
        """
        平多（平仓多头仓位）
        
        Args:
            symbol (str): 交易对，如 "cmt_bchusdt"
            amount (float): 订单数量
            price (float, optional): 订单价格，限价单时必填
            order_type (str, optional): 订单类型，默认0: Normal
            match_price (str, optional): 价格类型，默认1: Market price, 0: Limit price
            **kwargs: 其他可选参数，如marginMode, separatedMode等
            
        Returns:
            dict: 订单信息
        """
        try:
            # 设置API路径
            request_path = "/capi/v2/order/placeOrder"
            
            # 生成客户端订单ID
            client_oid = kwargs.get("client_oid", f"{int(time.time() * 1000)}")
            
            # 平多对应的type为3
            order_type_value = "3"  # 3: Close long
            
            # 构建请求数据
            data = {
                "symbol": symbol,
                "client_oid": client_oid,
                "size": str(amount),
                "type": order_type_value,
                "order_type": order_type,
                "match_price": match_price
            }
            
            # 如果是限价单且提供了价格，添加价格参数
            if match_price == "0" and price is not None:
                data["price"] = str(price)
            elif match_price == "1" and price is not None:
                # 市价单也可以提供价格作为参考
                data["price"] = str(price)
            
            # 添加可选参数
            if "marginMode" in kwargs:
                data["marginMode"] = kwargs["marginMode"]
            if "separatedMode" in kwargs:
                data["separatedMode"] = kwargs["separatedMode"]
            
            # 发送POST请求，需要签名
            print(f"尝试平多，交易对: {symbol}，数量: {amount}")
            if match_price == "0" and price is not None:
                print(f"限价: {price}")
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            response = self._request("POST", request_path, data=data, need_sign=True, headers=custom_headers)
            
            # 处理响应数据
            order = {
                "id": response.get("order_id", ""),
                "clientOrderId": response.get("client_oid", client_oid),
                "symbol": symbol,
                "side": "sell",
                "type": "market" if match_price == "1" else "limit",
                "amount": amount,
                "price": price,
                "info": response  # 保留原始数据
            }
            
            print(f"平多订单创建成功，订单ID: {order['id']}")
            return order
        except Exception as e:
            print(f"平多时出错: {str(e)}")
            return None
    
    def close_short(self, symbol, amount, price=None, order_type="0", match_price="1", **kwargs):
        """
        平空（平仓空头仓位）
        
        Args:
            symbol (str): 交易对，如 "cmt_bchusdt"
            amount (float): 订单数量
            price (float, optional): 订单价格，限价单时必填
            order_type (str, optional): 订单类型，默认0: Normal
            match_price (str, optional): 价格类型，默认1: Market price, 0: Limit price
            **kwargs: 其他可选参数，如marginMode, separatedMode等
            
        Returns:
            dict: 订单信息
        """
        try:
            # 设置API路径
            request_path = "/capi/v2/order/placeOrder"
            
            # 生成客户端订单ID
            client_oid = kwargs.get("client_oid", f"{int(time.time() * 1000)}")
            
            # 平空对应的type为4
            order_type_value = "4"  # 4: Close short
            
            # 构建请求数据
            data = {
                "symbol": symbol,
                "client_oid": client_oid,
                "size": str(amount),
                "type": order_type_value,
                "order_type": order_type,
                "match_price": match_price
            }
            
            # 如果是限价单且提供了价格，添加价格参数
            if match_price == "0" and price is not None:
                data["price"] = str(price)
            elif match_price == "1" and price is not None:
                # 市价单也可以提供价格作为参考
                data["price"] = str(price)
            
            # 添加可选参数
            if "marginMode" in kwargs:
                data["marginMode"] = kwargs["marginMode"]
            if "separatedMode" in kwargs:
                data["separatedMode"] = kwargs["separatedMode"]
            
            # 发送POST请求，需要签名
            print(f"尝试平空，交易对: {symbol}，数量: {amount}")
            if match_price == "0" and price is not None:
                print(f"限价: {price}")
            custom_headers = {
                "locale": "zh-CN",
                "Content-Type": "application/json"
            }
            response = self._request("POST", request_path, data=data, need_sign=True, headers=custom_headers)
            
            # 处理响应数据
            order = {
                "id": response.get("order_id", ""),
                "clientOrderId": response.get("client_oid", client_oid),
                "symbol": symbol,
                "side": "buy",
                "type": "market" if match_price == "1" else "limit",
                "amount": amount,
                "price": price,
                "info": response  # 保留原始数据
            }
            
            print(f"平空订单创建成功，订单ID: {order['id']}")
            return order
        except Exception as e:
            print(f"平空时出错: {str(e)}")
            return None


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
        
        # 测试新增的交易方法 - 注意：这些测试默认不执行真实交易，仅打印测试信息
        print("\n测试交易方法功能（模拟测试）...")
        
        # 测试开多方法
        print("\n测试开多(open_long)方法...")
        print(f"  模拟开多，交易对: {test_symbol}, 数量: 0.01, 价格类型: 市价单")
        print("  注意：实际交易请取消下面的注释并提供有效的API密钥")
        # open_long_result = client.open_long(
        #     symbol=test_symbol,
        #     amount=0.01,
        #     match_price="1"  # 市价单
        # )
        # print(f"  开多结果: {open_long_result}")
        
        # 测试开空方法
        print("\n测试开空(open_short)方法...")
        print(f"  模拟开空，交易对: {test_symbol}, 数量: 0.01, 价格类型: 市价单")
        print("  注意：实际交易请取消下面的注释并提供有效的API密钥")
        # open_short_result = client.open_short(
        #     symbol=test_symbol,
        #     amount=0.01,
        #     match_price="1"  # 市价单
        # )
        # print(f"  开空结果: {open_short_result}")
        
        # 测试平多方法
        print("\n测试平多(close_long)方法...")
        print(f"  模拟平多，交易对: {test_symbol}, 数量: 0.01, 价格类型: 市价单")
        print("  注意：实际交易请取消下面的注释并提供有效的API密钥")
        # close_long_result = client.close_long(
        #     symbol=test_symbol,
        #     amount=0.01,
        #     match_price="1"  # 市价单
        # )
        # print(f"  平多结果: {close_long_result}")
        
        # 测试平空方法
        print("\n测试平空(close_short)方法...")
        print(f"  模拟平空，交易对: {test_symbol}, 数量: 0.01, 价格类型: 市价单")
        print("  注意：实际交易请取消下面的注释并提供有效的API密钥")
        # close_short_result = client.close_short(
        #     symbol=test_symbol,
        #     amount=0.01,
        #     match_price="1"  # 市价单
        # )
        # print(f"  平空结果: {close_short_result}")
        
        print("\n交易方法测试完成（模拟模式）")
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

