# Checks

Network Checkは、外部から観察できる公開情報を表示するread-onlyの確認サービスです。対象システムの設定やデータを変更しません。

ポートスキャン、脆弱性診断、認証試行、メール送信は行いません。また、表示結果だけでサービス全体の正常性や安全性を保証することはできません。DNSやHTTPの応答は、確認時点、resolver、network、対象側の設定などによって変わる場合があります。

## Client Information

- Route: `/`

### 何を確認する機能か

applicationから見える接続元IPアドレスとrequest headerの一部を表示します。

### 主な表示項目

- IPv4またはIPv6として見える接続元IPアドレス
- User-Agent
- Accept-Language

### 利用例

現在の接続がapplicationからIPv4とIPv6のどちらに見えているか、browserがどのようなheaderを送っているかを確認できます。

### この確認だけでは分からないこと

端末内部のinterface、router、VPN、NAT、proxyなど、network構成全体を調査する機能ではありません。表示されるIPアドレスは、applicationがrequestから読み取れる値です。

## Domain

- Route: `/domain`

### 何を確認する機能か

入力したdomainの公開DNS recordを問い合わせ、IPv4 / IPv6対応状況を分類します。

### 主な表示項目

- A
- AAAA
- CNAME
- NS
- SOA
- IPv4-only、IPv6-only、dual-stackの分類

### 利用例

domainがどのIPアドレスへ案内されているか、authoritative name serverやSOA情報、IPv4 / IPv6のrecord有無を確認できます。

### この確認だけでは分からないこと

DNS recordが存在しても、Webやその他のserviceが正常に稼働しているとは限りません。実際の接続経路や全resolverからの見え方も保証しません。

### 安全上の境界

公開DNSへの問い合わせだけを行い、対象システムを変更しません。

## DNS Timing

- Route: `/dns-timing`

### 何を確認する機能か

AとAAAAのDNS問い合わせに要した時間を個別に測定します。

### 主な表示項目

- A問い合わせ時間（ms）
- AAAA問い合わせ時間（ms）
- 各問い合わせで得られたrecordまたはerror

### 利用例

確認時点でAとAAAAの問い合わせがどの程度の時間で完了したかを、参考値として比較できます。

### この確認だけでは分からないこと

一回のDNS問い合わせ時間は、回線速度全体、Web表示性能、継続的なDNS品質を示すものではありません。

## IPv4 / IPv6 Preference

- Route: `/ip-preference`

### 何を確認する機能か

AとAAAA recordの状態から、domainのIPv4 / IPv6利用可能性を分類します。

### 主な表示項目

- A record
- AAAA record
- IPv4-only、IPv6-only、dual-stack、address recordなしの分類

### 利用例

公開DNS上でIPv4とIPv6のどちらが案内されているかを確認できます。

### この確認だけでは分からないこと

OSやbrowserが実際に選んだ通信経路、接続成功、Happy Eyeballsの結果を完全に証明するものではありません。

## TLS

- Route: `/tls`

### 何を確認する機能か

入力したdomainの標準ポート443へ通常のTLS接続を行い、negotiation結果とserver certificateを表示します。

### 主な表示項目

- TLS version
- cipher、protocol、bits
- certificate expiration
- remaining days
- issuer
- subject
- Subject Alternative Name（SAN）

### 利用例

外部から通常接続したときに使用されたTLS versionとcipher、提示されたcertificateの対象や有効期限を確認できます。

### この確認だけでは分からないこと

対応するすべてのTLS versionやcipher suite、certificate chain全体、Web server全体の安全性を評価するものではありません。

### 安全上の境界

接続前に宛先がpublic addressであることを確認し、標準ポート443への通常接続だけを行います。ポートスキャンや脆弱性スキャンは行いません。

## HTTP/2

- Route: `/http2`

### 何を確認する機能か

runtimeの`curl`を使用し、`https://<domain>/`へのrequestでHTTP/2 negotiationを確認します。

### 主な表示項目

- HTTP version
- HTTP status
- 確認に使用したURL
- HTTP/2がnegotiationされたか
- runtimeの`curl`がHTTP/2非対応の場合の`unavailable`

### 利用例

入力したdomainのroot URLへ接続したとき、HTTP/2がnegotiationされるかと最初のHTTP statusを確認できます。

### この確認だけでは分からないこと

redirect先の最終状態、site内の他page、resource、通信性能、継続的なavailabilityは分かりません。crawlや性能測定は行いません。

### 安全上の境界

接続前に宛先がpublic addressであることを確認し、標準ポート443を使用します。redirectは自動追跡しません。

## MX

- Route: `/mx`

### 何を確認する機能か

domainのMX recordを問い合わせます。

### 主な表示項目

- mail exchanger
- priority

### 利用例

domain宛メールの配送先として公開されているhostと優先順位を確認できます。

### この確認だけでは分からないこと

MXが存在しても、mail serverの稼働やメール配送成功を保証しません。

### 安全上の境界

DNS問い合わせだけを行い、SMTP接続、認証試行、メール送信は行いません。

## SPF

- Route: `/spf`

### 何を確認する機能か

domainのDNS TXT recordから`v=spf1`で始まるSPF recordを抽出します。

### 主な表示項目

- SPF record
- recordが見つかったか

### 利用例

domainが公開している送信許可方針を読み取る手がかりとして利用できます。

### この確認だけでは分からないこと

SPF設定の完全性、実際の送信元が許可されるか、メールが到達するかは保証しません。

## DMARC

- Route: `/dmarc`

### 何を確認する機能か

`_dmarc.<domain>`のDNS TXT recordから`v=DMARC1`で始まるDMARC recordを抽出します。

### 主な表示項目

- DMARC record
- policy recordが見つかったか

### 利用例

SPFやDKIMの認証結果を受信側がどのように扱う方針かを確認する手がかりになります。

### この確認だけでは分からないこと

DKIM署名そのもの、実メールのSPF・DKIM・DMARC認証結果、report受信状況は検証しません。

## PTR

- Route: `/ptr`

### 何を確認する機能か

入力した1つのIPv4またはIPv6 addressをreverse lookupします。

### 主な表示項目

- reverse lookup name
- PTR record
- estimated reverse DNS authority zone

### 利用例

IPアドレスに公開されているreverse nameと、管理zoneの目安を確認できます。

### この確認だけでは分からないこと

表示するauthority zoneは推定値です。PTRがないことは必ずしも異常ではなく、IPアドレスの所有者やserviceの安全性も判定しません。

### 安全上の境界

reverse DNS問い合わせだけを行います。Domain Multi Checkには含まれません。

## CAA

- Route: `/caa`

### 何を確認する機能か

domainのCAA recordを問い合わせます。

### 主な表示項目

- flags
- tag（`issue`、`issuewild`、`iodef`など）
- value
- raw record

### 利用例

certificateを発行してよいCertificate Authorityに関する公開方針を確認できます。

### この確認だけでは分からないこと

CAAがないことは、TLS certificateが無効という意味ではありません。現在のcertificateが正しく発行されたかを総合判定する機能でもありません。

## Security Headers

- Route: `/security-headers`

### 何を確認する機能か

入力したpublic HTTP / HTTPS URLへrequestを送り、選択したresponse headerの有無と値を表示します。

### 主な表示項目

- HTTP statusとrequest method
- Strict-Transport-Security
- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy

### 利用例

指定したURLの最初のresponseに、対象headerが含まれているかを確認できます。

### この確認だけでは分からないこと

headerの有無だけで、設定内容の十分性、すべてのpageへの適用、Web site全体の安全性を保証することはできません。

### 安全上の境界

- public HTTP / HTTPS URLだけを受け付けます。
- embedded credentialsを拒否します。
- HTTP / HTTPSのnon-default portを拒否します。
- localhostを拒否します。
- private、reserved、non-public addressを拒否します。
- redirectを自動追跡しません。

Domain Multi Checkには含まれません。

## Domain Multi Check

- Route: `/multi-check`
- Public UI: `/network-check/`

### 何を確認する機能か

同じdomainを入力として使用する次の9項目から選択し、まとめて実行します。

1. Domain
2. DNS Timing
3. CAA
4. MX
5. SPF
6. DMARC
7. TLS
8. HTTP/2
9. IPv4 / IPv6 Preference

### 結果から分かること

選択した複数の確認結果を一度に比較できます。各結果の表示項目、意味、限界、安全境界は個別機能と同じです。

### この確認だけでは分からないこと

複数項目が成功しても、対象service全体の正常性や安全性を保証しません。PTRはIPアドレス、Security HeadersはURLを入力するため対象外です。

## Public Explanation Pages

- Guide route: `/network-check/guide/`
- Explanation route: `/network-check/{slug}/`

各確認項目の意味や結果の読み方を説明する読み物pageです。DNS、PTR、CNAME、IPv4 / IPv6、MX、SPF、DMARC、CAA、TLS、Security Headers、HTTP statusに関する説明を提供します。

説明pageは追加の診断を実行する機能ではありません。実際の確認は、対応する個別routeまたはDomain Multi Checkから行います。
