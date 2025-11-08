# Quick Start Guide - AWS Deployment & Benchmarking

**Deploy Lab2 and Lab3 to AWS EC2 and run performance benchmarks in 5 minutes**

## Prerequisites

- AWS Account with credentials
- Python 3.6+
- ApacheBench (`ab`)

## Setup (One-time)

### 1. Install Dependencies

```bash
pip install boto3 python-dotenv
```

### 2. Configure AWS Credentials

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your AWS credentials
nano .env  # or use any text editor
```

Add your AWS credentials:
```
AWS_ACCESS_KEY=your_key_here
AWS_SECRET_KEY=your_secret_here
```

### 3. Generate Lab3 Database (Required)

```bash
cd Lab3
python crawler.py
cd ..
```

## Deploy to AWS

### Deploy Both Labs

```bash
python aws_ec2_installer.py --lab both --action all
```

**What this does:**
- Creates EC2 key pair (`ece326-keypair.pem`)
- Launches 2 EC2 instances (one for Lab2, one for Lab3)
- Installs all dependencies
- Copies application files

**Output will show:**
```
Instance ID:  i-xxxxx
Public IP:    3.83.233.24
```

Save these IPs!

### Start Applications on EC2

For each instance:

```bash
# SSH into instance
ssh -i ece326-keypair.pem ubuntu@YOUR_PUBLIC_IP

# Start application
nohup python3 frontend.py > frontend.log 2>&1 &

# Exit SSH
exit
```

Test in browser:
- Lab2: http://YOUR_LAB2_IP:8080
- Lab3: http://YOUR_LAB3_IP:8080

## Run Benchmarks

```bash
python benchmark_comparison.py \
    --lab2-url http://3.83.233.24:8080 \
    --lab3-url http://98.93.66.138:8080
```

**Results saved to:**
- `BENCHMARK_RESULTS.md` - Comparison report
- `BENCHMARK_RESULTS.json` - Raw data

## Cleanup (Important!)

When done, terminate instances to avoid charges:

```bash
# List running instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]' --output table

# Terminate instances
aws ec2 terminate-instances --instance-ids i-xxxxx i-yyyyy
```

## Common Commands

### Deploy Only Lab2
```bash
python aws_ec2_installer.py --lab 2 --action all
```

### Deploy Only Lab3
```bash
python aws_ec2_installer.py --lab 3 --action all
```

### Benchmark Only Lab2
```bash
python benchmark_comparison.py --lab2-url http://YOUR_IP:8080
```

### Custom Benchmark (more intensive)
```bash
python benchmark_comparison.py \
    --lab2-url http://IP1:8080 \
    --lab3-url http://IP2:8080 \
    --requests 2000 \
    --concurrency 20
```

### SSH into Instance
```bash
ssh -i ece326-keypair.pem ubuntu@YOUR_PUBLIC_IP
```

### Check Application Status
```bash
# On EC2 instance
ps aux | grep frontend
tail -f frontend.log
```

### Restart Application
```bash
# On EC2 instance
pkill -f frontend.py
nohup python3 frontend.py > frontend.log 2>&1 &
```

## Troubleshooting

### "Permission denied" when SSH
```bash
chmod 400 ece326-keypair.pem
```

### "boto3 not found"
```bash
pip install boto3 python-dotenv
```

### "ab command not found"
```bash
# Ubuntu/Debian
sudo apt-get install apache2-utils

# macOS
brew install httpd
```

### Application not responding
```bash
# SSH into instance
ssh -i ece326-keypair.pem ubuntu@YOUR_IP

# Check logs
tail -100 frontend.log

# Check if running
ps aux | grep frontend

# Restart
pkill -f frontend.py
nohup python3 frontend.py > frontend.log 2>&1 &
```

## File Checklist

Before deploying:

**For Lab2:**
- [ ] `.env` file with AWS and Google credentials
- [ ] `Lab2/client_secret.json` (Google OAuth)
- [ ] `Lab2/static/` directory

**For Lab3:**
- [ ] `.env` file with AWS credentials
- [ ] `Lab3/search_engine.db` (run `python crawler.py` first!)

## Cost Estimate

**AWS Free Tier eligible:**
- 2 x t3.micro instances × 24 hours = **$0** (within free tier)
- After free tier: ~$0.50/day

**Total for 3-day lab requirement: $0 - $1.50**

## Need More Help?

See comprehensive guide: `AWS_DEPLOYMENT_GUIDE.md`

---

**Quick Reference:**

| Task | Command |
|------|---------|
| Install tools | `pip install boto3 python-dotenv` |
| Deploy both labs | `python aws_ec2_installer.py --lab both --action all` |
| Start app on EC2 | `nohup python3 frontend.py > frontend.log 2>&1 &` |
| Run benchmark | `python benchmark_comparison.py --lab2-url URL1 --lab3-url URL2` |
| SSH to instance | `ssh -i ece326-keypair.pem ubuntu@IP` |
| Terminate instance | `aws ec2 terminate-instances --instance-ids i-xxxxx` |

---

Happy deploying! 🚀
