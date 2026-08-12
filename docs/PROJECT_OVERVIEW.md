# Project Overview

## プロジェクトの目的

Network Checkは、公開されているネットワーク・ドメイン情報を外部から読み取り、理解しやすい形で表示するread-onlyの確認サービスです。DNS、TLS、HTTP、メール関連DNSレコードなどを、通常の問い合わせや接続によって観察します。

対象システムの設定やデータは変更しません。表示結果は、その時点で外部から観察できた情報であり、サービス全体の正常性や安全性を保証するものではありません。

## 想定利用者

- 自分が管理するドメインの公開設定を確認したい人
- DNS、TLS、HTTPなどの基本情報を学びたい人
- IPv4 / IPv6対応状況やメール関連DNSレコードの概要を確認したい人
- Network Checkの公開実装や文書を参照したい開発者

## 主要機能の分類

| 分類 | 機能 |
|---|---|
| 接続元情報 | Client Information |
| DNS・IP | Domain、DNS Timing、IPv4 / IPv6 Preference、PTR、CAA |
| Web接続 | TLS、HTTP/2、Security Headers |
| メール関連DNS | MX、SPF、DMARC |
| まとめて確認 | Domain Multi Check |
| 読み物 | Public Explanation Pages |

各機能の表示項目、結果の意味、利用例、限界は[Checks](CHECKS.md)で説明します。

## Architecture

UIを分離し、同じNetwork Checkのcoreを別サイトへ展開しやすくしています。check logicは共通coreとして再利用し、application logicはUIから独立させ、site-specific UI / presentationはcomposition layerで組み立てます。既存check logicをサイトごとに複製・再実装する構成ではなく、同一source内のmodule boundaryとして再利用するものであり、coreを別HTTP serviceやmicroserviceとして分離するものではありません。

## 安全上の境界

Network Checkは次の行為を行いません。

- 対象システムの変更
- ポートスキャン
- 脆弱性診断や侵入試験
- brute-forceや認証情報の試行
- SMTP認証試験やメール送信
- 大規模なcrawl

TLSとHTTP/2は、public destinationであることを確認してから標準ポート443へ通常接続します。Security Headersはpublic HTTP / HTTPS URLだけを対象とし、非公開・特殊用途の宛先や非標準ポートを拒否します。

## データ取扱いの基本姿勢

入力されたドメイン、IPアドレス、URLや確認結果を、入力履歴として保存することを目的にしていません。runtimeでは匿名の日次集計counterを保存する場合がありますが、入力対象、request本文、client identifier、確認結果は集計recordへ含めません。

詳細は[Data Handling](DATA_HANDLING.md)を参照してください。

## Public Repositoryの役割

Public Repositoryは、公開可能と確認したsource、template、static asset、設定例、文書を、参照・portfolio用途で提供するためのRepositoryです。private Source Repository全体の複製ではなく、選択した公開対象だけで構成します。

privateな運用文書、環境固有path、production情報、認証情報、log、database、runtime outputは公開対象に含めません。詳細は[Public Repository Policy](PUBLIC_REPOSITORY_POLICY.md)と[Directory Structure](DIRECTORY_STRUCTURE.md)を参照してください。

## 関連文書

- [README](../README.md): 利用者向けの入口、起動方法、主要route
- [Checks](CHECKS.md): 各確認機能の正式な解説
- [Data Handling](DATA_HANDLING.md): request dataと匿名集計の扱い
- [Security Policy](SECURITY_POLICY.md): 安全境界と機能限界
- [Public Repository Policy](PUBLIC_REPOSITORY_POLICY.md): public / private境界
- [Directory Structure](DIRECTORY_STRUCTURE.md): Public Repositoryの構成
