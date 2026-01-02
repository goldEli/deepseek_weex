#!/usr/bin/env python3
"""
多档位移动止盈交易机器人
实现智能的多档位止盈止损策略，自动监控持仓并执行止盈止损操作
"""

import os
import time
from dotenv import load_dotenv
import logging

# 导入我们的WEEX SDK
from weex_sdk import WeexClient

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_tier_bot.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()

# 交易所配置
WEEX_API_KEY = os.getenv('WEEX_API_KEY')
WEEX_SECRET = os.getenv('WEEX_SECRET') or os.getenv('WEEX_API_SECRET')
WEEX_ACCESS_PASSPHRASE = os.getenv('WEEX_ACCESS_PASSPHRASE')

# 初始化WEEX交易所客户端
exchange = WeexClient(
    api_key=WEEX_API_KEY,
    api_secret=WEEX_SECRET,
    api_passphrase=WEEX_ACCESS_PASSPHRASE,
    testnet=False
)

# 多档位止盈策略配置
STRATEGY_CONFIG = {
    'symbol': 'cmt_btcusdt',
    'monitor_interval': 4,  # 监控间隔（秒）
    
    # 固定止损设置
    'fixed_stop_loss': 0.05,  # 5% 强制止损
    
    # 多档位止盈配置
    'tiers': {
        0: {  # 低档保护
            'trigger_profit': 0.03,  # 3%利润触发
            'stop_loss_ratio': 0.20,  # 20%止损比例
            'description': '低档保护止盈'
        },
        1: {  # 第一档
            'trigger_profit': 0.05,  # 5%利润触发
            'stop_loss_ratio': 0.30,  # 30%止损比例
            'description': '第一档移动止盈'
        },
        2: {  # 第二档
            'trigger_profit': 0.10,  # 10%利润触发
            'stop_loss_ratio': 0.50,  # 50%止损比例
            'description': '第二档移动止盈'
        }
    },
    
    'test_mode': False  # 测试模式
}

# 全局状态变量
class PositionTracker:
    def __init__(self):
        self.positions = {}        # symbol -> position_amount
        self.highest_profits = {}  # symbol -> highest_profit_pct
        self.current_tiers = {}    # symbol -> current_tier_level
        self.entry_prices = {}     # symbol -> entry_price
        self.position_sides = {}   # symbol -> side (long/short)
        
    def update_position(self, symbol, amount, side, entry_price):
        """更新持仓信息"""
        self.positions[symbol] = amount
        self.position_sides[symbol] = side
        self.entry_prices[symbol] = entry_price
        
        # 初始化最高盈利记录
        if symbol not in self.highest_profits:
            self.highest_profits[symbol] = 0.0
        
        # 初始化档位记录
        if symbol not in self.current_tiers:
            self.current_tiers[symbol] = -1
    
    def remove_position(self, symbol):
        """移除持仓信息"""
        self.positions.pop(symbol, None)
        self.highest_profits.pop(symbol, None)
        self.current_tiers.pop(symbol, None)
        self.entry_prices.pop(symbol, None)
        self.position_sides.pop(symbol, None)

# 初始化持仓跟踪器
tracker = PositionTracker()

def get_current_market_price(symbol):
    """获取当前市场价格"""
    try:
        # 获取最新的OHLCV数据
        ohlcv = exchange.fetch_ohlcv(symbol, '1m', limit=1)
        if ohlcv and len(ohlcv) > 0:
            return ohlcv[0][4]  # close价格
        return None
    except Exception as e:
        logging.error(f"获取市场价格失败 {symbol}: {e}")
        return None

def get_current_positions():
    """获取当前持仓"""
    try:
        positions = exchange.fetch_positions(STRATEGY_CONFIG['symbol'])
        active_positions = []
        
        for pos in positions:
            if pos['symbol'] == STRATEGY_CONFIG['symbol'] and pos['size'] > 0:
                active_positions.append({
                    'symbol': pos['symbol'],
                    'side': pos['side'],  # 'long' or 'short'
                    'size': pos['size'],
                    'entry_price': pos['entryPrice'],
                    'current_price': get_current_market_price(pos['symbol']),
                    'unrealized_pnl': pos['unrealizedPnl'],
                    'leverage': pos['leverage']
                })
        
        return active_positions
    except Exception as e:
        logging.error(f"获取持仓失败: {e}")
        return []

def calculate_profit_percentage(position, current_price):
    """计算盈利百分比"""
    if position['side'] == 'long':
        return (current_price - position['entry_price']) / position['entry_price']
    else:  # short
        return (position['entry_price'] - current_price) / position['entry_price']

def calculate_dynamic_stop_loss(position, current_price, tier_level):
    """计算动态止损价格"""
    entry_price = position['entry_price']
    stop_loss_ratio = STRATEGY_CONFIG['tiers'][tier_level]['stop_loss_ratio']
    
    if position['side'] == 'long':
        # 多仓：止损价格 = 入场价格 * (1 - 止损比例)
        return entry_price * (1 - stop_loss_ratio)
    else:  # short
        # 空仓：止损价格 = 入场价格 * (1 + 止损比例)
        return entry_price * (1 + stop_loss_ratio)

def should_close_position(position, current_price):
    """判断是否应该平仓"""
    profit_pct = calculate_profit_percentage(position, current_price)
    symbol = position['symbol']
    
    # 检查固定止损
    if profit_pct <= -STRATEGY_CONFIG['fixed_stop_loss']:
        return True, f"固定止损触发: {profit_pct:.2%}"
    
    # 更新最高盈利记录
    if profit_pct > tracker.highest_profits[symbol]:
        tracker.highest_profits[symbol] = profit_pct
    
    # 检查档位止损
    current_tier = tracker.current_tiers[symbol]
    
    for tier_level in range(len(STRATEGY_CONFIG['tiers']) - 1, -1, -1):
        tier_config = STRATEGY_CONFIG['tiers'][tier_level]
        trigger_profit = tier_config['trigger_profit']
        
        # 如果达到触发条件
        if tracker.highest_profits[symbol] >= trigger_profit:
            # 如果档位升级或者当前档位匹配
            if tier_level > current_tier or current_tier == -1:
                # 更新当前档位
                tracker.current_tiers[symbol] = tier_level
                
                # 计算新的止损价格
                stop_loss_price = calculate_dynamic_stop_loss(position, current_price, tier_level)
                
                # 检查是否触发止损
                if position['side'] == 'long' and current_price <= stop_loss_price:
                    return True, f"{tier_config['description']}止损触发: {stop_loss_price:.2f}"
                elif position['side'] == 'short' and current_price >= stop_loss_price:
                    return True, f"{tier_config['description']}止损触发: {stop_loss_price:.2f}"
                
                break
    
    return False, ""

def execute_close_order(position, reason):
    """执行平仓操作"""
    try:
        if STRATEGY_CONFIG['test_mode']:
            logging.info(f"[测试模式] 平仓原因: {reason}")
            logging.info(f"[测试模式] 持仓: {position['symbol']} {position['side']} {position['size']}")
            return True
        
        # 执行平仓
        side = 'buy' if position['side'] == 'sell' else 'sell'
        
        result = exchange.create_market_order(
            position['symbol'],
            side,
            position['size'],
            reduce_only=True
        )
        
        logging.info(f"平仓成功: {reason}")
        logging.info(f"平仓结果: {result}")
        
        # 移除持仓跟踪
        tracker.remove_position(position['symbol'])
        
        return True
        
    except Exception as e:
        logging.error(f"平仓失败: {e}")
        return False

def monitor_positions():
    """监控持仓并执行止盈止损"""
    logging.info("开始监控持仓...")
    
    while True:
        try:
            # 获取当前持仓
            current_positions = get_current_positions()
            
            # 同步持仓跟踪器中的持仓信息
            current_symbols = {pos['symbol'] for pos in current_positions}
            tracked_symbols = set(tracker.positions.keys())
            
            # 添加新持仓
            for position in current_positions:
                tracker.update_position(
                    position['symbol'],
                    position['size'],
                    position['side'],
                    position['entry_price']
                )
            
            # 移除已平仓的记录
            for symbol in tracked_symbols - current_symbols:
                tracker.remove_position(symbol)
            
            # 检查每个持仓
            for position in current_positions:
                symbol = position['symbol']
                current_price = position['current_price']
                
                if current_price is None:
                    continue
                
                profit_pct = calculate_profit_percentage(position, current_price)
                current_tier = tracker.current_tiers[symbol]
                
                # 记录状态
                logging.info(f"持仓监控 {symbol}:")
                logging.info(f"  方向: {position['side']}")
                logging.info(f"  数量: {position['size']}")
                logging.info(f"  入场价: {position['entry_price']:.2f}")
                logging.info(f"  当前价: {current_price:.2f}")
                logging.info(f"  盈亏: {profit_pct:.2%}")
                logging.info(f"  最高盈利: {tracker.highest_profits[symbol]:.2%}")
                logging.info(f"  当前档位: {current_tier}")
                
                # 检查是否需要平仓
                should_close, close_reason = should_close_position(position, current_price)
                
                if should_close:
                    logging.warning(f"执行平仓: {close_reason}")
                    execute_close_order(position, close_reason)
                else:
                    # 显示当前档位信息
                    if current_tier >= 0:
                        tier_config = STRATEGY_CONFIG['tiers'][current_tier]
                        stop_loss_price = calculate_dynamic_stop_loss(position, current_price, current_tier)
                        logging.info(f"  当前档位: {tier_config['description']}")
                        logging.info(f"  止损价格: {stop_loss_price:.2f}")
            
            logging.info(f"监控完成，等待 {STRATEGY_CONFIG['monitor_interval']} 秒后继续...")
            time.sleep(STRATEGY_CONFIG['monitor_interval'])
            
        except KeyboardInterrupt:
            logging.info("用户中断监控")
            break
        except Exception as e:
            logging.error(f"监控过程出错: {e}")
            time.sleep(STRATEGY_CONFIG['monitor_interval'])

def main():
    """主函数"""
    logging.info("=" * 60)
    logging.info("多档位移动止盈交易机器人启动")
    logging.info("=" * 60)
    
    # 显示策略配置
    logging.info("策略配置:")
    logging.info(f"  交易对: {STRATEGY_CONFIG['symbol']}")
    logging.info(f"  监控间隔: {STRATEGY_CONFIG['monitor_interval']} 秒")
    logging.info(f"  固定止损: {STRATEGY_CONFIG['fixed_stop_loss']:.1%}")
    
    for tier_level, config in STRATEGY_CONFIG['tiers'].items():
        logging.info(f"  档位{tier_level}: {config['description']}")
        logging.info(f"    触发盈利: {config['trigger_profit']:.1%}")
        logging.info(f"    止损比例: {config['stop_loss_ratio']:.1%}")
    
    if STRATEGY_CONFIG['test_mode']:
        logging.warning("当前为测试模式，不会真实执行交易")
    
    # 检查交易所连接
    try:
        positions = exchange.fetch_positions(STRATEGY_CONFIG['symbol'])
        logging.info("交易所连接正常")
    except Exception as e:
        logging.error(f"交易所连接失败: {e}")
        return
    
    # 开始监控
    monitor_positions()

if __name__ == "__main__":
    main()