# Security Group Open Port Scanner

A Python (boto3) script that scans EC2 Security Groups for inbound rules open to the entire internet (`0.0.0.0/0` or `::/0`), flags the port/protocol, and can send an SNS email alert when found.

## What it does

1. Lists all security groups in a region.
2. Checks every inbound rule for a source of `0.0.0.0/0` (IPv4) or `::/0` (IPv6).
3. Flags the port and protocol involved.
4. Calls out well-known sensitive ports by name (SSH, RDP, MySQL, PostgreSQL, MongoDB, etc.) as HIGH RISK, since these are common attacker targets.
5. Optionally publishes a summary to an SNS topic for email/SMS alerting.

## Why an open 0.0.0.0/0 rule is dangerous

A rule with source `0.0.0.0/0` means the port is reachable from any IP address on the internet. Attackers run continuous automated scans looking for exactly this — open SSH/RDP to brute-force, exposed databases to dump, or open management ports to exploit. Many real breaches trace back to a security group rule opened "temporarily" and never closed.

## Setup

```bash
pip install boto3
aws configure
```

Requires `ec2:DescribeSecurityGroups` (read-only) and `sns:Publish` scoped to a specific topic (only if using `--sns-topic-arn`).

## Usage

```bash
python3 sg_open_port_scanner.py --region ap-south-1

# With SNS email alert:
python3 sg_open_port_scanner.py --region ap-south-1 --sns-topic-arn arn:aws:sns:ap-south-1:xxxx:sg-alerts
```

## Tested against a real misconfiguration

I created a sandboxed test security group, opened port 22 (SSH) to `0.0.0.0/0`, and confirmed the script caught it:

[HIGH RISK] sg-xxxx (nisha-test-open-sg): port 22/TCP open to 0.0.0.0/0 (SSH)

I also configured a scoped SNS permission (publish access to one specific topic only, not full SNS access) and confirmed a real alert email was delivered. All test resources — the security group, the SNS topic, and the temporary IAM permission — were deleted immediately after validation.

## Remediation if a rule is flagged

1. Restrict the source CIDR to only what needs access, instead of `0.0.0.0/0`.
2. For SSH/RDP, prefer AWS Systems Manager Session Manager or a bastion host/VPN instead of exposing the port directly.
3. Keep databases in a private subnet with no direct internet access.
4. Consider AWS Config's `restricted-ssh` managed rule for ongoing detection.

## Notes

This script is read-only with respect to EC2. The only write action it can take is publishing to SNS, and only if `--sns-topic-arn` is provided with a permission scoped to that specific topic.
