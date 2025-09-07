# AI-fied Translate AI - Deployment Guide

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd video-translation
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Manual Deployment

1. **Install dependencies**
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # Node.js dependencies
   npm install
   ```

2. **Set up environment variables**
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
   ```

3. **Start the services**
   ```bash
   # Terminal 1: Start FastAPI backend
   python -m uvicorn api:app --host 0.0.0.0 --port 8000
   
   # Terminal 2: Start Node.js frontend
   node server.js
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# JWT Configuration
JWT_SECRET_KEY=your-secret-key

# Optional: LALAL.AI for advanced audio separation
LALALAI_API_KEY=your-lalalai-key

# Server Configuration
NODE_ENV=production
PORT=3000
API_PORT=8000
```

### Google Cloud Setup

1. Create a Google Cloud project
2. Enable the Text-to-Speech API
3. Create a service account and download the JSON key
4. Place the JSON file in your project directory

## 📊 Production Considerations

### Performance Optimization

1. **GPU Support**: Install CUDA for faster OCR processing
2. **Redis**: Use Redis for job queue management
3. **Load Balancing**: Use nginx for load balancing
4. **CDN**: Use a CDN for static file serving

### Security

1. **HTTPS**: Use SSL certificates for production
2. **API Keys**: Store API keys securely (use environment variables)
3. **Authentication**: Implement proper user authentication
4. **Rate Limiting**: Add rate limiting to prevent abuse

### Monitoring

1. **Logging**: Configure proper logging levels
2. **Health Checks**: Monitor service health
3. **Metrics**: Track usage and performance metrics
4. **Alerts**: Set up alerts for failures

## 🌐 Cloud Deployment

### AWS Deployment

1. **EC2 Instance**
   ```bash
   # Launch EC2 instance with GPU support
   # Install Docker and Docker Compose
   # Deploy using docker-compose
   ```

2. **ECS with Fargate**
   ```yaml
   # Use the provided Dockerfile
   # Configure ECS task definition
   # Set up load balancer
   ```

### Google Cloud Deployment

1. **Cloud Run**
   ```bash
   # Build and push Docker image
   gcloud builds submit --tag gcr.io/PROJECT-ID/translate-ai
   
   # Deploy to Cloud Run
   gcloud run deploy --image gcr.io/PROJECT-ID/translate-ai
   ```

2. **Compute Engine**
   ```bash
   # Create VM instance
   # Install Docker
   # Deploy using docker-compose
   ```

### Azure Deployment

1. **Container Instances**
   ```bash
   # Build and push to Azure Container Registry
   # Deploy using Azure Container Instances
   ```

2. **App Service**
   ```bash
   # Deploy as a web app
   # Configure custom Docker image
   ```

## 🔍 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify API keys are correctly set
   - Check API key permissions
   - Ensure sufficient API quota

2. **Audio Processing Issues**
   - Check FFmpeg installation
   - Verify audio file formats
   - Monitor system resources

3. **OCR Issues**
   - Ensure proper font files are available
   - Check image quality and resolution
   - Verify language support

4. **Performance Issues**
   - Monitor CPU and memory usage
   - Check disk space
   - Optimize video processing parameters

### Logs

Check logs in the following locations:
- Application logs: `logs/` directory
- Docker logs: `docker-compose logs`
- System logs: `/var/log/`

## 📈 Scaling

### Horizontal Scaling

1. **Load Balancer**: Use nginx or cloud load balancer
2. **Multiple Instances**: Deploy multiple container instances
3. **Database**: Use external database for job management
4. **Queue**: Use Redis or RabbitMQ for job queuing

### Vertical Scaling

1. **GPU**: Add GPU support for faster processing
2. **Memory**: Increase RAM for large video processing
3. **Storage**: Use fast SSD storage
4. **CPU**: Use high-performance CPUs

## 🔄 Updates

### Rolling Updates

1. **Docker**: Use rolling updates with Docker Compose
2. **Blue-Green**: Implement blue-green deployment
3. **Canary**: Use canary releases for testing

### Backup

1. **Data**: Backup user data and processed videos
2. **Configuration**: Backup configuration files
3. **Database**: Regular database backups

## 📞 Support

For deployment issues:
1. Check the logs
2. Review this documentation
3. Check system requirements
4. Contact support team

## 🎯 Performance Benchmarks

### Expected Performance

- **Video Processing**: 1-2 minutes per minute of video
- **Audio Separation**: 30-60 seconds per minute of audio
- **OCR Processing**: 10-20 seconds per frame
- **Translation**: 5-10 seconds per text block

### Resource Requirements

- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores, GPU
- **Production**: 16GB RAM, 8 CPU cores, GPU, SSD storage
