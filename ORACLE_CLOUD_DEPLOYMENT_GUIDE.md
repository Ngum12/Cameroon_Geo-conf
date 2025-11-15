# 🚀 PROJECT SENTINEL - Oracle Cloud Always Free Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Oracle Cloud Account Setup](#oracle-cloud-account-setup)
3. [VM Instance Creation](#vm-instance-creation)
4. [Server Setup](#server-setup)
5. [Deployment](#deployment)
6. [Configuration](#configuration)
7. [Monitoring](#monitoring)

---

## ✅ Prerequisites

- Oracle Cloud account (completely FREE)
- SSH client (PuTTY for Windows, built-in for Mac/Linux)
- Domain name (optional, or use Oracle's public IP)
- GitHub account (for code deployment)

---

## 🌐 Oracle Cloud Account Setup

### Step 1: Sign Up for Oracle Cloud
1. Go to: https://www.oracle.com/cloud/free/
2. Click **"Start for free"**
3. Fill in your details:
   - Email address
   - Country
   - Name
4. **Important:** You'll get:
   - $300 credit for 30 days (for testing paid services)
   - **Always Free tier** (NEVER expires)

### Step 2: Verify Your Account
1. Verify your email
2. Add credit card (for identity verification only)
   - **You will NOT be charged**
   - Always Free resources never expire
3. Wait for account approval (usually instant)

---

## 🖥️ VM Instance Creation

### Create VM Instance 1 - Primary Services (Backend + Database)

1. **Login to Oracle Cloud Console**
   - Go to: https://cloud.oracle.com/

2. **Navigate to Compute Instances**
   - Menu → Compute → Instances

3. **Create Instance**
   - Click **"Create Instance"**
   
   **Name:** `sentinel-backend`
   
   **Image and Shape:**
   - Image: **Ubuntu 22.04**
   - Shape: **VM.Standard.E2.1.Micro** (Always Free)
     - 1 CPU, 1GB RAM
   
   **Networking:**
   - VCN: Create new or use default
   - Subnet: Public subnet
   - Public IP: ✅ **Assign a public IPv4 address**
   
   **SSH Keys:**
   - ✅ Generate SSH key pair
   - **Download private key** (save as `sentinel-backend.key`)
   
   **Boot Volume:**
   - 50GB (Free tier allows up to 200GB total)
   
4. Click **"Create"**
5. Wait 2-3 minutes for provisioning

### Create VM Instance 2 - ML Services

Repeat the above steps:
- **Name:** `sentinel-ml-services`
- Same configuration
- Download private key as `sentinel-ml.key`

---

## 🔒 Configure Security & Firewall

### Step 1: Configure VCN Security Lists

1. Go to: **Networking → Virtual Cloud Networks**
2. Click your VCN name
3. Click **"Security Lists"**
4. Click **"Default Security List"**
5. Click **"Add Ingress Rules"**

Add these rules:

| Source CIDR | IP Protocol | Source Port | Destination Port | Description |
|-------------|-------------|-------------|------------------|-------------|
| 0.0.0.0/0 | TCP | All | 22 | SSH |
| 0.0.0.0/0 | TCP | All | 80 | HTTP |
| 0.0.0.0/0 | TCP | All | 443 | HTTPS |
| 0.0.0.0/0 | TCP | All | 8000-8005 | API Services |
| 0.0.0.0/0 | TCP | All | 5173 | Frontend |

---

## 💻 Server Setup - VM Instance 1 (Backend)

### Step 1: Connect to Your VM

**For Windows (PowerShell):**
```powershell
# Set correct permissions for the key
icacls sentinel-backend.key /inheritance:r
icacls sentinel-backend.key /grant:r "$($env:USERNAME):(R)"

# Connect via SSH
ssh -i sentinel-backend.key ubuntu@YOUR_PUBLIC_IP
```

**For Mac/Linux:**
```bash
# Set correct permissions
chmod 400 sentinel-backend.key

# Connect via SSH
ssh -i sentinel-backend.key ubuntu@YOUR_PUBLIC_IP
```

### Step 2: Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    ufw \
    ca-certificates \
    gnupg \
    lsb-release

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# Log out and back in for Docker permissions
exit
```

### Step 3: Configure Firewall (Ubuntu UFW)

```bash
# Reconnect to server
ssh -i sentinel-backend.key ubuntu@YOUR_PUBLIC_IP

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp       # SSH
sudo ufw allow 80/tcp       # HTTP
sudo ufw allow 443/tcp      # HTTPS
sudo ufw allow 8000/tcp     # Django Backend
sudo ufw allow 5173/tcp     # Frontend
sudo ufw enable

# Check status
sudo ufw status
```

### Step 4: Clone Your Project

```bash
# Create app directory
mkdir -p ~/apps
cd ~/apps

# Clone your repository
git clone https://github.com/YOUR_USERNAME/sentinet_cameroon.git
cd sentinet_cameroon/project-sentinel

# Or upload via SCP from your local machine:
# scp -i sentinel-backend.key -r C:\Users\Ngum\Documents\sentinet_cameroon ubuntu@YOUR_PUBLIC_IP:~/apps/
```

---

## 💰 Cost Breakdown

### Oracle Cloud Always Free Tier
- ✅ **2 AMD VMs** (1 OCPU, 1GB RAM each) - **FREE FOREVER**
- ✅ **4 ARM VMs** (4 OCPUs, 24GB RAM total) - **FREE FOREVER** (if you want even more!)
- ✅ **100GB Block Storage** - **FREE FOREVER**
- ✅ **10GB Object Storage** - **FREE FOREVER**
- ✅ **Flexible Load Balancer** - **FREE FOREVER**

### Total Monthly Cost: **$0.00** 🎉

---

**🎉 Congratulations! Your Project Sentinel is now running on 100% FREE Oracle Cloud infrastructure!**




