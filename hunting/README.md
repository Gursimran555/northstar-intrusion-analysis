# Hunting queries

Three correlation hunts for the NorthStar case, for Microsoft Sentinel / Defender XDR. The first versions are in [`original/`](original). They were run in Azure Monitor Log Analytics against small simulated `datatable()` datasets and found the scenario's events.

Re-reading them against how the telemetry behaves in a real environment turned up the problems below. The revised versions fix them.

| Hunt | Problem in the first version | Effect | Fix |
|---|---|---|---|
| Q1 | `\s-(e\|enc\|encodedcommand)\s` | PowerShell accepts any prefix of `-EncodedCommand` (`-en`, `-enco`, `-encod`…) plus `-ec`, after `-`, `--`, `/`, or an en dash, em dash or horizontal bar (see `CommandLineParameterParser.cs` and `IsDash()` in PowerShell's source). The regex matched 3 of the 15 flag names, and only after a plain hyphen | Regex covers every prefix and every lead character, and doesn't match `-Encoding` |
| Q1 | `join kind=inner baseline` | A user with no successful sign-in in the 14-day lookback (a new starter, someone back from leave) has no baseline row, so their sign-ins disappear from the hunt instead of being flagged | `leftouter` join, flagged as `NoBaseline` |
| Q1 | `powershell.exe` only | `pwsh.exe` (PowerShell 7) was not covered | Both |
| Q2 | `LogonType == 10` for 4624 and 4625 | With Network Level Authentication, which is on by default, a failed RDP attempt is rejected before a session exists and is logged as 4625 **type 3**. The hunt counted successes, but not the failed attempts around them | 4625 with type 3 or 10. Type 3 also covers SMB, so failures are read as remote logon failures from that host |
| Q2, Q3 | Join on raw host names | `CompromisedEntity`, `WorkstationName`, `Computer` and `DeviceName` can be an FQDN in one table and a NetBIOS name in another, in different case. The join then silently returns nothing | Compare on the short upper-case host name |
| Q3 | Upload volume grouped by `SourceHostName` | Many firewalls and proxies log only the source IP | Map IP to device through `DeviceNetworkInfo`, use `SourceHostName` as a fallback |
| Q3 | Only Event 1102 | 1102 is the Security log. Clearing System, Application or Sysmon logs is Event 104 in the System log | Both |

## Checking the queries

[`tools/kql_check.js`](../tools/kql_check.js) parses and type-checks every query with Microsoft's own KQL parser, [Kusto.Language](https://www.npmjs.com/package/@kusto/language-service-next), against the table columns in [`tools/kql_schemas.json`](../tools/kql_schemas.json). It catches syntax errors, misspelled columns and type mismatches. CI runs it on every push.

```bash
npm install
npm run kql
```

It doesn't run the queries. The revised versions haven't been re-run against data yet. A misspelled column fails the check, but a wrong threshold or join logic doesn't.
