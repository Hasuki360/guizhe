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
其余第三方规则不需要在这里维护，直接引用 MetaCubeX 的现成 `.srs`，见第四节。

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

对应 NetProxy 管理器：

- **设置 → 内核配置 → 主配置 → 路由**（`route.rule_set` 与 `route.rules`）
- **设置 → 内核配置 → 主配置 → 自定义出站**（`outbounds`）

URL 统一使用 raw 地址（NetProxy 默认通过 `s-download` HTTP Client 走代理下载，raw 可直连）。
若设备网络访问 GitHub raw 困难，可在 URL 前加 `https://gh-proxy.com/` 前缀。

## 一、声明本仓库的规则集

追加到 `route.rule_set`：

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

## 二、自定义出站

默认配置里已有 `Proxy`（顶层选择器）、`direct`、`block`，**不要重复定义**。
下面先建地区选择器（对应原 Clash 配置里的 `filter` 正则），再建业务分组。

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

## 三、其余第三方规则：只需往 tag 数组里加名字

**不需要新建 `rule_set` 条目。** 默认主配置里已经有一组按模板批量下载的远程规则：

```json
{
  "type": "remote",
  "tag": ["...已有..."],
  "format": "binary",
  "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/sing/geo/{tag}.srs",
  "update_interval": "24h",
  "path": "./rules/remote/{tag}.srs"
}
```

把下面这些名字追加进它的 `tag` 数组即可，`url` 和 `path` 里的 `{tag}` 会自动替换：

```json
[
  "geosite/telegram",
  "geosite/twitter",
  "geosite/discord",
  "geosite/whatsapp",
  "geosite/github",
  "geosite/youtube",
  "geosite/pixiv",
  "geosite/tiktok",
  "geosite/openai",
  "geosite/okx",
  "geosite/bing",
  "geosite/microsoft",
  "geosite/googlefcm",
  "geosite/google-cn",
  "geosite/gfw"
]
```

默认配置原有 8 个（`geosite/category-ads-all`、`geosite/apple-cn`、`geosite/category-ai-!cn`、
`geosite/google`、`geosite/geolocation-!cn`、`geosite/cn`、`geoip/cn`、`geoip/telegram`）保留不动，
合计 23 个。

### 逐个可用性（已逐个请求验证）

| 原 Clash 规则集 | 用哪个 tag | 出站 | 状态 |
| --- | --- | --- | --- |
| Telegram | `geosite/telegram` + `geoip/telegram` | Proxy | 有 |
| Twitter | `geosite/twitter` | Proxy | 有 |
| Discord | `geosite/discord` | Proxy | 有 |
| WhatsApp | `geosite/whatsapp` | Proxy | 有 |
| GitHub | `geosite/github` | Proxy | 有 |
| YouTube（油管） | `geosite/youtube` | Proxy | 有 |
| Pixiv | `geosite/pixiv` | Proxy | 有 |
| TikTok | `geosite/tiktok` | Proxy | 有 |
| OKX | `geosite/okx` | Proxy | 有 |
| 微软 Bing | `geosite/bing` | Proxy | 有 |
| 微软服务 | `geosite/microsoft` | direct | 有 |
| Google FCM | `geosite/googlefcm` | direct | 有 |
| Google CN | `geosite/google-cn` | direct | 有 |
| GFW 清单 | `geosite/gfw` | Proxy | 有 |
| 谷歌 | `geosite/google` | Proxy | 有（默认已含） |
| OpenAI | `geosite/openai` | Proxy | 有 |
| **Gemini** | ❌ 无独立 tag | Proxy | 由 `geosite/category-ai-!cn` 覆盖 |
| **Claude** | ❌ 无独立 tag | Proxy | 由 `geosite/category-ai-!cn` 覆盖 |
| **EHGallery** | ❌ 无独立 tag | EXhentai | 本仓库 `thirdparty/ehgallery.json` |
| **BilibiliHMT** | ❌ 无独立 tag | 哔哩哔哩港澳台 | 本仓库 `thirdparty/bilibili-hmt.json` |
| 秋风广告规则 | `Ads_AWAvenue`（默认已内置） | reject | 有 |
| Fake-IP-Filter | ❌ 不需要 | — | NetProxy 默认不用 fake-ip |

## 四、完整 `route.rules`（顺序即优先级）

把默认主配置的 `route.rules` **整段替换**成下面这份，即可还原原来的分流顺序。
注释只能看这里的说明，JSON 里不能带注释。

| # | 规则 | 说明 |
| --- | --- | --- |
| 1 | Direct 模式直连 | 模式覆盖，必须最前 |
| 2 | sniff | 嗅探 SNI，后面的域名规则依赖它 |
| 3 | DNS 劫持 | 53 端口与 dns 协议 |
| 4 | 拒绝 QUIC | 原配置第 1-2 条；若某些应用依赖 QUIC 可删掉这条 |
| 5 | Proxy 模式代理 | 模式覆盖 |
| 6-7 | 本地 `proxy` / `direct` | 保留默认 |
| 8 | 广告拦截 | 保留默认，`RuleAllowAds` 模式会跳过 |
| 9-14 | 本仓库 6 个自定义规则集 | 私有规则 + 第三方补全 |
| 15 | Pixiv / GitHub / TikTok / OKX | → Proxy |
| 16 | Telegram / Twitter / Discord / WhatsApp | → Proxy |
| 17 | OpenAI + 境外 AI | → Proxy（含 Gemini、Claude） |
| 18 | Google FCM / Google CN | → direct |
| 19-21 | YouTube / Google / Bing | → Proxy |
| 22 | 微软服务 | → direct |
| 23 | GFW 清单 | → Proxy |
| 24 | Apple CN / CN 域名 | → direct |
| 25 | 其它境外 | → Proxy |
| 26 | 解析目标 IP | `match_only`，只解析不路由 |
| 27-28 | 国内 IP / Telegram IP | → direct / Proxy |
| 29 | 私网 | → direct |
| 30 | 兜底 | → Proxy |

```json
{
  "rules": [
    { "clash_mode": "Direct", "action": "route", "outbound": "direct" },
    { "action": "sniff" },
    { "type": "logical", "mode": "or", "rules": [{ "port": 53 }, { "protocol": "dns" }], "action": "hijack-dns" },
    {
      "type": "logical",
      "mode": "and",
      "rules": [
        { "network": "udp" },
        { "port": 443 },
        { "rule_set": ["geosite/youtube", "geosite/google"] }
      ],
      "action": "reject"
    },
    { "clash_mode": "Proxy", "action": "route", "outbound": "Proxy" },
    { "rule_set": "proxy", "action": "route", "outbound": "Proxy" },
    { "rule_set": "direct", "action": "route", "outbound": "direct" },
    {
      "type": "logical",
      "mode": "and",
      "rules": [
        { "clash_mode": "RuleAllowAds", "invert": true },
        { "rule_set": ["block", "Ads_AWAvenue", "geosite/category-ads-all"] }
      ],
      "action": "reject"
    },
    { "rule_set": "莲纪的网站规则", "action": "route", "outbound": "莲纪的网站" },
    { "rule_set": "莲纪的直连规则", "action": "route", "outbound": "direct" },
    { "rule_set": "莲纪的需要优质代理规则", "action": "route", "outbound": "优质代理" },
    { "rule_set": "莲纪的代理规则", "action": "route", "outbound": "Proxy" },
    { "rule_set": "EXhentai", "action": "route", "outbound": "EXhentai" },
    { "rule_set": "BilibiliHMT", "action": "route", "outbound": "哔哩哔哩港澳台" },
    {
      "rule_set": ["geosite/pixiv", "geosite/github", "geosite/tiktok", "geosite/okx"],
      "action": "route",
      "outbound": "Proxy"
    },
    {
      "rule_set": ["geosite/telegram", "geosite/twitter", "geosite/discord", "geosite/whatsapp"],
      "action": "route",
      "outbound": "Proxy"
    },
    {
      "rule_set": ["geosite/openai", "geosite/category-ai-!cn"],
      "action": "route",
      "outbound": "Proxy"
    },
    {
      "rule_set": ["geosite/googlefcm", "geosite/google-cn"],
      "action": "route",
      "outbound": "direct"
    },
    { "rule_set": "geosite/youtube", "action": "route", "outbound": "Proxy" },
    { "rule_set": "geosite/google", "action": "route", "outbound": "Proxy" },
    { "rule_set": "geosite/bing", "action": "route", "outbound": "Proxy" },
    { "rule_set": "geosite/microsoft", "action": "route", "outbound": "direct" },
    { "rule_set": "geosite/gfw", "action": "route", "outbound": "Proxy" },
    { "rule_set": ["geosite/apple-cn", "geosite/cn"], "action": "route", "outbound": "direct" },
    { "rule_set": "geosite/geolocation-!cn", "action": "route", "outbound": "Proxy" },
    { "action": "resolve", "match_only": true },
    { "rule_set": "geoip/cn", "action": "route", "outbound": "direct" },
    { "rule_set": "geoip/telegram", "action": "route", "outbound": "Proxy" },
    { "ip_is_private": true, "outbound": "direct" },
    { "clash_mode": "Rule", "action": "route", "outbound": "Proxy" }
  ],
  "final": "Proxy"
}
```

## 五、已知差异与坑

- **`use_all_providers` / `include` 是 reF1nd 分支特有字段**：NetProxy 的核心是
  [reF1nd/sing-box](https://github.com/reF1nd/sing-box)，不是上游 SagerNet 版本。
  这两个字段在上游 sing-box 会直接报 `unknown field`，**不能照抄上游示例写自定义出站**。
- **`match_only` 也是分支特有**：上游 sing-box 1.14 已移除该字段，但 NetProxy 默认主配置
  的 `resolve` 规则就在用它，替换主配置时要保留。
- **没有 `exclude`**：NetProxy 文档只列了 `include`。原 Clash 配置里"排除 1.5x / 2x / 10x
  倍率节点"无法用 `exclude-filter` 直译，需自行实测内核是否支持，或把 `include` 收紧。
- **`no-resolve` 不存在**：sing-box 里 IP 类条件只在目标 IP 已知时生效（直连 IP 或经过
  `action: resolve` 之后）。本仓库转换时已忽略该参数，语义与 Clash 的 `no-resolve` 一致。
- **`fallback` 类型无对应**：Clash 的 `fallback` 策略组在 sing-box 里只能近似成 `urltest`。
- **`广告` 组的 REJECT / PASS 切换**：由 NetProxy 的出站模式 `RuleAllowAds` 实现，不用单独建组。
- **单条规则内不同字段是 AND**：同一对象里同时写 `domain_suffix` 和 `ip_cidr` 表示两者都要命中。
  所以转换脚本会把不同类型拆成不同对象，手写时也要注意。

---

最后核对：2026-11-06
