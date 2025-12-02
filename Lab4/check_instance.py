#!/usr/bin/env python3
"""
Quick diagnostic script to check what's wrong with the EC2 instance
"""
import subprocess
import sys

if len(sys.argv) != 2:
    print("Usage: python check_instance.py <instance_ip>")
    sys.exit(1)

ip = sys.argv[1]
key_file = "ece326-keypair.pem"

print(f"Checking instance at {ip}...")
print("=" * 70)

# Check if frontend is running
print("\n1. Checking if frontend.py is running:")
cmd = ['ssh', '-i', key_file, '-o', 'StrictHostKeyChecking=no', 
       f'ubuntu@{ip}', 'ps aux | grep frontend.py | grep -v grep']
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(result.stdout if result.stdout else "❌ Not running")

# Check frontend log
print("\n2. Frontend log contents:")
cmd = ['ssh', '-i', key_file, '-o', 'StrictHostKeyChecking=no',
       f'ubuntu@{ip}', 'cat frontend.log 2>&1 || echo "Log file not found"']
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(result.stdout)

# Check if files exist
print("\n3. Checking if required files exist:")
cmd = ['ssh', '-i', key_file, '-o', 'StrictHostKeyChecking=no',
       f'ubuntu@{ip}', 'ls -la *.py *.db static/ 2>&1']
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(result.stdout)

# Try to start manually and see error
print("\n4. Trying to start frontend.py manually:")
cmd = ['ssh', '-i', key_file, '-o', 'StrictHostKeyChecking=no',
       f'ubuntu@{ip}', 'python3 frontend.py 2>&1 & sleep 2; cat frontend.log 2>&1']
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10)
print(result.stdout)
print(result.stderr)
