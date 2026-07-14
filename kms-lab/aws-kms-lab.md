# AWS KMS Hands-On Lab: Key Lifecycle, BYOK, and Service Integration

## Overview
This lab covers AWS Key Management Service (KMS) from key creation through
real-world service integration and secure cleanup. It demonstrates:

- Symmetric and asymmetric KMS key creation
- Bring-Your-Own-Key (BYOK) import using OpenSSL and RSA key wrapping
- SSE-KMS encryption for Amazon S3
- EBS volume encryption at EC2 launch
- Direct encrypt/decrypt operations via AWS CLI
- Cost-conscious cleanup (instance termination, bucket deletion, key deletion scheduling)

**Region used:** `eu-north-1` (Stockholm)
**Access model:** IAM user (`Nisha01`) — root login never used

---

## 1. Customer-Managed KMS Keys

Created two customer-managed keys via the KMS console:

| Alias | Type | Key Usage | Purpose |
|---|---|---|---|
| `nisha/sym` | Symmetric (SYMMETRIC_DEFAULT) | Encrypt/Decrypt | S3, EBS, CLI encryption |
| `nisha/asym` | Asymmetric (RSA_2048) | Encrypt/Decrypt | Signature/small-payload use cases |

**Key takeaway:** S3 SSE-KMS and EBS volume encryption only work with **symmetric**
keys — they rely on `GenerateDataKey`, an API not supported by asymmetric keys.
Asymmetric keys are used for signing/verification or encrypting small payloads
outside AWS, not for bulk/service-level encryption.

---

## 2. Bring-Your-Own-Key (BYOK) via External Key Import

Practiced importing externally-generated key material into a KMS key with
`Origin: EXTERNAL` (alias `nisha/external`).

**Process:**
1. Created a KMS key with key material origin set to **External (Import Key material)**
2. Downloaded AWS's public wrapping key (`WrappingPublicKey.bin`, RSA_4096) and a
   time-limited import token (`ImportToken.bin`, 24-hour validity)
3. Generated a 256-bit AES key locally:
   ```bash
   openssl rand -out PlaintextKeyMaterial.bin 32
   ```
4. Wrapped (encrypted) the key material using AWS's public wrapping key:
   ```bash
   openssl pkeyutl -encrypt \
     -in PlaintextKeyMaterial.bin \
     -out EncryptedKeyMaterial.bin \
     -inkey WrappingPublicKey.bin \
     -keyform DER -pubin \
     -pkeyopt rsa_padding_mode:oaep \
     -pkeyopt rsa_oaep_md:sha256
   ```
5. Uploaded the wrapped key material + import token via the console to complete
   the import — key material state transitioned to **Current / Imported**

**Why this matters:** BYOK lets an organization retain control over raw key
generation (a common compliance requirement) while still storing/using the key
inside AWS KMS. AWS never sees the plaintext key material — only its encrypted
(wrapped) form.

---

## 3. S3 Server-Side Encryption with KMS (SSE-KMS)

- Created bucket `nisha-kms-demo` with **default encryption** set to
  **SSE-KMS** using `nisha/sym`
- Enabled **S3 Bucket Keys** to reduce KMS API call volume/cost
- Uploaded a test object (`test-kms.txt`) without specifying a per-object key —
  it inherited the bucket's default encryption
- Verified via object **Properties → Server-side encryption settings**:
  - Encryption type: `SSE-KMS`
  - Encryption key ARN matched `nisha/sym`

---

## 4. EBS Volume Encryption at EC2 Launch

- Launched a `t3.micro` EC2 instance (`EC2-kms-demo`) with a single 8 GiB `gp3`
  root volume
- Enabled **Encrypted** on the volume and selected `nisha/sym` as the KMS key
- Verified via **EC2 → Elastic Block Store → Volumes**:
  - Encryption: `Encrypted`
  - KMS Key alias: `nisha/sym`

**Security config used:** SSH access restricted to "My IP" only in the security
group (not open to `0.0.0.0/0`).

---

## 5. Direct Encrypt/Decrypt via AWS CLI

Configured AWS CLI v2 with an IAM access key for `Nisha01`, then performed raw
encrypt/decrypt operations against `nisha/sym`:

```bash
# Encrypt
aws kms encrypt \
  --key-id <key-id> \
  --plaintext fileb://secret.txt \
  --output text \
  --query CiphertextBlob \
  --cli-binary-format raw-in-base64-out | base64 -d > secret.encrypted

# Decrypt (no --key-id needed — KMS reads it from ciphertext metadata)
aws kms decrypt \
  --ciphertext-blob fileb://secret.encrypted \
  --output text \
  --query Plaintext \
  --cli-binary-format raw-in-base64-out | base64 -d > secret-decrypted.txt
```

**Result:** Original plaintext and decrypted output matched exactly, confirming
a successful round-trip.

**Key takeaway:** `aws kms decrypt` never requires you to specify a key ID —
the ciphertext blob carries key metadata internally. Direct KMS encrypt/decrypt
is limited to payloads ≤ 4 KB; larger data uses **envelope encryption** via
`GenerateDataKey`, where KMS returns a data key used locally to encrypt the
actual file.

---

## 6. Cleanup (Cost Control)

To avoid ongoing charges, all resources were decommissioned in this order:

1. **EC2 instance** → Terminated (`Delete on termination = Yes`, so the
   encrypted root volume was removed automatically)
2. **S3 bucket** → Object deleted, then bucket deleted (`nisha-kms-demo`)
3. **KMS keys** → All three keys (`nisha/sym`, `nisha/external`, `nisha/asym`)
   scheduled for deletion with a 7-day minimum waiting period
   - No charges accrue once deletion is scheduled
   - Deletion is irreversible after the waiting period expires

---

## Skills Demonstrated
- KMS key lifecycle management (create, import, rotate, schedule deletion)
- Symmetric vs. asymmetric key selection based on service compatibility
- BYOK / external key import workflow (RSA-OAEP wrapping with OpenSSL)
- SSE-KMS integration with S3 (bucket-level default encryption, Bucket Keys)
- EBS volume encryption at instance launch
- AWS CLI-based encrypt/decrypt operations and envelope encryption concepts
- Least-privilege practices: IAM user over root, SSH restricted to specific IP
- Cost-aware cloud hygiene: proactive cleanup of billable resources
