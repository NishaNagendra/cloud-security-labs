# S3 Public Access Audit

A Python (boto3) script that scans every S3 bucket in an AWS account and flags any that are publicly accessible.

## What it does

For each bucket, the script checks three independent signals:

1. **Bucket ACL grants** — flags any grant to `AllUsers` (the entire internet) or `AuthenticatedUsers` (any AWS account).
2. **Bucket policy status** — uses AWS's own `GetBucketPolicyStatus` API to catch buckets made public through policy.
3. **Public Access Block (PAB) configuration** — flags buckets where PAB is missing or only partially enabled.

## Why it matters

Publicly exposed S3 buckets are one of the most common causes of real-world cloud data breaches. A bucket can look private in one place (e.g. ACLs) and still be exposed in another (e.g. bucket policy), which is why this script checks all three layers in one pass.

## Setup

```bash
pip install boto3
aws configure
```

Requires read-only IAM permissions: `s3:ListAllMyBuckets`, `s3:GetBucketAcl`, `s3:GetBucketPolicyStatus`, `s3:GetPublicAccessBlock`.

## Usage

```bash
python3 s3_public_access_audit.py
python3 s3_public_access_audit.py --profile my-profile --region ap-south-1
```

## Tested against a real misconfiguration

I validated this script by creating a sandboxed test bucket, disabling Public Access Block, and applying a public-read bucket policy. The script correctly flagged both issues:
The bucket was locked back down and deleted immediately after the test.

## Remediation if a bucket is flagged

1. Remove ACL grants to `AllUsers` / `AuthenticatedUsers` unless intentional (e.g. static website hosting).
2. Review and tighten the bucket policy — avoid `"Principal": "*"` without a strict condition.
3. Enable all four Public Access Block settings unless there's a documented reason not to.
4. Consider AWS Config's `s3-bucket-public-read-prohibited` managed rule for ongoing detection.

## Notes

This script is read-only — it never modifies any bucket setting.
