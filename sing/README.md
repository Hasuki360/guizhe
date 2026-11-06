# sing-box 规则集（自动生成）

本目录是给 **sing-box 内核**（如 [NetProxy-Magisk](https://github.com/Fanju6/NetProxy-Magisk)）用的规则集，
格式为 sing-box 的 `source` 规则集：`{"version": 1, "rules": [...]}`。

Clash / mihomo **不能**直接读取这里的文件，它们仍然用 `rule/` 下的 `.yaml` / `.list`。
两套格式并存，互不影响。

## 文件对照

| 文件 | 来源 | 对应 Clash 规则集 |
| --- | --- | --- |
| `hasuki.json` | `rule/hasuki.yaml` | 莲纪的网站规则 |
| `custom-direct.json` | `rule/Custom_Direct.yaml` | 莲纪的直连规则 |
| `custom-proxy.json` | `rule/Custom_Proxy.yaml` | 莲纪的代理规则 |
| `custom-proxy-premium.json` | `rule/Custom_Proxy_Premium.yaml` | 莲纪的需要优质代理规则 |
| `thirdparty/ehgallery.json` | blackmatrix7 `EHGallery.yaml` | EXhentai |
| `thirdparty/bilibili-hmt.json` | xiaolin-007 `BilibiliHMT.txt` | 哔哩哔哩港澳台 |

`thirdparty/` 下放的是**社区（MetaCubeX 等）没有提供 sing-box 版、只能自己转**的规则集。
其余第三方规则（Google、YouTube、GitHub、Telegram、Twitter、Discord、TikTok、Pixiv、
OpenAI、OKX 等）不需要在这里维护，直接引用 MetaCubeX 的现成 `.srs` 即可，见文末。

## 生成方式

由 `.github/workflows/sing-box.yml` 自动完成，**不需要手工编辑 `sing/` 里的文件**：

- 修改 `rule/*.yaml` 并推送 → 自动重新生成
- 每天 04:17 UTC 自动拉一次第三方上游，上游更新后自动跟进
- 也可在 Actions 页面手动 `Run workflow`

转换脚本：`scripts/clash2sing.py`（本地可单独运行）

```bash
python3 scripts/clash2sing.py rule/hasuki.yaml sing/hasuki.json --name hasuki
```

流程里会用真实 `sing-box` 二进制执行 `rule-set compile` 校验，任何一个规则集编译不过都会让任务失败。

---

# 在 NetProxy 中接入

以下内容对应 NetProxy 管理器：

- **设置 → 内核配置 → 主配置 → 路由**（`route.rule_set` 与 `route.rules`）
- **设置 → 内核配置 → 主配置 → 自定义出站**（`outbounds`）

URL 统一使用 raw 地址（NetProxy 默认通过 `s-download` HTTP Client 走代理下载，raw 可直连）。
若设备网络访问 GitHub raw 困难，可在 URL 前加 `https://gh-proxy.com/` 前缀。

## 一、声明规则集（追加到 `route.rule_set`）

```json
[
  {
    "type": "remote",
    "tag": "莲纪的网站规则",
    "format": "source",
    "url": "https://raw.githubusercontent.com/Hasuki360/guizhe/main/sing/hasuki.json",
    "update_interval": "24h",
    "path": "./rules/remote/hasuki.json"
  },
  {
    "type": "remote",
    "tag": "莲纪的直连规则",
    "format": "source",
    "url": "https://raw.githubusercontent.com/Hasuki360/guizhe/main/sing/custom-direct.json",
    "update_interval": "24h",
    "path": "./rules/remote/custom-direct.json"
  },
  {
    "type": "remote",
    "tag": "莲纪的代理规则",
    "format": "source",
    "url": "https://raw.githubusercontent.com/Hasuki360/guizhe/main/sing/custom-proxy.json",
    "update_interval": "24h",
    "path": "./rules/remote/custom-proxy.json"
  },
  {
    "type": "remote",
    "tag": "莲纪的需要优质代理规则",
    "format": "source",
    "url": "https://raw.githubusercontent.com/Hasuki360/guizhe/main/sing/custom-proxy-premium.json",
    "update_interval": "24h",
    "path": "./rules/remote/custom-proxy-premium.json"
  },
  {
    "type": "remote",
    "tag": "EXhentai",
    "format": "source",
    "url": "https://raw.githubusercontent.com/Hasuki360/guizhe/main/sing/thirdparty/ehgallery.json",
    "update_interval": "24h",
    "path": "./rules/remote/ehgallery.json"
  },
  {
    "type": "remote",
    "tag": "BilibiliHMT",
    "format": "source",
    "url": "https://raw.githubusercontent.com/Hasuki360/guizhe/main/sing/thirdparty/bilibili-hmt.json",
    "update_interval": "24h",
    "path": "./rules/remote/bilibili-hmt.json"
  }
]
```

## 二、自定义出站（`outbounds` 分区）

默认配置里已有 `Proxy`（顶层选择器）、`direct`、`block`，**不要重复定义**。
下面先建地区选择器（对应原 Clash 配置里那些 `filter` 正则），再建业务分组。

```json
{
  "outbounds": [
    {
      "type": "selector",
      "tag": "Hong Kong",
      "use_all_providers": true,
      "include": "(?i)(🇭🇰|香港|港区|港區|hong[ _-]?kong|(^|[^a-z])hk([^a-z]|$))",
      "interrupt_exist_connections": true
    },
    {
      "type": "selector",
      "tag": "Japan",
      "use_all_providers": true,
      "include": "(?i)(🇯🇵|日本|东京|東京|大阪|京都|名古屋|福冈|福岡|japan|(^|[^a-z])jp([^a-z]|$))",
      "interrupt_exist_connections": true
    },
    {
      "type": "selector",
      "tag": "Singapore",
      "use_all_providers": true,
      "include": "(?i)(🇸🇬|新加坡|狮城|獅城|singapore|(^|[^a-z])sg([^a-z]|$))",
      "interrupt_exist_connections": true
    },
    {
      "type": "selector",
      "tag": "United States",
      "use_all_providers": true,
      "include": "(?i)(🇺🇸|美国|美國|洛杉矶|洛杉磯|西雅图|西雅圖|硅谷|纽约|紐約|芝加哥|圣何塞|united[ _-]?states|america|(^|[^a-z])us([^a-z]|$))",
      "interrupt_exist_connections": true
    },
    {
      "type": "selector",
      "tag": "Taiwan",
      "use_all_providers": true,
      "include": "(?i)(🇹🇼|台湾|臺灣|台北|新北|桃园|桃園|台中|高雄|taiwan|(^|[^a-z])tw([^a-z]|$))",
      "interrupt_exist_connections": true
    },
    {
      "type": "selector",
      "tag": "Macau",
      "use_all_providers": true,
      "include": "(?i)(🇲🇴|澳门|澳門|macau|macao|(^|[^a-z])mo([^a-z]|$))",
      "interrupt_exist_connections": true
    },
    {
      "type": "selector",
      "tag": "莲纪的网站",
      "outbounds": ["direct", "Hong Kong", "Japan", "Singapore", "United States", "Proxy"],
      "default": "direct",
      "interrupt_exist_connections": true
    },
    {
      "type": "selector",
      "tag": "EXhentai",
      "outbounds": ["direct", "Japan", "Hong Kong", "Proxy"],
      "default": "direct",
      "interrupt_exist_connections": true
    },
    {
      "type": "selector",
      "tag": "优质代理",
      "outbounds": ["Proxy", "United States", "Singapore", "Japan", "Hong Kong", "direct"],
      "default": "Proxy",
      "interrupt_exist_connections": true
    },
    {
      "type": "selector",
      "tag": "哔哩哔哩港澳台",
      "outbounds": ["direct", "Hong Kong", "Macau", "Taiwan", "Proxy"],
      "default": "direct",
      "interrupt_exist_connections": true
    }
  ]
}
```

> 想再加 AI / TikTok / 谷歌商店 这类独立分组，照抄业务分组的写法再配一条路由规则即可。

## 三、路由规则（插入到 `route.rules`）

**插入位置**：广告拦截规则之后、`geosite/category-ai-!cn` 与 `geosite/google` 之前。
放在后面会被更宽的 `geosite/geolocation-!cn` 抢先匹配，等于没生效。

```json
{
  "rule_set": "莲纪的网站规则",
  "action": "route",
  "outbound": "莲纪的网站"
},
{
  "rule_set": "莲纪的直连规则",
  "action": "route",
  "outbound": "direct"
},
{
  "rule_set": "莲纪的需要优质代理规则",
  "action": "route",
  "outbound": "优质代理"
},
{
  "rule_set": "莲纪的代理规则",
  "action": "route",
  "outbound": "Proxy"
},
{
  "rule_set": "EXhentai",
  "action": "route",
  "outbound": "EXhentai"
},
{
  "rule_set": "BilibiliHMT",
  "action": "route",
  "outbound": "哔哩哔哩港澳台"
}
```

## 四、不需要在这里维护的规则

下列业务直接引用 MetaCubeX 现成的 `.srs`，加进 `route.rule_set` 中现有那组
`https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/sing/geo/{tag}.srs`
的 `tag` 数组即可：

| 用途 | tag |
| --- | --- |
| Telegram / Twitter / Discord | `geosite/telegram` `geosite/twitter` `geosite/discord` |
| GitHub / YouTube / Spotify | `geosite/github` `geosite/youtube` `geosite/spotify` |
| TikTok / Pixiv / OpenAI / OKX | `geosite/tiktok` `geosite/pixiv` `geosite/openai` `geosite/okx` |
| Google 全家桶 | `geosite/google` `geoip/google` |
| Netflix / Bilibili | `geosite/netflix` `geosite/bilibili` |
| 境外 AI（含 Claude、Gemini） | `geosite/category-ai-!cn`（默认配置已启用） |

`claude`、`gemini`、`ehgallery` 在上游没有独立 tag，前两个已被 `geosite/category-ai-!cn` 覆盖，
EHGallery 已在本仓库 `sing/thirdparty/` 自行转换。

## 五、已知差异与坑

- **`use_all_providers` / `include` 是 reF1nd 分支特有字段**：NetProxy 的核心是
  [reF1nd/sing-box](https://github.com/reF1nd/sing-box)，不是上游 SagerNet 版本。
  这两个字段在上游 sing-box 里会直接报 `unknown field`，**不能照抄上游示例写自定义出站**，
  以 NetProxy 官方文档的写法为准。
- **没有 `exclude`**：NetProxy 文档只列了 `include`，未列出 `exclude`。
  原 Clash 配置里"排除 1.5x / 2x / 10x 倍率节点"这类需求无法用 `exclude-filter` 直译，
  需要自己实测内核是否支持该字段，或改用更严格的 `include` 正则。
- **`no-resolve` 不存在**：sing-box 里 IP 类条件只在目标 IP 已知时生效（直连 IP 或经过
  `action: resolve` 之后）。本仓库转换时已忽略该参数，语义与 Clash 的 `no-resolve` 一致。
- **`fallback` 类型无对应**：Clash 的 `fallback` 策略组在 sing-box 里只能近似成 `urltest`。
- **`广告` 组的 REJECT / PASS 切换**：由 NetProxy 的出站模式 `RuleAllowAds`（规则，允许广告）实现，
  不需要单独建组。

---

最后核对：2026-11-06
