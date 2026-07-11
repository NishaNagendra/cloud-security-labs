# GuardDuty — Enabled and Explored

## What I did
Enabled Amazon GuardDuty (all features) in us-east-1 to explore its 
threat detection capabilities. Reviewed the empty findings dashboard 
on a fresh account (no findings, since no suspicious activity had 
occurred yet). Reviewed AWS documentation on finding types and watched 
a walkthrough demo covering the console, severity levels, and 
multi-account management.

## Key learnings
- GuardDuty analyzes CloudTrail, VPC Flow Logs, and DNS logs — no 
  agents or infrastructure required
- Findings are categorized by severity: Critical, High, Medium, Low
- A 30-day free trial starts the moment GuardDuty is first enabled 
  per region
- Disabled after initial exploration to manage trial timing 
  alongside other services being tested this week (Security Hub, etc.)

## Interview-ready summary
GuardDuty is a threat detection service that continuously monitors 
AWS accounts for malicious activity using threat intelligence and 
machine learning, with no infrastructure to manage.
