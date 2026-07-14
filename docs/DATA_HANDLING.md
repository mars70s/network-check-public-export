# Data Handling

この文書は、Network Checkがrequest処理中に扱う情報と、匿名利用集計として保存する情報の範囲を説明します。Privacy Policy、Security Policy、利用規約の代わりとなる文書ではありません。

## サービスが処理する入力

利用する機能に応じて、次の入力をrequestごとに処理します。

- domain
- 1つのIPv4またはIPv6 address
- public HTTP / HTTPS URL
- Domain Multi Checkで選択した確認項目

Client Informationでは、applicationから見える接続元IPアドレス、User-Agent、Accept-Languageをrequestから読み取って表示します。

各確認機能は、入力に応じてDNS record、DNS問い合わせ時間、TLS / HTTP negotiation結果、certificate情報、選択したHTTP response headerなどを取得し、そのrequestへの結果として表示します。

## 保存する情報

現在の実装が保存するのは、日ごとの利用回数をまとめる匿名利用集計recordです。保存フィールドは次の5つです。

| Field | 内容 |
|---|---|
| `event_date` | 集計対象の日付 |
| `event_type` | page表示やMulti Check実行などを表す内部event種別 |
| `target_id` | pageまたは確認項目を表す内部識別子 |
| `count` | 同じ日付・event種別・内部識別子に対する累計回数 |
| `updated_at` | 集計recordを最後に更新した時刻 |

`event_type`と`target_id`には、実装側で決めたevent名や機能IDを渡します。`target_id`は、利用者が入力したdomain、IPアドレス、URLを保存するためのfieldではありません。

## 匿名利用集計の目的

匿名利用集計は、公開pageやDomain Multi Checkがどの程度利用され、どの確認項目が選択されているかを件数で把握するために使用します。

この集計は利用回数を日単位でまとめるもので、個別利用者や個別の入力対象を追跡する目的ではありません。ただし、この文書は匿名性や安全性を絶対的に保証するものではなく、現在の実装で集計recordへ渡しているfieldと値の境界を説明するものです。

## 保存しない情報

現在の実装では、次の情報を匿名利用集計recordへ保存しません。

- 利用者が入力したdomain
- IPアドレス
- URL
- HTTP headers
- cookies
- session
- request body
- 個別の診断結果

通常の診断結果はrequestごとに生成され、入力対象ごとの診断履歴として保存しません。

## この文書で定めない事項

現在の実装で確認できない保存期間、削除時期、暗号化方法などは、この文書では定めません。将来、保存fieldや利用目的を変更する場合は、実装と公開文書を同じ変更範囲で確認する必要があります。
