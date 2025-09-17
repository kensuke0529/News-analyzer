# Vercel Deployment Guide for AI News Analyst

This guide covers deploying the AI News Analyst Flask app to Vercel.

## Prerequisites

1. Vercel account (free tier available)
2. OpenAI API key
3. Git repository (GitHub, GitLab, or Bitbucket)

## Required Environment Variables

Set these in your Vercel project settings:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Deployment Steps

### 1. Prepare Your Repository

The following files have been created/updated for Vercel deployment:

- `vercel.json` - Vercel configuration
- `wsgi.py` - WSGI entry point
- `requirements.txt` - Updated dependencies
- `rag/embedding.py` - Modified for serverless environment

### 2. Deploy to Vercel

#### Option A: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project directory
vercel

# Follow the prompts to configure your project
```

#### Option B: GitHub Integration
1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Vercel will auto-detect it's a Python project
6. Add your environment variables in project settings
7. Deploy!

### 3. Configure Environment Variables

In your Vercel dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add: `OPENAI_API_KEY` with your OpenAI API key
4. Redeploy if needed

## Important Notes

### Serverless Limitations

1. **Vector Store**: ChromaDB uses in-memory storage on Vercel (no persistent files)
2. **Session Storage**: Chat sessions reset on cold starts
3. **Cold Starts**: First request may be slower due to initialization
4. **Memory**: Limited to 1GB on free tier

### Performance Considerations

- Vector store initializes on each cold start
- Consider using a cloud vector database for production
- Monitor memory usage with large datasets

### Data Files

Ensure your `data/` directory is included in the deployment:
- `data/mit_ai_news.json`
- `data/combined-week-*.json` (if any)
- `data/week-*.json` (if any)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all Python files are in the correct directory structure
2. **Memory Issues**: Reduce dataset size or upgrade Vercel plan
3. **Cold Start Timeouts**: Consider using Vercel Pro for longer timeouts
4. **Vector Store Errors**: Check that data files exist and are valid JSON

### Debugging

Check Vercel function logs in the dashboard for detailed error messages.

## Production Recommendations

For a production deployment, consider:

1. **Database**: Use a proper database for session storage
2. **Vector Store**: Use a cloud vector database (Pinecone, Weaviate, etc.)
3. **Caching**: Implement Redis for better performance
4. **Monitoring**: Add logging and monitoring
5. **CDN**: Use Vercel's CDN for static assets

## Support

If you encounter issues:
1. Check the Vercel function logs
2. Verify environment variables are set correctly
3. Ensure all dependencies are in requirements.txt
4. Test locally with `vercel dev` before deploying
