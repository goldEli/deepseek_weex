# Get History Orders
GET /capi/v2/order/history

Request parameters

Parameter	Type	Required?	Description
symbol	String	No	Trading pair
pageSize	Integer	No	Items per page
createDate	Long	No	Number of days (must be ≤ 90 and cannot be negative)

Request example

curl "https://api-contract.weex.com/capi/v2/order/history?symbol=cmt_bchusdt&pageSize=10&createDate=1742213506548" \
   -H "ACCESS-KEY:*******" \
   -H "ACCESS-SIGN:*******" \
   -H "ACCESS-PASSPHRASE:*****" \
   -H "ACCESS-TIMESTAMP:1659076670000" \
   -H "locale:zh-CN" \
   -H "Content-Type: application/json"


Response parameters

Paramete	Type	Description
Symbol	string	Trading pair
size	string	Order amount
client_oid	string	Client identifier
createTime	long	Creation time
filled_qty	string	Filled quantity
fee	string	Transaction fee
order_id	string	Order ID
price	string	Order price
price_avg	string	Average filled price
status	string	Order status
pending: The order has been submitted for matching, but the result has not been processed yet.
open: The order has been processed by the matching engine (order placed), and may have been partially filled.
filled: The order has been completely filled [final state].
canceling: The order is being canceled.
canceled: The order has been canceled. It may have been partially filled. [final state].
untriggered: The conditional order has not been triggered yet.
type	string	Order type
open_long: Open long
open_short: Open short
close_long: Close long
close_short: Close short
offset_liquidate_long: Reduce position, close long
offset_liquidate_short: Reduce position, close short
agreement_close_long: Agreement close long
agreement_close_short: Agreement close short
burst_liquidate_long: Liquidation close long
burst_liquidate_short: Liquidation close short
order_type	string	Order type
normal: Regular limit order, valid until canceled.
postOnly: Maker-only order
fok: Fill or kill, must be completely filled or canceled immediately.
ioc: Immediate or cancel, fill as much as possible and cancel the remaining.
totalProfits	string	Total PnL
contracts	Integer	Order size in contract units
filledQtyContracts	Integer	Filled quantity in contract units
presetTakeProfitPrice	String	Preset take-profit price
presetStopLossPrice	String	Preset stop-loss price

Response example

[
{
  "symbol": "cmt_btcusdt",
  "size": "2143",
  "client_oid": "892754345",
  "createTime": "1716595200000",
  "filled_qty": "53",
  "fee": "12",
  "order_id": "5716595202300",
  "price": "65000",
  "price_avg": "6200",
  "status": "pending",
  "type": "open_long",
  "order_type": "normal",
  "totalProfits": "100",
  "contracts": 21430
}
]