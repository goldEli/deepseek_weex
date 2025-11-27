# WEEX 现货API文档

本文档基于WEEX官方现货API文档整理，包含配置类、市场数据类和账户类API的详细说明。

## 目录

- [1. 配置类API](#1-配置类api)
  - [1.1 获取服务器时间](#11-获取服务器时间)
  - [1.2 获取币种信息](#12-获取币种信息)
  - [1.3 获取所有交易对信息](#13-获取所有交易对信息)
  - [1.4 获取单个交易对信息](#14-获取单个交易对信息)
- [2. 市场数据类API](#2-市场数据类api)
  - [2.1 获取单个交易对行情](#21-获取单个交易对行情)
  - [2.2 获取所有交易对行情](#22-获取所有交易对行情)
  - [2.3 获取成交数据](#23-获取成交数据)
  - [2.4 获取K线数据](#24-获取k线数据)
  - [2.5 获取深度数据](#25-获取深度数据)
- [3. 账户类API](#3-账户类api)
  - [3.1 获取账户资产](#31-获取账户资产)
  - [3.2 获取交易记录](#32-获取交易记录)
  - [3.3 获取资金流水](#33-获取资金流水)
  - [3.4 获取转账记录](#34-获取转账记录)
- [4. 交易类API](#4-交易类api)
  - [4.1 下单](#41-下单)
  - [4.2 取消订单](#42-取消订单)
  - [4.3 批量下单](#43-批量下单)
  - [4.4 获取订单信息](#44-获取订单信息)
  - [4.5 获取历史订单](#45-获取历史订单)
  - [4.6 获取当前订单](#46-获取当前订单)
  - [4.7 获取成交明细](#47-获取成交明细)
  - [4.8 下单（触发单）](#48-下单触发单)
  - [4.9 取消触发单](#49-取消触发单)
  - [4.10 获取当前计划订单](#410-获取当前计划订单)
  - [4.11 获取历史计划订单](#411-获取历史计划订单)

## 1. 配置类API

### 1.1 获取服务器时间

**API描述**：获取WEEX服务器的当前时间戳。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/public/time`
- 权重(IP)：1

**请求参数**：无

**请求示例**：
```
curl "https://api-spot.weex.com/api/v2/public/time"
```

**响应参数**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| code  | string | 响应码，"00000"表示成功 |
| msg   | string | 响应消息 |
| requestTime | long | 请求时间戳 |
| data  | long | 服务器时间戳 |

**响应示例**：
```json
{
    "code": "00000",
    "msg": "success",
    "requestTime": 1622097118135,
    "data": 1622097118134
}
```

### 1.2 获取币种信息

**API描述**：获取平台支持的币种基本信息。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/public/currencies`

**响应示例**：
```json
{
    "code": "00000",
    "msg": "success",
    "requestTime": 1622097139437,
    "data": [
        {
            "coinId": "1",
            "coinName": "BTC",
            "transfer": "true",
            "chains": [
                {
                    "chain": null,
                    "needTag": "false",
                    "withdrawAble": "true",
                    "rechargeAble": "true",
                    "withdrawFee": "0.005",
                    "depositConfirm": "1",
                    "withdrawConfirm": "1",
                    "minDepositAmount": "0.001",
                    "minWithdrawAmount": "0.001",
                    "browserUrl": "https://blockchair.com/bitcoin/testnet/transaction/"
                }
            ]
        },
        {
            "coinId": "2",
            "coinName": "USDT",
            "transfer": "true",
            "chains": [
                {
                    "chain": "ERC20",
                    "needTag": "false",
                    "withdrawAble": "true",
                    "rechargeAble": "true",
                    "withdrawFee": "0.01",
                    "depositConfirm": "12",
                    "withdrawConfirm": "1",
                    "minDepositAmount": "0.1",
                    "minWithdrawAmount": "0.1",
                    "browserUrl": "https://ropsten.etherscan.io/tx/"
                }
            ]
        }
    ]
}
```

### 1.3 获取所有交易对信息

**API描述**：获取平台支持API交易的所有交易对。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/public/products`
- 权重(IP)：1

**请求参数**：无

**请求示例**：
```
curl "https://api-spot.weex.com/api/v2/public/products"
```

**响应参数**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| code  | string | 响应码，"00000"表示成功 |
| msg   | string | 响应消息 |
| requestTime | long | 请求时间戳 |
| data  | array | 支持API交易的交易对列表 |

**响应示例**：
```json
{
  "code": "00000",
  "data": ["ETHUSDC_SPBL", "BTCUSDT_SPBL"],
  "msg": "success",
  "requestTime": "1743647243696"
}
```

### 1.4 获取单个交易对信息

**API描述**：获取指定交易对的详细信息。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/public/products/{symbol}`

**响应示例**：
```json
{
  "code": "00000",
  "msg": "success",
  "requestTime": 1743661516052,
  "data": [
    {
      "symbol": "BTCUSDT_SPBL",
      "baseCoin": "BTC",
      "quoteCoin": "USDT",
      "tickSize": "0.1",
      "stepSize": "0.00000001",
      "minTradeAmount": "0.00001",
      "maxTradeAmount": "99999",
      "takerFeeRate": "0.001",
      "makerFeeRate": "0",
      "buyLimitPriceRatio": "0.99",
      "sellLimitPriceRatio": "0.99",
      "marketBuyLimitSize": "99999",
      "marketSellLimitSize": "99999",
      "marketFallbackPriceRatio": "0",
      "enableTrade": true,
      "enableDisplay": true,
      "displayDigitMerge": "",
      "displayNew": false,
      "displayHot": false,
      "supportTracing": true,
      "supportPlanMarket": true
    }
  ]
}
```

## 2. 市场数据类API

### 2.1 获取单个交易对行情

**API描述**：获取单个交易对的最新行情信息。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/market/ticker/{symbol}`

**响应参数**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| code  | string | 响应码，"00000"表示成功 |
| msg   | string | 响应消息 |
| requestTime | long | 请求时间戳 |
| data  | object | 交易对行情数据 |

**data字段详情**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| symbol | string | 交易对符号 |
| priceChange | string | 价格变动量 |
| priceChangePercent | string | 价格变动百分比 |
| trades | integer | 成交笔数 |
| size | string | 成交量 |
| value | string | 成交额 |
| high | string | 最高价 |
| low | string | 最低价 |
| open | string | 开盘价 |
| close | string | 收盘价 |
| highTime | long | 最高价时间 |
| lowTime | long | 最低价时间 |
| startTime | long | 开始时间 |
| endTime | long | 结束时间 |
| lastPrice | string | 最新价格 |
| openInterest | string | 未平仓合约数 |
| ts | long | 时间戳 |

**响应示例**：
```json
{
  "code": "00000",
  "msg": "success",
  "requestTime": 1743665793483,
  "data": {
    "symbol": "BTCUSDT_SPBL",
    "priceChange": "-965.6",
    "priceChangePercent": "-0.011451",
    "trades": 105901,
    "size": "78570.57284800",
    "value": "6731333236.9492884000",
    "high": "88495.5",
    "low": "82175.9",
    "open": "84319.6",
    "close": "83354.0",
    "highTime": 1743625002550,
    "lowTime": 1743638655112,
    "startTime": 1743576300000,
    "endTime": 1743665400000,
    "lastPrice": "83354.0",
    "openInterest": "0",
    "ts": 1750060557824
  }
}
```

### 2.2 获取所有交易对行情

**API描述**：获取所有交易对的最新行情信息。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/market/tickers`

**响应参数**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| code  | string | 响应码，"00000"表示成功 |
| msg   | string | 响应消息 |
| requestTime | long | 请求时间戳 |
| data  | array | 所有交易对行情数据数组 |

**响应示例**：
```json
{
  "code": "00000",
  "msg": "success",
  "requestTime": 1743667090710,
  "data": [{
    "symbol": "BTCUSDT_SPBL",
    "priceChange": "-628.0",
    "priceChangePercent": "-0.007465",
    "trades": 106283,
    "size": "78680.72453000",
    "value": "6740487302.7932238000",
    "high": "88495.5",
    "low": "82175.9",
    "open": "84125.9",
    "close": "83497.9",
    "highTime": 1743625002550,
    "lowTime": 1743638655112,
    "startTime": 1743577200000,
    "endTime": 1743666300000,
    "lastPrice": "83497.9",
    "openInterest": "0",
    "ts": 1750060557824
  }]
}
```

### 2.3 获取成交数据

**API描述**：获取指定交易对的最近成交记录。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/market/trades/{symbol}`

**响应参数**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| code  | string | 响应码，"00000"表示成功 |
| msg   | string | 响应消息 |
| requestTime | long | 请求时间戳 |
| data  | array | 成交数据数组 |

**data数组元素详情**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| symbol | string | 交易对符号 |
| tradeId | string | 成交订单ID |
| fillTime | long | 成交时间戳 |
| fillPrice | string | 成交价格 |
| fillQuantity | string | 成交数量 |
| tradeValue | string | 成交总金额(价格×数量) |
| bestMatch | boolean | 是否完全匹配 |
| buyerMaker | boolean | 买方是否为做市商 |

**响应示例**：
```json
{
    "code": "00000",
    "msg": "success",
    "requestTime": 1743668717640,
    "data": [
        {
            "symbol": "BTCUSDT_SPBL",
            "tradeId": "778a5376-a0b6-4c8f-ab64-dd6ea40f896e",
            "fillTime": 1743668713364,
            "fillPrice": "83609.7",
            "fillQuantity": "0.00011400",
            "tradeValue": "9.531505800",
            "bestMatch": true,
            "buyerMaker": true
        }
    ]
}
```

### 2.4 获取K线数据

**API描述**：获取指定交易对的K线数据。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/market/candles/{symbol}`

**请求参数**：
- interval：时间周期（如1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w）
- limit：返回数据条数
- startTime：开始时间戳（可选）
- endTime：结束时间戳（可选）

**响应参数**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| code  | string | 响应码，"00000"表示成功 |
| msg   | string | 响应消息 |
| requestTime | long | 请求时间戳 |
| data  | array | K线数据数组 |

**data数组元素详情**：
每个K线数据是一个数组，包含以下元素：
1. 时间戳（毫秒）
2. 开盘价
3. 最高价
4. 最低价
5. 收盘价
6. 成交量
7. 成交额

**响应示例**：
```json
{
  "code": "00000",
  "msg": "success",
  "requestTime": 1743669821003,
  "data": [
    [
      1743669000000,
      "83654.0",
      "83778.0",
      "83531.5",
      "83688.7",
      "248.17024800",
      "20755885.859164900"
    ],
    [
      1743667200000,
      "83457.9",
      "83719.0",
      "83457.9",
      "83654.0",
      "247.94000200",
      "20730711.264144200"
    ]
  ]
}
```

### 2.5 获取深度数据

**API描述**：获取指定交易对的订单簿深度数据。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/market/depth/{symbol}`

**请求参数**：
- limit：返回数据条数（可选）

**响应参数**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| code  | string | 响应码，"00000"表示成功 |
| msg   | string | 响应消息 |
| requestTime | long | 请求时间戳 |
| data  | object | 订单簿深度数据 |

**data字段详情**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| asks | array | 卖单价格和数量数组，每项为[价格, 数量] |
| bids | array | 买单价格和数量数组，每项为[价格, 数量] |
| timestamp | string | 时间戳 |

**响应示例**：
```json
{
    "code": "00000",
    "msg": "success",
    "requestTime": 1622102974025,
    "data": {
        "asks": [
            [
                "38084.5",
                "0.0039"
            ],
            [
                "38085.7",
                "0.0018"
            ],
            [
                "38086.7",
                "0.0310"
            ],
            [
                "38088.2",
                "0.5303"
            ]
        ],
        "bids": [
            [
                "38073.7",
                "0.4993000000000000"
            ],
            [
                "38073.4",
                "0.4500"
            ],
            [
                "38073.3",
                "0.1179"
            ],
            [
                "38071.5",
                "0.2162"
            ]
        ],
        "timestamp": "1622102974025"
    }
}
```

## 3. 账户类API

### 3.1 获取账户资产

**API描述**：获取账户中所有币种的资产信息。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/account/balance`
- 认证：需要API密钥、签名和时间戳

**响应参数**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| code  | string | 响应码，"00000"表示成功 |
| msg   | string | 响应消息 |
| requestTime | long | 请求时间戳 |
| data  | array | 资产数据数组 |

**data数组元素详情**：
| 字段名 | 类型 | 字段描述 |
|-------|------|---------|
| coinId | integer | 币种ID |
| coinName | string | 币种名称 |
| available | string | 可用余额 |
| frozen | string | 冻结余额 |
| equity | string | 总资产（可用+冻结） |

**响应示例**：
```json
{
  "code": "00000",
  "msg": "success",
  "requestTime": 1743729400189,
  "data": [{
    "coinId": 1,
    "coinName": "BTC",
    "available": "0.0040000000000000",
    "frozen": "0",
    "equity": "0.0040000000000000"
  }, {
    "coinId": 2,
    "coinName": "USDT",
    "available": "10000999657.8927028500000000",
    "frozen": "0",
    "equity": "10000999657.8927028500000000"
  }]
}
```

### 3.2 获取交易记录

**API描述**：获取账户的交易记录。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/account/bills`
- 认证：需要API密钥、签名和时间戳

**请求参数**：
- coinId：币种ID（可选）
- type：交易类型（可选）
- startTime：开始时间戳（可选）
- endTime：结束时间戳（可选）
- page：页码（可选）
- pageSize：每页条数（可选）

### 3.3 获取资金流水

**API描述**：获取账户的资金流水记录。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/account/fund/bills`
- 认证：需要API密钥、签名和时间戳

**请求参数**：
- coinName：币种名称（可选）
- type：流水类型（可选）
- startTime：开始时间戳（可选）
- endTime：结束时间戳（可选）
- page：页码（可选）
- pageSize：每页条数（可选）

### 3.4 获取转账记录

**API描述**：获取账户的转账记录。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/account/transfer/records`
- 认证：需要API密钥、签名和时间戳

**请求参数**：
- startTime：开始时间戳（可选）
- endTime：结束时间戳（可选）
- page：页码（可选）
- pageSize：每页条数（可选）

## 4. 交易类API

### 4.1 下单

**API描述**：创建新订单。

**HTTP请求**：
- 方法：POST
- 路径：`/api/v2/trade/orders`
- 认证：需要API密钥、签名和时间戳

**请求参数**：
| 字段名 | 类型 | 必需 | 描述 |
|-------|------|------|------|
| symbol | string | 是 | 交易对符号 |
| side | string | 是 | 买/卖方向 (BUY/SELL) |
| type | string | 是 | 订单类型 (LIMIT/MARKET) |
| quantity | string | 是 | 订单数量 |
| price | string | 否 | 价格（限价单必填） |
| timeInForce | string | 否 | 订单有效期 |
| clientOrderId | string | 否 | 客户端自定义订单ID |

### 4.2 取消订单

**API描述**：取消指定订单。

**HTTP请求**：
- 方法：DELETE
- 路径：`/api/v2/trade/orders/{orderId}`
- 认证：需要API密钥、签名和时间戳

### 4.3 批量下单

**API描述**：同时创建多个订单。

**HTTP请求**：
- 方法：POST
- 路径：`/api/v2/trade/batch-orders`
- 认证：需要API密钥、签名和时间戳

**请求参数**：
| 字段名 | 类型 | 必需 | 描述 |
|-------|------|------|------|
| symbol | string | 是 | 交易对符号 |
| orderList | array | 是 | 订单列表 |

**orderList数组元素详情**：
| 字段名 | 类型 | 必需 | 描述 |
|-------|------|------|------|
| side | string | 是 | 买/卖方向 (BUY/SELL) |
| type | string | 是 | 订单类型 (LIMIT/MARKET) |
| quantity | string | 是 | 订单数量 |
| price | string | 否 | 价格（限价单必填） |
| clientOrderId | string | 否 | 客户端自定义订单ID |
| timeInForce | string | 否 | 订单有效期 |
| reduceOnly | boolean | 否 | 是否为减仓订单 |
| closeOnTrigger | boolean | 否 | 触发后是否自动平仓 |

### 4.4 获取订单信息

**API描述**：获取指定订单的详细信息。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/trade/orders/{orderId}`
- 认证：需要API密钥、签名和时间戳

### 4.5 获取历史订单

**API描述**：获取账户的历史订单记录。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/trade/orders/history`
- 认证：需要API密钥、签名和时间戳

**请求参数**：
- symbol：交易对符号（可选）
- side：买/卖方向（可选）
- type：订单类型（可选）
- startTime：开始时间戳（可选）
- endTime：结束时间戳（可选）
- page：页码（可选）
- pageSize：每页条数（可选）

### 4.6 获取当前订单

**API描述**：获取账户当前未成交的订单。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/trade/orders/current`
- 认证：需要API密钥、签名和时间戳

**请求参数**：
- symbol：交易对符号（可选）
- side：买/卖方向（可选）
- type：订单类型（可选）
- page：页码（可选）
- pageSize：每页条数（可选）

### 4.7 获取成交明细

**API描述**：获取订单的成交明细。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/trade/fills`
- 认证：需要API密钥、签名和时间戳

**请求参数**：
- symbol：交易对符号（可选）
- orderId：订单ID（可选）
- startTime：开始时间戳（可选）
- endTime：结束时间戳（可选）
- page：页码（可选）
- pageSize：每页条数（可选）

### 4.8 下单（触发单）

**API描述**：创建触发订单。

**HTTP请求**：
- 方法：POST
- 路径：`/api/v2/trade/trigger-orders`
- 认证：需要API密钥、签名和时间戳

### 4.9 取消触发单

**API描述**：取消指定的触发订单。

**HTTP请求**：
- 方法：DELETE
- 路径：`/api/v2/trade/trigger-orders/{orderId}`
- 认证：需要API密钥、签名和时间戳

### 4.10 获取当前计划订单

**API描述**：获取账户当前有效的计划订单。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/trade/trigger-orders/current`
- 认证：需要API密钥、签名和时间戳

### 4.11 获取历史计划订单

**API描述**：获取账户的历史计划订单记录。

**HTTP请求**：
- 方法：GET
- 路径：`/api/v2/trade/trigger-orders/history`
- 认证：需要API密钥、签名和时间戳

## API认证说明

对于需要认证的API请求，需要在HTTP请求头中添加以下信息：

- `ACCESS-KEY`：API密钥
- `ACCESS-SIGN`：签名，使用HMAC-SHA256算法对请求内容进行签名
- `ACCESS-TIMESTAMP`：当前时间戳（毫秒）
- `ACCESS-PASSPHRASE`：API密钥对应的密码（如果有）

签名生成步骤：
1. 构造签名内容：`timestamp + method + endpoint + body`
2. 使用API密钥对应的私钥，通过HMAC-SHA256算法生成签名
3. 将签名转换为小写十六进制字符串

## 错误码说明

| 错误码 | 描述 |
|-------|------|
| 00000 | 请求成功 |
| 50006 | 请求方法不支持 |

*注：本文档基于WEEX官方现货API文档整理，如有更新请以官方文档为准。*