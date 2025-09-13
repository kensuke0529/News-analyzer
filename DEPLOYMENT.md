# Deployment Guide for AI News Analyst

This guide will help you deploy the AI News Analyst application to Render.

## Prerequisites

1. **OpenAI API Key**: You need an OpenAI API key for the AI functionality
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository contains all the necessary files:
- `app.py` (main Flask application)
- `requirements.txt` (Python dependencies)
- `render.yaml` (Render configuration)
- `start.sh` (startup script)
- `Procfile` (alternative deployment method)
- `runtime.txt` (Python version specification)
- `env.example` (environment variables template)

### 2. Set Up Environment Variables

In your Render dashboard, you'll need to set the following environment variable:

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### 3. Deploy to Render

#### Option A: Using render.yaml (Recommended)

1. Connect your Git repository to Render
2. Render will automatically detect the `render.yaml` file
3. The deployment will use the configuration specified in the file

#### Option B: Manual Configuration

1. Go to your Render dashboard
2. Click "New +" → "Web Service"
3. Connect your Git repository
4. Configure the service:
   - **Name**: `ai-news-analyst`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start.sh`
   - **Plan**: Free (or upgrade as needed)

### 4. Environment Variables Setup

In the Render dashboard, go to your service's "Environment" tab and add:

```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 5. Deploy

Click "Create Web Service" and wait for the deployment to complete.

## Important Notes

### Database Initialization

The application will automatically initialize the ChromaDB vector store on first startup. This process:
- Loads all available news articles from the `data/` directory
- Creates embeddings using HuggingFace's sentence-transformers
- Stores them in ChromaDB for fast retrieval

### File Persistence

- The ChromaDB database files are stored in the `chroma_langchain_db/` directory
- On Render's free tier, these files are ephemeral and will be recreated on each deployment
- For production use, consider upgrading to a paid plan with persistent storage

### Performance Considerations

- The free tier has limited resources and may have slower startup times
- Vector store initialization can take a few minutes on first deployment
- Consider upgrading to a paid plan for better performance

## Troubleshooting

### Common Issues

1. **Build Failures**: Check that all dependencies in `requirements.txt` are compatible
2. **Startup Timeouts**: The vector store initialization may take time; consider increasing timeout settings
3. **Memory Issues**: The free tier has limited memory; consider upgrading if you encounter issues

### Logs

Check the Render dashboard logs for any error messages during deployment or runtime.

## Alternative Deployment Platforms

This application can also be deployed to:
- **Heroku**: Use the `Procfile` for deployment
- **Railway**: Similar to Render, supports Python applications
- **DigitalOcean App Platform**: Supports Python with similar configuration

## Security Notes

- Never commit your actual API keys to the repository
- Use environment variables for all sensitive configuration
- The `env.example` file shows what environment variables are needed

## Support

If you encounter issues during deployment, check:
1. Render's documentation: [render.com/docs](https://render.com/docs)
2. Application logs in the Render dashboard
3. Ensure all required environment variables are set
