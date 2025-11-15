#!/bin/bash

# PROJECT SENTINEL - Oracle Cloud ML Services Deployment Script
# For VM Instance 2 (ML/NLP Services)

set -e  # Exit on any error

echo "======================================"
echo "PROJECT SENTINEL - ML Services Deployment"
echo "Oracle Cloud VM Instance 2"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Please do not run as root${NC}"
   exit 1
fi

# Step 1: Update System
echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Step 2: Install Dependencies
echo -e "${YELLOW}[2/8] Installing dependencies...${NC}"
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    ufw \
    htop \
    ca-certificates \
    gnupg \
    lsb-release \
    python3-pip

# Step 3: Install Docker
echo -e "${YELLOW}[3/8] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# Step 4: Install Docker Compose
echo -e "${YELLOW}[4/8] Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

# Step 5: Configure Firewall
echo -e "${YELLOW}[5/8] Configuring firewall...${NC}"
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 8001/tcp comment 'ML Prediction API'
sudo ufw allow 8004/tcp comment 'NLP Translation'
sudo ufw allow 8005/tcp comment 'NLP NER'
echo -e "${GREEN}✓ Firewall configured${NC}"

# Step 6: Setup Swap (Important for ML models)
echo -e "${YELLOW}[6/8] Setting up swap space (2GB)...${NC}"
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo -e "${GREEN}✓ Swap configured (2GB)${NC}"
else
    echo -e "${GREEN}✓ Swap already configured${NC}"
fi

# Step 7: Clone/Update Repository
echo -e "${YELLOW}[7/8] Setting up application directory...${NC}"
APP_DIR="$HOME/apps/sentinet_cameroon"

if [ -d "$APP_DIR" ]; then
    echo -e "${YELLOW}Repository exists, pulling latest changes...${NC}"
    cd "$APP_DIR"
    git pull
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    mkdir -p "$HOME/apps"
    cd "$HOME/apps"
    
    # Manual upload message
    echo -e "${RED}Please upload your project files to: $APP_DIR${NC}"
    echo -e "${YELLOW}Use: scp -i your-key.key -r /local/path ubuntu@YOUR_IP:~/apps/${NC}"
    read -p "Press Enter when files are uploaded..."
fi

cd "$APP_DIR/project-sentinel"

# Step 8: Deploy ML Services
echo -e "${YELLOW}[8/8] Starting ML services with Docker Compose...${NC}"

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

# Use ML-only compose file
if [ -f ../docker-compose.ml-only.yml ]; then
    cp ../docker-compose.ml-only.yml docker-compose.yml
fi

# Pull and build images
echo -e "${YELLOW}Pulling Docker images (this may take 10-15 minutes)...${NC}"
echo -e "${YELLOW}Note: ML models will be downloaded on first run (may take additional time)${NC}"
docker-compose pull

echo -e "${YELLOW}Building ML service images...${NC}"
docker-compose build

# Start services
echo -e "${YELLOW}Starting ML services...${NC}"
docker-compose up -d

# Wait for services to start
echo -e "${YELLOW}Waiting for ML models to load (60 seconds)...${NC}"
sleep 60

# Check service health
echo ""
echo -e "${GREEN}======================================"
echo -e "ML SERVICES DEPLOYMENT COMPLETE!"
echo -e "======================================${NC}"
echo ""
echo -e "${GREEN}Services Status:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}Access your ML services:${NC}"
echo -e "ML Prediction API:   http://$PUBLIC_IP:8001/docs"
echo -e "NLP Translation:     http://$PUBLIC_IP:8004/docs"
echo -e "NLP NER Service:     http://$PUBLIC_IP:8005/docs"
echo ""
echo -e "${YELLOW}⚠ IMPORTANT - Update Backend VM:${NC}"
echo "1. SSH to your backend VM (VM Instance 1)"
echo "2. Edit .env.production:"
echo "   ML_API_URL=http://$PUBLIC_IP:8001"
echo "   NLP_TRANSLATION_URL=http://$PUBLIC_IP:8004"
echo "   NLP_NER_URL=http://$PUBLIC_IP:8005"
echo "3. Restart backend services:"
echo "   cd ~/apps/sentinet_cameroon/project-sentinel"
echo "   docker-compose restart"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "docker-compose logs -f"
echo ""
echo -e "${YELLOW}Test ML services:${NC}"
echo "curl http://$PUBLIC_IP:8001/health"
echo "curl http://$PUBLIC_IP:8004/health"
echo "curl http://$PUBLIC_IP:8005/health"
echo ""
echo -e "${GREEN}🎉 ML Services are now running!${NC}"




