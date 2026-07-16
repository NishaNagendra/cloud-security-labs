# CloudTrail + Athena: Querying AWS API Activity Logs

## Objective
Enable AWS CloudTrail across all regions, understand the structure of raw CloudTrail logs, and use Amazon Athena to run SQL queries against those logs directly in S3 — without needing to load them into a database first.

## What is CloudTrail?
CloudTrail records every API call made in an AWS account — console actions, CLI commands, and SDK calls alike. Each event captures:

- **Who** — the IAM identity that made the call (`userIdentity`)
- **What** — the action performed (`eventName`) and which service it hit (`eventSource`)
- **When** — a timestamp (`eventTime`)
- **Where from** — the caller's IP address (`sourceIPAddress`) and AWS region (`awsRegion`)
- **Read or write** — whether the call only viewed data or changed something (`readOnly`)

This makes CloudTrail the backbone of audit logging, incident response, and compliance in AWS.

## Setup

**1. Created a multi-region trail**
- AWS Console → CloudTrail → Create trail
- Applied to all regions (a single trail captures activity account-wide, not just one region)
- Storage: new S3 bucket, SSE-S3 encryption (avoided customer-managed KMS to prevent unnecessary per-key charges)
- Log file validation: enabled (lets you verify logs haven't been tampered with, via digest files)
- Management events: Read + Write, all API activity

**2. Inspected a raw log file**
Downloaded a `.json.gz` file from:
```
s3://<bucket>/AWSLogs/<account-id>/CloudTrail/<region>/<year>/<month>/<day>/
```

Sample record structure:
```json
{
  "eventVersion": "1.11",
  "userIdentity": {
    "type": "IAMUser",
    "arn": "arn:aws:iam::<account-id>:user/Nisha01",
    "userName": "Nisha01",
    "sessionContext": {
      "attributes": { "mfaAuthenticated": "false" }
    }
  },
  "eventTime": "2026-07-16T00:32:59Z",
  "eventSource": "cloudtrail.amazonaws.com",
  "eventName": "ListTrails",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "203.0.113.0",
  "readOnly": true,
  "eventType": "AwsApiCall",
  "sessionCredentialFromConsole": "true"
}
```

## Querying with Athena

**1. Created the Athena table**

Rather than hand-writing the nested `STRUCT` DDL (angle-bracket syntax is easy to mangle on paste), used CloudTrail's built-in table generator:
> CloudTrail Console → Event history → **Create Athena table** → select the trail's S3 bucket → Create table

This auto-generates a `CREATE EXTERNAL TABLE` statement with the correct nested types for `userIdentity`, `resources`, and `tlsDetails`, using the `org.apache.hive.hcatalog.data.JsonSerDe` SerDe.

**2. Queried recent activity**

```sql
SELECT
  eventTime,
  eventName,
  userIdentity.userName AS username,
  sourceIPAddress,
  awsRegion
FROM cloudtrail_logs_aws_cloudtrail_logs_<account-id>_<suffix>
ORDER BY eventTime DESC
LIMIT 20;
```

**3. Found console login events**

```sql
SELECT
  eventTime,
  userIdentity.userName AS username,
  sourceIPAddress
FROM cloudtrail_logs_aws_cloudtrail_logs_<account-id>_<suffix>
WHERE eventName = 'ConsoleLogin'
ORDER BY eventTime DESC;
```

## Notes & lessons learned
- Athena charges **$5 per TB scanned**; a lab-sized CloudTrail dataset (KBs–MBs) costs fractions of a cent per query.
- The Athena query result S3 location must be set once before running any query (Query settings → Query result location).
- A new AWS account/browser session may not have a `default` database selected automatically — create one explicitly if the dropdown is empty (`CREATE DATABASE IF NOT EXISTS <name>;`).
- CloudTrail logs its own API calls too (e.g. `ListTrails`, `GetTrailStatus`) — a good example of the audit trail being self-referential.
- Best practice: log in as an IAM user for daily work rather than the root account, and enable MFA on that IAM user.

## Interview takeaway
> "CloudTrail logs every API call in JSON format — the identity (`userIdentity`), the action (`eventName`/`eventSource`), timestamp (`eventTime`), source IP (`sourceIPAddress`), region (`awsRegion`), and read/write status (`readOnly`). Athena lets you run standard SQL directly against these logs in S3 without needing to load them into a separate database, which makes it a fast way to investigate specific activity — like finding every login to an account — without setting up additional infrastructure."
