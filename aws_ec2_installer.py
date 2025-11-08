#!/usr/bin/env python3
"""
AWS EC2 Installer and Setup Script
ECE326 Labs - Automated deployment for Lab2 and Lab3

This script automates the process of:
1. Setting up AWS EC2 instances for both Lab2 and Lab3
2. Installing all required dependencies
3. Deploying the applications
4. Preparing for benchmark testing

Usage:
    python aws_ec2_installer.py --lab [2|3|both] --action [setup|deploy|all]

Examples:
    # Setup and deploy Lab2
    python aws_ec2_installer.py --lab 2 --action all

    # Setup and deploy both labs
    python aws_ec2_installer.py --lab both --action all

    # Only setup EC2 instances (no deployment)
    python aws_ec2_installer.py --lab both --action setup
"""

import argparse
import os
import sys
import time
import subprocess
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("ERROR: boto3 is required. Install it with: pip install boto3")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv is required. Install it with: pip install python-dotenv")
    sys.exit(1)


class EC2Installer:
    """Handles AWS EC2 instance setup and deployment"""

    def __init__(self, lab_number):
        self.lab = lab_number
        load_dotenv()

        # AWS Configuration
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY')
        self.aws_secret_key = os.getenv('AWS_SECRET_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.key_name = os.getenv('KEY_NAME', 'ece326-keypair')
        self.security_group_name = os.getenv('SECURITY_GROUP_NAME', 'ece326-group5')
        self.instance_type = os.getenv('INSTANCE_TYPE', 't3.micro')
        self.ubuntu_ami = os.getenv('UBUNTU_AMI', 'ami-0c398cb65a93047f2')

        if not self.aws_access_key or not self.aws_secret_key:
            print("ERROR: AWS credentials not found in .env file")
            sys.exit(1)

        # Initialize boto3 client
        self.ec2_client = boto3.client(
            'ec2',
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key
        )

        self.ec2_resource = boto3.resource(
            'ec2',
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key
        )

        self.instance_id = None
        self.public_ip = None

    def create_key_pair(self):
        """Create EC2 key pair if it doesn't exist"""
        print(f"\n{'='*60}")
        print(f"Creating Key Pair: {self.key_name}")
        print(f"{'='*60}")

        try:
            # Check if key pair already exists
            self.ec2_client.describe_key_pairs(KeyNames=[self.key_name])
            print(f"✓ Key pair '{self.key_name}' already exists")
            return
        except ClientError:
            pass

        # Create new key pair
        key_pair = self.ec2_client.create_key_pair(KeyName=self.key_name)

        # Save private key to file
        pem_file = f"{self.key_name}.pem"
        with open(pem_file, 'w') as f:
            f.write(key_pair['KeyMaterial'])

        # Set proper permissions
        os.chmod(pem_file, 0o400)
        print(f"✓ Key pair created and saved to {pem_file}")
        print(f"  IMPORTANT: Keep this file safe!")

    def create_security_group(self):
        """Create and configure security group"""
        print(f"\n{'='*60}")
        print(f"Creating Security Group: {self.security_group_name}")
        print(f"{'='*60}")

        try:
            # Check if security group exists
            response = self.ec2_client.describe_security_groups(
                GroupNames=[self.security_group_name]
            )
            group_id = response['SecurityGroups'][0]['GroupId']
            print(f"✓ Security group '{self.security_group_name}' already exists")
            return group_id
        except ClientError:
            pass

        # Create security group
        response = self.ec2_client.create_security_group(
            GroupName=self.security_group_name,
            Description=f'ECE326 Lab{self.lab} Security Group'
        )
        group_id = response['GroupId']
        print(f"✓ Security group created: {group_id}")

        # Configure security group rules
        ip_permissions = [
            # SSH
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            # HTTP
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            # Custom ports for web apps
            {'IpProtocol': 'tcp', 'FromPort': 8080, 'ToPort': 8081, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            # ICMP (ping)
            {'IpProtocol': 'icmp', 'FromPort': -1, 'ToPort': -1, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        ]

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=ip_permissions
        )
        print("✓ Security group rules configured")
        print("  - SSH (port 22)")
        print("  - HTTP (port 80)")
        print("  - Web Apps (ports 8080-8081)")
        print("  - ICMP (ping)")

        return group_id

    def launch_instance(self):
        """Launch EC2 instance"""
        print(f"\n{'='*60}")
        print(f"Launching EC2 Instance for Lab{self.lab}")
        print(f"{'='*60}")

        # Create security group first
        group_id = self.create_security_group()

        # Launch instance
        instances = self.ec2_resource.create_instances(
            ImageId=self.ubuntu_ami,
            InstanceType=self.instance_type,
            KeyName=self.key_name,
            SecurityGroupIds=[group_id],
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': f'ECE326-Lab{self.lab}'},
                    {'Key': 'Lab', 'Value': f'Lab{self.lab}'}
                ]
            }]
        )

        instance = instances[0]
        self.instance_id = instance.id

        print(f"✓ Instance launched: {self.instance_id}")
        print("  Waiting for instance to start...")

        # Wait for instance to be running
        instance.wait_until_running()
        instance.reload()

        self.public_ip = instance.public_ip_address
        print(f"✓ Instance is running!")
        print(f"  Instance ID: {self.instance_id}")
        print(f"  Public IP: {self.public_ip}")

        # Wait a bit for SSH to be available
        print("  Waiting for SSH to be available (30 seconds)...")
        time.sleep(30)

        return self.instance_id, self.public_ip

    def get_setup_commands(self):
        """Get setup commands based on lab number"""
        base_commands = [
            "sudo apt update && sudo apt upgrade -y",
            "sudo apt install -y python3 python3-pip apache2-utils sysstat dstat htop",
        ]

        if self.lab == 2:
            lab_commands = [
                "pip3 install boto3 python-dotenv oauth2client google-api-python-client httplib2 beaker bottle",
            ]
        elif self.lab == 3:
            lab_commands = [
                "pip3 install beautifulsoup4 bottle urllib3 boto3 python-dotenv",
            ]
        else:  # both
            lab_commands = [
                "pip3 install boto3 python-dotenv oauth2client google-api-python-client httplib2 beaker bottle beautifulsoup4 urllib3",
            ]

        return base_commands + lab_commands

    def setup_instance(self):
        """Setup instance with required dependencies"""
        print(f"\n{'='*60}")
        print(f"Setting Up Instance Dependencies")
        print(f"{'='*60}")

        if not self.public_ip:
            print("ERROR: Instance not launched yet")
            return False

        pem_file = f"{self.key_name}.pem"
        if not os.path.exists(pem_file):
            print(f"ERROR: Key file {pem_file} not found")
            return False

        commands = self.get_setup_commands()

        for i, cmd in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] Running: {cmd[:60]}...")
            ssh_cmd = f'ssh -i {pem_file} -o StrictHostKeyChecking=no ubuntu@{self.public_ip} "{cmd}"'

            result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  ⚠ Warning: Command failed (non-critical)")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}")
            else:
                print(f"  ✓ Success")

        print(f"\n✓ Instance setup completed!")
        return True

    def deploy_lab2(self):
        """Deploy Lab2 to EC2 instance"""
        print(f"\n{'='*60}")
        print(f"Deploying Lab2 to EC2")
        print(f"{'='*60}")

        pem_file = f"{self.key_name}.pem"
        lab2_dir = Path(__file__).parent / "Lab2"

        if not lab2_dir.exists():
            print(f"ERROR: Lab2 directory not found")
            return False

        # Files to copy
        files = [
            "frontend.py",
            "backend.py",
            "requirements.txt",
            ".env",
            "client_secret.json"
        ]

        dirs = ["static"]

        print("\nCopying files to EC2...")
        for f in files:
            file_path = lab2_dir / f
            if file_path.exists():
                scp_cmd = f'scp -i {pem_file} -o StrictHostKeyChecking=no {file_path} ubuntu@{self.public_ip}:~/'
                result = subprocess.run(scp_cmd, shell=True, capture_output=True)
                if result.returncode == 0:
                    print(f"  ✓ {f}")
                else:
                    print(f"  ⚠ {f} (optional, skipped)")

        for d in dirs:
            dir_path = lab2_dir / d
            if dir_path.exists():
                scp_cmd = f'scp -i {pem_file} -o StrictHostKeyChecking=no -r {dir_path} ubuntu@{self.public_ip}:~/'
                result = subprocess.run(scp_cmd, shell=True, capture_output=True)
                if result.returncode == 0:
                    print(f"  ✓ {d}/")

        print("\n✓ Lab2 deployment completed!")
        print(f"\nTo start Lab2 on EC2:")
        print(f"  ssh -i {pem_file} ubuntu@{self.public_ip}")
        print(f"  nohup python3 frontend.py > frontend.log 2>&1 &")
        print(f"\nAccess Lab2 at: http://{self.public_ip}:8080")

        return True

    def deploy_lab3(self):
        """Deploy Lab3 to EC2 instance"""
        print(f"\n{'='*60}")
        print(f"Deploying Lab3 to EC2")
        print(f"{'='*60}")

        pem_file = f"{self.key_name}.pem"
        lab3_dir = Path(__file__).parent / "Lab3"

        if not lab3_dir.exists():
            print(f"ERROR: Lab3 directory not found")
            return False

        # Check if database exists
        db_file = lab3_dir / "search_engine.db"
        if not db_file.exists():
            print("\n⚠ WARNING: search_engine.db not found!")
            print("  You need to run the crawler locally first:")
            print(f"    cd {lab3_dir}")
            print(f"    python crawler.py")
            response = input("\nContinue anyway? (y/n): ")
            if response.lower() != 'y':
                return False

        # Files to copy
        files = [
            "frontend.py",
            "storage.py",
            "search_engine.db",
            "requirements.txt"
        ]

        print("\nCopying files to EC2...")
        for f in files:
            file_path = lab3_dir / f
            if file_path.exists():
                scp_cmd = f'scp -i {pem_file} -o StrictHostKeyChecking=no {file_path} ubuntu@{self.public_ip}:~/'
                result = subprocess.run(scp_cmd, shell=True, capture_output=True)
                if result.returncode == 0:
                    print(f"  ✓ {f}")
                else:
                    print(f"  ⚠ {f} (failed)")

        print("\n✓ Lab3 deployment completed!")
        print(f"\nTo start Lab3 on EC2:")
        print(f"  ssh -i {pem_file} ubuntu@{self.public_ip}")
        print(f"  nohup python3 frontend.py > frontend.log 2>&1 &")
        print(f"\nAccess Lab3 at: http://{self.public_ip}:8080")

        return True

    def print_summary(self):
        """Print deployment summary"""
        print(f"\n{'='*60}")
        print(f"DEPLOYMENT SUMMARY - Lab{self.lab}")
        print(f"{'='*60}")
        print(f"Instance ID:  {self.instance_id}")
        print(f"Public IP:    {self.public_ip}")
        print(f"Key file:     {self.key_name}.pem")
        print(f"Region:       {self.aws_region}")
        print(f"\nSSH Connection:")
        print(f"  ssh -i {self.key_name}.pem ubuntu@{self.public_ip}")
        print(f"\nWeb Application:")
        print(f"  http://{self.public_ip}:8080")
        print(f"\nBenchmark Testing:")
        print(f"  ab -n 1000 -c 10 http://{self.public_ip}:8080/")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='AWS EC2 Installer for ECE326 Labs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup and deploy Lab2
  python aws_ec2_installer.py --lab 2 --action all

  # Setup and deploy Lab3
  python aws_ec2_installer.py --lab 3 --action all

  # Only setup EC2 instances for both labs
  python aws_ec2_installer.py --lab both --action setup

  # Full deployment for both labs (creates 2 instances)
  python aws_ec2_installer.py --lab both --action all
        """
    )

    parser.add_argument('--lab', choices=['2', '3', 'both'], required=True,
                        help='Which lab to deploy (2, 3, or both)')
    parser.add_argument('--action', choices=['setup', 'deploy', 'all'], required=True,
                        help='Action to perform (setup=create EC2, deploy=copy files, all=both)')

    args = parser.parse_args()

    labs = [args.lab] if args.lab != 'both' else ['2', '3']

    for lab in labs:
        print(f"\n{'#'*60}")
        print(f"# Processing Lab{lab}")
        print(f"{'#'*60}")

        installer = EC2Installer(lab)

        # Create key pair (shared across labs)
        installer.create_key_pair()

        if args.action in ['setup', 'all']:
            # Launch instance
            installer.launch_instance()

            # Setup dependencies
            installer.setup_instance()

        if args.action in ['deploy', 'all']:
            # Deploy lab
            if lab == '2':
                installer.deploy_lab2()
            else:
                installer.deploy_lab3()

        # Print summary
        installer.print_summary()

        if len(labs) > 1:
            print("\n" + "="*60)
            print("Waiting 5 seconds before processing next lab...")
            print("="*60)
            time.sleep(5)


if __name__ == '__main__':
    main()
