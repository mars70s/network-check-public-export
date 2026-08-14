# Backlog

## この文書の目的

この文書は、Network Check public export repositoryについて、将来検討できる改善候補を記録するためのものです。

以下を明示します。

- Backlogの項目は、現在のcloseout状態を保つための未完了条件ではありません。
- Backlogが存在すること自体は、CLOSEDとして記録済みのreview findingを再びOPENへ戻しません。
- 各項目は将来のwork候補であり、着手が確定した作業ではありません。
- 新しい承認済みWork Unit・scope決定なしに、Backlog項目がそのままactive workになることはありません。

この文書は、現在完了している作業と、将来検討しうる作業を混同しないために存在します。

## Status語彙

Backlog項目には、以下のstatusのいずれかを付けます。

| Status | 意味 |
|---|---|
| CANDIDATE | 将来候補。着手判断はまだ行っていない。 |
| DEFERRED | 意図的に後回しにした。 |
| OPTIONAL | 実施しなくても現在のcloseout状態に影響しない。 |
| REVIEW_LATER | 将来、条件や要求が変わった場合に再評価する。 |
| NOT_PLANNED | 現時点では実施予定なし。 |

## 項目の記載形式

各項目は以下を持ちます。

- ID
- Title
- Status
- Origin / Trigger
- Why it is not current work
- Reopen condition / Activation condition
- Notes

---

## B-01 Usage Metrics / Data Handling automated evidence

Status: OPTIONAL

Origin:
F4 coverage-gap review, Option B（意図的に見送った候補）。

Why it is not current work:
現在の公開Evidence closeoutは、この追加coverageを必要としません。`docs/DATA_HANDLING.md`の記述と`usage_metrics.py`のSCHEMAは、Additional Finding closeout時点でコードレベルの確認は行っていますが、専用の自動テストは未整備です。

Activation condition:
data handling contractの挙動を変更する場合、より強い公開claimを追加する場合、または追加の自動Evidenceが明示的に要求された場合。

Notes:
候補範囲: aggregate schemaの形状確認、`record_usage_event`の入力制約（count<=0拒否等）、user-entered domain/IP/URLを保存しない契約の直接確認。

---

## B-02 Multi Check latency / concurrency design

Status: REVIEW_LATER

Origin:
F2独立レビュー、およびF2 close時点の残課題認識。

Why it is not current work:
F2でevent-loop blockingは解消済みです。Multi Check自体は引き続き逐次実行であり、9項目選択時のrequest latencyそのものの改善は今回のcorrectness/security closeoutの対象外でした。

Activation condition:
実際のlatencyが問題として顕在化した場合、または並行実行化のtrade-off（実行順序保証・failure isolationとの整合、resource消費増）を含めて検討する必要が生じた場合。

Notes:
parallelization、async化、resource制御のいずれも、現状ではperformance optimization候補であり、security/correctness上の必須条件ではありません。

---

## B-03 Extended destination/input edge-case tests

Status: OPTIONAL

Origin:
F4 security-critical gap review。

Why it is not current work:
現在の`is_disallowed_target_ip`は`not is_global`による包括判定を持ち、代表的な禁止アドレス（loopback/private/link-local/reserved相当）は既にtest_destination_guard.pyでカバーされています。multicast/unspecified等の個別flagやIDNA、IPリテラル入力の境界値は、追加のcoverageとして候補に留まります。

Activation condition:
coverage率向上目的ではなく、具体的なsecurity claim上の必要性が生じた場合にのみ着手する。

Notes:
IDNA変換パス、hostname normalizationのedge caseを含む。

---

## B-04 TLS / HTTP2 success-path deterministic tests

Status: OPTIONAL

Origin:
F4 coverage-gap review。

Why it is not current work:
現在自動テストがあるのはguard-before-connectの順序保証のみで、TLS証明書解析やHTTP/2 parserの成功経路そのものは検証対象外です。これは現行のdestination-safety contractのclose条件ではありません。

Activation condition:
証明書解析やHTTP/2応答解釈のロジックを変更する場合、または成功経路の回帰を自動検知する必要が生じた場合。

Notes:
mock/fakeによる成功経路の追加検証候補。

---

## B-05 Redirect behavior verification

Status: REVIEW_LATER

Origin:
F4 security-critical gap review。

Why it is not current work:
redirect非追跡というclaimはsource読解で確認済みですが、常設の自動テストとしては未整備です。live external network testを常設自動テスト化することは前提にしていません。

Activation condition:
redirect関連のclaimを強化する場合、またはdeterministicなmock手段が明確になった場合。

Notes:
実ネットワークに依存しない検証方法が確立できることが前提。

---

## B-06 SQLite synchronous I/O review

Status: REVIEW_LATER

Origin:
F2/F2b event-loop blocking remediationの副次観察。

Why it is not current work:
`network_check/web/public.py`（record_usage_event呼び出し）や`network_check/web/metrics.py`が使う軽量なsqlite3同期I/Oは、DNS/TLS/subprocess系の待機時間と比べて性質・優先度が異なり、F2/F2bのfindingには含まれていませんでした。

Activation condition:
アクセス量やruntime要求が変化し、event-loopへの影響を再評価する必要が生じた場合。

Notes:
現在のfindingではなく、観察に基づく将来の再評価候補です。

---

## B-07 Architecture SVG browser visual recheck

Status: OPTIONAL

Origin:
F3（osiix.com側で実施したArchitecture representation修正）。

Why it is not current work:
F3の実施時、Browser paneの不調によりpixel単位での最終目視確認が限定的でした。XML構文検証・座標計算・本番HTTP 200確認は完了済みで、F3は既にCLOSEDです。

Activation condition:
ブラウザでの目視確認機会が得られた場合に一度確認する程度の軽微な候補。

Notes:
この項目はF3をOPENへ戻しません。

---

## B-08 Independent re-review after remediation

Status: OPTIONAL

Origin:
F1〜F5 + Additional Finding remediation全体。

Why it is not current work:
今回の一連の修正が外部視点でも解消したと確認する第三者レビューは、価値はありますが、現在のcloseoutの前提条件ではありません。

Activation condition:
公開範囲の拡大、大きな機能追加、または外部からの新たな指摘があった場合。

Notes:
再レビュー未実施でも現在のcloseout状態は有効です。

---

## B-09 UI / UX future improvements

Status: CANDIDATE

Origin:
なし（一般的な将来候補として保持）。

Why it is not current work:
具体的な利用者の不便や要望が観測されていません。

Activation condition:
具体的な観測・要望が得られた場合に、個別のWork Unitとして検討する。

Notes:
抽象的な「もっと使いやすくする」をこの項目のままactive taskにはしません。
