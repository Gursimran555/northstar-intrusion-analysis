# northstar-intrusion-analysis

An intelligence-led investigation of a simulated intrusion at a healthcare organisation, plus a small tool for Analysis of Competing Hypotheses (ACH). The tool shows which pieces of evidence a conclusion actually rests on.

NorthStar Health Network is a training scenario. Eight separate alerts over 48 hours: a phishing email, a new-IP Microsoft 365 sign-in, encoded PowerShell, a logon scheduled task, an LSASS alert, RDP to a research server, 2.3 GB uploaded to cloud storage, and cleared logs. The question: is this one intrusion, and who is behind it? All hostnames, accounts, IPs and domains are placeholders; none is real infrastructure.

```
$ python -m ach case/matrix_v2.yaml

| H1: Coordinated external intrusion                                      | 0    | 0 |
| H2: Insider who stole the data and disguised it as an external attack   | 0.75 | 2 |
| H3: Unrelated events in the same 48 hours                               | 6.5  | 7 |

H1 stops being ahead if these 2 item(s) are wrong or removed:
- E10 (medium credibility): Commercial feed: domain seen in malware campaigns (B2)
  + E12 (low credibility): OSINT blog: domain allegedly linked to an Eastern European group (C4)
```

## What re-checking the analysis changed

My first assessment concluded, with moderate confidence, that an external actor phished a researcher and stole research data. ACH backed it up: the external hypothesis had no evidence against it, the insider hypothesis had three items against it.

The insider hypothesis wasn't "an employee stole data". It was "an employee stole data **and disguised it as an external attack**". Two of the three items I'd counted against it were a sign-in from a new IP and a credential-dumping alert. Those are exactly what that disguise would produce on purpose. I had rated the evidence against a careless insider, not against the hypothesis I'd written down.

Re-rated ([`case/matrix_v2.yaml`](case/matrix_v2.yaml), changes listed in [`case/ach_v2.md`](case/ach_v2.md)):

- **The same answer leads, but on much less.** The external hypothesis is ahead only because of two outside claims about one domain: a commercial feed rated B2 and a blog rated C4. Neither has been verified. If both are wrong, external and insider are tied.
- **Confidence split.** High confidence that the eight events are one intrusion. Low confidence that it was external rather than an insider.
- **Next steps changed.** More threat hunting won't separate the two. These four things will:
  - who owns the receiving cloud account;
  - whether the researcher could already open the data on the research server;
  - how MFA was satisfied for the new-IP sign-in;
  - whether the C2 domain matches a government advisory's indicators.

  The SOC, management and executive briefs in [`case/report.md`](case/report.md) were updated to match.

## The ACH tool

```bash
pip install -r requirements.txt
python -m ach case/matrix_v2.yaml --compare case/matrix_v1.yaml --markdown out.md
```

A matrix is a YAML file of hypotheses and evidence. Each evidence item has a credibility level (`high` / `medium` / `low` / `none`, e.g. from Admiralty ratings) and a rating per hypothesis (`CC`, `C`, `N`, `I`, `II`, or `?` for not yet known). The tool reports:

- **Ranking by weighted inconsistency.** Following Heuer, only evidence *against* a hypothesis counts, because most evidence fits several explanations. Each item is weighted by credibility, so a C4 blog counts a quarter as much as our own EDR.
- **What the leader rests on.** The smallest sets of evidence that, if wrong, would leave the leading hypothesis no longer ahead. It searches every combination of up to four items.
- **Non-diagnostic evidence.** Items rated the same for every hypothesis. They may matter for the story, but they don't help choose.
- **Open questions.** Items marked `?`, i.e. what to collect next.
- **Changes between versions** of a matrix, with the reason for each re-rating.

## What's in the case file

[`case/report.md`](case/report.md) covers:

- a priority intelligence requirement and six specific ones, plus five intelligence gaps;
- data, information and intelligence for three events;
- Admiralty ratings for five sources;
- ACH: first version, re-rated version, and what would settle it;
- ATT&CK mapping (13 techniques);
- Diamond Model and Pyramid of Pain;
- three hunting hypotheses and three detections (IOC, behaviour, correlation);
- a confidence assessment;
- separate products for the SOC, security management and executives.

The ATT&CK mapping is checked against **Enterprise v20** by [`tools/check_attack.py`](tools/check_attack.py): every ID is current, the names match, and each tactic is valid for its technique. Since v19, Defense Evasion is split into Stealth and Defense Impairment, and log clearing is T1685.005 (was T1070.001). CI downloads the v20 bundle and runs the check.

## Hunting queries

[`hunting/`](hunting) has three KQL correlation hunts for Sentinel / Defender XDR. The first versions are in `hunting/original/`, and [`hunting/README.md`](hunting/README.md) explains each change:

- **Encoded-command regex.** PowerShell accepts any prefix of `-EncodedCommand` plus `-ec`, after `-`, `/` or three Unicode dashes. The first version matched 3 of the 15 flag names, and only after a plain hyphen.
- **Inner join to the baseline.** Users with no sign-in in the last 14 days disappeared from the hunt instead of being flagged.
- **RDP logon type.** With Network Level Authentication, failed RDP attempts are logged as Logon Type 3, not 10.
- **Host names.** They don't match across tables (FQDN vs NetBIOS name).
- **Log clearing.** 1102 only covers the Security log. Clearing other logs is System event 104.

Every query is parsed and type-checked in CI with Microsoft's Kusto.Language parser against declared table schemas. That catches syntax errors and wrong column names, not wrong logic. The revised hunts haven't been re-run against data.

## Layout

```
ach/                 ACH scoring, linchpin search, markdown report
case/                report, ACH matrices (v1, v2) and their outputs, ATT&CK mapping
hunting/             revised KQL hunts; original/ has the first versions
tools/               KQL checker (Node), ATT&CK mapping checker (Python)
tests/               19 tests, incl. "the case matrices give the results the report states"
```

## License

MIT
