import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
REGION = os.getenv('AWS_REGION', 'us-east-1')
KEY_NAME = os.getenv('KEY_NAME', 'ece326-keypair')
SECURITY_GROUP_NAME = os.getenv('SECURITY_GROUP_NAME')
INSTANCE_TYPE = os.getenv('INSTANCE_TYPE', 't3.micro')
UBUNTU_AMI = os.getenv('UBUNTU_AMI', 'ami-0c7217cdde317cfec')

print("🚀 Starting EC2 Instance Deployment\n")
print(f"Region: {REGION}")
print(f"Instance Type: {INSTANCE_TYPE}")
print(f"Security Group: {SECURITY_GROUP_NAME}\n")

# Validate required environment variables
if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    print("❌ Error: AWS credentials not found in .env file")
    print("Please create a .env file with AWS_ACCESS_KEY and AWS_SECRET_KEY")
    exit(1)

if not SECURITY_GROUP_NAME:
    print("❌ Error: SECURITY_GROUP_NAME not set in .env file")
    exit(1)

# Initialize EC2 client and resource
ec2_client = boto3.client(
    'ec2',
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

ec2_resource = boto3.resource(
    'ec2',
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def create_key_pair():
    """Create EC2 key pair if it doesn't exist"""
    try:
        response = ec2_client.create_key_pair(KeyName=KEY_NAME)
        
        # Save private key
        pem_file = f'{KEY_NAME}.pem'
        with open(pem_file, 'w') as f:
            f.write(response['KeyMaterial'])
        
        # Set permissions
        os.chmod(pem_file, 0o400)
        
        print(f"✓ Key pair created: {pem_file}")
    except ec2_client.exceptions.ClientError as e:
        if 'InvalidKeyPair.Duplicate' in str(e):
            print(f"! Key pair {KEY_NAME} already exists")
        else:
            raise

def create_security_group():
    """Create security group if it doesn't exist"""
    try:
        response = ec2_client.create_security_group(
            GroupName=SECURITY_GROUP_NAME,
            Description=f'Security group for ECE326 lab'
        )
        sg_id = response['GroupId']
        print(f"✓ Security group created: {sg_id}")
    except ec2_client.exceptions.ClientError as e:
        if 'InvalidGroup.Duplicate' in str(e):
            # Get existing security group
            response = ec2_client.describe_security_groups(
                Filters=[{'Name': 'group-name', 'Values': [SECURITY_GROUP_NAME]}]
            )
            sg_id = response['SecurityGroups'][0]['GroupId']
            print(f"! Security group already exists: {sg_id}")
        else:
            raise
    
    return sg_id

def configure_security_rules(security_group_id):
    """Configure security group rules"""
    try:
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                # ICMP for ping
                {
                    'IpProtocol': 'icmp',
                    'FromPort': -1,
                    'ToPort': -1,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                # SSH
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                # HTTP
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                # Port 8080
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 8080,
                    'ToPort': 8080,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                # Port 8081
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 8081,
                    'ToPort': 8081,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        print("✓ Security rules configured")
    except ec2_client.exceptions.ClientError as e:
        if 'InvalidPermission.Duplicate' in str(e):
            print("! Security rules already exist")
        else:
            raise

def launch_instance(security_group_id):
    """Launch EC2 instance"""
    instances = ec2_resource.create_instances(
        ImageId=UBUNTU_AMI,
        MinCount=1,
        MaxCount=1,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=[security_group_id]
    )
    
    instance = instances[0]
    print(f"\n✓ Instance created: {instance.id}")
    print("⏳ Waiting for instance to start (this may take 1-2 minutes)...")
    
    instance.wait_until_running()
    instance.reload()
    
    print(f"\n{'='*60}")
    print(f"🎉 INSTANCE IS RUNNING!")
    print(f"{'='*60}")
    print(f"Instance ID:  {instance.id}")
    print(f"Public IP:    {instance.public_ip_address}")
    print(f"Key file:     {KEY_NAME}.pem")
    print(f"\n📝 SSH Command:")
    print(f"ssh -i {KEY_NAME}.pem ubuntu@{instance.public_ip_address}")
    print(f"\n📝 SCP Command (to copy files):")
    print(f"scp -i {KEY_NAME}.pem yourfile.py ubuntu@{instance.public_ip_address}:~/")
    print(f"{'='*60}\n")
    
    return instance

def main():
    try:
        # Step 1: Create key pair
        create_key_pair()
        
        # Step 2: Create and configure security group
        sg_id = create_security_group()
        
        # Step 3: Configure security rules
        configure_security_rules(sg_id)
        
        # Step 4: Launch instance
        instance = launch_instance(sg_id)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()