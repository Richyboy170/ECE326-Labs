---
description: How to deploy the search engine to AWS EC2 using aws_deploy.py
---

# How to Use aws_deploy.py

This workflow explains how to deploy your ECE326 Lab 4 search engine to AWS EC2 using the one-click deployment script.

## Prerequisites

Before running `aws_deploy.py`, ensure you have:

1. **AWS Account** with EC2 access
2. **AWS IAM Credentials** (Access Key and Secret Key)
3. **Python 3** installed with `boto3` and `python-dotenv` packages
4. **SSH client** available in your PATH (for file transfer and remote access)
5. **All required project files** in your Lab4 directory

## Required Files

The deployment script checks for these files before deployment:

**Required:**
- `frontend.py` - Main web application
- `storage.py` - Database storage module
- `ranking.py` - Search ranking logic
- `cache.py` - Caching module
- `analytics.py` - Analytics tracking
- `snippets.py` - Search result snippet generation
- `search_engine.db` - Main database
- `analytics.db` - Analytics database
- `requirements.txt` - Python dependencies
- `static/` directory - Static web assets

**Optional (but recommended):**
- `backend.py` - Backend services
- `.env` - Environment variables
- `client_secret.json` - OAuth credentials (if using Google auth)

## Step 1: Configure AWS Credentials

Create your credentials file from the template:

```bash
# Copy the template
cp aws_credentials.env.template aws_credentials.env
```

Edit `aws_credentials.env` and fill in your AWS credentials:

```bash
# AWS Access Credentials (Required)
AWS_ACCESS_KEY=your_actual_access_key_here
AWS_SECRET_KEY=your_actual_secret_key_here

# AWS Region (Required)
AWS_REGION=us-east-1

# EC2 Key Pair Name (Required)
KEY_NAME=ece326-keypair

# Security Group Name (Required)
SECURITY_GROUP_NAME=ece326-search-engine-sg

# EC2 Instance Type (Optional - defaults to t3.micro)
INSTANCE_TYPE=t3.micro

# Ubuntu AMI ID (Optional - defaults to Ubuntu 22.04 for us-east-1)
UBUNTU_AMI=ami-0c7217cdde317cfec
```

> **SECURITY NOTE**: Add `aws_credentials.env` to your `.gitignore` to prevent exposing your credentials!

## Step 2: Run the Deployment Script

// turbo
```bash
python aws_deploy.py
```

The script will automatically:

1. ✅ Load and validate AWS credentials
2. ✅ Check all required files exist
3. ✅ Connect to AWS
4. ✅ Create a fresh SSH key pair (with timestamp to avoid conflicts)
5. ✅ Setup security group with ports 22 (SSH), 80 (HTTP), and 8080 (App)
6. ✅ Launch EC2 instance
7. ✅ Wait for instance to be ready (~2-3 minutes)
8. ✅ Copy all project files to the instance
9. ✅ Install Python dependencies
10. ✅ Start the search engine application

## Step 3: Access Your Deployed Application

After successful deployment, you'll see output like:

```
======================================================================
  DEPLOYMENT SUCCESSFUL!
======================================================================

Instance ID:  i-0123456789abcdef0
Public IP:    54.123.45.67
Key File:     ece326-keypair-20251202-083000.pem

🌐 Search Engine URL:
   http://54.123.45.67:8080

📊 Analytics Dashboard:
   http://54.123.45.67:8080/analytics

🔑 SSH Access:
   ssh -i ece326-keypair-20251202-083000.pem ubuntu@54.123.45.67

📝 View Logs:
   ssh -i ece326-keypair-20251202-083000.pem ubuntu@54.123.45.67 'tail -f frontend.log'

🛑 To terminate this instance:
   python aws_terminate.py i-0123456789abcdef0
```

## Step 4: Test Your Deployment

Visit the search engine URL in your browser:
- **Main Search**: `http://<PUBLIC_IP>:8080`
- **Analytics Dashboard**: `http://<PUBLIC_IP>:8080/analytics`

## Step 5: Monitor and Troubleshoot (if needed)

### View Application Logs

```bash
ssh -i <KEY_FILE>.pem ubuntu@<PUBLIC_IP> 'tail -f frontend.log'
```

### Check if Application is Running

```bash
ssh -i <KEY_FILE>.pem ubuntu@<PUBLIC_IP> 'ps aux | grep frontend.py'
```

### Restart Application Manually

```bash
ssh -i <KEY_FILE>.pem ubuntu@<PUBLIC_IP>
# On the EC2 instance:
pkill -f frontend.py
nohup python3 frontend.py > frontend.log 2>&1 &
exit
```

## Step 6: Terminate Instance When Done

To avoid AWS charges, terminate your instance when finished:

// turbo
```bash
python aws_terminate.py <INSTANCE_ID>
```

Example:
```bash
python aws_terminate.py i-0123456789abcdef0
```

## Common Issues and Solutions

### Issue: "Missing required files"
**Solution**: Ensure all required files listed above are in your Lab4 directory.

### Issue: "AWS credentials error"
**Solution**: 
- Verify your AWS Access Key and Secret Key are correct
- Check that your IAM user has EC2 permissions
- Ensure there are no extra spaces in `aws_credentials.env`

### Issue: "Instance launches but application doesn't start"
**Solution**:
1. SSH into the instance
2. Check `frontend.log` for errors
3. Verify `requirements.txt` dependencies installed correctly
4. Manually restart the application

### Issue: "Can't connect to search engine URL"
**Solution**:
- Wait an additional 1-2 minutes after deployment completes
- Verify security group has port 8080 open
- Check that application is running: `ps aux | grep frontend.py`

### Issue: "SSH connection refused"
**Solution**:
- EC2 instances take 2-3 minutes to fully initialize
- Wait a bit longer and try again
- Verify key file permissions (should be 400 on Unix systems)

## Tips for Grading/Demo

1. **Save the key file**: Keep the `.pem` file that's generated - you'll need it for SSH access
2. **Note the URLs**: Copy the search engine URL and analytics dashboard URL for easy access
3. **Test before demo**: Run a few searches to verify everything works
4. **Keep instance ID**: You'll need it to terminate the instance later

## Advanced: Using Different Regions or Instance Types

Edit `aws_credentials.env` before deployment:

```bash
# For example, use us-west-2 region
AWS_REGION=us-west-2

# Use a larger instance (not free tier)
INSTANCE_TYPE=t3.small

# You'll need the appropriate AMI for that region
# Find AMIs at: https://cloud-images.ubuntu.com/locator/ec2/
UBUNTU_AMI=ami-xxxxxxxxxx
```
