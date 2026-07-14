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
- security response header visibility
- lightweight public network diagnostics
- simple dark mode support

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
- セキュリティ関連レスポンスヘッダー表示
- 軽量ネットワーク診断
- 簡易ダークモード対応

---

# Screenshot / スクリーンショット

Network Check running locally.

ローカル環境で動作している Network Check の画面例です。

![Network Check screenshot](docs/images/network-check-screenshot.png)

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
- DNS CNAME record lookup
- DNS NS record lookup
- DNS SOA record lookup
- IPv4-only detection
- IPv6-only detection
- Dual-stack validation

- DNS A レコード確認
- DNS AAAA レコード確認
- DNS CNAME レコード確認
- DNS NS レコード確認
- DNS SOA レコード確認
- IPv4 only 判定
- IPv6 only 判定
- Dual-stack 判定

## TLS Check / TLS確認

- Negotiated TLS version display
- Cipher information display
- Certificate expiration display
- Remaining days display
- Issuer / subject / SAN display
- Standard TLS connection check on port 443

- 使用された TLS バージョン表示
- 暗号スイート情報表示
- 証明書有効期限表示
- 残り日数表示
- 発行者 / 対象 / SAN 表示
- 443番ポートへの通常の TLS 接続確認

## HTTP/2 Check / HTTP/2確認

- HTTP/2 negotiation check
- HTTP status code display
- Automatic redirect following is disabled.
- Runtime capability fallback when HTTP/2 is unavailable

- HTTP/2 接続確認
- HTTP ステータスコード表示
- 自動リダイレクト追跡は無効です。
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


## PTR Check / PTR確認

- DNS PTR record lookup
- IPv4 reverse DNS lookup
- IPv6 reverse DNS lookup
- Reverse name display
- Estimated reverse DNS authority zone display
- Single IP address input only

- DNS PTRレコード確認
- IPv4逆引き確認
- IPv6逆引き確認
- 逆引き名表示
- 推定される逆引きDNS管理ゾーン表示
- 1つのIPアドレスのみ入力


## CAA Check / CAA確認

- DNS CAA record lookup
- Certificate Authority Authorization display
- issue / issuewild / iodef tag display
- Flags, tag, value, and raw record display
- Single domain input only

- DNS CAAレコード確認
- 証明書発行許可情報の表示
- issue / issuewild / iodef タグ表示
- flags / tag / value / raw record 表示
- 1つのドメインのみ入力

## Multi Check / 一括確認

- Individual check pages remain available for each supported diagnostic function
- `/multi-check` provides a Multi Check UI for selected domain-based checks
- Multi Check currently focuses on checks that use a domain name as input
- PTR and Security Headers remain separate because they use different input types

- 各診断機能は個別チェックページから利用可能
- `/multi-check` は選択したドメイン系チェックをまとめて確認する UI
- Multi Check は現在、ドメイン名を入力にするチェックを対象
- PTR と Security Headers は入力形式が異なるため個別ページとして提供

## Security Headers / セキュリティヘッダー確認

- Selected HTTP response header display
- Strict-Transport-Security display
- Content-Security-Policy display
- X-Frame-Options display
- X-Content-Type-Options display
- Referrer-Policy display
- Permissions-Policy display
- Public HTTP / HTTPS URL input only

- 主要HTTPレスポンスヘッダー表示
- Strict-Transport-Security 表示
- Content-Security-Policy 表示
- X-Frame-Options 表示
- X-Content-Type-Options 表示
- Referrer-Policy 表示
- Permissions-Policy 表示
- 公開HTTP / HTTPS URLのみ入力可能

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
| `/checks` | All Checks / diagnostic function list |
| `/domain` | DNS IPv4 / IPv6 verification |
| `/tls` | TLS version and cipher check |
| `/http2` | HTTP/2 negotiation check |
| `/dns-timing` | DNS A / AAAA response timing |
| `/ip-preference` | IPv4 / IPv6 preference analysis |
| `/mx` | DNS MX record check |
| `/spf` | DNS SPF record check |
| `/dmarc` | DNS DMARC record check |
| `/multi-check` | Multi Check UI for selected domain-based checks |
| `/network-check/` | Public-facing Network Check page |
| `/ptr` | DNS PTR reverse lookup |
| `/caa` | DNS CAA record check |
| `/security-headers` | Selected HTTP security response header display |
| `/privacy` | Privacy Policy |
| `/terms` | Terms of Service |
| `/contact` | Contact information |
| `/health` | Health check endpoint |

---

# Technology Stack / 技術構成

- Python 3.9 or newer
- FastAPI
- Jinja2
- dnspython
- Uvicorn
- Python standard `ssl` / `socket` / `urllib`
- Runtime `curl` for HTTP/2 capability check

---

# Installation / インストール

## Clone repository

```bash
git clone https://github.com/mars70s/network-check-public-export.git
cd network-check
```

## Create virtual environment

### Linux / macOS

```bash
python3 -m venv venv
```

### Windows PowerShell

```powershell
py -3 -m venv venv
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

```bash
pip install -r requirements.txt
```

---

# Local Development / ローカル開発

## Start development server

```bash
uvicorn main:app --reload
```

## Open browser

```text
http://127.0.0.1:8000
```

---

# Deployment Notes / デプロイに関する補足

Deployment method depends on the target environment.

デプロイ方法は実行環境により異なります。

This public repository does not assume a specific production server, reverse proxy, process manager, or service name.

この公開リポジトリでは、特定の本番サーバー、reverse proxy、process manager、service 名を前提にしません。

General deployment considerations:

- keep environment-specific values outside Git
- use `.env` or an equivalent mechanism for local configuration
- run the application with an appropriate ASGI server
- bind the ASGI server to localhost when it is placed behind a reverse proxy
- place reverse proxy, TLS, process manager, and restart policy under the operator's responsibility
- test routes locally before deployment

一般的な注意事項:

- 環境固有値は Git の外に分離する
- `.env` または同等の仕組みでローカル設定を管理する
- 適切な ASGI server でアプリケーションを実行する
- reverse proxy 配下では ASGI server を localhost に限定して待ち受けさせる
- reverse proxy、TLS、process manager、restart policy は運用者の責任で設定する
- デプロイ前にローカルで route を確認する

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

Do not commit the following files or data to Git.

以下のファイルやデータは Git にコミットしないでください。

- `.env` files / `.env` ファイル
- databases / DBファイル
- API keys / APIキー
- private keys or certificates / 秘密鍵・証明書
- logs / ログ
- local notes / ローカルメモ

---
# Repository Structure / ディレクトリ構成

```text
network-check/
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── docs/
│   ├── AGENTS.md
│   ├── PROJECT_RULES.md
│   ├── NOW.md
│   ├── CURRENT_STATE.md
│   ├── ROADMAP.md
│   ├── NEXT_ACTIONS.md
│   ├── CHANGELOG.md
│   ├── DEVELOPMENT_WORKFLOW.md
│   ├── HANDOFF_PROMPT.md
│   ├── PUBLIC_REPOSITORY_EXPORT.md
│   ├── PUBLIC_UI_COPY_GUIDE.md
│   ├── REFACTOR_CHECK_MODULES.md
│   ├── images/
│   └── public_templates/
├── network_check/
│   └── checks/
│       ├── dns.py
│       ├── tls.py
│       ├── http2.py
│       ├── dns_timing.py
│       ├── ip_preference.py
│       ├── mail.py
│       ├── ptr.py
│       ├── caa.py
│       └── security_headers.py
├── templates/
│   ├── base.html
│   ├── public_base.html
│   ├── index.html
│   ├── checks.html
│   ├── multi_check.html
│   ├── public_network_check.html
│   ├── domain.html
│   ├── tls.html
│   ├── http2.html
│   ├── dns_timing.html
│   ├── ip_preference.html
│   ├── mx.html
│   ├── spf.html
│   ├── dmarc.html
│   ├── ptr.html
│   ├── caa.html
│   ├── security_headers.html
│   ├── privacy.html
│   ├── terms.html
│   └── contact.html
└── static/
    ├── style.css
    ├── app.js
    └── multi_check.js
```

## Directory Notes / ディレクトリ説明

| Path | Description |
|---|---|
| `main.py` | FastAPI application entry point |
| `requirements.txt` | Python dependencies |
| `.env.example` | Example environment configuration |
| `.gitignore` | Files excluded from Git |
| `docs/` | Development, current-state, public-export, and handoff documents |
| `docs/PUBLIC_REPOSITORY_EXPORT.md` | Public-safe selected-file export procedure |
| `docs/PUBLIC_UI_COPY_GUIDE.md` | Public UI and copy direction for `/network-check/` |
| `docs/REFACTOR_CHECK_MODULES.md` | Consolidated check-module refactor guidance |
| `docs/public_templates/` | Public-safe documentation templates |
| `network_check/checks/` | Modular backend check implementations |
| `templates/base.html` | Common layout template |
| `templates/public_base.html` | Public-facing layout template |
| `templates/index.html` | Client network information page |
| `templates/checks.html` | All Checks / diagnostic function list page |
| `templates/multi_check.html` | Domain Multi Check page |
| `templates/public_network_check.html` | Public-facing Network Check page |
| `templates/domain.html` | Domain DNS verification page |
| `templates/tls.html` | TLS check page |
| `templates/http2.html` | HTTP/2 check page |
| `templates/dns_timing.html` | DNS response timing page |
| `templates/ip_preference.html` | IPv4 / IPv6 preference analysis page |
| `templates/mx.html` | DNS MX record check page |
| `templates/spf.html` | DNS SPF record check page |
| `templates/dmarc.html` | DNS DMARC record check page |
| `templates/ptr.html` | DNS PTR reverse lookup page |
| `templates/caa.html` | DNS CAA record check page |
| `templates/security_headers.html` | Security response headers check page |
| `templates/privacy.html` | Privacy Policy page |
| `templates/terms.html` | Terms of Service page |
| `templates/contact.html` | Contact page |
| `static/style.css` | Stylesheet |
| `static/app.js` | Browser-side JavaScript |
| `static/multi_check.js` | Browser-side Domain Multi Check result rendering |
| `tools/` | Private-side helper scripts for repository maintenance and public-safe export preparation |

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

## Public site visual alignment

When this application is exposed under `doudemoiikedo.com/network-check/`, its public-facing wording and visual tone should remain aligned with the parent site.

The parent site defines the public presentation direction:

- calm and relaxed tone
- low-pressure wording
- warm off-white / brown color palette
- minimal technical-tool impression
- Japanese-first text with light English support where appropriate

This repository owns the Network Check application behavior and implementation.

The surrounding public-site concept, top-page navigation wording, and visual alignment policy are coordinated from the public-site maintenance workflow, not from this application alone.
