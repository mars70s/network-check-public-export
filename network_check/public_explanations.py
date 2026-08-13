from __future__ import annotations

from typing import Any


Segment = dict[str, str]
Paragraph = list[Segment]


def text(value: str) -> Segment:
    return {"text": value}


def code(value: str) -> Segment:
    return {"code": value}


def link(label: str, href: str) -> Segment:
    return {"text": label, "href": href}


def paragraph(*parts: Segment | str) -> Paragraph:
    rendered: Paragraph = []
    for part in parts:
        if isinstance(part, str):
            rendered.append(text(part))
        else:
            rendered.append(part)
    return rendered


def section(heading: str, paragraphs: list[Paragraph]) -> dict[str, Any]:
    return {
        "heading": heading,
        "paragraphs": paragraphs,
    }


def card(
    kicker: str,
    title: str,
    sections: list[dict[str, Any]],
    *,
    lead: Paragraph | None = None,
    term_table: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "kicker": kicker,
        "title": title,
        "sections": sections,
    }
    if lead is not None:
        data["lead"] = lead
    if term_table:
        data["term_table"] = term_table
    return data


def page(
    *,
    slug: str,
    page_order: int,
    eyebrow: str,
    title: str,
    subtitle: str,
    summary: str,
    input_type: str,
    related_checks: list[str],
    cards: dict[str, dict[str, Any]],
    terms: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "slug": slug,
        "page_order": page_order,
        "eyebrow": eyebrow,
        "title": title,
        "subtitle": subtitle,
        "summary": summary,
        "input_type": input_type,
        "related_checks": related_checks,
        "cards": cards,
        "terms": terms or [],
    }



PUBLIC_EXPLANATIONS: dict[str, dict[str, Any]] = {
    "dns": page(
        slug="dns",
        page_order=1,
        eyebrow="DNS / Domain Name System",
        title="DNS のこと",
        subtitle="ドメイン名が、どの住所へ案内されているかを確認する",
        summary="ドメイン名が、DNS 上でどの住所や別の名前へ案内されているかを読むための入口です。",
        input_type="domain",
        related_checks=["DNS / A / AAAA / CNAME / NS / SOA"],
        cards={
            "general": card(
                "基本の見方",
                "DNSの基本",
                [
                    section(
                        "ドメイン名が、どの住所へ案内されているかを確認する",
                        [
                            paragraph("このページは、外部から確認できる公開 DNS 情報の読み方を解説する場所です。Web サイトやサーバーの良し悪し、安全性、運用状態そのものを判定するものではありません。Network Check で表示される各項目について、ここで何が分かるのか、そしてこれだけでは何とも言えないことを整理して説明します。"),
                        ],
                    ),
                    section(
                        "基本の見方：名前と住所を結びつける手がかり",
                        [
                            paragraph("たとえば", code("example.com"), "という名前が、外から確認したときにどの住所を指しているように見えるのか。あるいは、別の名前を経由して案内されているのか。このページでは、そうしたドメイン名の行き先に関する手がかりを確認できます。"),
                            paragraph("ほかにも、メールを受け取るための宛先、メールの送信元を確認するための情報、あるいは証明書を発行してよい認証局の指定など、DNS 上に置かれたさまざまな公開情報を読み解くことができます。"),
                        ],
                    ),
                    section(
                        "案内板としての DNS",
                        [
                            paragraph("DNS は、いわば建物の入口に置かれた案内板のようなものです。どこへ向かえばよいかは教えてくれますが、その先の道が通れるか、建物が開いているか、中の設備が正しく動いているかまでは、案内板を見ただけでは分かりません。"),
                        ],
                    ),
                    section(
                        "各項目で分かること、分からないこと",
                        [
                            paragraph(code("A"), "は、DNS 上に IPv4 の住所が見つかるかを見る項目です。ただし、住所が見つかっても、その先の Web サーバーが実際に応答するとは限りません。"),
                            paragraph(code("AAAA"), "は、DNS 上に IPv6 の住所が見つかるかを見る項目です。住所が見つかった場合でも、そこへ至る道が通っているか、サーバーの受付窓口が開いているかまでは別の確認が必要です。"),
                            paragraph(code("CNAME"), "は、そのドメイン名が別の名前へ案内されているかを見る項目です。案内先の存在は分かりますが、その先の設定や紐づけがすべて正しいとは限りません。"),
                            paragraph(code("NS"), "と", code("SOA"), "は、そのドメインの DNS 情報を担当するサーバーや管理情報に関係します。担当サーバーやシリアル番号などが分かっても、運用全体の健全性をそれだけで判断するものではありません。"),
                            paragraph(code("MX"), "、", code("SPF"), "、", code("DMARC"), "は、メールの配送先や送信元の確認に関係する DNS 情報です。これらの情報が見つかっても、メールが必ず届くとは限りません。"),
                            paragraph(code("CAA"), "は、そのドメインに対して証明書を発行してよい認証局の指定に関係する DNS 情報です。これは発行許可に関する指定であり、現在使われている TLS 証明書そのものの状態を示すものではありません。"),
                            paragraph(code("DNS Timing"), "は、ドメイン名から住所を調べるときに、応答が返るまでにかかったおおよその時間です。この時間が短くても、Web ページ全体の表示が速いとは限りません。"),
                        ],
                    ),
                    section(
                        "Network Check との関係",
                        [
                            paragraph("実際のツール画面では、これらの情報がカードごとに整理されて表示されます。「ドメイン名と住所の関係」では A、AAAA、CNAME、NS、SOA などを確認し、「住所を調べる速さ」では DNS の応答時間を確認します。メールに関係するカードでは MX、SPF、DMARC を確認し、「証明書を出してよい相手」では CAA を確認します。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "DNS", "value": "Domain Name System"},
                    {"label": "A", "value": "Address record"},
                    {"label": "AAAA", "value": "IPv6 address record"},
                    {"label": "CNAME", "value": "Canonical Name record"},
                    {"label": "NS", "value": "Name Server record"},
                    {"label": "SOA", "value": "Start of Authority record"},
                    {"label": "MX", "value": "Mail Exchange record"},
                    {"label": "SPF", "value": "Sender Policy Framework"},
                    {"label": "DMARC", "value": "Domain-based Message Authentication, Reporting, and Conformance"},
                    {"label": "CAA", "value": "Certification Authority Authorization"},
                    {"label": "TLS", "value": "Transport Layer Security"},
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "DNS record visibility と service reachability",
                        [
                            paragraph("DNS record visibility と service reachability は別の概念です。このページで確認しているのは、DNS 応答として外部から取得できる record の有無と、その確認条件における DNS lookup の応答時間です。"),
                            paragraph("A record と AAAA record は、対象名に対する IPv4 / IPv6 address record が DNS 応答として得られたことを示します。CNAME record は対象名が別の canonical name を参照していること、NS record と SOA record はその zone の authoritative name server や管理情報に関係することを示します。"),
                        ],
                    ),
                    section(
                        "DNS だけでは判断できない範囲",
                        [
                            paragraph("MX record、SPF、DMARC は mail exchanger や mail authentication に関係する DNS 情報であり、CAA record は certificate authority に対する発行許可の指定に関係する DNS 情報です。"),
                            paragraph("一方で、IP address への到達性、HTTP / HTTPS service の応答性、TLS handshake の成否、TLS certificate の適合性、有効期限、失効状態、mail delivery の結果、受信側 policy の扱い、Web application の正常性は、DNS record の有無だけでは判断できません。"),
                        ],
                    ),
                    section(
                        "DNS Timing の読み方",
                        [
                            paragraph("DNS Timing は、resolver の種類、cache の状態、query type、network condition などの影響を受ける測定値です。page load time、TCP / TLS connection time、server processing time、browser rendering time とは別に扱う必要があります。"),
                        ],
                    ),
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで確認できるのは、外から見える DNS record と、その確認条件における DNS lookup の応答時間です。"),
                            paragraph("DNS record は、公開情報としての案内先や関連設定を読むための手がかりになりますが、Web サイト全体の安全性、運用の正しさ、所有者、到達性、メール配送結果を保証するものではありません。"),
                        ],
                    ),
                ],
            ),
        },
    ),
    "ptr": page(
        slug="ptr",
        page_order=2,
        eyebrow="PTR / Reverse DNS",
        title="PTR のこと",
        subtitle="住所から、そこに出ている表札を見る",
        summary="IP アドレスから、逆引き DNS 上に見える名前を確認するための解説です。",
        input_type="ip",
        related_checks=["PTR"],
        cards={
            "general": card(
                "基本の見方",
                "PTRの基本",
                [
                    section(
                        "住所から見える名前を確認する",
                        [
                            paragraph("PTR は、IP アドレスから、そこに出ている表札のような名前を見るための仕組みです。通常の DNS が名前から住所を探すのに対して、PTR では住所から名前をたどります。"),
                            paragraph("ここでいう住所は IP アドレスを指します。あるドメイン名が IP アドレスへ案内されている場合、その IP アドレス側にどのような逆引き名が出ているかを確認することで、外から見える手がかりが一つ増えます。"),
                        ],
                    ),
                    section(
                        "表札は、持ち主の証明ではない",
                        [
                            paragraph("PTR で名前が見つかっても、それだけでドメインの所有者、正当性、安全性、到達性が分かるわけではありません。表札が見えることと、その場所がどう使われているかは別の話です。"),
                            paragraph("PTR が見つからない場合も、それだけで問題があるとは言い切れません。用途や運用方針によっては、逆引き名を出さない構成もあります。"),
                        ],
                    ),
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "PTR record と reverse zone",
                        [
                            paragraph("PTR は reverse DNS zone に置かれる record です。IPv4 では", code("in-addr.arpa"), "、IPv6 では", code("ip6.arpa"), "の名前空間を使い、IP address から reverse name を問い合わせます。"),
                            paragraph("PTR の管理主体は、対象ドメインの管理主体と一致するとは限りません。IP address の割り当て元、ホスティング事業者、ネットワーク運用者などが reverse zone を管理している場合があります。"),
                        ],
                    ),
                    section(
                        "読み違えやすい点",
                        [
                            paragraph("PTR の存在は reverse DNS visibility を示しますが、forward-confirmed reverse DNS の成立、サービス到達性、メール配送品質、TLS 証明書との整合性までは示しません。"),
                            paragraph("複数の名前が返る場合や、汎用的なホスト名が返る場合もあります。運用上の判断では、A / AAAA、MX、SPF、TLS など他の見える情報と切り分けて読む必要があります。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "PTR", "value": "Pointer record"},
                    {"label": "Reverse DNS", "value": "IP address から名前を引く DNS の見方"},
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで確認できるのは、入力された IP アドレスについて、外から見える PTR 情報があるかどうかです。"),
                            paragraph("PTR は公開 DNS の一部として見える手がかりであり、所有者確認、本人確認、到達性確認、安全性の保証ではありません。"),
                        ],
                    ),
                    section(
                        "判断しないこと",
                        [
                            paragraph("PTR があることをもって、そのサーバーが信頼できる、正しく運用されている、メールが届きやすい、といった判断はしません。PTR がない場合も、それだけで危険や不備とは扱いません。"),
                        ],
                    ),
                ],
            ),
        },
    ),
    "cname": page(
        slug="cname",
        page_order=3,
        eyebrow="CNAME / Canonical Name",
        title="CNAME のこと",
        subtitle="名前のバトンリレーを見る",
        summary="ある名前が、DNS 上で別の名前へ案内されているかを見るための解説です。",
        input_type="domain",
        related_checks=["DNS / CNAME"],
        cards={
            "general": card(
                "基本の見方",
                "CNAMEの基本",
                [
                    section(
                        "別の名前へ案内される様子を見る",
                        [
                            paragraph("CNAME は、あるドメイン名が別の名前へ案内されていることを示す DNS の情報です。たとえば入口に置かれた案内札が、さらに別の受付へ進むよう示している状態に近いものです。"),
                            paragraph("このページでは、その名前のバトンリレーが外からどのように見えるかを確認します。CNAME がある場合、最終的には A や AAAA のような住所の情報へたどり着くことがあります。"),
                        ],
                    ),
                    section(
                        "リダイレクトとは別のもの",
                        [
                            paragraph("CNAME は DNS 上の案内であり、Web ページを別の URL へ移動させる HTTP redirect とは別の仕組みです。ブラウザ上でページが移動して見えるかどうかとは、直接同じ意味ではありません。"),
                            paragraph("CNAME の経路があることは、それだけで悪い状態を意味しません。CDN、ホスティング、外部サービス連携などで、自然に使われることがあります。"),
                        ],
                    ),
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "DNS-level alias として読む",
                        [
                            paragraph("CNAME record は、owner name が canonical name を参照していることを示します。問い合わせ側は、その canonical name をさらに解決して、A / AAAA などの address record へ進むことがあります。"),
                            paragraph("これは HTTP layer の redirect ではありません。HTTP status code、Location header、最終 URL とは別の層で起きる名前解決上の関係です。"),
                        ],
                    ),
                    section(
                        "chain の読み方",
                        [
                            paragraph("CNAME chain があること自体は異常とは限りません。ただし、chain が長い場合や途中の名前が意図と違う場合は、運用上の委任先や外部サービス設定を確認する手がかりになります。"),
                            paragraph("CNAME と同じ名前に他の record を置くことには DNS 上の制約があります。実際の可否や挙動は zone 設計、サービス仕様、resolver の応答を分けて確認します。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "CNAME", "value": "Canonical Name record"},
                    {"label": "Canonical name", "value": "案内先として示される正式名"},
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで分かるのは、DNS 上で対象名が別の名前へ案内されているか、その案内先がどう見えるかです。"),
                            paragraph("CNAME は名前の関係を示す情報であり、Web サイトの品質、応答の正常性、所有者、契約関係、安全性を証明するものではありません。"),
                        ],
                    ),
                    section(
                        "判断しないこと",
                        [
                            paragraph("CNAME があること、長いこと、外部サービス名が見えることだけで、良い状態や悪い状態とは判断しません。必要に応じて、DNS、HTTP、TLS などを分けて読みます。"),
                        ],
                    ),
                ],
            ),
        },
    ),
    "ipv4-ipv6": page(
        slug="ipv4-ipv6",
        page_order=4,
        eyebrow="IPv4 / IPv6",
        title="IPv4 / IPv6 のこと",
        subtitle="DNS 上で見える、2種類の住所を確認する",
        summary="IPv4 と IPv6 の住所が DNS 上で見つかるかを読むための解説です。",
        input_type="domain",
        related_checks=["IP Preference", "A / AAAA"],
        cards={
            "general": card(
                "基本の見方",
                "IPv4 / IPv6の基本",
                [
                    section(
                        "2種類の住所を見る",
                        [
                            paragraph("インターネット上の住所には、IPv4 と IPv6 という形式があります。Network Check で表示される IPv4 / IPv6 の結果は、DNS 上でそのドメイン名に住所が見つかるかを示すものです。このページでは、その見方を整理します。"),
                            paragraph("IPv6 は、IPv4 アドレスの不足を背景に広がってきた住所の形式で、現在も使われており、今後さらに主流になっていくと考えられます。"),
                        ],
                    ),
                    section(
                        "見つかることと、使えることを分けて読む",
                        [
                            paragraph("DNS 上に IPv4 や IPv6 の住所が見つかることは、外から確認できる手がかりです。ただし、住所が見つかることと、その先のサーバーが実際に安定して応答することは別です。利用者の環境、回線、経路、サーバー側の待ち受け設定などによって、実際の接続結果は変わることがあります。"),
                            paragraph("IPv4 だけが見つかる場合、IPv6 だけが見つかる場合、両方見つかる場合があります。どれが適切かは、そのサイトやサービスの設計によって変わります。"),
                        ],
                    ),
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "A / AAAA record visibility",
                        [
                            paragraph("IPv4 は主に A record、IPv6 は AAAA record として DNS から確認されます。この確認は DNS response として address record が得られるかを見るもので、TCP connection や HTTP / TLS service の成立を直接測るものではありません。"),
                            paragraph("dual-stack に見える場合でも、実際の接続経路は client network、resolver、Happy Eyeballs、route、firewall、service bind などの影響を受けます。"),
                        ],
                    ),
                    section(
                        "観測結果の扱い",
                        [
                            paragraph("DNS 上で A record や AAAA record が返る場合は、IPv4 や IPv6 の入口が公開されている可能性を示します。ただし、到達性、証明書、HTTP 応答、アプリケーションの正常性は別に扱います。"),
                            paragraph("表示上は", code("IPv4 / IPv6 で接続できます"), "ではなく、", code("DNS 上で IPv4 / IPv6 の住所が見つかります"), "のように、観測範囲を限定して表現します。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "A", "value": "IPv4 address record"},
                    {"label": "AAAA", "value": "IPv6 address record"},
                    {"label": "Dual-stack", "value": "IPv4 と IPv6 の両方を使える構成を指すことが多い表現"},
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで確認できるのは、DNS 上で IPv4 または IPv6 の住所が見つかるかどうかです。"),
                            paragraph("住所が見つかることは、接続の成功、サーバーの正常性、利用者ごとの接続経路、安全性を保証するものではありません。"),
                        ],
                    ),
                    section(
                        "判断しないこと",
                        [
                            paragraph("IPv4 と IPv6 のどちらか一方だけが見つかることを、それだけで不備とは判断しません。両方が見つかる場合も、その通信が常に使われる、または全体として安全であるとは判断しません。"),
                        ],
                    ),
                ],
            ),
        },
    ),
    "mx": page(
        slug="mx",
        page_order=5,
        eyebrow="MX / Mail Exchange",
        title="MX のこと",
        subtitle="メールを受け取る窓口として案内されるサーバーを見る",
        summary="そのドメイン宛てのメールを、どのメールサーバーが受け取るよう案内されているかを見る解説です。",
        input_type="domain",
        related_checks=["MX"],
        cards={
            "general": card(
                "基本の見方",
                "MXの基本",
                [
                    section(
                        "メールの受け取り窓口を見る",
                        [
                            paragraph("MXレコードは、そのドメイン宛てのメールを受け取る窓口として、どのメールサーバーが案内されているかを示します。"),
                            paragraph("Web サイトを開くための住所とは別に、メールを届けるときにはメール用の案内先が使われます。このページでは、その案内先が DNS 上でどう見えるかを確認します。"),
                        ],
                    ),
                    section(
                        "届くことの保証ではない",
                        [
                            paragraph("MX が見つかることは、メールの受け取り先として案内されている名前が分かるということです。ただし、実際にメールが届くかどうかは、送信側、受信側、迷惑メール判定、認証設定、サーバー状態などにも左右されます。"),
                            paragraph("MX がない場合でも、用途によってはメールを受け取らないドメインとして自然なことがあります。"),
                        ],
                    ),
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "MX record と preference",
                        [
                            paragraph("MX record は mail exchanger host と preference を示します。preference は複数の配送先がある場合の優先度に関係しますが、実際の配送挙動は送信 MTA の実装や接続結果にも依存します。"),
                            paragraph("MX に示された host name は、さらに A / AAAA record によって address へ解決されます。MX record の存在だけで、SMTP service の応答や配送成功は確認できません。"),
                        ],
                    ),
                    section(
                        "運用上の読み方",
                        [
                            paragraph("複数 MX、外部メールサービス、バックアップ MX などは一般的に見られます。見るべき対象は、MX の有無だけでなく、案内先の名前、優先度、関連する SPF / DMARC との役割分担です。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "MX", "value": "Mail Exchange record"},
                    {"label": "Preference", "value": "MX record に含まれる優先度の値"},
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで確認できるのは、そのドメイン宛てのメール配送先として DNS 上にどの MX が案内されているかです。"),
                            paragraph("メールが必ず届くこと、迷惑メールにならないこと、受信側の設定が正しいこと、運用が健全であることまでは、この確認だけでは分かりません。"),
                        ],
                    ),
                ],
            ),
        },
    ),
    "spf": page(
        slug="spf",
        page_order=6,
        eyebrow="SPF / Sender Policy Framework",
        title="SPF のこと",
        subtitle="そのドメインを名乗る送信元の手がかりを見る",
        summary="そのドメインを名乗ってメールを送るとき、どの送信元が認められているかを DNS 上で見る解説です。",
        input_type="domain",
        related_checks=["SPF"],
        cards={
            "general": card(
                "基本の見方",
                "SPFの基本",
                [
                    section(
                        "送信元のルールを見る",
                        [
                            paragraph("SPF は、そのドメインを名乗ってメールを送るときに、どの送信元が認められているかを DNS 上に示す仕組みです。"),
                            paragraph("このページでは、外から見える SPF の記録を確認し、そのドメインがメール送信元についてどのような方針を公開しているかを読む手がかりにします。"),
                        ],
                    ),
                    section(
                        "見た目の差出人だけの話ではない",
                        [
                            paragraph("SPF は主にメール配送時の送信元確認に関係します。メール画面に表示される From の見た目だけを、それ単独で証明する仕組みではありません。"),
                            paragraph("SPF があることは、送信元に関する方針が公開されているという手がかりです。ただし、それだけで迷惑メール判定やなりすまし対策が完全になるわけではありません。"),
                        ],
                    ),
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "TXT record と envelope sender",
                        [
                            paragraph("SPF は通常、DNS TXT record として公開され、", code("v=spf1"), "で始まります。評価対象は主に SMTP の envelope sender や HELO/EHLO identity に関係し、visible From address の証明とは分けて扱います。"),
                            paragraph("record には", code("ip4"), "、", code("ip6"), "、", code("include"), "、", code("a"), "、", code("mx"), "などの mechanism が含まれることがあります。"),
                        ],
                    ),
                    section(
                        "解釈の注意点",
                        [
                            paragraph("SPF record が存在しても、実際のメール配送では DKIM、DMARC、受信側 policy、reputation、転送経路などが影響します。"),
                            paragraph("このページでは外から見える record を読むことを目的とし、配送結果や受信側での最終判断までは扱いません。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "SPF", "value": "Sender Policy Framework"},
                    {"label": "TXT", "value": "DNS 上に文字列情報を置く record type"},
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで確認できるのは、SPF record が DNS 上に見えるか、その内容がどのように公開されているかです。"),
                            paragraph("SPF の存在は、メールの安全性、到達性、正当性、迷惑メール判定の結果を保証するものではありません。"),
                        ],
                    ),
                ],
            ),
        },
    ),
    "dmarc": page(
        slug="dmarc",
        page_order=7,
        eyebrow="DMARC",
        title="DMARC のこと",
        subtitle="認証に失敗したメールへの対応方針を見る",
        summary="SPF や DKIM の確認が通らなかった場合に、どう扱ってほしいかを DNS 上で読む解説です。",
        input_type="domain",
        related_checks=["DMARC"],
        cards={
            "general": card(
                "基本の見方",
                "DMARCの基本",
                [
                    section(
                        "失敗したメールへの扱い方を見る",
                        [
                            paragraph("DMARC は、ドメインを管理する側が、そのドメインを名乗るメールについて、SPF や DKIM の確認が通らなかった場合に、受信側のメールシステムへ「どのように扱ってほしいか」を DNS 上に公開しておく仕組みです。"),
                            paragraph("いわば、認証に失敗したメールに対する扱い方のメモを、ドメイン側から受信側へ見える場所に置いておくようなものです。"),
                        ],
                    ),
                    section(
                        "p=none は監視のための方針",
                        [
                            paragraph("DMARC には", code("p=none"), "、", code("p=quarantine"), "、", code("p=reject"), "のような方針が含まれることがあります。", code("p=none"), "は監視や集計に使われることがあり、それだけで危険な状態を意味するものではありません。"),
                            paragraph("DMARC は、受信側がどう扱うかに関係する情報です。公開されている方針を読むことで、そのドメインがメール認証失敗時の扱いについて何を表明しているかを確認できます。"),
                        ],
                    ),
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "DMARC record の位置と役割",
                        [
                            paragraph("DMARC は通常、", code("_dmarc.example.com"), "のような名前に TXT record として公開され、", code("v=DMARC1"), "で始まります。"),
                            paragraph("DMARC は SPF または DKIM の結果に加え、domain alignment を評価する枠組みです。SPF record の存在確認とは別に、受信側の評価処理が関係します。"),
                        ],
                    ),
                    section(
                        "policy と reporting",
                        [
                            paragraph("policy tag の", code("p"), "は、認証に失敗したメールへの扱い方の希望を示します。", code("rua"), "や", code("ruf"), "などの reporting tag が含まれることもあります。"),
                            paragraph("ただし、受信側がその方針をどう実装するか、report を送るかどうか、最終的に配送するかどうかは、受信側システムの判断にも左右されます。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "DMARC", "value": "Domain-based Message Authentication, Reporting, and Conformance"},
                    {"label": "p=none", "value": "強い処理を求めず、主に監視に使われる方針"},
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで確認できるのは、DMARC record が DNS 上に見えるか、その方針がどのように公開されているかです。"),
                            paragraph("DMARC があること、または方針が強いことは、すべてのなりすましメールを防ぐことや、すべての正当なメールが届くことを保証しません。"),
                        ],
                    ),
                    section(
                        "判断しないこと",
                        [
                            paragraph("このページでは", code("p=none"), "を危険と断定しません。運用段階、監視方針、メール基盤の移行状況によって意味が変わるためです。"),
                        ],
                    ),
                ],
            ),
        },
    ),
    "caa": page(
        slug="caa",
        page_order=8,
        eyebrow="CAA / Certification Authority Authorization",
        title="CAA のこと",
        subtitle="証明書を発行してよい認証局の方針を見る",
        summary="そのドメインの証明書発行を、どの認証局へ許可しているかを DNS 上で見る解説です。",
        input_type="domain",
        related_checks=["CAA"],
        cards={
            "general": card(
                "基本の見方",
                "CAAの基本",
                [
                    section(
                        "証明書を出してよい相手を見る",
                        [
                            paragraph("CAA は、そのドメインの証明書を発行してよい認証局を、DNS 上に示しておく仕組みです。どの認証局に証明書の発行を許可しているかを見ることで、そのドメインが表明している証明書の発行方針を、外から確認する手がかりになります。"),
                            paragraph("このページでは、現在使われている証明書そのものではなく、証明書を発行してよい相手として DNS 上にどのような方針が置かれているかを確認します。"),
                        ],
                    ),
                    section(
                        "CAA がないことの読み方",
                        [
                            paragraph("CAA が見つからない場合も、それだけで危険とは言えません。CAA は発行方針を示すための情報であり、現在の TLS 証明書の有効性やサイト全体の状態とは分けて読みます。"),
                        ],
                    ),
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "CAA record の tag",
                        [
                            paragraph("CAA record には flags、tag、value が含まれます。代表的な tag には", code("issue"), "、", code("issuewild"), "、", code("iodef"), "があります。"),
                            paragraph(code("issue"), "は通常の証明書発行を許可する CA、", code("issuewild"), "は wildcard certificate に関する許可、", code("iodef"), "は問題報告先に関係します。"),
                        ],
                    ),
                    section(
                        "TLS certificate との切り分け",
                        [
                            paragraph("CAA は certificate issuance policy の signal であり、現在提示されている TLS certificate の subject、SAN、issuer、有効期限、chain validation を直接表すものではありません。"),
                            paragraph("発行時に参照される情報と、接続時に提示される証明書の情報は、観測する層が異なります。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "CAA", "value": "Certification Authority Authorization"},
                    {"label": "CA", "value": "Certificate Authority / 認証局"},
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで確認できるのは、DNS 上に公開されている CAA の有無と内容です。"),
                            paragraph("CAA は証明書発行方針の手がかりであり、現在の HTTPS 接続、証明書の有効期限、失効状態、サイト全体の安全性を保証するものではありません。"),
                        ],
                    ),
                ],
            ),
        },
    ),
    "tls": page(
        slug="tls",
        page_order=9,
        eyebrow="TLS / Transport Layer Security",
        title="TLS のこと",
        subtitle="HTTPS 開始の合図として、証明書を確認する",
        summary="HTTPS で接続を始めるときに見える証明書や TLS 情報を読むための解説です。",
        input_type="domain",
        related_checks=["TLS"],
        cards={
            "general": card(
                "基本の見方",
                "TLSの基本",
                [
                    section(
                        "HTTPS の入口で見える証明書を見る",
                        [
                            paragraph("TLS という規格は、HTTP の通信を暗号化し、HTTPS として接続するために使われます。このページでは、HTTPS で接続を始めるときに見える証明書を確認します。"),
                            paragraph("証明書には、どの名前に対して発行されているか、どの認証局が発行したか、有効期限がいつまでかといった情報が含まれており、HTTPS の入口で見える状態を確かめる手がかりになります。"),
                        ],
                    ),
                    section(
                        "証明書が見えることの限界",
                        [
                            paragraph("証明書が確認できることは、Web サイト全体が安全であることを意味しません。ここで見るのは、あくまで外から確認できる HTTPS 開始時の手がかりです。"),
                            paragraph("ページの内容、運営者の信頼性、アプリケーションの状態、ログイン後の動きまでは、この情報だけでは分かりません。"),
                        ],
                    ),
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "handshake で見える情報",
                        [
                            paragraph("TLS check では、対象 domain に対して server name を指定して 443 番へ接続し、negotiated TLS version、cipher suite、certificate issuer、subject、SAN、有効期限などを確認します。"),
                            paragraph("SAN に対象名が含まれるか、certificate chain が検証できるか、有効期限が近いかは、HTTPS の入口を読むうえで重要な手がかりです。"),
                        ],
                    ),
                    section(
                        "version、cipher、失効確認",
                        [
                            paragraph("TLS version や cipher suite は接続時に合意された結果です。client 側の実装や設定によって見える値が変わる場合があります。"),
                            paragraph("OCSP や CRL などの失効確認は、接続環境や実装によって扱いが変わります。このページだけで、失効状態や運用全体を完全に判断することはできません。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "TLS", "value": "Transport Layer Security"},
                    {"label": "SAN", "value": "Subject Alternative Name"},
                    {"label": "Cipher suite", "value": "TLS 接続で合意された暗号方式の組み合わせ"},
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで確認できるのは、HTTPS 接続の入口で外から見える TLS と証明書の情報です。"),
                            paragraph("証明書が見えることや期限が残っていることは、サイト全体の安全性、運営者の信頼性、アプリケーションの状態を保証するものではありません。"),
                        ],
                    ),
                ],
            ),
        },
    ),
    "security-headers": page(
        slug="security-headers",
        page_order=10,
        eyebrow="Security Headers",
        title="Security Headers のこと",
        subtitle="ブラウザへ渡される扱い方のルールを見る",
        summary="Web サイトがブラウザへ渡す HTTP 応答ヘッダーの一部を読むための解説です。",
        input_type="url",
        related_checks=["Security Headers"],
        cards={
            "general": card(
                "基本の見方",
                "Security Headersの基本",
                [
                    section(
                        "ブラウザへの伝え方を見る",
                        [
                            paragraph("Security Headers は、Webサイトがブラウザへ渡す、ページや通信の扱い方に関するルールです。たとえば、そのページが別の場所からデータを読み込むことをどこまで許すか、このページを別のページの中に表示してよいか、通信を HTTPS に寄せるかといった方針が、HTTP の応答に含まれることがあります。"),
                            paragraph("このページでは、外から見える範囲で、ブラウザにどのような扱い方が伝えられているかを確認します。"),
                        ],
                    ),
                    section(
                        "人間向けの利用規約ではない",
                        [
                            paragraph("Security Headers は、人が読む約束ごとではなく、ブラウザに向けて渡される HTTP response header です。表示されているページの中身や運営方針そのものを説明するものではありません。"),
                            paragraph("ヘッダーが見つかることは一つの手がかりですが、それだけで Web サイト全体の安全性を判断することはできません。"),
                        ],
                    ),
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "selected response headers",
                        [
                            paragraph("この確認では、HTTP / HTTPS URL に対して外から通常の request を送り、応答に含まれる一部の security-related headers を確認します。"),
                            paragraph("代表例として、", code("Strict-Transport-Security"), "、", code("Content-Security-Policy"), "、", code("X-Frame-Options"), "、", code("X-Content-Type-Options"), "、", code("Referrer-Policy"), "、", code("Permissions-Policy"), "などがあります。"),
                        ],
                    ),
                    section(
                        "存在と内容を分けて読む",
                        [
                            paragraph("header が存在しても、その値が目的に合っているか、アプリケーション全体と矛盾しないかまでは別の確認が必要です。"),
                            paragraph("redirect、path、response status、method、CDN、reverse proxy によって見える header が変わる場合があります。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "HSTS", "value": "Strict-Transport-Security"},
                    {"label": "CSP", "value": "Content-Security-Policy"},
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで確認できるのは、指定した公開 HTTP / HTTPS URL の応答に、対象とする header が見えるかどうかです。"),
                            paragraph("header の有無は、Web サイトの安全性、脆弱性の有無、設定全体の正しさ、利用者保護の十分さを保証するものではありません。"),
                        ],
                    ),
                ],
            ),
        },
    ),
    "http-status": page(
        slug="http-status",
        page_order=11,
        eyebrow="HTTP Status",
        title="HTTP Status のこと",
        subtitle="サーバーが最初に返す応答の番号を見る",
        summary="ページが返ったのか、別の場所へ案内されたのか、見つからないのかを知る手がかりとして HTTP status を読む解説です。",
        input_type="domain",
        related_checks=["HTTP Status", "HTTP/2"],
        cards={
            "general": card(
                "基本の見方",
                "HTTP Statusの基本",
                [
                    section(
                        "応答の状態を示す番号を見る",
                        [
                            paragraph("Webページを開こうとすると、ブラウザはまずドメイン名をもとに、接続先のサーバーの住所を探します。接続先が見つかると、ブラウザはそのサーバーへ問い合わせます。サーバーは本文を返す前に、まず応答の状態を示す番号を返します。"),
                            paragraph("HTTP Status は、この番号を確認するものです。ページが返ってきたのか、別の場所へ案内されたのか、見つからなかったのか、サーバー側で応答できなかったのかを知る手がかりになります。"),
                        ],
                    ),
                    section(
                        "番号は入口の手がかり",
                        [
                            paragraph(code("200"), "番台、", code("300"), "番台、", code("400"), "番台、", code("500"), "番台のように、番号の範囲によって大まかな意味が分かれます。"),
                            paragraph("ただし、同じ番号でもサイトの設計やアクセスした URL によって意味合いは変わります。番号だけでページ全体の状態を決めつけることはできません。"),
                        ],
                    ),
                ],
            ),
            "technical": card(
                "技術者視点",
                "技術者視点",
                [
                    section(
                        "HTTP response generally",
                        [
                            paragraph("HTTP Status は HTTP response に含まれる状態コードであり、HTTP/2 専用の概念ではありません。HTTP/1.1、HTTP/2、HTTP/3 など、HTTP response の意味として扱う情報です。"),
                            paragraph("現行の Network Check では、HTTP/2 確認の中で HTTP version、status code、redirect 後の final URL を取得しています。そのため表示上は HTTP/2 check と近い場所にありますが、status code 自体は HTTP 応答一般の情報です。"),
                        ],
                    ),
                    section(
                        "redirect と final URL",
                        [
                            paragraph("redirect を追跡する場合、最初の status code と最終的に到達した URL の status code が異なることがあります。観測結果では、どの段階の応答を見ているかを意識する必要があります。"),
                            paragraph("HEAD request と GET request で応答が異なるサーバーもあります。status code は有用な入口情報ですが、アプリケーションの全体状態を単独で表すものではありません。"),
                        ],
                    ),
                ],
                term_table=[
                    {"label": "2xx", "value": "要求が受け付けられ、応答が返ったことを示す範囲"},
                    {"label": "3xx", "value": "別の場所への案内などを示す範囲"},
                    {"label": "4xx", "value": "要求側に関係する問題を示すことが多い範囲"},
                    {"label": "5xx", "value": "サーバー側で応答できなかったことを示すことが多い範囲"},
                ],
            ),
            "boundary": card(
                "使い方の範囲 / Safety boundary",
                "使い方の範囲 / Safety boundary",
                [
                    section(
                        "この確認で分かる範囲",
                        [
                            paragraph("このページで確認できるのは、外から通常の HTTP 応答として見える status code と、その周辺情報です。"),
                            paragraph("status code は、ページの存在や応答状態の手がかりになりますが、Web サイト全体の正常性、可用性、安全性、運用状態を保証するものではありません。"),
                        ],
                    ),
                ],
            ),
        },
    ),
}


def public_explanation_slugs() -> tuple[str, ...]:
    return tuple(PUBLIC_EXPLANATIONS.keys())


def get_public_explanation(slug: str) -> dict[str, Any] | None:
    return PUBLIC_EXPLANATIONS.get(slug)


def guide_explanation_items() -> list[dict[str, Any]]:
    return sorted(
        PUBLIC_EXPLANATIONS.values(),
        key=lambda item: int(item["page_order"]),
    )
