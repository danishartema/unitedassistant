# Unified Assistant - Hugging Face Spaces Deployment

## 🚀 Quick Deploy to Hugging Face Spaces

This project is configured for easy deployment to Hugging Face Spaces with Supabase database integration.

## 📋 Prerequisites

1. **Hugging Face Account**: Create an account at [huggingface.co](https://huggingface.co)
2. **Supabase Project**: Create a project at [supabase.com](https://supabase.com)
3. **OpenAI API Key**: Get your API key from [platform.openai.com](https://platform.openai.com/api-keys)

## 🚀 Deploy to Hugging Face Spaces

### Option 1: Deploy via Hugging Face Web Interface

1. **Go to [Hugging Face Spaces](https://huggingface.co/spaces)**
2. **Click "Create new Space"**
3. **Choose settings:**
   - **Owner**: Your username
   - **Space name**: `unified-assistant` (or your preferred name)
   - **Space SDK**: `Docker`
   - **License**: Choose appropriate license
   - **Visibility**: Public or Private

4. **Upload your code:**
   - Clone this repository
   - Upload all files to your new Space

5. **Configure Environment Variables:**
   - Go to your Space → Settings → Repository secrets
   - Add the following secrets:

```
SUPABASE_DB_URL=postgresql+asyncpg://postgres:WiHcl5UgLmP1rLGZ@nqdhdqdtpvqfecbsjaar.supabase.co:5432/postgres
ENVIRONMENT=production
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=Qee7sf39ipUhe_1pKCnsMLPU-aanOt-xs0gx3bsBuFo
DEBUG=false
HOST=0.0.0.0
PORT=7860
```

### Option 2: Deploy via Git

1. **Fork this repository** to your GitHub account
2. **Create a new Space** on Hugging Face
3. **Connect your GitHub repository**
4. **Configure environment variables** as shown above

## 🔧 Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SUPABASE_DB_URL` | PostgreSQL connection string | ✅ Yes | `postgresql+asyncpg://postgres:password@host:5432/postgres` |
| `ENVIRONMENT` | Set to "production" | ✅ Yes | `production` |
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ Yes | `sk-...` |
| `SECRET_KEY` | Secret key for JWT tokens | ✅ Yes | `your-secret-key` |
| `DEBUG` | Debug mode | Optional | `false` |
| `HOST` | Host binding | Optional | `0.0.0.0` |
| `PORT` | Port number | Optional | `7860` |

## 🐳 Docker Configuration

The project includes a `Dockerfile` optimized for Hugging Face Spaces:

- **Base Image**: Python 3.11-slim
- **Port**: 7860 (Hugging Face Spaces standard)
- **Health Check**: Automatic health monitoring
- **Environment**: Production-ready configuration

## 📊 Monitoring Your Deployment

### Check Deployment Status

1. **Visit your Space URL**: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`
2. **Check logs**: Go to your Space → Settings → Logs
3. **Health endpoint**: Visit `/health` on your deployed app

### Expected Logs on Startup

```
🔧 Database Configuration:
   Environment: production
   Is Production: True
   Is Hugging Face Deployment: True
   Supabase DB URL set: Yes
   Effective Database URL: postgresql+asyncpg://postgres:***@nqdhdqdtpvqfecbsjaar.supabase.co:5432/postgres
   Database Type: PostgreSQL/Supabase
✅ Using PostgreSQL/Supabase configuration
✅ Database tables created successfully
🚀 Application startup complete
```

## 🔍 Testing Your Deployment

### 1. Health Check
```bash
curl https://YOUR_SPACE_NAME.hf.space/health
```

### 2. API Documentation
Visit: `https://YOUR_SPACE_NAME.hf.space/docs`

### 3. Root Endpoint
Visit: `https://YOUR_SPACE_NAME.hf.space/`

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check your `SUPABASE_DB_URL` is correct
   - Verify your Supabase project is active
   - Check Hugging Face Space logs for errors

2. **Environment Variables Not Set**
   - Go to Space Settings → Repository secrets
   - Add all required environment variables
   - Redeploy your Space

3. **Port Issues**
   - Hugging Face Spaces uses port 7860 by default
   - The Dockerfile is already configured correctly

4. **Build Failures**
   - Check the `requirements.txt` file is present
   - Verify all dependencies are compatible
   - Check build logs in your Space

### Debug Commands

```bash
# Check environment variables
python debug_env.py

# Test database connection
python test_database_config.py

# Quick connection test
python quick_test.py
```

## 📈 Performance Optimization

### For Production Deployment

1. **Database Connection Pooling**: Already configured for Supabase
2. **Async Operations**: All database operations are async
3. **Caching**: Consider adding Redis for session caching
4. **Monitoring**: Use Hugging Face Space logs for monitoring

## 🔒 Security Notes

- ✅ Never commit `.env` files to version control
- ✅ Use Hugging Face secrets for all sensitive data
- ✅ Supabase automatically handles SSL connections
- ✅ Database credentials are encrypted in transit
- ✅ JWT tokens are properly secured

## 📞 Support

If you encounter issues:

1. **Check Hugging Face Space logs**
2. **Verify environment variables**
3. **Test database connection locally first**
4. **Review the troubleshooting section above**

## 🎉 Success!

Once deployed, your Unified Assistant will be available at:
`https://YOUR_SPACE_NAME.hf.space`

The application will automatically:
- ✅ Connect to your Supabase database
- ✅ Create all necessary tables
- ✅ Start the FastAPI server
- ✅ Provide API documentation at `/docs`
- ✅ Handle authentication and user management
- ✅ Support all AI assistant features

---

**Happy Deploying! 🚀** 