# ECE326 Lab 4 - AWS Deployment Scripts

This document provides comprehensive instructions for using the one-click AWS deployment and termination scripts.

## Overview

The deployment scripts automate the entire process of launching your search engine on AWS EC2, from creating the instance to having a fully functional, publicly accessible application.

### What's Included

- **aws_deploy.py** - One-click deployment script that launches EC2 and deploys your application
- **aws_terminate.py** - Script to cleanly shut down running EC2 instances
- **aws_credentials.env.template** - Template for AWS credentials configuration

## Prerequisites

### 1. AWS Account Setup

- Active AWS account with EC2 access
- AWS Access Key ID and Secret Access Key
  - Get these from: AWS Console → IAM → Users → Security Credentials → Create Access Key

### 2. Local Requirements

- Python 3.7 or later
- Required Python packages:
  ```bash
  pip install boto3 python-dotenv
  ```
- SSH client installed (for file copying)
  - Linux/Mac: Built-in
  - Windows: OpenSSH (usually pre-installed on Windows 10+)

### 3. Application Files

Before deploying, ensure you have:
- ✅ `search_engine.db` (run `python crawler.py` if missing)
- ✅ All Python files (`frontend.py`, `storage.py`, etc.)
- ✅ `static/` directory with templates
- ✅ `requirements.txt`

## Setup Instructions

### Step 1: Configure AWS Credentials

1. Copy the template file:
   ```bash
   cp aws_credentials.env.template aws_credentials.env
   ```

2. Edit `aws_credentials.env` and fill in your credentials:
   ```env
   AWS_ACCESS_KEY=your_actual_access_key
   AWS_SECRET_KEY=your_actual_secret_key
   AWS_REGION=us-east-1
   KEY_NAME=ece326-keypair
   SECURITY_GROUP_NAME=ece326-search-engine-sg
   INSTANCE_TYPE=t3.micro
   UBUNTU_AMI=ami-0c7217cdde317cfec
   ```

3. **IMPORTANT**: Add to `.gitignore` to prevent credential exposure:
   ```bash
   echo "aws_credentials.env" >> .gitignore
   ```

### Step 2: Verify Required Files

Check that you have all required files:
```bash
# List required files
ls -la frontend.py storage.py ranking.py cache.py analytics.py snippets.py
ls -la search_engine.db analytics.db requirements.txt
ls -la static/
```

If `search_engine.db` is missing, create it:
```bash
python crawler.py
```

## Deployment Usage

### Deploy to AWS

Run the deployment script:
```bash
python aws_deploy.py
```

### What the Script Does

The script performs the following steps automatically:

1. ✅ **Load AWS Credentials** - Validates credentials from `aws_credentials.env`
2. ✅ **Check Files** - Ensures all required files are present
3. ✅ **Connect to AWS** - Establishes connection to AWS EC2
4. ✅ **Setup Key Pair** - Creates SSH key pair (or uses existing)
5. ✅ **Setup Security Group** - Configures firewall rules (ports 22, 80, 8080)
6. ✅ **Launch Instance** - Starts new EC2 instance
7. ✅ **Wait for SSH** - Waits until SSH becomes available (may take 1-2 minutes)
8. ✅ **Copy Files** - Transfers all application files to instance
9. ✅ **Install Dependencies** - Installs Python packages on instance
10. ✅ **Start Application** - Launches the search engine

### Successful Deployment Output

```
======================================================================
  DEPLOYMENT SUCCESSFUL!
======================================================================

Instance ID:  i-0ee9470aa16dc1a09
Public IP:    204.236.209.159

🌐 Search Engine URL:
   http://204.236.209.159:8080

📊 Analytics Dashboard:
   http://204.236.209.159:8080/analytics

🔑 SSH Access:
   ssh -i ece326-keypair.pem ubuntu@204.236.209.159

📝 View Logs:
   ssh -i ece326-keypair.pem ubuntu@204.236.209.159 'tail -f frontend.log'

🛑 To terminate this instance:
   python aws_terminate.py i-0ee9470aa16dc1a09

======================================================================
```

### Accessing Your Search Engine

After successful deployment:

1. **Open your browser** to the URL shown (e.g., `http://204.236.209.159:8080`)
2. **Test the search** - Enter keywords and verify results appear
3. **Check analytics** - Visit `/analytics` to see tracking dashboard

## Termination Usage

### Terminate an Instance

To shut down a running instance:
```bash
python aws_terminate.py <instance_id>
```

Example:
```bash
python aws_terminate.py i-0ee9470aa16dc1a09
```

### What the Script Does

1. ✅ Validates instance ID format
2. ✅ Loads AWS credentials
3. ✅ Connects to AWS
4. ✅ Retrieves instance information
5. ✅ Displays instance details (IP, state, launch time)
6. ✅ Asks for confirmation
7. ✅ Terminates the instance
8. ✅ Reports success/failure

### Termination Output

```
======================================================================
  TERMINATION SUCCESSFUL!
======================================================================

Instance ID:      i-0ee9470aa16dc1a09
Previous State:   running
Current State:    terminating

The instance is now terminating and will be fully terminated shortly.

======================================================================
```

## Troubleshooting

### Common Issues

#### 1. Missing Credentials File

**Error:**
```
❌ Error: aws_credentials.env not found!
```

**Solution:**
```bash
cp aws_credentials.env.template aws_credentials.env
# Edit the file and add your AWS credentials
```

#### 2. Missing Required Files

**Error:**
```
❌ Error: Missing required files:
  - search_engine.db
```

**Solution:**
```bash
python crawler.py  # Generate the database
```

#### 3. SSH Connection Timeout

**Error:**
```
❌ SSH did not become available after 30 attempts
```

**Solution:**
- Wait a few more minutes and try SSH manually:
  ```bash
  ssh -i ece326-keypair.pem ubuntu@<PUBLIC_IP>
  ```
- Check AWS Console to verify instance is running
- Ensure security group allows SSH (port 22)

#### 4. Application Not Starting

**Error:**
```
❌ Failed to start application
```

**Solution:**
1. SSH into the instance:
   ```bash
   ssh -i ece326-keypair.pem ubuntu@<PUBLIC_IP>
   ```

2. Check logs:
   ```bash
   cat frontend.log
   ```

3. Try starting manually:
   ```bash
   python3 frontend.py
   ```

#### 5. Invalid Instance ID

**Error:**
```
❌ Error: Instance i-0ee9470aa16dc1a09 not found
```

**Solution:**
- Verify the instance ID is correct
- Check you're using the correct AWS region in `aws_credentials.env`
- Verify instance exists in AWS Console

### Checking Instance Status

#### Via AWS Console
1. Go to: https://console.aws.amazon.com/ec2/
2. Click "Instances" in sidebar
3. Find your instance by ID or IP

#### Via Script
After deployment, you can SSH to check status:
```bash
# SSH into instance
ssh -i ece326-keypair.pem ubuntu@<PUBLIC_IP>

# Check if frontend is running
ps aux | grep frontend.py

# Check logs
tail -f frontend.log

# Check port 8080 is listening
sudo netstat -tlnp | grep 8080
```

### Restarting the Application

If the application crashes:
```bash
# SSH into instance
ssh -i ece326-keypair.pem ubuntu@<PUBLIC_IP>

# Kill existing process
pkill -f frontend.py

# Restart application
nohup python3 frontend.py > frontend.log 2>&1 &

# Verify it's running
ps aux | grep frontend.py
```

## Security Best Practices

### Credentials Security

1. **Never commit credentials to Git**
   ```bash
   # Ensure .gitignore includes:
   aws_credentials.env
   *.pem
   ```

2. **Restrict key file permissions** (Unix/Mac)
   ```bash
   chmod 400 ece326-keypair.pem
   ```

3. **Use IAM roles with minimal permissions**
   - Only grant EC2 permissions needed
   - Avoid using root AWS credentials

### Instance Security

1. **Restrict security group access** (if needed)
   - Edit security group in AWS Console
   - Limit SSH (port 22) to your IP only
   - Keep ports 80, 8080 open for public access

2. **Terminate instances when not in use**
   - AWS charges for running instances
   - Always terminate after demonstrations/testing

3. **Update dependencies regularly**
   ```bash
   ssh -i ece326-keypair.pem ubuntu@<PUBLIC_IP>
   sudo apt update && sudo apt upgrade -y
   ```

## Cost Management

### Avoiding Unexpected Charges

1. **Terminate instances after use**
   ```bash
   python aws_terminate.py <instance_id>
   ```

2. **Check running instances**
   - AWS Console → EC2 → Instances
   - Look for "running" instances

3. **Set up billing alerts**
   - AWS Console → Billing → Billing Preferences
   - Enable "Receive Billing Alerts"

### Free Tier Limits

- t2.micro or t3.micro: 750 hours/month (free tier)
- After free tier: ~$0.01-0.02 per hour

## Advanced Usage

### Using Different Regions

Edit `aws_credentials.env`:
```env
AWS_REGION=us-west-2  # Change to desired region
```

**Note:** You'll need to find the correct Ubuntu AMI for that region:
- Visit: https://cloud-images.ubuntu.com/locator/ec2/
- Search for: "22.04 LTS"
- Copy AMI ID for your region

### Customizing Instance Type

For better performance, use a larger instance:
```env
INSTANCE_TYPE=t3.small  # More CPU and memory
```

**Cost consideration:** Larger instances cost more!

### Multiple Deployments

To run multiple instances simultaneously:
1. Edit `aws_credentials.env` and change `KEY_NAME` and `SECURITY_GROUP_NAME`
2. Run `python aws_deploy.py` again
3. Each deployment will use different resources

## File Reference

### Required Files for Deployment

These files must exist in your Lab4 directory:

- `frontend.py` - Web interface
- `storage.py` - Database interface
- `ranking.py` - Advanced ranking algorithm
- `cache.py` - Query caching
- `analytics.py` - Analytics tracking
- `snippets.py` - Snippet generation
- `search_engine.db` - Search database (generated by crawler)
- `analytics.db` - Analytics database
- `requirements.txt` - Python dependencies
- `static/` - Directory with HTML templates and CSS

### Optional Files

These files will be copied if they exist:

- `backend.py` - AWS automation script (not needed on instance)
- `.env` - Environment variables
- `client_secret.json` - Google OAuth credentials (if using Google Login)

## Support and Resources

### AWS Documentation
- EC2 Getting Started: https://docs.aws.amazon.com/ec2/
- boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

### Course Resources
- Lab 4 PDF: `ECE326-Lab4.pdf`
- Application README: `README_for_running_code.md`
- Features Documentation: `README_LAB4_FEATURES.md`

### Getting Help

If you encounter issues:
1. Check this troubleshooting guide
2. Review error messages carefully
3. Check AWS Console for instance status
4. SSH into instance to debug manually
5. Review application logs (`frontend.log`)

## Quick Reference

### Common Commands

```bash
# Deploy to AWS
python aws_deploy.py

# Terminate instance
python aws_terminate.py i-0ee9470aa16dc1a09

# SSH into instance
ssh -i ece326-keypair.pem ubuntu@<PUBLIC_IP>

# View logs
ssh -i ece326-keypair.pem ubuntu@<PUBLIC_IP> 'tail -f frontend.log'

# Copy updated file to instance
scp -i ece326-keypair.pem frontend.py ubuntu@<PUBLIC_IP>:~/

# Restart application on instance
ssh -i ece326-keypair.pem ubuntu@<PUBLIC_IP> 'pkill -f frontend.py && nohup python3 frontend.py > frontend.log 2>&1 &'
```

### Typical Workflow

1. **Setup** (one-time)
   ```bash
   cp aws_credentials.env.template aws_credentials.env
   # Edit aws_credentials.env with your credentials
   ```

2. **Deploy**
   ```bash
   python aws_deploy.py
   # Wait for deployment to complete
   # Note the Instance ID and Public IP
   ```

3. **Test**
   - Open browser to `http://<PUBLIC_IP>:8080`
   - Perform searches
   - Check analytics

4. **Terminate**
   ```bash
   python aws_terminate.py <instance_id>
   ```
