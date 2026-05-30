# Network Check

Lightweight IPv4 / IPv6, DNS, TLS, and HTTP/2 diagnostic service.

Network Check は IPv4 / IPv6、DNS、TLS、HTTP/2 の基本確認を目的とした軽量ネットワーク診断サービスです。

This project focuses on:

- IPv4 / IPv6 visibility
- DNS A / AAAA validation
- dual-stack verification
- TLS version checking
- HTTP/2 negotiation checking
- DNS response timing
- IPv4 / IPv6 preference analysis
- MX record checking
- SPF record checking
- DMARC record checking
- lightweight public network diagnostics

本プロジェクトは以下を目的としています。

- IPv4 / IPv6 可視化
- DNS A / AAAA レコード検証
- dual-stack 対応確認
- TLS バージョン確認
- HTTP/2 接続確認
- DNS 応答時間確認
- IPv4 / IPv6 優先状況確認
- MXレコード確認
- SPFレコード確認
- DMARCレコード確認
- 軽量ネットワーク診断

---

# Features / 機能

## Client Information / クライアント情報

- IPv4 / IPv6 detection
- User-Agent display
- Accept-Language display

- IPv4 / IPv6 判定
- User-Agent 表示
- Accept-Language 表示

## Domain Verification / ドメイン検証

- DNS A record lookup
- DNS AAAA record lookup
- IPv4-only detection
- IPv6-only detection
- Dual-stack validation

- DNS A レコード確認
- DNS AAAA レコード確認
- IPv4 only 判定
- IPv6 only 判定
- Dual-stack 判定

## TLS Check / TLS確認

- Negotiated TLS version display
- Cipher information display
- Standard TLS connection check on port 443

- 使用された TLS バージョン表示
- 暗号スイート情報表示
- 443番ポートへの通常の TLS 接続確認

## HTTP/2 Check / HTTP/2確認

- HTTP/2 negotiation check
- HTTP status code display
- Final URL display after redirects
- Runtime capability fallback when HTTP/2 is unavailable

- HTTP/2 接続確認
- HTTP ステータスコード表示
- リダイレクト後の最終 URL 表示
- 実行環境が HTTP/2 非対応の場合の unavailable 表示

## DNS Timing / DNS応答時間

- DNS A query timing
- DNS AAAA query timing
- Response time display in milliseconds

- DNS A レコード応答時間
- DNS AAAA レコード応答時間
- ミリ秒単位の応答時間表示


## IPv4 / IPv6 Preference / IPv4・IPv6優先状況

- DNS-record based IPv4 / IPv6 availability analysis
- Dual-stack / IPv4-only / IPv6-only classification
- A / AAAA record visibility

- DNSレコードベースの IPv4 / IPv6 利用可能性確認
- Dual-stack / IPv4 only / IPv6 only 判定
- A / AAAA レコード表示


## MX Record Check / MXレコード確認

- DNS MX record lookup
- Mail exchanger host display
- MX priority display

- DNS MXレコード確認
- メール配送先ホスト表示
- MX優先度表示


## SPF Record Check / SPFレコード確認

- DNS TXT record lookup
- SPF record extraction
- v=spf1 record display

- DNS TXTレコード確認
- SPFレコード抽出
- v=spf1レコード表示


## DMARC Record Check / DMARCレコード確認

- DNS TXT lookup for _dmarc.&lt;domain&gt;
- DMARC record extraction
- v=DMARC1 record display

- _dmarc.&lt;domain&gt; のDNS TXT確認
- DMARCレコード抽出
- v=DMARC1レコード表示

## Public Release Preparation / 公開向け対応

- Privacy Policy page
- Terms page
- Contact page
- `.env` based configuration
- Safety notes for diagnostic functions

- Privacy Policy ページ
- Terms ページ
- Contact ページ
- `.env` ベース設定
- 診断機能に関する安全上の注意

---

# Routes / ルート

| Route | Description |
|---|---|
| `/` | Client network information |
| `/domain` | DNS IPv4 / IPv6 verification |
| `/tls` | TLS version and cipher check |
| `/http2` | HTTP/2 negotiation check |
| `/dns-timing` | DNS A / AAAA response timing |
| `/ip-preference` | IPv4 / IPv6 preference analysis |
| `/mx` | DNS MX record check |
| `/spf` | DNS SPF record check |
| `/dmarc` | DNS DMARC record check |
| `/privacy` | Privacy Policy |
| `/terms` | Terms of Service |
| `/contact` | Contact information |
| `/health` | Health check endpoint |

---

# Technology Stack / 技術構成

- Python 3.12
- FastAPI
- Jinja2
- dnspython
- Uvicorn
- Python standard `ssl` / `socket`
- Runtime `curl` for HTTP/2 capability check

---

# Installation / インストール

## Clone repository

```bash
git clone https://github.com/mars70s/network-check.git
cd network-check
```

## Create virtual environment

```powershell
py -3.12 -m venv venv
```

## Activate virtual environment

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

## Install dependencies

```powershell
pip install -r requirements.txt
```

---

# Local Development / ローカル開発

## Start development server

```powershell
uvicorn main:app --reload
```

## Open browser

```text
http://127.0.0.1:8000
```

---

# Production Deployment Flow / 本番反映フロー

## Local Development

```text
Edit locally
↓
Test locally
↓
git commit
↓
git push
```

## Production Deployment

```bash
cd /path/to/network-check
git pull
systemctl restart network-check
```

Note:
The restart command assumes the application is managed via systemd.

補足:
上記コマンドは systemd によるサービス管理を前提としています。

---

# Environment Variables / 環境変数

Create `.env` from `.env.example`.

`.env.example` を参考に `.env` を作成してください。

Example:

    SITE_NAME=Network Check
    PUBLIC_BASE_PATH=/network-check
    CONTACT_NAME=Network Check Project
    CONTACT_EMAIL=contact@example.com

---
# Security Notes / セキュリティ注意事項

Do NOT commit:

- `.env`
- databases
- API keys
- private certificates
- logs
- local notes

Gitへコミットしないこと:

- `.env`
- DBファイル
- APIキー
- 証明書
- ログ
- ローカルメモ

---

# Repository Structure / ディレクトリ構成

```text
network-check/
├── main.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── docs/
│   ├── PROJECT_RULES.md
│   ├── CURRENT_STATE.md
│   ├── ROADMAP.md
│   ├── NEXT_ACTIONS.md
│   ├── CHANGELOG.md
│   └── DEVELOPMENT_WORKFLOW.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── domain.html
│   ├── tls.html
│   ├── http2.html
│   ├── dns_timing.html
│   ├── ip_preference.html
│   ├── mx.html
│   ├── spf.html
│   ├── dmarc.html
│   ├── privacy.html
│   ├── terms.html
│   └── contact.html
└── static/
    ├── style.css
    └── app.js
```

## Directory Notes / ディレクトリ説明

| Path | Description |
|---|---|
| `main.py` | FastAPI application entry point |
| `requirements.txt` | Python dependencies |
| `.env.example` | Example environment configuration |
| `.gitignore` | Files excluded from Git |
| `docs/` | Development and operation documents |
| `templates/base.html` | Common layout template |
| `templates/index.html` | Client network information page |
| `templates/domain.html` | Domain DNS verification page |
| `templates/tls.html` | TLS check page |
| `templates/http2.html` | HTTP/2 check page |
| `templates/dns_timing.html` | DNS response timing page |
| `templates/ip_preference.html` | IPv4 / IPv6 preference analysis page |
| `templates/mx.html` | DNS MX record check page |
| `templates/spf.html` | DNS SPF record check page |
| `templates/dmarc.html` | DNS DMARC record check page |
| `templates/privacy.html` | Privacy Policy page |
| `templates/terms.html` | Terms of Service page |
| `templates/contact.html` | Contact page |
| `static/style.css` | Stylesheet |
| `static/app.js` | Browser-side JavaScript |

---

# Operational Notes / 運用方針

Recommended workflow:

```text
Local Development
↓
GitHub Push
↓
Production Pull
↓
Restart Service
```

推奨運用:

```text
ローカル開発
↓
GitHub push
↓
本番 git pull
↓
サービス再起動
```

Avoid direct editing on production servers whenever possible.

可能な限り本番機の直接編集は避けてください。

---

# Legal / 法務

This repository includes:

- Privacy Policy
- Terms of Service
- Contact page
- Legal and safety notes for diagnostic functions

for public accessibility and international release preparation.

本リポジトリには以下が含まれます。

- Privacy Policy
- Terms
- Contact page
- 診断機能に関する法務・安全上の注意

これは公開運用および国際公開準備のためです。

---

# License

Copyright (c) 2026 mars70s. All rights reserved unless otherwise stated.

This repository is published for reference and portfolio purposes.
Redistribution, modification, or commercial use requires prior permission.

本リポジトリは参考およびポートフォリオ目的で公開しています。
ソースコードの無断転載、再配布、改変、および商用利用は禁止されています。利用を希望される場合は、事前に許可を得てください。

---

# Status

Active development.

開発継続中。







