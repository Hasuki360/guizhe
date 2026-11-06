#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clash classical 规则文件 -> sing-box 规则集 (format: source, version 1)

用法:
    python3 scripts/clash2sing.py <输入> <输出>
    <输入> 可以是本地路径，也可以是 http(s) URL

支持的 Clash 规则类型:
    DOMAIN / DOMAIN-SUFFIX / DOMAIN-KEYWORD / DOMAIN-REGEX
    IP-CIDR / IP-CIDR6 / SRC-IP-CIDR
    DST-PORT / SRC-PORT / PROCESS-NAME

关键设计:
    1. 同类型规则合并进同一个对象（数组内是 OR）；不同类型必须拆成不同对象，
       因为 sing-box 同一个对象内不同字段之间是 AND 关系。
       例: {"domain_suffix":["a.com"],"ip_cidr":["1.2.3.0/24"]} 表示两者都要命中，是错的。
    2. 输出字段顺序固定，保证重复运行 diff 稳定。
    3. no-resolve 这类尾部参数直接忽略：在 sing-box 里是否做 IP 匹配
       由路由侧（action: resolve / match_only）决定，不需要写在规则集里。
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import sys
import urllib.request

# Clash 规则类型 -> sing-box 字段名
TYPE_MAP = {
    "DOMAIN": "domain",
    "DOMAIN-SUFFIX": "domain_suffix",
    "DOMAIN-KEYWORD": "domain_keyword",
    "DOMAIN-REGEX": "domain_regex",
    "IP-CIDR": "ip_cidr",
    "IP-CIDR6": "ip_cidr",
    "SRC-IP-CIDR": "source_ip_cidr",
    "DST-PORT": "port",
    "SRC-PORT": "source_port",
    "PROCESS-NAME": "process_name",
}

# 输出时的固定字段顺序（保证 diff 稳定）
FIELD_ORDER = [
    "domain",
    "domain_suffix",
    "domain_keyword",
    "domain_regex",
    "ip_cidr",
    "source_ip_cidr",
    "port",
    "source_port",
    "process_name",
]

INT_FIELDS = {"port", "source_port"}

# 明确不支持的写法，遇到就报错，避免静默丢规则
UNSUPPORTED = {
    "GEOSITE": "sing-box 用 rule_set 引用 geosite，不需要写进本地规则集",
    "GEOIP": "sing-box 用 rule_set 引用 geoip，不需要写进本地规则集",
    "RULE-SET": "Clash 的 RULE-SET 引用在 sing-box 里由 route.rules 表达",
    "MATCH": "兜底规则由 route.final 表达",
    "PROCESS-PATH": "请改用 PROCESS-NAME 或 sing-box 的 process_path 字段手工处理",
    "SUB-RULE": "Clash 特有，sing-box 用 logical 规则表达",
    "SRC-GEOIP": "Clash 特有，请改用 source_ip_cidr",
    "IP-ASN": "Clash 特有，sing-box 需改用 ip_asn 字段手工处理",
}


class ConvertError(Exception):
    pass


def read_source(src: str) -> str:
    """读取本地文件或 http(s) URL。"""
    if src.startswith(("http://", "https://")):
        req = urllib.request.Request(src, headers={"User-Agent": "guizhe-rule-builder/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8-sig")
    with open(src, "r", encoding="utf-8-sig") as fh:
        return fh.read()


def iter_rule_lines(text: str):
    """从 Clash classical 文件里抽出规则行，产出 (行号, 规则串)。"""
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "payload:":
            continue
        # 兼容 "- DOMAIN,xxx" 与裸 "DOMAIN,xxx"
        if line.startswith("- "):
            line = line[2:].strip()
        elif line.startswith("-"):
            line = line[1:].strip()
        if not line or line.startswith("#"):
            continue
        yield lineno, line


def normalise(kind: str, value: str) -> str:
    """按类型做值级校验与规范化。"""
    if kind == "ip_cidr" or kind == "source_ip_cidr":
        try:
            return str(ipaddress.ip_network(value, strict=False))
        except ValueError as exc:
            raise ConvertError(f"非法 IP 段 {value!r}: {exc}") from exc
    if kind == "domain_regex":
        try:
            re.compile(value)
        except re.error as exc:
            raise ConvertError(f"非法正则 {value!r}: {exc}") from exc
        return value
    if kind in INT_FIELDS:
        if not value.isdigit():
            raise ConvertError(f"端口不是整数: {value!r}")
        return int(value)
    if kind in ("domain", "domain_suffix", "domain_keyword", "process_name"):
        # sing-box 的 domain_suffix 用裸后缀即可，前导点会被一并匹配
        return value.lstrip(".") if kind == "domain_suffix" else value
    return value


def convert(text: str, name: str = "") -> dict:
    buckets: dict[str, list] = {f: [] for f in FIELD_ORDER}
    seen: dict[str, set] = {f: set() for f in FIELD_ORDER}
    errors: list[str] = []
    total = 0

    for lineno, line in iter_rule_lines(text):
        parts = [p.strip() for p in line.split(",")]
        raw_kind = parts[0].upper()

        if raw_kind in UNSUPPORTED:
            errors.append(f"第 {lineno} 行: 不支持 {raw_kind} —— {UNSUPPORTED[raw_kind]}")
            continue

        field = TYPE_MAP.get(raw_kind)
        if field is None:
            errors.append(f"第 {lineno} 行: 未知规则类型 {raw_kind!r}")
            continue
        if len(parts) < 2 or not parts[1]:
            errors.append(f"第 {lineno} 行: {raw_kind} 缺少匹配值")
            continue

        # parts[2:] 里是 no-resolve 之类的尾部参数，忽略
        try:
            value = normalise(field, parts[1])
        except ConvertError as exc:
            errors.append(f"第 {lineno} 行: {exc}")
            continue

        if value in seen[field]:
            continue
        seen[field].add(value)
        buckets[field].append(value)
        total += 1

    if errors:
        raise ConvertError("\n".join(errors))

    rules = [{f: buckets[f]} for f in FIELD_ORDER if buckets[f]]
    out = {"version": 1, "rules": rules}

    if not rules:
        raise ConvertError("转换结果为空：输入文件里没有可识别的规则")

    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Clash classical 规则 -> sing-box 规则集")
    ap.add_argument("src", help="输入文件路径或 http(s) URL")
    ap.add_argument("out", help="输出 JSON 路径")
    ap.add_argument("--name", default="", help="规则集名称，仅用于日志")
    args = ap.parse_args()

    label = args.name or args.src
    try:
        text = read_source(args.src)
    except Exception as exc:  # noqa: BLE001
        print(f"[错误] 读取失败 {args.src}: {exc}", file=sys.stderr)
        return 1

    try:
        doc = convert(text, label)
    except ConvertError as exc:
        print(f"[错误] {label} 转换失败:\n{exc}", file=sys.stderr)
        return 1

    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    counts = ", ".join(f"{f}={len(v)}" for r in doc["rules"] for f, v in r.items())
    n = sum(len(v) for r in doc["rules"] for v in r.values())
    print(f"[OK] {label} -> {args.out}  共 {n} 条  ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
