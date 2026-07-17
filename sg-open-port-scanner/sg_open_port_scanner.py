#!/usr/bin/env python3
"""
sg_open_port_scanner.py

Scans EC2 Security Groups for inbound rules that allow traffic from
0.0.0.0/0 (any IPv4 address) or ::/0 (any IPv6 address), flags the
port/protocol involved, and optionally sends an SNS alert when found.
"""

import argparse
import sys

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

OPEN_IPV4 = "0.0.0.0/0"
OPEN_IPV6 = "::/0"

SENSITIVE_PORTS = {
    22: "SSH",
    3389: "RDP",
    3306: "MySQL",
    5432: "PostgreSQL",
    1433: "MSSQL",
    27017: "MongoDB",
    6379: "Redis",
    9200: "Elasticsearch",
    23: "Telnet",
    21: "FTP",
}


def describe_port_range(perm):
    protocol = perm.get("IpProtocol", "unknown")
    if protocol == "-1":
        return "ALL PORTS", "ALL"

    from_port = perm.get("FromPort")
    to_port = perm.get("ToPort")

    if from_port is None or to_port is None:
        return "ALL PORTS", protocol.upper()

    if from_port == to_port:
        port_str = str(from_port)
    else:
        port_str = f"{from_port}-{to_port}"

    return port_str, protocol.upper()


def label_for_port(from_port, to_port):
    if from_port is None or to_port is None:
        return None
    for port, name in SENSITIVE_PORTS.items():
        if from_port <= port <= to_port:
            return name
    return None


def find_open_rules(security_group):
    findings = []
    group_id = security_group["GroupId"]
    group_name = security_group.get("GroupName", "N/A")

    for perm in security_group.get("IpPermissions", []):
        port_str, protocol = describe_port_range(perm)
        from_port = perm.get("FromPort")
        to_port = perm.get("ToPort")
        service_label = label_for_port(from_port, to_port)
        label_suffix = f" ({service_label})" if service_label else ""

        for ip_range in perm.get("IpRanges", []):
            if ip_range.get("CidrIp") == OPEN_IPV4:
                severity = "HIGH RISK" if service_label else "FLAGGED"
                findings.append(
                    f"  [{severity}] {group_id} ({group_name}): "
                    f"port {port_str}/{protocol} open to {OPEN_IPV4}{label_suffix}"
                )

        for ip_range in perm.get("Ipv6Ranges", []):
            if ip_range.get("CidrIpv6") == OPEN_IPV6:
                severity = "HIGH RISK" if service_label else "FLAGGED"
                findings.append(
                    f"  [{severity}] {group_id} ({group_name}): "
                    f"port {port_str}/{protocol} open to {OPEN_IPV6}{label_suffix}"
                )

    return findings


def send_sns_alert(session, region, topic_arn, findings_by_group):
    sns = session.client("sns", region_name=region)
    lines = ["Security Group audit found open inbound rule(s) to the internet:\n"]
    for group_id, findings in findings_by_group.items():
        lines.extend(findings)
    message = "\n".join(lines)

    try:
        sns.publish(
            TopicArn=topic_arn,
            Subject="AWS Security Alert: Open Security Group Rule Detected",
            Message=message,
        )
        print(f"\nSNS alert sent to topic: {topic_arn}")
    except ClientError as e:
        print(f"\nCould not send SNS alert: {e.response['Error']['Message']}")


def main():
    parser = argparse.ArgumentParser(description="Scan EC2 Security Groups for rules open to the internet.")
    parser.add_argument("--profile", help="AWS named profile to use (optional)")
    parser.add_argument("--region", default="us-east-1", help="AWS region to scan")
    parser.add_argument("--sns-topic-arn", help="If set, publish a summary alert to this SNS topic")
    args = parser.parse_args()

    session_kwargs = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile

    try:
        session = boto3.Session(**session_kwargs)
        ec2 = session.client("ec2", region_name=args.region)
        paginator = ec2.get_paginator("describe_security_groups")
        security_groups = []
        for page in paginator.paginate():
            security_groups.extend(page["SecurityGroups"])
    except NoCredentialsError:
        print("No AWS credentials found. Run `aws configure` first.")
        sys.exit(1)
    except ClientError as e:
        print(f"Could not describe security groups: {e.response['Error']['Message']}")
        sys.exit(1)

    if not security_groups:
        print(f"No security groups found in region {args.region}.")
        return

    print(f"Scanning {len(security_groups)} security group(s) in {args.region}...\n")

    findings_by_group = {}
    for sg in security_groups:
        findings = find_open_rules(sg)
        if findings:
            findings_by_group[sg["GroupId"]] = findings

    if not findings_by_group:
        print("No security groups with rules open to the internet were found.")
        return

    total_findings = 0
    for group_id, findings in findings_by_group.items():
        for f in findings:
            print(f)
            total_findings += 1

    print("\n--- Summary ---")
    print(f"Security groups scanned: {len(security_groups)}")
    print(f"Security groups flagged: {len(findings_by_group)}")
    print(f"Total risky rules found: {total_findings}")

    if args.sns_topic_arn:
        send_sns_alert(session, args.region, args.sns_topic_arn, findings_by_group)
    else:
        print("\nTip: pass --sns-topic-arn <arn> to get an email/SMS alert for these findings.")


if __name__ == "__main__":
    main()
