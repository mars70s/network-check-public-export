# NOW

## Current checkpoint

- Repository: `mars70s/network-check-public-export`
- Branch: `main`
- Implementation baseline（F1〜F5 + Additional Findingの実装修正が完了した時点のcommit）: `b4bc4164ce87aab236a004fe2d355e89001191e8`
- Docs closeout commit（本文書と`docs/BACKLOG.md`を新設した時点のcommit）: `d8dbff49a5f09fe04b1e538f3d83b1e49064a757`
- Automated tests: 43/43 PASS（implementation baseline `b4bc416`時点、`tests/`配下、`python -m unittest discover -s tests`で確認。docs closeout commitはdocs-onlyのためtest構成に影響しない）

## Review remediation status

独立横断レビューを起点として実施した、F1〜F5および追加findingの修正・検証はすべて完了しています。

| ID | 内容 | Status | Commit |
|---|---|---|---|
| F1 | Public Export Boundary（無関係ドメインのbranding/contact除去、composition root genericization） | CLOSED | `1001e07`, `8b57a95` |
| F2 | Multi Check event-loop blocking（`/api/multi-check/run`を`run_in_threadpool`経由へ） | CLOSED | `e03694b` |
| F2b | Individual Check Route Blocking（11個のPOST routeを`run_in_threadpool`経由へ） | CLOSED | `4c1e57d` |
| F3 | Architecture representation accuracy | CLOSED | osiix.com repository側で実施（`1653c61`）。public-export側はcode pathをそのEvidenceとして扱う |
| F4 | Test Specification / Automated Coverage Gap | CLOSED | `6a4b8bd` |
| F5 | Error Message Sanitization | CLOSED | `e082549` |
| Additional Finding | Usage Metrics Information Exposure（raw exception、DB path常時表示） | CLOSED | `b4bc416` |

F3のみ、修正対象がOSIIX Projectページ（`osiix.com`リポジトリ）側であったため、当repositoryにはcommitが存在しません。public-export側では、Architecture claimの根拠となる実際のcode path（Composition/Application/Checks-Core の分岐構造）自体が変更されていないことを確認済みで、F3のCLOSEDはこの前提の上に成立しています。

## What this means

- 独立横断レビューで指摘されたfinding系列は、すべてCLOSEDとして記録されています。
- 現在のNetwork Check public exportは、承認済みscopeについてcloseout済みの状態です。「未完了」ではありません。
- 将来の改善候補は`docs/BACKLOG.md`へ分離しています。Backlogの存在は、このcloseout statusをOPENへ戻しません。

## NEXT_SINGLE_ACTION

NONE

新たな指摘・要望が生じた場合は、個別のWork Unitとして改めてscopeを確認・承認した上で着手します。`docs/BACKLOG.md`記載の項目も、そのままでは着手済み作業になりません。
