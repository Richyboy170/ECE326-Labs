#!/usr/bin/env python3
"""
AWS Instance Termination Script for ECE326 Lab 4
Terminates an EC2 instance by instance ID
"""

import boto3
import os
import sys
from dotenv import load_dotenv

# Configuration
CREDENTIALS_FILE = 'aws_credentials.env'


def print_header(message):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {message}")
    print(f"{'=' * 70}\n")


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
    required_vars = ['AWS_ACCESS_KEY', 'AWS_SECRET_KEY', 'AWS_REGION']
    
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
    }


def create_ec2_client(config):
    """Create EC2 client"""
    try:
        client = boto3.client(
            'ec2',
            region_name=config['region'],
            aws_access_key_id=config['access_key'],
            aws_secret_access_key=config['secret_key']
        )
        
        # Test connection
        client.describe_regions()
        
        return client
    except Exception as e:
        print(f"❌ Error connecting to AWS: {e}")
        sys.exit(1)


def get_instance_info(client, instance_id):
    """Get information about an instance"""
    try:
        response = client.describe_instances(InstanceIds=[instance_id])
        
        if not response['Reservations']:
            return None
        
        instance = response['Reservations'][0]['Instances'][0]
        return instance
        
    except client.exceptions.ClientError as e:
        if 'InvalidInstanceID.NotFound' in str(e):
            return None
        raise


def terminate_instance(client, instance_id):
    """Terminate an EC2 instance"""
    try:
        response = client.terminate_instances(InstanceIds=[instance_id])
        return response['TerminatingInstances'][0]
    except Exception as e:
        print(f"❌ Error terminating instance: {e}")
        return None


def main():
    """Main termination function"""
    print_header("ECE326 Lab 4 - AWS Instance Termination")
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python aws_terminate.py <instance_id>")
        print("\nExample:")
        print("  python aws_terminate.py i-0ee9470aa16dc1a09")
        print("\nTo get your instance ID:")
        print("  - Check the output from aws_deploy.py")
        print("  - Or check AWS Console -> EC2 -> Instances")
        sys.exit(1)
    
    instance_id = sys.argv[1]
    
    # Validate instance ID format
    if not instance_id.startswith('i-'):
        print(f"❌ Error: Invalid instance ID format: {instance_id}")
        print(f"Instance IDs should start with 'i-'")
        sys.exit(1)
    
    # Load credentials
    print("Loading AWS credentials...")
    config = load_aws_credentials()
    print("✓ Credentials loaded")
    
    # Connect to AWS
    print("\nConnecting to AWS...")
    ec2_client = create_ec2_client(config)
    print("✓ Connected to AWS")
    
    # Get instance information
    print(f"\nChecking instance: {instance_id}")
    instance = get_instance_info(ec2_client, instance_id)
    
    if instance is None:
        print(f"❌ Error: Instance {instance_id} not found")
        print(f"\nPossible reasons:")
        print(f"  - Instance ID is incorrect")
        print(f"  - Instance is in a different region (current: {config['region']})")
        print(f"  - You don't have permission to access this instance")
        sys.exit(1)
    
    # Display instance information
    state = instance['State']['Name']
    print(f"\n{'=' * 70}")
    print(f"Instance Information:")
    print(f"{'=' * 70}")
    print(f"Instance ID:    {instance_id}")
    print(f"Current State:  {state}")
    
    if 'PublicIpAddress' in instance:
        print(f"Public IP:      {instance['PublicIpAddress']}")
    
    if 'InstanceType' in instance:
        print(f"Instance Type:  {instance['InstanceType']}")
    
    if 'LaunchTime' in instance:
        print(f"Launch Time:    {instance['LaunchTime']}")
    
    # Check current state
    if state == 'terminated':
        print(f"\n⚠️  Instance is already terminated")
        print(f"{'=' * 70}\n")
        sys.exit(0)
    
    if state == 'terminating':
        print(f"\n⚠️  Instance is already terminating")
        print(f"{'=' * 70}\n")
        sys.exit(0)
    
    # Confirm termination
    print(f"\n{'=' * 70}")
    print(f"⚠️  WARNING: This will terminate the instance!")
    print(f"{'=' * 70}")
    
    confirm = input(f"\nAre you sure you want to terminate {instance_id}? (yes/no): ")
    
    if confirm.lower() not in ['yes', 'y']:
        print(f"\n❌ Termination cancelled")
        sys.exit(0)
    
    # Terminate instance
    print(f"\n🛑 Terminating instance {instance_id}...")
    result = terminate_instance(ec2_client, instance_id)
    
    if result:
        previous_state = result['PreviousState']['Name']
        current_state = result['CurrentState']['Name']
        
        print_header("TERMINATION SUCCESSFUL!")
        print(f"Instance ID:      {instance_id}")
        print(f"Previous State:   {previous_state}")
        print(f"Current State:    {current_state}")
        print(f"\nThe instance is now terminating and will be fully terminated shortly.")
        print(f"\n{'=' * 70}\n")
    else:
        print(f"\n❌ Failed to terminate instance")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Termination cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during termination:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
