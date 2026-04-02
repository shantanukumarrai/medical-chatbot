#!/bin/bash
# ═══════════════════════════════════════════════════
#  MediBot — One-Command Setup Script
#  Run this from the project root:
#    chmod +x setup.sh && ./setup.sh
# ═══════════════════════════════════════════════════

set -e  # Exit on any error

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🏥  MediBot Setup Script             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Check Python ──────────────────────────
echo -e "${YELLOW}[1/6] Checking Python version...${NC}"
python_version=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ Python 3 not found. Install from https://python.org${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Found: $python_version${NC}"

# ── Step 2: Create virtual environment ───────────
echo ""
echo -e "${YELLOW}[2/6] Creating virtual environment...${NC}"
cd backend
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment created and activated${NC}"

# ── Step 3: Install dependencies ─────────────────
echo ""
echo -e "${YELLOW}[3/6] Installing Python dependencies...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✅ Dependencies installed${NC}"

# ── Step 4: Setup .env ────────────────────────────
echo ""
echo -e "${YELLOW}[4/6] Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Created .env from template.${NC}"
    echo -e "${YELLOW}   👉 Open backend/.env and add your API keys before continuing!${NC}"
    echo ""
    echo "   Required keys:"
    echo "   • OPENAI_API_KEY   → https://platform.openai.com/api-keys"
    echo "   • PINECONE_API_KEY → https://app.pinecone.io"
    echo ""
    read -p "Press ENTER after you've added your API keys to .env..."
else
    echo -e "${GREEN}✅ .env already exists${NC}"
fi

# ── Step 5: Ingest documents ──────────────────────
echo ""
echo -e "${YELLOW}[5/6] Ingesting documents into Pinecone...${NC}"
echo "   (This creates your vector database — takes 30-60 seconds)"
python ingest.py

# ── Step 6: Done ──────────────────────────────────
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         ✅  Setup Complete!              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}To start the API server:${NC}"
echo "   cd backend && source venv/bin/activate && python app.py"
echo ""
echo -e "${GREEN}To open the frontend:${NC}"
echo "   cd frontend && python3 -m http.server 3000"
echo "   Then visit: http://localhost:3000"
echo ""
echo -e "${GREEN}To run tests:${NC}"
echo "   cd backend && python -m pytest tests/ -v"
echo ""
