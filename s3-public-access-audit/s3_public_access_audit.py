#!/usr/bin/env python3
"""
s3_public_access_audit.py

Audits every S3 bucket in the account and flags any that are publicly
accessible, either through:
  1. Bucket ACLs granting access to "AllUsers" or "AuthenticatedUsers"
  2. A bucket policy that Amazon's own policy-status check considers public
  3. Public Access Block settings that are NOT fully locked down
"""

import argparse
import sys

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

ALL_USERS_URI = "http://acs.amazonaws.com/groups/global/AllUsers"
AUTHENTICATED_USERS_URI = "http://acs.amazonaws.com/groups/global/AuthenticatedUsers"


def get_public_acl_grants(s3_client, bucket_name):
    findings = []
    try:
        acl = s3_client.get_bucket_acl(Bucket=bucket_name)
    except ClientError as e:
        findings.append(f"  [ERROR] Could not read ACL: {e.response['Error']['Message']}")
        return findings

    for grant in acl.get("Grants", []):
        grantee = grant.get("Grantee", {})
        uri = grantee.get("URI", "")
        permission = grant.get("Permission", "UNKNOWN")

        if uri == ALL_USERS_URI:
            findings.append(f"  [PUBLIC-ACL] Grants '{permission}' to ALL USERS (anyone on the internet)")
        elif uri == AUTHENTICATED_USERS_URI:
            findings.append(f"  [PUBLIC-ACL] Grants '{permission}' to ANY AUTHENTICATED AWS USER (not just your account)")

    return findings


def get_public_policy_status(s3_client, bucket_name):
    findings = []
    try:
        status = s3_client.get_bucket_policy_status(Bucket=bucket_name)
        is_public = status["PolicyStatus"]["IsPublic"]
        if is_public:
            findings.append("  [PUBLIC-POLICY] Bucket policy is flagged as PUBLIC by AWS")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code != "NoSuchBucketPolicy":
            findings.append(f"  [ERROR] Could not read policy status: {e.response['Error']['Message']}")

    return findings


def get_weak_public_access_block(s3_client, bucket_name):
    findings = []
    try:
        config = s3_client.get_public_access_block(Bucket=bucket_name)
        settings = config["PublicAccessBlockConfiguration"]
        weak_settings = [name for name, enabled in settings.items() if not enabled]
        if weak_settings:
            findings.append(f"  [WEAK-PAB] Public Access Block NOT fully enabled - disabled: {', '.join(weak_settings)}")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "NoSuchPublicAccessBlockConfiguration":
            findings.append("  [WEAK-PAB] No Public Access Block configuration set at all (defaults are not safe)")
        else:
            findings.append(f"  [ERROR] Could not read Public Access Block: {e.response['Error']['Message']}")

    return findings


def audit_bucket(s3_client, bucket_name):
    findings = []
    findings.extend(get_public_acl_grants(s3_client, bucket_name))
    findings.extend(get_public_policy_status(s3_client, bucket_name))
    findings.extend(get_weak_public_access_block(s3_client, bucket_name))
    return findings


def main():
    parser = argparse.ArgumentParser(description="Audit S3 buckets for public access.")
    parser.add_argument("--profile", help="AWS named profile to use (optional)")
    parser.add_argument("--region", default="us-east-1", help="Region for the client (bucket listing is global)")
    args = parser.parse_args()

    session_kwargs = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile

    try:
        session = boto3.Session(**session_kwargs)
        s3 = session.client("s3", region_name=args.region)
        buckets = s3.list_buckets()["Buckets"]
    except NoCredentialsError:
        print("No AWS credentials found. Run `aws configure` first.")
        sys.exit(1)
    except ClientError as e:
        print(f"Could not list buckets: {e.response['Error']['Message']}")
        sys.exit(1)

    if not buckets:
        print("No S3 buckets found in this account.")
        return

    print(f"Auditing {len(buckets)} bucket(s)...\n")

    flagged_count = 0
    for bucket in buckets:
        name = bucket["Name"]
        findings = audit_bucket(s3, name)

        if findings:
            flagged_count += 1
            print(f"Bucket: {name}  -->  FLAGGED")
            for f in findings:
                print(f)
            print()
        else:
            print(f"Bucket: {name}  -->  OK (no public access detected)")

    print("\n--- Summary ---")
    print(f"Total buckets checked: {len(buckets)}")
    print(f"Buckets flagged:       {flagged_count}")


if __name__ == "__main__":
    main()
