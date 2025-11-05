#!/bin/bash
# Deployment script for Lab 3 Search Engine on AWS
# Usage: ./deploy.sh YOUR_EC2_IP YOUR_KEY.pem

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: ./deploy.sh YOUR_EC2_IP YOUR_KEY.pem"
    echo "Example: ./deploy.sh 3.80.127.131 my-key.pem"
    exit 1
fi

EC2_IP=$1
KEY_FILE=$2
EC2_USER="ubuntu"

echo "======================================"
echo "Lab 3 AWS Deployment Script"
echo "======================================"
echo "Target: $EC2_USER@$EC2_IP"
echo "Key: $KEY_FILE"
echo ""

# Check if database exists
if [ ! -f "search_engine.db" ]; then
    echo "ERROR: search_engine.db not found!"
    echo "Please run the crawler first:"
    echo "  python crawler.py"
    exit 1
fi

echo "Step 1: Copying files to EC2..."
scp -i "$KEY_FILE" frontend.py "$EC2_USER@$EC2_IP":~/
scp -i "$KEY_FILE" storage.py "$EC2_USER@$EC2_IP":~/
scp -i "$KEY_FILE" search_engine.db "$EC2_USER@$EC2_IP":~/
scp -i "$KEY_FILE" requirements.txt "$EC2_USER@$EC2_IP":~/

echo ""
echo "Step 2: Installing dependencies on EC2..."
ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" << 'EOF'
    sudo apt update
    sudo apt install -y python3-pip
    pip3 install -r requirements.txt
EOF

echo ""
echo "Step 3: Starting frontend server..."
ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" << 'EOF'
    # Kill any existing frontend
    pkill -f frontend.py || true

    # Start new frontend in background
    nohup python3 frontend.py > frontend.log 2>&1 &

    echo "Waiting for server to start..."
    sleep 3

    # Check if server is running
    if ps aux | grep -v grep | grep frontend.py > /dev/null; then
        echo "✓ Frontend server is running"
    else
        echo "✗ Failed to start frontend server"
        cat frontend.log
        exit 1
    fi
EOF

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo "Your search engine is now running at:"
echo "  http://$EC2_IP:8080"
echo ""
echo "To check logs:"
echo "  ssh -i $KEY_FILE $EC2_USER@$EC2_IP 'tail -f frontend.log'"
echo ""
echo "To stop the server:"
echo "  ssh -i $KEY_FILE $EC2_USER@$EC2_IP 'pkill -f frontend.py'"
echo "======================================"
