# NorthStar intrusion - ACH, first version

## Ranking

Weighted inconsistency (lower is better). Consistent evidence doesn't score.

| Hypothesis | Weighted score | Items against |
|---|---|---|
| H1: Coordinated external intrusion | 0 | 0 |
| H2: Insider who stole the data and disguised it as an external attack | 2.5 | 3 |
| H3: Unrelated events in the same 48 hours | 6.5 | 7 |

## What the leading hypothesis rests on

H1 stops being ahead if these 3 item(s) are wrong or removed:

- E2 (high credibility): Sign-in from a never-seen IP shortly after the email + E5 (high credibility): LSASS credential dumping alert on the same workstation + E10 (medium credibility): Commercial feed: domain seen in malware campaigns (B2)

## Evidence that doesn't separate the hypotheses

- E1: Phishing email to a senior researcher
- E3: Encoded PowerShell 90 min later contacting an external domain
- E4: Scheduled task running PowerShell at logon

## Unrated (needs collection)

- E12: OSINT blog: domain allegedly linked to an Eastern European group (C4)
- E13: Anonymous social media breach claim (F6)
- E15: Who owns the receiving cloud account

## Matrix

| # | Evidence | Credibility | H1 | H2 | H3 |
|---|---|---|---|---|---|
| E1 | Phishing email to a senior researcher | high | C | N | C |
| E2 | Sign-in from a never-seen IP shortly after the email | high | C | I | N |
| E3 | Encoded PowerShell 90 min later contacting an external domain | high | C | N | N |
| E4 | Scheduled task running PowerShell at logon | high | C | N | N |
| E5 | LSASS credential dumping alert on the same workstation | high | C | I | N |
| E6 | RDP from that workstation as it.admin2 | high | C | N | I |
| E7 | Research data zipped on the server reached by RDP | high | C | C | I |
| E8 | 2.3 GB upload from that server to cloud storage | high | C | C | I |
| E9 | Security log cleared right after | high | C | C | I |
| E10 | Commercial feed: domain seen in malware campaigns (B2) | medium | C | I | I |
| E11 | Government advisory: same sequence seen at other healthcare organisations (A2) | high | C | N | I |
| E12 | OSINT blog: domain allegedly linked to an Eastern European group (C4) | low | ? | ? | ? |
| E13 | Anonymous social media breach claim (F6) | none | ? | ? | ? |
| E14 | Events follow the attack lifecycle in order within 48 hours | high | C | N | I |
| E15 | Who owns the receiving cloud account | high | ? | ? | ? |
