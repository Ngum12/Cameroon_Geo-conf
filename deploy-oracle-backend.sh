#!/bin/bash

# PROJECT SENTINEL - Oracle Cloud Backend Deployment Script
# For VM Instance 1 (Backend + Database)

set -e  # Exit on any error

echo "======================================"
echo "PROJECT SENTINEL - Backend Deployment"
echo "Oracle Cloud VM Instance 1"
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
echo -e "${YELLOW}[1/10] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Step 2: Install Dependencies
echo -e "${YELLOW}[2/10] Installing dependencies...${NC}"
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
    python3-pip \
    build-essential \
    libpq-dev

# Step 3: Install Docker
echo -e "${YELLOW}[3/10] Installing Docker...${NC}"
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
echo -e "${YELLOW}[4/10] Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

# Step 5: Configure Firewall
echo -e "${YELLOW}[5/10] Configuring firewall...${NC}"
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow 8000/tcp comment 'Django Backend'
sudo ufw allow 8003/tcp comment 'Human Interface API'
sudo ufw allow 8002/tcp comment 'RL System API'
sudo ufw allow 5173/tcp comment 'Frontend'
echo -e "${GREEN}✓ Firewall configured${NC}"

# Step 6: Setup Swap (Important for 1GB RAM)
echo -e "${YELLOW}[6/10] Setting up swap space (2GB)...${NC}"
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
echo -e "${YELLOW}[7/10] Setting up application directory...${NC}"
APP_DIR="$HOME/apps/sentinet_cameroon"

if [ -d "$APP_DIR" ]; then
    echo -e "${YELLOW}Repository exists, pulling latest changes...${NC}"
    cd "$APP_DIR"
    git pull
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    mkdir -p "$HOME/apps"
    cd "$HOME/apps"
    
    # Option 1: Clone from GitHub (if you have it there)
    # git clone https://github.com/YOUR_USERNAME/sentinet_cameroon.git
    
    # Option 2: Manual upload message
    echo -e "${RED}Please upload your project files to: $APP_DIR${NC}"
    echo -e "${YELLOW}Use: scp -i your-key.key -r /local/path ubuntu@YOUR_IP:~/apps/${NC}"
    read -p "Press Enter when files are uploaded..."
fi

cd "$APP_DIR/project-sentinel"

# Step 8: Configure Environment
echo -e "${YELLOW}[8/10] Configuring environment variables...${NC}"
if [ ! -f .env.production ]; then
    echo -e "${YELLOW}Creating .env.production file...${NC}"
    
    # Generate secure secret key
    SECRET_KEY=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    # Get public IP
    PUBLIC_IP=$(curl -s ifconfig.me)
    
    cat > .env.production << EOF
# Django Settings
DJANGO_SECRET_KEY=$SECRET_KEY
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$PUBLIC_IP,localhost,127.0.0.1

# Database
POSTGRES_DB=sentinel_db
POSTGRES_USER=sentinel_user
POSTGRES_PASSWORD=$DB_PASSWORD
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Public IP
PUBLIC_IP=$PUBLIC_IP

# ML Services (Point to VM Instance 2 - Update this after deploying VM2)
ML_API_URL=http://YOUR_ML_VM_IP:8001
NLP_TRANSLATION_URL=http://YOUR_ML_VM_IP:8004
NLP_NER_URL=http://YOUR_ML_VM_IP:8005

# Security
CORS_ALLOWED_ORIGINS=http://$PUBLIC_IP:5173,http://localhost:5173

# Twilio (Optional - Add your credentials)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
TWILIO_WHATSAPP_NUMBER=

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EOF

    echo -e "${GREEN}✓ Environment file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env.production and update ML_VM_IP after deploying VM Instance 2${NC}"
else
    echo -e "${GREEN}✓ Environment file already exists${NC}"
fi

# Step 9: Deploy with Docker Compose
echo -e "${YELLOW}[9/10] Starting services with Docker Compose...${NC}"

# Copy the Oracle optimized compose file
if [ -f ../docker-compose.oracle.yml ]; then
    cp ../docker-compose.oracle.yml docker-compose.yml
fi

# Load environment variables
export $(cat .env.production | grep -v '^#' | xargs)

# Pull and build images
echo -e "${YELLOW}Pulling Docker images (this may take 10-15 minutes)...${NC}"
docker-compose pull

echo -e "${YELLOW}Building custom images...${NC}"
docker-compose build

# Start services
echo -e "${YELLOW}Starting all services...${NC}"
docker-compose up -d

# Wait for services to start
echo -e "${YELLOW}Waiting for services to start (30 seconds)...${NC}"
sleep 30

# Step 10: Initialize Database
echo -e "${YELLOW}[10/10] Initializing database...${NC}"

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
docker-compose exec -T backend python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
docker-compose exec -T backend python manage.py collectstatic --noinput

# Create superuser (interactive)
echo -e "${YELLOW}Creating superuser account...${NC}"
echo -e "${GREEN}Please enter admin credentials:${NC}"
docker-compose exec backend python manage.py createsuperuser

# Check service health
echo ""
echo -e "${GREEN}======================================"
echo -e "DEPLOYMENT COMPLETE!"
echo -e "======================================${NC}"
echo ""
echo -e "${GREEN}Services Status:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}Access your application:${NC}"
echo -e "Frontend:    http://$PUBLIC_IP:5173"
echo -e "Backend API: http://$PUBLIC_IP:8000/api/v1/"
echo -e "Admin Panel: http://$PUBLIC_IP:8000/admin/"
echo -e "API Docs:    http://$PUBLIC_IP:8003/docs"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Deploy ML services on VM Instance 2 using: ./deploy-oracle-ml.sh"
echo "2. Update ML_API_URL in .env.production with VM2 IP address"
echo "3. Restart services: docker-compose restart"
echo "4. (Optional) Setup Nginx reverse proxy"
echo "5. (Optional) Configure SSL with Let's Encrypt"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "docker-compose logs -f"
echo ""
echo -e "${GREEN}🎉 Project Sentinel is now running!${NC}"




