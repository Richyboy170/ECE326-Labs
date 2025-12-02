#!/usr/bin/env python3
"""
AWS One-Click Deployment Script for ECE326 Lab 4
Deploys the search engine to AWS EC2 with a single command
"""

import boto3
import os
import sys
import time
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Configuration
CREDENTIALS_FILE = 'aws_credentials.env'
REQUIRED_FILES = [
    'frontend.py',
    'storage.py',
    'ranking.py',
    'cache.py',
    'analytics.py',
    'snippets.py',
    'search_engine.db',
    'analytics.db',
    'requirements.txt',
]
REQUIRED_DIRS = ['static']
OPTIONAL_FILES = ['backend.py', '.env', 'client_secret.json']
EC2_USER = 'ubuntu'
APP_PORT = 8080


def print_header(message):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {message}")
    print(f"{'=' * 70}\n")


def print_step(step_num, message):
    """Print formatted step message"""
    print(f"\n[Step {step_num}] {message}")
    print("-" * 70)


def load_aws_credentials():
    """Load AWS credentials from environment file"""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Error: {CREDENTIALS_FILE} not found!")
        print(f"\nPlease create {CREDENTIALS_FILE} from the template:")
        print(f"  1. Copy aws_credentials.env.template to {CREDENTIALS_FILE}")
        print(f"  2. Fill in your AWS credentials")
        print(f"  3. Run this script again")
        sys.exit(1)
    
    load_dotenv(CREDENTIALS_FILE)
    
    # Validate required credentials
    required_vars = ['AWS_ACCESS_KEY', 'AWS_SECRET_KEY', 'AWS_REGION', 
                     'KEY_NAME', 'SECURITY_GROUP_NAME']
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Error: Missing required variables in {CREDENTIALS_FILE}:")
        for var in missing:
            print(f"  - {var}")
        sys.exit(1)
    
    return {
        'access_key': os.getenv('AWS_ACCESS_KEY'),
        'secret_key': os.getenv('AWS_SECRET_KEY'),
        'region': os.getenv('AWS_REGION'),
        'key_name': os.getenv('KEY_NAME'),
        'security_group_name': os.getenv('SECURITY_GROUP_NAME'),
        'instance_type': os.getenv('INSTANCE_TYPE', 't3.micro'),
        'ami_id': os.getenv('UBUNTU_AMI', 'ami-0c7217cdde317cfec'),
    }


def check_required_files():
    """Check that all required files exist"""
    print("Checking required files...")
    missing_files = []
    
    for file in REQUIRED_FILES:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"  ✓ {file}")
    
    for dir_name in REQUIRED_DIRS:
        if not os.path.isdir(dir_name):
            missing_files.append(f"{dir_name}/ (directory)")
        else:
            print(f"  ✓ {dir_name}/")
    
    if missing_files:
        print(f"\n❌ Error: Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        sys.exit(1)
    
    print("✓ All required files present")


def create_ec2_clients(config):
    """Create EC2 client and resource"""
    try:
        client = boto3.client(
            'ec2',
            region_name=config['region'],
            aws_access_key_id=config['access_key'],
            aws_secret_access_key=config['secret_key']
        )
        
        resource = boto3.resource(
            'ec2',
            region_name=config['region'],
            aws_access_key_id=config['access_key'],
            aws_secret_access_key=config['secret_key']
        )
        
        # Test connection
        client.describe_regions()
        print("✓ AWS connection successful")
        
        return client, resource
    except Exception as e:
        print(f"❌ Error connecting to AWS: {e}")
        sys.exit(1)


def create_key_pair(client, key_name):
    """Create or reuse a key pair"""
    pem_file = f"{key_name}.pem"
    abs_pem_file = os.path.abspath(pem_file)
    
    # Check if key exists on AWS
    key_exists_on_aws = False
    try:
        client.describe_key_pairs(KeyNames=[key_name])
        key_exists_on_aws = True
    except:
        pass
        
    # Check if key file exists locally
    key_exists_locally = os.path.exists(abs_pem_file)
    
    # REUSE LOGIC
    if key_exists_on_aws and key_exists_locally:
        print(f"✓ Reusing existing key pair: {key_name}")
        print(f"  Key file: {abs_pem_file}")
        
        # Ensure permissions are correct even when reusing
        if os.name == 'nt':
            set_key_permissions_windows(abs_pem_file)
        else:
            try:
                os.chmod(abs_pem_file, 0o400)
            except:
                pass
                
        return abs_pem_file
        
    # RECREATE LOGIC
    print(f"Creating new key pair: {key_name}...")
    
    # If it exists on AWS but we don't have the file, we MUST delete it from AWS
    if key_exists_on_aws and not key_exists_locally:
        print(f"  ⚠️  Key '{key_name}' exists on AWS but local file is missing.")
        print(f"  Deleting old key from AWS to create a new one...")
        try:
            client.delete_key_pair(KeyName=key_name)
        except Exception as e:
            print(f"  ❌ Error deleting old key: {e}")
            sys.exit(1)
            
    # If we have the file but it's not on AWS (rare), we'll just overwrite the file
    
    try:
        # Create new key
        key_pair = client.create_key_pair(KeyName=key_name)
        
        # Save private key to file
        with open(abs_pem_file, 'w') as f:
            f.write(key_pair['KeyMaterial'])
            
        # Set permissions (Unix-like systems)
        try:
            os.chmod(abs_pem_file, 0o400)
        except:
            pass
            
        # Set permissions (Windows)
        if os.name == 'nt':
            set_key_permissions_windows(abs_pem_file)
        
        print(f"✓ Created new key pair: {abs_pem_file}")
        return abs_pem_file
        
    except Exception as e:
        print(f"❌ Error creating key pair: {e}")
        sys.exit(1)


def set_key_permissions_windows(key_file):
    """Set strict permissions on key file for Windows"""
    try:
        abs_path = os.path.abspath(key_file)
        # Remove inheritance
        subprocess.run(['icacls', abs_path, '/inheritance:r'], capture_output=True)
        # Grant full access to current user only
        username = os.getlogin()
        subprocess.run(['icacls', abs_path, '/grant:r', f'{username}:F'], capture_output=True)
        # print(f"✓ Set strict permissions on {key_file}")
    except Exception as e:
        print(f"⚠️  Could not set Windows permissions: {e}")


def setup_security_group(client, sg_name):
    """Create and configure security group"""
    try:
        # Try to create security group
        response = client.create_security_group(
            GroupName=sg_name,
            Description='Security group for ECE326 search engine'
        )
        sg_id = response['GroupId']
        print(f"✓ Security group created: {sg_id}")
        
    except client.exceptions.ClientError as e:
        if 'InvalidGroup.Duplicate' in str(e):
            # Get existing security group
            response = client.describe_security_groups(
                Filters=[{'Name': 'group-name', 'Values': [sg_name]}]
            )
            sg_id = response['SecurityGroups'][0]['GroupId']
            print(f"✓ Using existing security group: {sg_id}")
        else:
            raise
    
    # ALWAYS ensure rules are configured (in case they were removed)
    # First, get current rules
    try:
        sg_info = client.describe_security_groups(GroupIds=[sg_id])
        existing_rules = sg_info['SecurityGroups'][0]['IpPermissions']
        
        # Check if SSH rule exists
        ssh_exists = any(
            rule.get('IpProtocol') == 'tcp' and 
            rule.get('FromPort') == 22 and 
            rule.get('ToPort') == 22 and
            any(ip_range.get('CidrIp') == '0.0.0.0/0' for ip_range in rule.get('IpRanges', []))
            for rule in existing_rules
        )
        
        if not ssh_exists:
            print(f"⚠️  SSH rule missing, adding it now...")
        
    except Exception as e:
        print(f"⚠️  Could not verify existing rules: {e}")
        ssh_exists = False
    
    # Configure security rules (will skip duplicates automatically)
    rules_to_add = [
        # SSH - CRITICAL for deployment
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH from anywhere'}]
        },
        # HTTP
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP'}]
        },
        # Port 8080 (Application)
        {
            'IpProtocol': 'tcp',
            'FromPort': 8080,
            'ToPort': 8080,
            'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Application port'}]
        },
    ]
    
    for rule in rules_to_add:
        try:
            client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[rule]
            )
            port = rule['FromPort']
            print(f"✓ Added rule for port {port}")
        except client.exceptions.ClientError as e:
            if 'InvalidPermission.Duplicate' in str(e):
                pass  # Rule already exists, that's fine
            else:
                print(f"⚠️  Warning adding rule for port {rule['FromPort']}: {e}")
    
    # Verify SSH is now accessible
    print(f"✓ Security group configured with SSH (22), HTTP (80), and App (8080)")
    
    return sg_id


def launch_instance(resource, config, sg_id):
    """Launch EC2 instance"""
    print(f"Launching EC2 instance...")
    print(f"  Instance type: {config['instance_type']}")
    print(f"  AMI: {config['ami_id']}")
    
    instances = resource.create_instances(
        ImageId=config['ami_id'],
        MinCount=1,
        MaxCount=1,
        InstanceType=config['instance_type'],
        KeyName=config['key_name'],
        SecurityGroupIds=[sg_id]
    )
    
    instance = instances[0]
    print(f"✓ Instance created: {instance.id}")
    print(f"⏳ Waiting for instance to start (this may take 1-2 minutes)...")
    
    instance.wait_until_running()
    instance.reload()
    
    print(f"✓ Instance is running!")
    print(f"  Instance ID: {instance.id}")
    print(f"  Public IP: {instance.public_ip_address}")
    
    return instance


def wait_for_ssh(ip_address, key_file):
    """Wait for SSH to become available - simplified for Windows compatibility"""
    print(f"⏳ Waiting for instance to fully initialize...")
    print(f"   EC2 instances typically take 2-3 minutes after 'running' status")
    print(f"   Waiting 30 seconds to ensure SSH is ready...")
    
    # Simple time-based wait since Windows subprocess SSH detection is unreliable
    # But actual SSH commands work fine once instance is ready
    for i in range(6):
        time.sleep(5)
        print(f"   {(i+1)*5}/30 seconds elapsed...")
    
    print(f"✓ Initial wait complete, proceeding with deployment")
    print(f"   (If SSH fails, instance may need a few more seconds)")
    return True  # Always return True, let actual SSH commands handle failures


def copy_files_to_instance(ip_address, key_file):
    """Copy all required files to EC2 instance"""
    print(f"Copying files to EC2 instance...")
    
    # Helper function to copy with retries
    def scp_with_retry(files, is_dir=False, max_retries=3):
        for attempt in range(max_retries):
            try:
                for file in files if isinstance(files, list) else [files]:
                    if not os.path.exists(file):
                        continue
                    
                    cmd = ['scp', '-i', key_file, '-o', 'StrictHostKeyChecking=no',
                           '-o', 'UserKnownHostsFile=/dev/null',
                           '-o', 'ConnectTimeout=30']
                    
                    if is_dir:
                        cmd.append('-r')
                    
                    cmd.extend([file, f'{EC2_USER}@{ip_address}:~/'])
                    
                    result = subprocess.run(cmd, capture_output=True, encoding='utf-8', 
                                          errors='replace', timeout=60)
                    
                    if result.returncode == 0:
                        print(f"  ✓ {file}")
                    else:
                        if attempt == max_retries - 1:  # Last attempt
                            if file in REQUIRED_FILES or file in REQUIRED_DIRS:
                                print(f"  ❌ Failed to copy {file}")
                                return False
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  Retry {attempt + 1}/{max_retries} for files...")
                    time.sleep(10)
                else:
                    return False
        return True
    
    # Copy individual files
    if not scp_with_retry(REQUIRED_FILES + OPTIONAL_FILES):
        return False
    
    # Copy directories
    if not scp_with_retry(REQUIRED_DIRS, is_dir=True):
        return False
    
    # Copy sessions directory if it exists
    if os.path.isdir('sessions'):
        scp_with_retry(['sessions'], is_dir=True)
    
    print("✓ All files copied successfully")
    return True


def install_dependencies(ip_address, key_file):
    """Install dependencies on EC2 instance"""
    print(f"Installing dependencies on EC2 instance...")
    
    install_script = """
    sudo apt update
    sudo apt install -y python3-pip
    pip3 install -r requirements.txt
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            cmd = ['ssh', '-i', key_file, '-o', 'StrictHostKeyChecking=no',
                   '-o', 'UserKnownHostsFile=/dev/null',
                   '-o', 'ConnectTimeout=30',
                   '-o', 'IdentitiesOnly=yes']
            
            # Add verbose flag on last attempt to debug
            if attempt == max_retries - 1:
                cmd.append('-v')
                
            cmd.extend([f'{EC2_USER}@{ip_address}', install_script])
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            
            if result.returncode == 0:
                print("✓ Dependencies installed successfully")
                return True
            else:
                # Only print error on last attempt or if it's not a connection error
                if attempt == max_retries - 1:
                    print(f"❌ Failed to install dependencies")
                    print(f"Error: {result.stderr}")
                    # Also print stdout in case verbose info is there
                    if result.stdout:
                        print(f"Output: {result.stdout}")
                else:
                    print(f"  ⚠️  Attempt {attempt + 1}/{max_retries} failed. Retrying in 10s...")
                    time.sleep(10)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"❌ Exception during dependency installation: {e}")
            else:
                print(f"  ⚠️  Attempt {attempt + 1}/{max_retries} error: {e}. Retrying in 10s...")
                time.sleep(10)
                
    return False


def start_application(ip_address, key_file):
    """Start the search engine application"""
    print(f"Starting search engine application...")
    
    startup_script = """
    # Kill any existing frontend
    pkill -f frontend.py || true
    
    # Start frontend in background
    nohup python3 frontend.py > frontend.log 2>&1 &
    
    # Wait for server to start
    sleep 5
    
    # Check if server is running
    if ps aux | grep -v grep | grep frontend.py > /dev/null; then
        echo "SUCCESS"
    else
        echo "FAILED"
        echo "=== Frontend Log ==="
        cat frontend.log || echo "No log file found"
        exit 1
    fi
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            cmd = ['ssh', '-i', key_file, '-o', 'StrictHostKeyChecking=no',
                   '-o', 'UserKnownHostsFile=/dev/null',
                   '-o', 'ConnectTimeout=30',
                   '-o', 'IdentitiesOnly=yes']
            
            # Add verbose flag on last attempt to debug
            if attempt == max_retries - 1:
                cmd.append('-v')
                
            cmd.extend([f'{EC2_USER}@{ip_address}', startup_script])
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            
            if result.returncode == 0 and 'SUCCESS' in result.stdout:
                print("✓ Application started successfully")
                return True
            else:
                if attempt == max_retries - 1:
                    print(f"❌ Failed to start application")
                    print(f"Output: {result.stdout}")
                    print(f"Error: {result.stderr}")
                else:
                    print(f"  ⚠️  Attempt {attempt + 1}/{max_retries} failed. Retrying in 10s...")
                    time.sleep(10)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"❌ Exception starting application: {e}")
            else:
                print(f"  ⚠️  Attempt {attempt + 1}/{max_retries} error: {e}. Retrying in 10s...")
                time.sleep(10)
                
    return False


def main():
    """Main deployment function"""
    print_header("ECE326 Lab 4 - One-Click AWS Deployment")
    
    # Step 1: Load credentials
    print_step(1, "Loading AWS Credentials")
    config = load_aws_credentials()
    
    # Step 2: Check files
    print_step(2, "Checking Required Files")
    check_required_files()
    
    # Step 3: Connect to AWS
    print_step(3, "Connecting to AWS")
    ec2_client, ec2_resource = create_ec2_clients(config)
    
    # Step 4: Setup key pair (create or reuse)
    print_step(4, "Setting Up Key Pair")
    # Use the configured key name directly (no timestamp)
    unique_key_name = config['key_name']
    key_file = create_key_pair(ec2_client, unique_key_name)
    
    # Step 5: Setup security group
    print_step(5, "Setting Up Security Group")
    sg_id = setup_security_group(ec2_client, config['security_group_name'])
    
    # Step 6: Launch instance
    print_step(6, "Launching EC2 Instance")
    instance = launch_instance(ec2_resource, config, sg_id)
    ip_address = instance.public_ip_address
    
    # Step 7: Wait for SSH
    print_step(7, "Waiting for SSH Access")
    wait_for_ssh(ip_address, key_file)  # Always proceeds after wait
    
    # Step 8: Copy files
    print_step(8, "Copying Files to Instance")
    if not copy_files_to_instance(ip_address, key_file):
        print("❌ Deployment failed: File copy error")
        sys.exit(1)
    
    # Step 9: Install dependencies
    print_step(9, "Installing Dependencies")
    if not install_dependencies(ip_address, key_file):
        print("\n❌ Automatic dependency installation failed.")
        print("⚠️  BUT the instance is running and files are copied!")
        print("\n🛠️  MANUAL RECOVERY INSTRUCTIONS:")
        print("   You can finish the deployment manually by running these commands:")
        print(f"\n   1. Connect to the instance:")
        # Use basename for easier copy-pasting (avoids path space issues)
        key_filename = os.path.basename(key_file)
        print(f"      ssh -i {key_filename} {EC2_USER}@{ip_address}")
        print(f"\n   2. Run these commands on the instance:")
        print("      sudo apt update")
        print("      sudo apt install -y python3-pip")
        print("      pip3 install -r requirements.txt")
        print("      nohup python3 frontend.py > frontend.log 2>&1 &")
        print(f"\n   3. Test your search engine:")
        print(f"      http://{ip_address}:{APP_PORT}")
        print(f"\n   (You can ignore the script failure if you complete these steps manually)")
        sys.exit(1)
    
    # Step 10: Start application
    print_step(10, "Starting Search Engine Application")
    if not start_application(ip_address, key_file):
        print("\n❌ Automatic application startup failed.")
        print("⚠️  BUT the instance is running and dependencies are installed!")
        print("\n🛠️  MANUAL RECOVERY INSTRUCTIONS:")
        print("   You can finish the deployment manually by running these commands:")
        print(f"\n   1. Connect to the instance:")
        key_filename = os.path.basename(key_file)
        print(f"      ssh -i {key_filename} {EC2_USER}@{ip_address}")
        print(f"\n   2. Start the application:")
        print("      pkill -f frontend.py")
        print("      nohup python3 frontend.py > frontend.log 2>&1 &")
        print(f"\n   3. Test your search engine:")
        print(f"      http://{ip_address}:{APP_PORT}")
        sys.exit(1)
    
    # Success!
    print_header("DEPLOYMENT SUCCESSFUL!")
    print(f"Instance ID:  {instance.id}")
    print(f"Public IP:    {ip_address}")
    if instance.public_dns_name:
        print(f"Public DNS:   {instance.public_dns_name}")
    print(f"Key Pair:     {unique_key_name}")
    print(f"Key File:     {key_file}")
    print(f"\n🌐 Search Engine URL:")
    print(f"   http://{ip_address}:{APP_PORT}")
    print(f"\n📊 Analytics Dashboard:")
    print(f"   http://{ip_address}:{APP_PORT}/analytics")
    print(f"\n🔑 SSH Access:")
    key_filename = os.path.basename(key_file)
    print(f"   ssh -i {key_filename} {EC2_USER}@{ip_address}")
    print(f"\n📝 View Logs:")
    print(f"   ssh -i {key_filename} {EC2_USER}@{ip_address} 'tail -f frontend.log'")
    print(f"\n🛑 To terminate this instance:")
    print(f"   python aws_terminate.py {instance.id}")
    print(f"\n⚠️  IMPORTANT: Save the key file '{key_filename}' to access this instance!")
    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Deployment failed with error:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
