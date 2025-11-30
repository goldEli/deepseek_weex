
定义缺失的方法 已经添加 curl 参考
定义缺失的方法 - 需要用户提供curl参考来实现以下功能：
1. fetch_ohlcv - 获取K线数据（对应exchange.fetch_ohlcv）
参考“ curl "https://api-contract.weex.com/capi/v2/market/candles?symbol=cmt_bchusdt&granularity=1m&startTime=1716707460000&endTime=1816707460000"”

Request parameters
symbol	String	Yes	Trading pair
granularity	String	Yes	Candlestick interval[1m,5m,15m,30m,1h,4h,12h,1d,1w]
limit	Integer	No	Default: 100
priceType	String	No	Price Type : LAST latest market price; MARK mark; INDEX index;
LAST by default

Response parameters

Parameter	Type	Description
[	array	array
[	array	array
> string	string	Candlestick time
> string	string	Opening price
> string	string	Highest price
> string	string	Lowest price
> string	string	Closing price
> string	string	Trading size
> string	string	Trading volume
]	array	array
]	array	array


Response example

[
    [
        "1716707460000",//Candlestick time
        "69174.3",//Opening price
        "69174.4",//Highest price
        "69174.1",//Lowest price
        "69174.3",//Closing price
        "0", //Trading size
        "0.011" //Trading volume
    ]
]

------------------------------
2. fetch_positions - 获取持仓情况（对应exchange.fetch_positions）
参考 
curl "https://api-contract.weex.com/capi/v2/account/position/allPosition" \
   -H "ACCESS-KEY:*******" \
   -H "ACCESS-SIGN:*******" \
   -H "ACCESS-PASSPHRASE:*****" \
   -H "ACCESS-TIMESTAMP:1659076670000" \
   -H "locale:zh-CN" \
   -H "Content-Type: application/json"

Response parameters

Parameter	Type	Description
id	Long	Position ID
account_id	Long	Associated account ID
coin_id	Integer	Associated collateral currency ID
contract_id	Long	Associated futures ID
symbol	String	Trading pair
side	String	Position direction such as Long or short
margin_mode	String	Margin mode of current position
SHARED: Cross Mode
ISOLATED: Isolated Mode
separated_mode	String	Current position's separated mode
COMBINED: Combined mode
SEPARATED: Separated mode
separated_open_order_id	Long	Opening order ID of separated position
leverage	String	Position leverage
size	String	Current position size
open_value	String	Initial value at position opening
open_fee	String	Opening fee
funding_fee	String	Funding fee
isolated_margin	String	Isolated margin
is_auto_append_isolated_margin	boolean	Whether the auto-adding of funds for the isolated margin is enabled (only for isolated mode)
cum_open_size	String	Accumulated opened positions
cum_open_value	String	Accumulated value of opened positions
cum_open_fee	String	Accumulated fees paid for opened positions
cum_close_size	String	Accumulated closed positions
cum_close_value	String	Accumulated value of closed positions
cum_close_fee	String	Accumulated fees paid for closing positions
cum_funding_fee	String	Accumulated settled funding fees
cum_liquidate_fee	String	Accumulated liquidation fees
created_match_sequence_id	Long	Matching engine sequence ID at creation
updated_match_sequence_id	Long	Matching engine sequence ID at last update
created_time	Long	Creation time
updated_time	Long	Update time
contractVal	String	Futures face value
unrealizePnl	String	Unrealized PnL
liquidatePrice	String	Estimated liquidation price
If the value = 0, it means the position is at low risk and there is no liquidation price at this time

Response example

[
    {
        "id": 0,
        "account_id": 0,
        "coin_id": 2,
        "contract_id": 10000002,
        "side": "Long",
        "margin_mode": "SHARED",
        "separated_mode": "COMBINED",
        "separated_open_order_id": 0,
        "leverage": "1",
        "size": "0.",
        "open_value": "0",
        "open_fee": "0.000000",
        "funding_fee": "0.000001",
        "isolated_margin": "0",
        "is_auto_append_isolated_margin": false,
        "cum_open_size": "0",
        "cum_open_value": "09",
        "cum_open_fee": "0.000000",
        "cum_close_size": "0",
        "cum_close_value": "0",
        "cum_close_fee": "0.000000",
        "cum_funding_fee": "0",
        "cum_liquidate_fee": "0",
        "created_match_sequence_id": 0,
        "updated_match_sequence_id": 0,
        "created_time": 1708395319042,
        "updated_time": 1713341325556
    }
]

------------------------------
3. create_market_order - 创建市价单（对应exchange.create_market_order）
参考
curl -X POST "https://api-contract.weex.com/capi/v2/order/placeOrder" \
   -H "ACCESS-KEY:*******" \
   -H "ACCESS-SIGN:*" \
   -H "ACCESS-PASSPHRASE:*" \
   -H "ACCESS-TIMESTAMP:1659076670000" \
   -H "locale:zh-CN" \
   -H "Content-Type: application/json" \
   -d '{"symbol": "cmt_bchusdt","client_oid": "111111111222222","size": "1","type": "1","order_type": "0",
     "match_price": "0","price": "100","presetTakeProfitPrice": "105","presetStopLossPrice": "95"}'

Request parameters

Parameter	Type	Required?	Description
symbol	String	Yes	Trading pair
client_oid	String	Yes	Custom order ID (no more than 40 characters)
size	String	Yes	Order quantity (cannot be zero or negative).
type	String	Yes	1: Open long, 2: Open short, 3: Close long, 4: Close short
order_type	String	Yes	0: Normal, 1: Post-Only, 2: Fill-Or-Kill, 3: Immediate Or Cancel
match_price	String	Yes	0: Limit price, 1: Market price
price	String	Yes	Order price (this is required for limit orders, and its accuracy and step size follow the futures information endpoint)
presetTakeProfitPrice	BigDecimal	No	Preset take-profit price
presetStopLossPrice	BigDecimal	No	Preset stop-loss price
marginMode	Integer	No	Margin mode
1: Cross Mode
3: Isolated Mode
Default is 1 (Cross Mode)
separatedMode	Integer	No	Position segregation mode
1: Combined mode
2: Separated mode
Default is 1 (Combined mode)

Response parameters

Parameter	Type	Description
client_oid	string	Client-generated order identifier
order_id	string	Order ID

{
	"client_oid": null,
	"order_id": "596471064624628269"
}

------------------end-------------------