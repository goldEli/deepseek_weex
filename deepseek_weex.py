import os
import time
import random
import schedule
from openai import OpenAI
import pandas as pd
from datetime import datetime
import json
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

WEEX_API_KEY = os.getenv('WEEX_API_KEY')
WEEX_SECRET = os.getenv('WEEX_SECRET')
WEEX_ACCESS_PASSPHRASE = os.getenv('WEEX_ACCESS_PASSPHRASE')

# 初始化DeepSeek客户端
deepseek_client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# WEEX API 基础URL - 根据curl命令更新为现货API域名
WEEX_API_BASE_URL = "https://api-spot.weex.com"

class WeexClient:
    def __init__(self, api_key=None, api_secret=None, api_passphrase=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.base_url = WEEX_API_BASE_URL
        self.session = requests.Session()
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 2  # 重试延迟时间（秒）
    
    def _generate_signature(self, timestamp, method, endpoint, params):
        """根据WEEX API要求生成HMAC签名"""
        # 构建签名内容：timestamp + method + endpoint + body
        method = method.upper()
        body = json.dumps(params) if params and method != 'GET' else ''
        message = f"{timestamp}{method}{endpoint}{body}"
        
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method, endpoint, params=None, need_sign=True):
        """发送API请求，带重试机制"""
        if params is None:
            params = {}
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'locale': 'zh-CN',
            'Content-Type': 'application/json'
        }
        
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                # 每次重试都重新生成签名（因为时间戳会变化）
                if need_sign and self.api_key:
                    # 使用正确的HTTP头名称格式
                    timestamp = str(int(time.time() * 1000))
                    headers['ACCESS-KEY'] = self.api_key
                    headers['ACCESS-TIMESTAMP'] = timestamp
                    
                    # 如果有passphrase，添加到请求头
                    if self.api_passphrase:
                        headers['ACCESS-PASSPHRASE'] = self.api_passphrase
                    
                    # 生成签名
                    signature = self._generate_signature(timestamp, method, endpoint, params)
                    headers['ACCESS-SIGN'] = signature
                
                # 确保请求路径是正确的API版本格式
                if not endpoint.startswith('/api/v2/'):
                    # 如果不是v2版本，保持原样
                    pass
                
                print(f"发送{method}请求到: {url}")
                print(f"请求参数: {params}")
                
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, headers=headers, timeout=15)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=params, headers=headers, timeout=15)
                else:
                    raise ValueError(f"不支持的请求方法: {method}")
                
                print(f"接收到响应，状态码: {response.status_code}")
                
                response.raise_for_status()
                
                try:
                    result = response.json()
                    print(f"响应数据: {result}")
                    return result
                except json.JSONDecodeError:
                    print(f"警告: 响应不是有效的JSON格式")
                    print(f"响应内容: {response.text}")
                    return {'raw_text': response.text}
                    
            except requests.exceptions.HTTPError as e:
                print(f"HTTP错误 (重试 {retry_count}/{self.max_retries}): {e}")
                
                if hasattr(e, 'response') and e.response is not None:
                    print(f"响应状态码: {e.response.status_code}")
                    try:
                        error_data = e.response.json()
                        print(f"错误详情: {error_data}")
                        # 处理特定的错误码
                        if e.response.status_code == 401:
                            print("认证失败，请检查API密钥和密钥")
                            return None  # 认证错误不重试
                        elif e.response.status_code == 429:
                            print("请求过于频繁，等待更长时间再重试...")
                            time.sleep(self.retry_delay * 2)
                        elif e.response.status_code >= 500:
                            print("服务器错误，进行重试...")
                        else:
                            # 其他客户端错误不重试
                            print("客户端错误，不进行重试")
                            return None
                    except:
                        print(f"响应内容: {e.response.text}")
            except requests.exceptions.ConnectionError as e:
                print(f"连接错误 (重试 {retry_count}/{self.max_retries}): {e}")
                print("网络连接问题，检查您的网络设置")
            except requests.exceptions.Timeout as e:
                print(f"请求超时 (重试 {retry_count}/{self.max_retries}): {e}")
            except Exception as e:
                print(f"未知错误 (重试 {retry_count}/{self.max_retries}): {e}")
                import traceback
                traceback.print_exc()
            
            # 增加重试计数并等待
            retry_count += 1
            if retry_count <= self.max_retries:
                wait_time = self.retry_delay * (2 ** (retry_count - 1))  # 指数退避
                print(f"{wait_time}秒后进行第{retry_count}次重试...")
                time.sleep(wait_time)
        
        print(f"达到最大重试次数 ({self.max_retries})，请求失败")
        return None

# 初始化WEEX客户端
exchange = WeexClient(api_key=WEEX_API_KEY, api_secret=WEEX_SECRET, api_passphrase=WEEX_ACCESS_PASSPHRASE)

# 交易参数配置
TRADE_CONFIG = {
    'symbol': 'BTC/USDT',
    'amount': 0.001,  # 交易数量 (BTC)
    'order_size': 0.001,  # 订单大小，用于订单执行函数
    'timeframe': '15m',  # 时间周期，可改为1h, 4h, 1d
    'test_mode': False,  # 测试模式
}

# 全局变量存储历史数据
price_history = []
signal_history = []
position = None


def setup_exchange():
    """设置交易所参数 - 符合WEEX现货API DOC.md规范"""
    try:

        # 获取余额 - WEEX API
        # 使用现货API的余额查询端点
        balance_response = exchange._request('GET', '/api/v2/account/balance')
        print(f"余额查询响应: {balance_response}")
        
        # 按照官方文档处理响应格式
        if balance_response:
            if isinstance(balance_response, dict):
                # 检查是否成功响应
                if balance_response.get('code') == '00000':
                    # 官方文档格式: data是数组，包含coinId, coinName, available等字段
                    if 'data' in balance_response and isinstance(balance_response['data'], list):
                        for coin in balance_response['data']:
                            if isinstance(coin, dict) and coin.get('coinName') == 'USDT':
                                # 使用官方文档指定的字段名
                                available_balance = float(coin.get('available', 0))
                                frozen_balance = float(coin.get('frozen', 0))
                                total_balance = float(coin.get('equity', 0))
                                print(f"当前USDT可用余额: {available_balance:.2f}")
                                print(f"当前USDT冻结余额: {frozen_balance:.2f}")
                                print(f"当前USDT总余额: {total_balance:.2f}")
                                break
                else:
                    print(f"查询余额失败: {balance_response.get('msg', '未知错误')}")
            else:
                print("余额查询响应格式异常")

        return True
    except Exception as e:
        print(f"交易所设置失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_btc_ohlcv():
    """获取BTC/USDT的K线数据（1小时或15分钟）"""
    try:
        # 转换时间周期格式
        timeframe_mapping = {
            '15m': '15min',
            '1h': '1hour',
            '4h': '4hour',
            '1d': '1day'
        }
        weex_timeframe = timeframe_mapping.get(TRADE_CONFIG['timeframe'], TRADE_CONFIG['timeframe'])
        
        # 获取最近10根K线 - WEEX API
        symbol = TRADE_CONFIG['symbol'].replace('/', '')
        params = {
            'symbol': symbol,
            'interval': weex_timeframe,
            'limit': 10
        }
        
        print(f"获取K线数据参数: {params}")
        # 使用现货API的K线数据端点 - 修正为正确的路径格式
        ohlcv_response = exchange._request('GET', f'/api/v2/market/candles/{symbol}', params=params, need_sign=False)
        
        print(f"K线数据响应: {ohlcv_response}")
        
        # 通用响应处理
        if not ohlcv_response:
            print("获取K线数据失败: 响应为空")
            return None
        
        # 检查是否成功响应
        if isinstance(ohlcv_response, dict):
            if ohlcv_response.get('code') != '00000':
                print(f"获取K线数据失败: {ohlcv_response.get('msg', '未知错误')}")
                return None
            
            # 提取数据
            if 'data' in ohlcv_response:
                ohlcv_data = ohlcv_response['data']
            else:
                print(f"获取K线数据失败: 响应中未找到data字段")
                return None
        else:
            print("获取K线数据失败: 响应不是预期的JSON格式")
            return None
        
        # 转换为DataFrame
        if isinstance(ohlcv_data, list):
            # 检查数据结构
            if ohlcv_data and isinstance(ohlcv_data[0], list):
                # 假设数据是列表格式 [timestamp, open, high, low, close, volume]
                df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            elif ohlcv_data and isinstance(ohlcv_data[0], dict):
                # 假设数据是字典格式，包含所需字段
                df = pd.DataFrame(ohlcv_data)
                # 重命名列以匹配预期格式
                if 'time' in df.columns:
                    df.rename(columns={'time': 'timestamp'}, inplace=True)
                if 'openPrice' in df.columns:
                    df.rename(columns={'openPrice': 'open', 'highPrice': 'high', 'lowPrice': 'low', 'closePrice': 'close'}, inplace=True)
            else:
                print("获取K线数据失败: 数据格式不支持")
                return None
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        current_data = df.iloc[-1]
        previous_data = df.iloc[-2] if len(df) > 1 else current_data

        return {
            'price': current_data['close'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'high': current_data['high'],
            'low': current_data['low'],
            'volume': current_data['volume'],
            'timeframe': TRADE_CONFIG['timeframe'],
            'price_change': ((current_data['close'] - previous_data['close']) / previous_data['close']) * 100,
            'kline_data': df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].tail(5).to_dict('records')
        }
    except Exception as e:
        print(f"获取K线数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_current_position():
    """获取当前持仓情况 - WEEX API"""
    try:
        # 注意：现货API没有专门的持仓查询端点
        # 在现货交易中，我们需要通过获取账户资产来判断持仓情况
        symbol = TRADE_CONFIG['symbol'].replace('/', '')
        
        print(f"获取账户资产参数: 交易对={symbol}")
        # 获取账户资产信息
        balance_response = exchange._request('GET', '/api/v2/account/balance', params={})
        
        print(f"账户资产响应: {balance_response}")
        
        if not balance_response or not isinstance(balance_response, dict):
            print("获取账户资产失败: 响应为空或格式错误")
            return None
        
        # 检查是否成功响应
        if balance_response.get('code') != '00000':
            print(f"获取账户资产失败: {balance_response.get('msg', '未知错误')}")
            return None
        
        # 提取基础货币和计价货币
        base_coin = TRADE_CONFIG['symbol'].split('/')[0]  # 例如BTC
        quote_coin = TRADE_CONFIG['symbol'].split('/')[1]  # 例如USDT
        
        # 遍历资产数据检查是否持有基础货币（作为多仓的判断依据）
        if 'data' in balance_response and isinstance(balance_response['data'], list):
            for coin in balance_response['data']:
                if isinstance(coin, dict) and coin.get('coinName') == base_coin:
                    # 获取基础货币余额
                    try:
                        available = float(coin.get('available', 0))
                        frozen = float(coin.get('frozen', 0))
                        total = available + frozen
                        
                        # 如果有基础货币余额，简单判断为持有多仓
                        # 注意：这是简化的判断逻辑，实际情况可能需要更复杂的订单跟踪
                        if total > 0:
                            print(f"检测到{base_coin}余额: {total}，判定为持有多仓")
                            
                            # 尝试获取当前价格来计算盈亏
                            price_data = get_btc_ohlcv()
                            current_price = price_data['price'] if price_data else 0
                            
                            # 由于没有平均入场价，这里使用当前价格作为估计
                            # 实际应用中，应该通过订单历史记录计算平均入场价
                            return {
                                'side': 'long',
                                'size': total,
                                'entry_price': current_price,  # 这是一个估计值
                                'unrealized_pnl': 0,  # 无法准确计算，设为0
                                'position_amt': total,
                                'symbol': symbol
                            }
                    except (ValueError, TypeError) as e:
                        print(f"解析{base_coin}余额失败: {e}")
        
        print("未检测到持仓")
        return None

    except Exception as e:
        print(f"获取持仓失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_with_deepseek(price_data):
    """使用DeepSeek分析市场并生成交易信号"""

    # 添加当前价格到历史记录
    price_history.append(price_data)
    if len(price_history) > 20:  # 保留更多历史数据用于长周期分析
        price_history.pop(0)

    # 构建K线数据文本
    kline_text = f"【最近5根{TRADE_CONFIG['timeframe']}K线数据】\n"
    for i, kline in enumerate(price_data['kline_data']):
        trend = "阳线" if kline['close'] > kline['open'] else "阴线"
        change = ((kline['close'] - kline['open']) / kline['open']) * 100
        kline_text += f"K线{i + 1}: {trend} 开盘:{kline['open']:.2f} 收盘:{kline['close']:.2f} 涨跌:{change:+.2f}%\n"

    # 构建技术指标文本
    if len(price_history) >= 5:
        closes = [data['price'] for data in price_history[-5:]]
        sma_5 = sum(closes) / len(closes)
        price_vs_sma = ((price_data['price'] - sma_5) / sma_5) * 100

        indicator_text = f"【技术指标】\n5周期均价: {sma_5:.2f}\n当前价格相对于均线: {price_vs_sma:+.2f}%"
    else:
        indicator_text = "【技术指标】\n数据不足计算技术指标"

    # 添加上次交易信号
    signal_text = ""
    if signal_history:
        last_signal = signal_history[-1]
        signal_text = f"\n【上次交易信号】\n信号: {last_signal.get('signal', 'N/A')}\n信心: {last_signal.get('confidence', 'N/A')}"

    # 添加当前持仓信息
    current_pos = get_current_position()
    position_text = "无持仓" if not current_pos else f"{current_pos['side']}仓, 数量: {current_pos['size']}, 盈亏: {current_pos['unrealized_pnl']:.2f}USDT"

    prompt = f"""
    你是一个专业的加密货币交易分析师。请基于以下BTC/USDT {TRADE_CONFIG['timeframe']}周期数据进行分析：

    {kline_text}

    {indicator_text}

    {signal_text}

    【当前行情】
    - 当前价格: ${price_data['price']:,.2f}
    - 时间: {price_data['timestamp']}
    - 本K线最高: ${price_data['high']:,.2f}
    - 本K线最低: ${price_data['low']:,.2f}
    - 本K线成交量: {price_data['volume']:.2f} BTC
    - 价格变化: {price_data['price_change']:+.2f}%
    - 当前持仓: {position_text}

    【分析要求】
    1. 基于{TRADE_CONFIG['timeframe']}K线趋势和技术指标给出交易信号: BUY(买入) / SELL(卖出) / HOLD(观望)
    2. 简要分析理由（考虑趋势连续性、支撑阻力、成交量等因素）
    3. 基于技术分析建议合理的止损价位
    4. 基于技术分析建议合理的止盈价位
    5. 评估信号信心程度

    请用以下JSON格式回复：
    {{
        "signal": "BUY|SELL|HOLD",
        "reason": "分析理由",
        "stop_loss": 具体价格,
        "take_profit": 具体价格,
        "confidence": "HIGH|MEDIUM|LOW"
    }}
    """

    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system",
                 "content": f"您是一位急需资金为母亲治疗癌症的交易员，你现在需要从加密货币交易市场赚取足够的金额治疗你的母亲，专注于{TRADE_CONFIG['timeframe']}周期趋势分析。请结合K线形态和技术指标做出判断。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )

        # 安全解析JSON
        result = response.choices[0].message.content
        start_idx = result.find('{')
        end_idx = result.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            json_str = result[start_idx:end_idx]
            signal_data = json.loads(json_str)
        else:
            print(f"无法解析JSON: {result}")
            return None

        # 保存信号到历史记录
        signal_data['timestamp'] = price_data['timestamp']
        signal_history.append(signal_data)
        if len(signal_history) > 30:
            signal_history.pop(0)

        return signal_data

    except Exception as e:
        print(f"DeepSeek分析失败: {e}")
        return None


def execute_trade(signal_data, price_data):
    """执行交易 - WEEX API"""
    current_position = get_current_position()

    print(f"交易信号: {signal_data['signal']}")
    print(f"信心程度: {signal_data['confidence']}")
    print(f"理由: {signal_data['reason']}")
    print(f"当前持仓: {current_position}")

    if TRADE_CONFIG['test_mode']:
        print("测试模式 - 仅模拟交易")
        return

    try:
        # WEEX API 下单函数 - 符合DOC.md规范
        def place_order(order_params_list):
            """下单辅助函数 - 根据WEEX API DOC.md规范"""
            # 构建批量下单参数
            params = {
                "symbol": order_params_list[0]['symbol'],  # 从第一个订单获取交易对
                "orderList": order_params_list
            }
            
            print(f"下单参数: {params}")
            # 使用正确的现货API端点路径
            order_response = exchange._request('POST', '/api/v2/trade/batch-orders', params=params)
            print(f"下单响应: {order_response}")
            
            # 按照DOC.md规范检查响应格式
            if not order_response:
                print("下单失败: 响应为空")
                return False
            
            if isinstance(order_response, dict):
                # WEEX API响应应该包含code字段
                if 'code' in order_response:
                    if order_response['code'] == '00000':
                        print("下单成功")
                        return True
                    else:
                        print(f"下单失败: {order_response.get('msg', '未知错误')}")
                        return False
                else:
                    print("下单失败: 响应格式不符合API规范")
                    return False
            
            print("下单失败: 响应格式错误")
            return False
        
        # 格式化交易对为WEEX现货API要求的格式，根据DOC.md规范，可能需要_SPBL后缀
        symbol = TRADE_CONFIG['symbol'].replace('/', '')
        
        # 获取当前价格
        current_price = price_data['price']
        
        # 交易逻辑
        if signal_data['signal'] == 'BUY':
            # 现货交易中，买入相当于开多仓
            # 注意：现货交易不支持做空，因此不需要处理short持仓的情况
            if not current_position:
                print("开多仓...")
                params = [{
                    "symbol": symbol,  # 根据DOC.md规范，交易对格式可能需要_SPBL后缀
                    "side": "BUY",  # 大写
                    "type": "LIMIT",  # 使用type字段且大写
                    "price": str(current_price),  # 使用当前价格作为限价
                    "quantity": str(TRADE_CONFIG['amount']),
                    "timeInForce": "GTC",  # 符合DOC.md规范的时间生效类型
                    "clientOrderId": f"{int(time.time())}{random.randint(100000, 999999)}"
                }]
                place_order(params)
            else:
                print("已有持仓，不执行买入操作")

        elif signal_data['signal'] == 'SELL':
            # 现货交易中，卖出相当于平多仓
            if current_position and current_position['side'] == 'long':
                print("卖出持仓...")
                params = [{
                    "symbol": symbol,  # 根据DOC.md规范，交易对格式可能需要_SPBL后缀
                    "side": "SELL",  # 大写
                    "type": "LIMIT",  # 使用type字段且大写
                    "price": str(current_price),  # 使用当前价格作为限价
                    "quantity": str(current_position['size']),
                    "timeInForce": "GTC",  # 符合DOC.md规范的时间生效类型
                    "clientOrderId": f"{int(time.time())}{random.randint(100000, 999999)}"
                }]
                place_order(params)
            else:
                print("没有持仓可卖出")

        elif signal_data['signal'] == 'HOLD':
            print("建议观望，不执行交易")
            return

        time.sleep(2)
        position = get_current_position()
        print(f"更新后持仓: {position}")

    except Exception as e:
        print(f"订单执行失败: {e}")
        import traceback
        traceback.print_exc()

def trading_bot():
    """主交易机器人函数"""
    print("\n" + "=" * 60)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. 获取K线数据
    price_data = get_btc_ohlcv()
    if not price_data:
        return

    print(f"BTC当前价格: ${price_data['price']:,.2f}")
    print(f"数据周期: {TRADE_CONFIG['timeframe']}")
    print(f"价格变化: {price_data['price_change']:+.2f}%")

    # 2. 使用DeepSeek分析
    signal_data = analyze_with_deepseek(price_data)
    if not signal_data:
        return

    # 3. 执行交易
    execute_trade(signal_data, price_data)


def main():
    """主函数"""
    print("BTC/USDT 自动交易机器人启动成功！")
    print("注意：当前使用WEEX现货API，仅支持买入和卖出操作，不支持杠杆和做空功能")

    if TRADE_CONFIG['test_mode']:
        print("当前为模拟模式，不会真实下单")
    else:
        print("实盘交易模式，请谨慎操作！")

    print(f"交易周期: {TRADE_CONFIG['timeframe']}")
    print("已启用K线数据分析和持仓跟踪功能")

    # 设置交易所
    if not setup_exchange():
        print("交易所初始化失败，程序退出")
        return

    # 根据时间周期设置执行频率
    if TRADE_CONFIG['timeframe'] == '1h':
        # 每小时执行一次，在整点后的1分钟执行
        schedule.every().hour.at(":01").do(trading_bot)
        print("执行频率: 每小时一次")
    elif TRADE_CONFIG['timeframe'] == '15m':
        # 每15分钟执行一次
        schedule.every(15).minutes.do(trading_bot)
        print("执行频率: 每15分钟一次")
    else:
        # 默认1小时
        schedule.every().hour.at(":01").do(trading_bot)
        print("执行频率: 每小时一次")

    # 立即执行一次
    trading_bot()

    # 循环执行
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    """
    测试和使用指南：
    
    1. 确保.env文件中包含以下环境变量：
       - WEEX_API_KEY: WEEX交易所API密钥
       - WEEX_SECRET: WEEX交易所API密钥
       - DEEPSEEK_API_KEY: DeepSeek API密钥
    
    2. 首次运行前，建议将TRADE_CONFIG中的test_mode设置为True进行测试
    
    3. 根据需要调整交易参数：
       - symbol: 交易对，如'BTC/USDT'（现货交易对格式）
       - amount: 交易数量（注意：现货交易对可能需要特定后缀）
       - timeframe: 时间周期，支持'15m', '1h', '4h', '1d'
    
    4. 脚本会根据设置的时间周期自动定时执行交易策略
    
    5. 日志会显示详细的API响应，便于调试
    """
    main()