# NorthStar intrusion - ACH, re-rated

## Ranking

Weighted inconsistency (lower is better). Consistent evidence doesn't score.

| Hypothesis | Weighted score | Items against |
|---|---|---|
| H1: Coordinated external intrusion | 0 | 0 |
| H2: Insider who stole the data and disguised it as an external attack | 0.75 | 2 |
| H3: Unrelated events in the same 48 hours | 6.5 | 7 |

## What the leading hypothesis rests on

H1 stops being ahead if these 2 item(s) are wrong or removed:

- E10 (medium credibility): Commercial feed: domain seen in malware campaigns (B2) + E12 (low credibility): OSINT blog: domain allegedly linked to an Eastern European group (C4)

## Evidence that doesn't separate the hypotheses

- E1: Phishing email to a senior researcher
- E2: Sign-in from a never-seen IP shortly after the email
- E3: Encoded PowerShell 90 min later contacting an external domain
- E4: Scheduled task running PowerShell at logon
- E5: LSASS credential dumping alert on the same workstation
- E13: Anonymous social media breach claim (F6)

## Unrated (needs collection)

- E15: Who owns the receiving cloud account (ask the provider to preserve and identify it)
- E16: Whether the researcher could already open the data on the research server (if yes, stealing admin credentials makes little sense for an insider)
- E17: How MFA was satisfied for the new-IP sign-in (push approved on the researcher's own phone points one way, token theft the other)
- E18: Whether the C2 domain and upload site match the government advisory's indicators (a match would be hard for an insider to arrange)

## Changes from the previous version

Previous scores: H1 0, H2 2.5, H3 6.5

- E2 for H2: I -> C (a VPN sign-in is exactly what a disguise would produce)
- E5 for H2: I -> N (staging an "attack" or getting admin rights both fit an insider, until E16 is known)
- E12 for H1: ? -> C (rated at low weight instead of left out, so its effect is visible)
- E12 for H2: ? -> I (rated at low weight instead of left out, so its effect is visible)
- E12 for H3: ? -> N (rated at low weight instead of left out, so its effect is visible)
- E13 for H1: ? -> N (cannot be judged; zero weight)
- E13 for H2: ? -> N (cannot be judged; zero weight)
- E13 for H3: ? -> N (cannot be judged; zero weight)
- E14 for H2: N -> C (a disguise would copy the lifecycle)
- E16 added: Whether the researcher could already open the data on the research server
- E17 added: How MFA was satisfied for the new-IP sign-in
- E18 added: Whether the C2 domain and upload site match the government advisory's indicators

## Matrix

| # | Evidence | Credibility | H1 | H2 | H3 |
|---|---|---|---|---|---|
| E1 | Phishing email to a senior researcher | high | C | N | C |
| E2 | Sign-in from a never-seen IP shortly after the email | high | C | C | N |
| E3 | Encoded PowerShell 90 min later contacting an external domain | high | C | N | N |
| E4 | Scheduled task running PowerShell at logon | high | C | N | N |
| E5 | LSASS credential dumping alert on the same workstation | high | C | N | N |
| E6 | RDP from that workstation as it.admin2 | high | C | N | I |
| E7 | Research data zipped on the server reached by RDP | high | C | C | I |
| E8 | 2.3 GB upload from that server to cloud storage | high | C | C | I |
| E9 | Security log cleared right after | high | C | C | I |
| E10 | Commercial feed: domain seen in malware campaigns (B2) | medium | C | I | I |
| E11 | Government advisory: same sequence seen at other healthcare organisations (A2) | high | C | N | I |
| E12 | OSINT blog: domain allegedly linked to an Eastern European group (C4) | low | C | I | N |
| E13 | Anonymous social media breach claim (F6) | none | N | N | N |
| E14 | Events follow the attack lifecycle in order within 48 hours | high | C | C | I |
| E15 | Who owns the receiving cloud account | high | ? | ? | ? |
| E16 | Whether the researcher could already open the data on the research server | high | ? | ? | ? |
| E17 | How MFA was satisfied for the new-IP sign-in | high | ? | ? | ? |
| E18 | Whether the C2 domain and upload site match the government advisory's indicators | high | ? | ? | ? |
