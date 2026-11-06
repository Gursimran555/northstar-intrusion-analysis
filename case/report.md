# NorthStar Health Network: intrusion assessment

A training scenario: eight suspicious events at a fictional healthcare organisation over about 48 hours, investigated separately by the SOC. The question is whether they are one intrusion, and what to do about it.

The scenario gives no hostnames, accounts or addresses, so the analysis uses placeholders: user `r.morgan`, workstation `NSH-RES-WS042`, research server `NSH-RES-SRV01`, sign-in IP `203.0.113.45` (a documentation range), C2 domain `ms365-authsync[.]example`, upload site `files.cloudshare[.]example`, admin account `it.admin2`. None of them is real infrastructure.

**Revision note.** The first version concluded "moderate confidence: external intrusion". Re-rating the ACH matrix against the insider hypothesis *as it was stated* (an insider disguising the theft as an outside attack) left that conclusion resting on two unverified outside claims about one domain. Sections 5, 9 and 11–14 were updated. Both matrices are in this folder.

## The events

| # | Event |
|---|---|
| 1 | Senior researcher receives a "Microsoft 365 session expired" email; the account then signs in from an IP never seen for that user |
| 2 | ~90 minutes later, encoded PowerShell on the researcher's workstation connects to an external domain |
| 3 | A scheduled task is created that runs PowerShell at every logon |
| 4 | Hours later, EDR flags suspicious access to LSASS on the same workstation |
| 5 | Several RDP connections from that workstation; one succeeds to a research server |
| 6 | Research directories are zipped into a temp folder |
| 7 | ~2.3 GB leaves the research server over HTTPS to a cloud file-sharing service |
| 8 | Windows Security logs are cleared |

## 1. Requirements

**PIR-01.** Is NorthStar experiencing a single multi-stage intrusion that began with the compromise of a senior researcher's Microsoft 365 account, and if so, which research data, accounts and systems are affected, so leadership can decide on containment and notification within 72 hours?

| SIR | Question |
|---|---|
| SIR-01 Initial access | How was the password obtained, was MFA bypassed or approved, and who else received the email? |
| SIR-02 Behaviour and persistence | What did the encoded PowerShell do, and is there persistence beyond the scheduled task? |
| SIR-03 Credential access | Which credentials were exposed through LSASS, and where have they been used since? |
| SIR-04 Lateral movement | Which systems were reached from the workstation or with the stolen credentials? |
| SIR-05 Collection and exfiltration | What was in the 2.3 GB, did it include patient data, and who owns the receiving account? |
| SIR-06 Infrastructure and attribution | What infrastructure supports the activity, and is there reliable evidence tying it to a known group, or to an insider? |

## 2. Intelligence gaps

| Gap | Why it matters | How to collect |
|---|---|---|
| How the M365 sign-in became code execution on the workstation | Without it the chain isn't proven, and another entry point may still be open | EDR process tree for `powershell.exe`, mail click logs, Entra ID sign-in details (MFA, device, token) |
| What was in the 2.3 GB and who owns the receiving account | Sets business impact, patient-data notification, and is the clearest test of insider vs external | Archive listings from the server or backups, proxy logs, preservation request to the provider |
| Which credentials were in LSASS | An admin credential puts every system it can reach at risk | Memory and disk forensics; hunt logons by every account cached on the workstation |
| What happened on the server while the log was cleared | More tooling or theft may be hidden | Forwarded SIEM copies, EDR telemetry, MFT and Prefetch |
| *(added)* Whether the researcher could already open the server's data | If yes, stealing admin credentials makes little sense for an insider; if no, it fits both | Access reviews and file-share ACLs for `NSH-RES-SRV01` |

## 3. Data, information, intelligence

| | PowerShell (event 2) | LSASS access (event 4) | Transfer (event 7) |
|---|---|---|---|
| Data | `powershell.exe -NoP -W Hidden -enc ...` on NSH-RES-WS042, connecting to `ms365-authsync[.]example` | EDR alert "Suspicious access to LSASS" on NSH-RES-WS042 | NSH-RES-SRV01 sent ~2.3 GB over HTTPS to `files.cloudshare[.]example` |
| Information | Encoded, hidden PowerShell in the researcher's session ~90 min after the new-IP sign-in; the domain appears in a commercial feed | Same workstation as the PowerShell and the new task; an IT admin had logged on there before | The server doesn't normally upload to cloud storage; the upload started ~30 min after research folders were zipped |
| Intelligence | Likely the step from a stolen cloud account to code inside the network (T1059.001). Other hosts contacting the domain may also be compromised | Credentials beyond the researcher's own, possibly admin, were probably taken (T1003.001), turning a one-user problem into a network one | Consistent with staged theft of research data (T1567.002); the largest business impact, and may trigger breach notification |

## 4. Source reliability (Admiralty)

| Source | Reliability | Credibility | Rating | Value | Corroborate? |
|---|---|---|---|---|---|
| Commercial TI feed: domain seen in malware campaigns | B, usually reliable; methods not transparent | 2, probably true; our EDR saw the same domain, but the campaign context is the vendor's | **B2** | High: an IOC to block and hunt | Yes: passive DNS, WHOIS, vendor's campaign details |
| OSINT blog: domain "allegedly" linked to an Eastern European group | C, fairly reliable; method unknown, blogs repeat each other | 4, doubtful; no evidence offered | **C4** | Low: a pivot lead only | Essential before any attribution |
| Internal EDR: PowerShell contacted the domain | A, our own sensor | 2, direct telemetry not yet confirmed by DNS or proxy logs | **A2** | Very high: primary evidence | DNS/proxy logs would make it A1 |
| Anonymous social media breach claim | F, cannot be judged | 6, cannot be judged | **F6** | Low for analysis; useful for comms and leak monitoring | Monitor only |
| Government advisory: similar sequence at healthcare organisations | A, official authority | 2, "similar" isn't "same actor" | **A2** | High: validates the threat, gives TTPs | Compare its IOCs with our telemetry |

## 5. Analysis of Competing Hypotheses

- **H1** External actor: phishing, credential theft, lateral movement, collection and exfiltration.
- **H2** Insider: the employee stole the research data and disguised it as an external attack.
- **H3** Unrelated events that happened in the same 48 hours.

Scored with [`ach`](../ach): weighted inconsistency, where only evidence *against* a hypothesis counts and each item is weighted by credibility (high 1, medium 0.5, low 0.25). Full outputs: [`ach_v1.md`](ach_v1.md), [`ach_v2.md`](ach_v2.md).

| | H1 | H2 | H3 |
|---|---|---|---|
| First version (`matrix_v1.yaml`) | 0 | 2.5 (3 items) | 6.5 (7 items) |
| Re-rated (`matrix_v2.yaml`) | 0 | 0.75 (2 items) | 6.5 (7 items) |

**What changed.** The first version counted the new-IP sign-in (E2) and the LSASS alert (E5) against H2. But H2 is an insider *who disguises the theft as an external attack*. A sign-in through a VPN and a credential-dumping alert are what that disguise would produce on purpose, so they can't count against it. They were rated against a careless insider, not the hypothesis on the page.

**What the conclusion rests on.** After re-rating, H1 stays ahead of H2 only because of E10 (commercial feed, B2) and E12 (OSINT blog, C4). Both are outside claims about the same domain, and neither has been verified. If both turned out to be wrong, H1 and H2 would be tied.

**What would settle it** (unrated items E15–E18 in the matrix):
1. The owner of the receiving cloud account.
2. Whether the researcher could already open the data on the research server.
3. How MFA was satisfied for the new-IP sign-in.
4. Whether the C2 domain and upload site match the government advisory's indicators. A match would be very hard for an insider to arrange.

H3 remains the least likely: the RDP came from the host where credentials were dumped, the data was zipped on the server it reached, uploaded ~30 minutes later, and the log was cleared after.

## 6. MITRE ATT&CK (Enterprise v20)

Checked with [`tools/check_attack.py`](../tools/check_attack.py) against the v20 STIX bundle: every ID is current, the names match, and each tactic is valid for its technique.

| Observation | Tactic | Technique | ID |
|---|---|---|---|
| Fake M365 email with sign-in link | Initial Access | Phishing: Spearphishing Link | T1566.002 |
| Sign-in with the phished password | Initial Access | Valid Accounts: Cloud Accounts | T1078.004 |
| PowerShell on the workstation | Execution | Command and Scripting Interpreter: PowerShell | T1059.001 |
| `-enc` Base64 command | Stealth | Obfuscated Files or Information: Command Obfuscation | T1027.010 |
| Outbound connection to the domain | Command and Control | Application Layer Protocol: Web Protocols | T1071.001 |
| Logon scheduled task | Persistence | Scheduled Task/Job: Scheduled Task | T1053.005 |
| LSASS access | Credential Access | OS Credential Dumping: LSASS Memory | T1003.001 |
| RDP to the research server | Lateral Movement | Remote Services: Remote Desktop Protocol | T1021.001 |
| RDP as `it.admin2` | Persistence | Valid Accounts: Domain Accounts | T1078.002 |
| Folders zipped | Collection | Archive Collected Data: Archive via Utility | T1560.001 |
| ZIPs staged in a temp folder | Collection | Data Staged: Local Data Staging | T1074.001 |
| 2.3 GB to cloud storage | Exfiltration | Exfiltration Over Web Service: Exfiltration to Cloud Storage | T1567.002 |
| Security log cleared | Defense Impairment | Disable or Modify Tools: Clear Windows Event Logs | T1685.005 |

Since v19 (April 2026), Defense Evasion is split into Stealth (TA0005) and Defense Impairment (TA0112), and log clearing moved from T1070.001 to T1685.005.

## 7. Diamond Model

- **Adversary.** Hands-on, moved from phishing to data theft in about 48 hours and cleared logs. Research data was the target, which points to espionage or extortion. Not attributed: the only attribution claim is a C4 blog, and an insider is not ruled out.
- **Capability.** Credential phishing, encoded PowerShell loader, scheduled-task persistence, LSASS dumping (tool unknown), RDP with stolen credentials, ZIP archiving, cloud upload, log clearing.
- **Infrastructure.** Phishing email and harvesting page; sign-in IP `203.0.113.45`; C2 domain `ms365-authsync[.]example`; a legitimate cloud file-sharing service; internally, the workstation and research server as pivots.
- **Victim.** A large healthcare organisation; a senior researcher, probably chosen for access to research systems; medical research documents, possibly linked to clinical-trial or patient data.

Each edge is a pivot. The C2 domain leads to more attacker domains and IPs (passive DNS, WHOIS, certificates). Searching our logs for those, the sign-in IP and the upload site finds other victims, such as other users who clicked or other servers uploading. Decoding the payload exposes more infrastructure. Comparing the victim profile with advisories narrows the adversary without relying on one blog.

## 8. Pyramid of Pain

| Indicator | Level |
|---|---|
| File hash | Hash values (trivial) |
| Malicious IP | IP addresses (easy) |
| Malicious domain | Domain names (simple) |
| PowerShell execution pattern | Host artifacts (annoying) |
| Scheduled-task persistence | TTPs (tough) |
| Credential dumping | TTPs (tough) |
| Operational procedure (phish → creds → RDP → archive → upload → clear) | TTPs (tough) |

Hashes, IPs and domains are the cheapest for the attacker to change. Behaviour detections cost them the most, because they have to change how they operate. The SOC should prioritise behaviour-based detection and keep IOC blocking as a fast second layer for containment and retro-hunting.

## 9. Hunting

Three hypotheses, each a KQL query in [`../hunting`](../hunting), all correlating more than one table:

| Hunt | Hypothesis | Telemetry |
|---|---|---|
| Q1 | A new-IP sign-in is followed within 2 hours by encoded PowerShell under the same account | SigninLogs, SecurityEvent 4688 |
| Q2 | The host with the LSASS alert is the source of remote logons within 24 hours | SecurityAlert, SecurityEvent 4624/4625 |
| Q3 | A host that creates archives in a temp folder then uploads > 0.5 GB, and may clear logs | DeviceFileEvents, DeviceNetworkInfo, CommonSecurityLog, SecurityEvent 1102, System 104 |

A negative result doesn't rule anything out: command-line logging may be off, the attacker may have used SMB or WinRM instead of RDP, or sent data in smaller pieces. Widen the search before concluding. What changed in the revised queries, and why, is in [`hunting/README.md`](../hunting/README.md).

## 10. Detections

| Type | Logic | ATT&CK | False positives | Response |
|---|---|---|---|---|
| IOC | Any DNS, proxy or sign-in activity involving the C2 domain or `203.0.113.45` | T1071.001, T1078.004 | Low; stale IOCs on shared hosting | Isolate host, block, revoke sessions |
| Behaviour | Event 4698: new scheduled task running PowerShell with an encoded-command flag or hidden window at logon | T1053.005, T1059.001 | Moderate: IT automation, software deployment; allow-list known accounts | Save task XML, decode, check C2, hunt the same task elsewhere |
| Correlation | LSASS alert followed within 24 h by remote logons from the same host with another account; critical if the target then archives and uploads > 0.5 GB | T1003.001, T1021.001, T1567.002 | Low; mostly authorised testing | Isolate both hosts, disable the account, reset cached credentials, open an incident |

## 11. Confidence

- **High confidence** that the eight events are related and not coincidence (H3 is inconsistent with seven items of our own telemetry).
- **Moderate confidence** that research data was exfiltrated and an admin credential was compromised.
- **Low confidence** that the actor was external rather than an insider. After re-rating, the difference between H1 and H2 rests on two unverified outside claims about the C2 domain (B2 feed, C4 blog).

Evidence quality: mostly our own telemetry with clear timestamps, but the payload, archive contents and part of the server's logs are missing. Corroboration: identity, endpoint and network data agree; the exfiltration rests on one network source.

## 12. Technical product (SOC)

IOCs: sign-in IP `203.0.113.45`; C2 `ms365-authsync[.]example`; upload `files.cloudshare[.]example`; logon scheduled task on NSH-RES-WS042; ZIPs in `C:\Windows\Temp` on NSH-RES-SRV01. ATT&CK: T1566.002, T1078.004, T1059.001, T1027.010, T1053.005, T1003.001, T1021.001, T1560.001, T1567.002, T1685.005. Deploy: TI match on the domain and IP; 4698 tasks running encoded PowerShell; LSASS alert followed by remote logons from the same host. Hunt: other recipients of the email, encoded PowerShell (all flag spellings) and new tasks on all endpoints, every logon by `it.admin2`, archive-then-upload on servers. Check the C2 domain and upload site against the government advisory's indicators first: it is the quickest way to separate an external actor from an insider.

## 13. Operational product (security management)

Likely sequence: phishing, M365 account takeover, PowerShell foothold and persistence on NSH-RES-WS042, credential theft, RDP to NSH-RES-SRV01, research data zipped and ~2.3 GB uploaded, logs cleared. Affected: the researcher's account, NSH-RES-WS042, NSH-RES-SRV01, `it.admin2`, two servers with failed attempts. Contain: reset accounts and revoke sessions, isolate both hosts with evidence preserved, block the domain and upload site, restrict RDP to research servers. An insider can't be excluded yet, so bring HR and legal in quietly and limit who knows the details. Gaps: what was taken, who received it, how the endpoint was first compromised, which credentials were stolen.

## 14. Strategic product (executives)

Research data was probably copied to an outside cloud service after a senior researcher's account was compromised. We are confident the events are linked. We can't yet say whether an outside group or someone inside did it, or whether patient information was included. Impact could include loss of research IP, privacy reporting obligations and reputational harm. Recommended now: bring in incident response support, start a legal and privacy review, and keep the investigation's details on a need-to-know basis.

## 15. Final assessment

- **Known:** phishing email; new-IP sign-in; encoded PowerShell ~90 min later contacting a feed-listed domain; logon scheduled task; LSASS alert; RDP from that workstation, one success to the research server; research folders zipped; ~2.3 GB uploaded; Security log cleared.
- **Assessed:** one coordinated intrusion (high); admin credentials probably stolen and research data probably exfiltrated (moderate); external rather than insider (low, pending E15–E18).
- **Unknown:** contents of the upload, owner of the receiving account, first code-execution vector, which credentials were dumped, whether other hosts are affected.
- **Recommended:** reset the researcher's and `it.admin2` credentials and everything cached on the workstation; revoke sessions; isolate both hosts; block the domain, IP and upload site; decode the PowerShell; recover archive listings; request preservation from the cloud provider; run the three hunts network-wide; check the advisory's indicators; involve HR and legal discreetly. Longer term: phishing-resistant MFA, Credential Guard for LSASS, RDP restricted to research servers, logs forwarded off-host in real time.
