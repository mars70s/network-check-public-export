# Public Repository Policy

## この文書の目的

この文書は、Network Checkのprivate Source RepositoryとPermanent Public Repositoryの役割、および公開・非公開の境界を説明します。

Public Repositoryは公開用成果物を保持するためのRepositoryです。private Source全体のbackup、完全なmirror、deploy先ではありません。

## private Source Repositoryの役割

private Source Repository `mars70s/network-check`は、Network Checkの実装、公開前の文書制作、公開対象の選定と確認を行うsource of truthです。

公開する内容は、まずSource側で完成させ、実装との一致、文書間の整合、公開・非公開境界を確認します。Sourceに存在するfileや情報が、そのまますべて公開対象になるわけではありません。

## Permanent Public Repositoryの役割

Permanent Public Repository `mars70s/network-check-public-export`は、公開対象として選定・確認された成果物を保持し、参照・portfolio用途で提供します。

Public Repositoryはprivate Source全体の完全な複製ではありません。公開対象は、公開する目的が明確で、内容と公開境界を確認したsource、document、template、static asset、設定例などに限定します。

選定と確認を行うことは、秘密情報の非混入や公開上の安全性を絶対的に保証することを意味しません。反映前に対象内容と差分を確認し、承認された範囲だけを扱います。

## 固定対象の公開文書

現在の公開用ドキュメント制作で完成・同期する対象は、次の7文書です。

1. `README.md`
2. `docs/PROJECT_OVERVIEW.md`
3. `docs/CHECKS.md`
4. `docs/DATA_HANDLING.md`
5. `docs/SECURITY_POLICY.md`
6. `docs/PUBLIC_REPOSITORY_POLICY.md`
7. `docs/DIRECTORY_STRUCTURE.md`

これらの文書はSource側で内容を完成・確認した後、Permanent Public側の同一pathへ反映し、両Repositoryの対象7文書を一致させます。

## 公開しない情報

次の情報や成果物は公開対象に含めません。

- 認証情報
- API key、token、password、秘密鍵
- 非公開設定値
- privateなlocal path
- server、network、database、logの内部情報
- 個人情報
- 未公開の運用手順
- private Sourceにだけ存在する内部資料
- 公開が承認されていない成果物

公開文書では、必要に応じて`example.com`などのexample値を使用し、実際のprivate情報を記載しません。データ取扱いの詳細は[Data Handling](DATA_HANDLING.md)、確認機能の安全境界は[Security Policy](SECURITY_POLICY.md)を参照してください。

## 反映の境界

Public Repositoryへの反映は、公開用成果物をGit上で更新する作業です。次の操作を意味しません。

- applicationのdeploy
- service restart
- runtime設定の変更
- private Source全体の公開
- 運用環境との自動同期

公開は自動実行を前提としません。また、完全なsanitizeが自動的に保証されるとは扱いません。対象file、内容、差分、公開しない情報の境界を反映前に確認します。

## Public Repositoryから分かる範囲

Public Repositoryは、公開された成果物の内容だけを示します。Public Repositoryだけから、非公開の実装、運用環境、内部構成を完全に把握または推定できることを保証しません。

公開されていない情報が存在しないことや、private SourceとPublic Repositoryの構成が同一であることも意味しません。

## 問題を報告する場合

公開成果物の問題を報告する場合は、再現や確認に必要な最小限の情報を使用し、秘密情報、認証情報、個人情報、privateな運用情報を含めないでください。
