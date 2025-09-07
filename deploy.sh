#!/bin/bash

# AI-fied Translate AI - Quick Deployment Script
# This script helps you deploy to different platforms

set -e

echo "🚀 AI-fied Translate AI Deployment Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_header "Checking requirements..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    print_status "All requirements are met!"
}

# Setup environment
setup_environment() {
    print_header "Setting up environment..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Created .env file from template. Please edit it with your API keys."
        else
            print_error "env.example file not found. Please create .env file manually."
            exit 1
        fi
    else
        print_status ".env file already exists."
    fi
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_status "Installing Node.js dependencies..."
    npm install
    
    print_status "Environment setup complete!"
}

# Deploy to Railway
deploy_railway() {
    print_header "Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_status "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    print_status "Logging into Railway..."
    railway login
    
    print_status "Initializing Railway project..."
    railway init
    
    print_warning "Please set the following environment variables in Railway dashboard:"
    echo "  - OPENAI_API_KEY"
    echo "  - GOOGLE_APPLICATION_CREDENTIALS_JSON"
    echo "  - JWT_SECRET_KEY"
    echo "  - API_BASE_URL (will be set automatically after deployment)"
    
    read -p "Press Enter after setting environment variables..."
    
    print_status "Deploying to Railway..."
    railway up
    
    print_status "Railway deployment complete!"
    print_status "Check your Railway dashboard for the deployment URL."
}

# Deploy to Render
deploy_render() {
    print_header "Deploying to Render..."
    
    print_warning "Render deployment requires manual setup:"
    echo "1. Go to https://render.com"
    echo "2. Create two web services:"
    echo "   - Backend: Connect your repo, Build: 'pip install -r requirements.txt', Start: 'python -m uvicorn api:app --host 0.0.0.0 --port \$PORT'"
    echo "   - Frontend: Connect your repo, Build: 'npm install', Start: 'node server.js'"
    echo "3. Set environment variables for both services"
    echo "4. Update API_BASE_URL in frontend service to point to backend URL"
    
    read -p "Press Enter when you've completed the Render setup..."
}

# Deploy with Docker
deploy_docker() {
    print_header "Building Docker image..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    print_status "Building Docker image..."
    docker build -t video-translation .
    
    print_status "Docker image built successfully!"
    print_warning "To run locally:"
    echo "  docker run -p 3000:3000 -p 8000:8000 -e OPENAI_API_KEY=your-key video-translation"
    
    print_warning "To push to registry:"
    echo "  docker tag video-translation yourusername/video-translation"
    echo "  docker push yourusername/video-translation"
}

# Test deployment
test_deployment() {
    print_header "Testing deployment..."
    
    # Test if services are running
    if curl -f http://localhost:3000/health &> /dev/null; then
        print_status "Frontend service is running!"
    else
        print_warning "Frontend service is not running on localhost:3000"
    fi
    
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_status "Backend service is running!"
    else
        print_warning "Backend service is not running on localhost:8000"
    fi
    
    print_status "Testing complete!"
}

# Main menu
show_menu() {
    echo ""
    echo "Select deployment option:"
    echo "1) Setup local environment"
    echo "2) Deploy to Railway (Recommended)"
    echo "3) Deploy to Render"
    echo "4) Build Docker image"
    echo "5) Test local deployment"
    echo "6) Exit"
    echo ""
}

# Main function
main() {
    check_requirements
    
    while true; do
        show_menu
        read -p "Enter your choice (1-6): " choice
        
        case $choice in
            1)
                setup_environment
                ;;
            2)
                deploy_railway
                ;;
            3)
                deploy_render
                ;;
            4)
                deploy_docker
                ;;
            5)
                test_deployment
                ;;
            6)
                print_status "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-6."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main
