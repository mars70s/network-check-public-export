# Security Policy

## この文書の範囲

Network Checkは、外部から観察できる公開情報を表示するread-onlyの確認サービスです。この文書は、各確認機能が行う処理の境界と、結果を読む際の限界を説明します。

Network Checkは脆弱性診断サービスではありません。表示結果は、対象serviceやWeb siteの総合的な安全性、正常性、脆弱性の有無を保証しません。

## 共通の安全境界

Network Checkは、対象システムの設定、data、稼働状態を変更しません。また、次の行為を行いません。

- ポートスキャン
- 脆弱性診断や侵入試験
- brute-force
- 認証情報の試行
- SMTP認証試験
- メール送信
- 大規模なcrawl

利用者は、自分が管理する対象、または確認を行う許可を得た対象に対して使用してください。

## 入力値と確認機能ごとの境界

### Domainを入力する確認

Domain、DNS Timing、IPv4 / IPv6 Preference、MX、SPF、DMARC、CAAは、入力したdomainに対して公開DNS recordを問い合わせます。DNS recordの有無や問い合わせ結果を表示するもので、対象側の設定を変更しません。

MX、SPF、DMARCはメール関連の公開DNS情報を表示しますが、SMTP接続、認証試行、メール送信、実際のメール認証は行いません。

### IPアドレスを入力する確認

PTRは、入力した1つのIPv4またはIPv6 addressに対してreverse DNS問い合わせを行います。portへの接続やservice調査は行いません。

### TLS

- Route: `/tls`
- 入力: domain

TLSは、接続前にdomainの解決先がpublic addressであることを確認し、標準ポート443へ通常のTLS接続を行います。negotiationされたTLS version、cipher、certificate情報を表示します。

対応するすべてのTLS versionやcipher suiteを列挙するscan、certificate構成全体の監査、脆弱性診断は行いません。

### HTTP/2

- Route: `/http2`
- 入力: domain

HTTP/2は、接続前にdomainの解決先がpublic addressであることを確認し、`https://<domain>/`の標準ポート443へrequestを送ってHTTP versionとHTTP statusを表示します。

- redirectを自動追跡しません。
- crawlを行いません。
- 性能測定を行いません。
- runtimeの`curl`がHTTP/2非対応の場合は`unavailable`を表示します。

この結果は、他のpageやresource、redirect先、継続的なavailabilityを確認するものではありません。

### Security Headers

- Route: `/security-headers`
- 入力: URL

Security Headersは、指定したURLのresponseに含まれる選択したheaderの有無と値を表示します。

#### 入力境界

- public HTTP / HTTPS URLだけを受け付けます。
- embedded credentialsを含むURLを拒否します。
- HTTP / HTTPSのnon-default portを拒否します。
- localhostを拒否します。
- private addressを拒否します。
- reserved addressを拒否します。
- その他のnon-public addressを拒否します。
- redirectを自動追跡しません。

#### 確認対象header

- Strict-Transport-Security
- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy

headerの有無と値を表示するだけで、設定内容の十分性、すべてのpageへの適用、Web site全体の安全性を評価または保証するものではありません。

### Client Information

Client Informationは、applicationから見える接続元IPアドレス、User-Agent、Accept-Languageをrequestから読み取って表示します。端末内部のnetwork構成を調査したり、端末の設定を変更したりする機能ではありません。

### Domain Multi Check

Domain Multi Checkは、同じdomainを入力にする選択済みの確認機能をまとめて実行します。各結果には個別機能と同じ入力境界と限界が適用されます。

PTRはIPアドレス、Security HeadersはURLを入力するため、Domain Multi Checkには含まれません。

## 結果の限界

確認結果は、requestを実行した時点で外部から観察できた情報です。DNS resolver、network経路、対象側の応答、実行環境などによって結果が変わる場合があります。

個別のrecord、certificate、protocol、headerが表示されたこと、または表示されなかったことだけを根拠に、対象全体が安全である、脆弱性がない、攻撃を受けないと判断することはできません。

データ取扱いについては[Data Handling](DATA_HANDLING.md)、機能ごとの表示項目と詳細な限界については[Checks](CHECKS.md)を参照してください。
