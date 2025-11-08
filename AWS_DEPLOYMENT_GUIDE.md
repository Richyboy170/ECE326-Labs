# AWS EC2 Deployment and Benchmark Guide

Complete guide for deploying Lab2 and Lab3 on AWS EC2 instances and running performance benchmarks.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [AWS EC2 Deployment](#aws-ec2-deployment)
5. [Benchmark Testing](#benchmark-testing)
6. [Troubleshooting](#troubleshooting)
7. [Cost Management](#cost-management)

## Overview

This repository provides automated tools for:

- **AWS EC2 Installer** (`aws_ec2_installer.py`): Automates EC2 instance creation, dependency installation, and application deployment for Lab2 and Lab3
- **Benchmark Comparison** (`benchmark_comparison.py`): Runs comprehensive performance tests and generates comparison reports

## Prerequisites

### Local Machine Requirements

1. **Python 3.6+**
   ```bash
   python3 --version
   ```

2. **Required Python Packages**
   ```bash
   pip install boto3 python-dotenv
   ```

3. **AWS Account**
   - Active AWS account with EC2 access
   - AWS Access Key ID and Secret Access Key
   - AWS Free Tier eligible (t2.micro or t3.micro instances)

4. **ApacheBench (for benchmarking)**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install apache2-utils

   # macOS
   brew install httpd  # ab comes with Apache
   ```

### AWS Setup

1. **Create AWS Account**
   - Sign up at https://aws.amazon.com/

2. **Create IAM User**
   - Go to AWS Console → IAM → Users → Add User
   - Enable "Programmatic access"
   - Attach policy: `AmazonEC2FullAccess`
   - Download credentials (Access Key ID and Secret Access Key)

3. **Configure Environment Variables**

   Create a `.env` file in the repository root:

   ```bash
   # AWS Credentials
   AWS_ACCESS_KEY=your_access_key_here
   AWS_SECRET_KEY=your_secret_key_here

   # AWS Configuration
   AWS_REGION=us-east-1
   KEY_NAME=ece326-keypair
   SECURITY_GROUP_NAME=ece326-group5
   INSTANCE_TYPE=t3.micro
   UBUNTU_AMI=ami-0c398cb65a93047f2

   # Google OAuth (for Lab2)
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   ```

   **IMPORTANT:** Never commit `.env` to version control!

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-repo/ECE326-Labs.git
cd ECE326-Labs
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install minimal dependencies for deployment
pip install boto3 python-dotenv
```

### 3. Verify Installation

```bash
# Check Python packages
python3 -c "import boto3; print('boto3 installed')"

# Check ApacheBench
ab -V
```

## AWS EC2 Deployment

### Quick Start

Deploy both Lab2 and Lab3 on separate EC2 instances:

```bash
python aws_ec2_installer.py --lab both --action all
```

This will:
1. Create EC2 key pair (`ece326-keypair.pem`)
2. Create security group with necessary ports
3. Launch EC2 instances for each lab
4. Install all dependencies
5. Deploy application files

### Lab-Specific Deployment

#### Deploy Only Lab2

```bash
python aws_ec2_installer.py --lab 2 --action all
```

#### Deploy Only Lab3

```bash
python aws_ec2_installer.py --lab 3 --action all
```

### Step-by-Step Deployment

#### Step 1: Setup EC2 Instances Only

```bash
# Create EC2 instances without deploying code
python aws_ec2_installer.py --lab both --action setup
```

This creates the infrastructure but doesn't copy application files.

#### Step 2: Deploy Application Files

```bash
# Deploy Lab2 files to existing instance
python aws_ec2_installer.py --lab 2 --action deploy

# Deploy Lab3 files to existing instance
python aws_ec2_installer.py --lab 3 --action deploy
```

### Important: Lab3 Database Preparation

**Before deploying Lab3**, you must generate the database locally:

```bash
cd Lab3

# Run the crawler to generate search_engine.db
python crawler.py

# Verify database was created
ls -lh search_engine.db
```

The deployment script will copy `search_engine.db` to the EC2 instance.

### Accessing Your Deployed Applications

After deployment, you'll see output like:

```
DEPLOYMENT SUMMARY - Lab2
============================================================
Instance ID:  i-0378f9759aaa7d8d4
Public IP:    3.83.233.24
Key file:     ece326-keypair.pem
Region:       us-east-1

SSH Connection:
  ssh -i ece326-keypair.pem ubuntu@3.83.233.24

Web Application:
  http://3.83.233.24:8080
```

#### Connect via SSH

```bash
ssh -i ece326-keypair.pem ubuntu@YOUR_PUBLIC_IP
```

#### Start the Application

**Lab2:**
```bash
nohup python3 frontend.py > frontend.log 2>&1 &
```

**Lab3:**
```bash
nohup python3 frontend.py > frontend.log 2>&1 &
```

#### Access in Browser

- **Lab2:** http://YOUR_LAB2_IP:8080
- **Lab3:** http://YOUR_LAB3_IP:8080

## Benchmark Testing

### Running Benchmarks

Once both applications are running on EC2:

```bash
python benchmark_comparison.py \
    --lab2-url http://3.83.233.24:8080 \
    --lab3-url http://98.93.66.138:8080
```

### Custom Test Parameters

```bash
# More intensive testing
python benchmark_comparison.py \
    --lab2-url http://3.83.233.24:8080 \
    --lab3-url http://98.93.66.138:8080 \
    --requests 2000 \
    --concurrency 20
```

### Benchmark Only One Lab

```bash
# Benchmark Lab2 only
python benchmark_comparison.py --lab2-url http://3.83.233.24:8080

# Benchmark Lab3 only
python benchmark_comparison.py --lab3-url http://98.93.66.138:8080
```

### Understanding Benchmark Results

The script generates two files:

1. **BENCHMARK_RESULTS.md** - Human-readable comparison report
2. **BENCHMARK_RESULTS.json** - Raw data for further analysis

#### Key Metrics Explained

| Metric | Description |
|--------|-------------|
| **Requests/Second (RPS)** | Number of requests handled per second |
| **Response Time** | Average time to complete a request |
| **50th Percentile** | 50% of requests completed within this time |
| **95th Percentile** | 95% of requests completed within this time |
| **99th Percentile** | 99% of requests completed within this time (worst case) |
| **Failed Requests** | Number of failed requests (should be 0) |

#### Sample Results

```
### Lab2 - OAuth Web Application

| Metric | Value |
|--------|-------|
| Average RPS | 466.20 req/sec |
| Average Response Time | 21.45 ms |
| Average 99th Percentile | 45.00 ms |

### Lab3 - Search Engine with PageRank

| Metric | Value |
|--------|-------|
| Average RPS | 257.03 req/sec |
| Average Response Time | 38.92 ms |
| Average 99th Percentile | 78.00 ms |
```

## Troubleshooting

### EC2 Deployment Issues

#### Problem: "boto3 not found"

```bash
pip install boto3 python-dotenv
```

#### Problem: "AWS credentials not found"

Ensure `.env` file exists with valid credentials:

```bash
cat .env  # Check file exists
```

#### Problem: "Permission denied (publickey)"

Fix key file permissions:

```bash
chmod 400 ece326-keypair.pem
```

#### Problem: Instance launched but can't connect

Wait 30-60 seconds for instance to fully start, then try again.

#### Problem: "Security group already exists"

The script will use the existing security group. This is normal.

### Application Issues

#### Lab2: Google OAuth Not Working

1. Ensure `client_secret.json` is copied to EC2:
   ```bash
   scp -i ece326-keypair.pem Lab2/client_secret.json ubuntu@YOUR_IP:~/
   ```

2. Update Google OAuth redirect URI to include EC2 public IP:
   - Go to Google Cloud Console
   - Add: `http://YOUR_EC2_IP:8080/redirect`

3. Edit `frontend.py` on EC2 to use correct redirect URI

#### Lab3: Database Not Found

Generate database locally before deploying:

```bash
cd Lab3
python crawler.py
ls -lh search_engine.db  # Verify it exists
```

Then redeploy Lab3:

```bash
python aws_ec2_installer.py --lab 3 --action deploy
```

#### Application Not Starting

Check logs:

```bash
ssh -i ece326-keypair.pem ubuntu@YOUR_IP
tail -100 frontend.log
```

Check if process is running:

```bash
ps aux | grep frontend
```

Kill and restart:

```bash
pkill -f frontend.py
nohup python3 frontend.py > frontend.log 2>&1 &
```

### Benchmark Issues

#### Problem: "ab command not found"

Install ApacheBench:

```bash
sudo apt-get install apache2-utils
```

#### Problem: "Connection refused" during benchmarks

Ensure application is running:

```bash
curl http://YOUR_IP:8080/
```

#### Problem: High failure rate

- Reduce concurrency: `--concurrency 5`
- Reduce requests: `--requests 500`
- Check EC2 instance type (t2.micro may be too small)

## Cost Management

### AWS Free Tier

- **750 hours/month** of t2.micro or t3.micro instances
- **15 GB** of data transfer out
- **30 GB** of EBS storage

### Estimate Costs

For this lab with 2 instances:

- **2 x t3.micro instances**: $0.0104/hour × 2 = $0.021/hour
- **24 hours active**: $0.50/day
- **3 days (lab requirement)**: ~$1.50 total

**Within Free Tier: $0**

### Cost Saving Tips

1. **Stop instances when not in use:**
   ```bash
   aws ec2 stop-instances --instance-ids i-xxxxx
   ```

2. **Terminate when done:**
   ```bash
   aws ec2 terminate-instances --instance-ids i-xxxxx
   ```

3. **Monitor usage:**
   - AWS Console → Billing Dashboard
   - Set up billing alerts

4. **Use AWS Free Tier:**
   - Stay within 750 hours/month
   - Use only t2.micro or t3.micro

### Important Cost Warnings

⚠️ **NEVER commit AWS keys to GitHub**
- Automated scanners will find them
- Your account will be compromised
- Minimum charge: $3000+

⚠️ **Always terminate instances when done**
```bash
# List running instances
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"

# Terminate all lab instances
aws ec2 terminate-instances --instance-ids i-xxxxx i-yyyyy
```

## Workflow Summary

### Complete Deployment and Benchmark Workflow

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your AWS credentials

# 2. Generate Lab3 database locally
cd Lab3
python crawler.py
cd ..

# 3. Deploy both labs to EC2
python aws_ec2_installer.py --lab both --action all

# 4. Note the public IPs from output
# Lab2 IP: 3.83.233.24
# Lab3 IP: 98.93.66.138

# 5. SSH and start applications
ssh -i ece326-keypair.pem ubuntu@3.83.233.24
nohup python3 frontend.py > frontend.log 2>&1 &
exit

ssh -i ece326-keypair.pem ubuntu@98.93.66.138
nohup python3 frontend.py > frontend.log 2>&1 &
exit

# 6. Run benchmarks
python benchmark_comparison.py \
    --lab2-url http://3.83.233.24:8080 \
    --lab3-url http://98.93.66.138:8080

# 7. View results
cat BENCHMARK_RESULTS.md

# 8. When done, terminate instances
aws ec2 terminate-instances --instance-ids i-xxxxx i-yyyyy
```

## File Structure

```
ECE326-Labs/
├── aws_ec2_installer.py        # EC2 deployment automation
├── benchmark_comparison.py     # Benchmark testing tool
├── AWS_DEPLOYMENT_GUIDE.md     # This guide
├── BENCHMARK_COMPARISON.md     # Test structure analysis
├── BENCHMARK_RESULTS.md        # Generated benchmark report
├── BENCHMARK_RESULTS.json      # Generated benchmark data
├── .env                        # AWS/Google credentials (DO NOT COMMIT)
├── ece326-keypair.pem          # EC2 SSH key (DO NOT COMMIT)
├── Lab2/
│   ├── frontend.py
│   ├── backend.py
│   ├── requirements.txt
│   └── ...
├── Lab3/
│   ├── frontend.py
│   ├── crawler.py
│   ├── storage.py
│   ├── pagerank.py
│   ├── search_engine.db        # Generated by crawler
│   └── ...
└── README.md
```

## Security Best Practices

1. **Never commit sensitive files:**
   - `.env`
   - `*.pem`
   - `client_secret.json`

2. **Use .gitignore:**
   ```
   .env
   *.pem
   client_secret.json
   ```

3. **Rotate credentials regularly:**
   - AWS access keys
   - Google OAuth credentials

4. **Restrict security groups:**
   - Only open necessary ports
   - Consider restricting to specific IPs

5. **Monitor AWS usage:**
   - Set up billing alerts
   - Review running instances daily

## Additional Resources

- **AWS EC2 Documentation:** https://docs.aws.amazon.com/ec2/
- **ApacheBench Guide:** https://httpd.apache.org/docs/current/programs/ab.html
- **Boto3 Documentation:** https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- **Lab Specifications:**
  - Lab2: `Lab2/ECE326-Lab2.pdf`
  - Lab3: `Lab3/ECE326-Lab3.pdf`

## Support

For issues or questions:

1. Check this guide's Troubleshooting section
2. Review lab PDF specifications
3. Check AWS EC2 documentation
4. Contact course instructors

---

**Last Updated:** 2025-11-08
**Course:** ECE326 - Programming Languages
**University of Toronto**
