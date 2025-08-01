# Hugging Face Spaces Deployment Guide

## 🚨 Important: Database Configuration Fix

**If you're experiencing `sqlite3.OperationalError: unable to open database file` errors:**

The application has been updated to automatically detect Hugging Face deployment and require Supabase database configuration. SQLite does not work in the containerized Hugging Face environment.

**Quick Fix:** Set the `SUPABASE_DB_URL` environment variable in your Hugging Face Space secrets.

## Quick Setup for Production

### 1. Create Supabase Database

1. Go to [https://supabase.com](https://supabase.com)
2. Create a new project
3. Get your database connection string from Settings → Database

### 2. Configure Hugging Face Spaces

1. Go to your Hugging Face Space
2. Navigate to **Settings** → **Repository secrets**
3. Add these environment variables:

```
SUPABASE_DB_URL=postgresql+asyncpg://postgres:[YOUR_PASSWORD]@[YOUR_HOST]:5432/postgres
ENVIRONMENT=production
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
```

### 3. Deploy

The application will automatically:
- ✅ Detect Hugging Face deployment environment
- ✅ Use Supabase database connection
- ✅ Create all necessary database tables
- ✅ Start the FastAPI server

## Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SUPABASE_DB_URL` | PostgreSQL connection string | ✅ Yes | `postgresql+asyncpg://postgres:password@host:5432/postgres` |
| `ENVIRONMENT` | Set to "production" | ✅ Yes | `production` |
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ Yes | `sk-...` |
| `SECRET_KEY` | Secret key for JWT tokens | ✅ Yes | `your-secret-key` |
| `HF_API_TOKEN` | Hugging Face API token | Optional | `hf_...` |

## What's New in This Update

### 1. Enhanced Environment Detection
- Automatically detects Hugging Face deployment environment
- Requires Supabase configuration in production
- Provides clear error messages for missing configuration

### 2. Better Error Handling
- Clear error messages guide you to set required environment variables
- Automatic fallback detection between SQLite (development) and Supabase (production)
- Improved logging for debugging

### 3. Database Configuration
- Automatic database type detection (SQLite vs PostgreSQL)
- Optimized connection pooling for Hugging Face Spaces
- Better error messages for database connection issues

## Testing Your Configuration

Run the test script to verify your database configuration:

```bash
python test_database_config.py
```

This will check:
- ✅ Environment variable configuration
- ✅ Database connection settings
- ✅ Actual database connectivity

## Troubleshooting

### Database Connection Issues

If you see `sqlite3.OperationalError: unable to open database file`:

1. **Set SUPABASE_DB_URL**: This is now required for Hugging Face deployment
2. **Check Environment Variables**: Ensure `SUPABASE_DB_URL` is set correctly
3. **Verify Supabase**: Make sure your Supabase project is active
4. **Check Network**: Ensure Hugging Face can reach your Supabase instance

### Common Error Messages

```
❌ SUPABASE_DB_URL environment variable is required for Hugging Face deployment
```
→ **Solution**: Set `SUPABASE_DB_URL` environment variable in your Hugging Face Space secrets

```
❌ Failed to create database tables: [Errno 2] No such file or directory
```
→ **Solution**: Set `SUPABASE_DB_URL` environment variable

```
❌ Database connection failed: connection refused
```
→ **Solution**: Check your Supabase connection string

```
❌ Database connection failed: authentication failed
```
→ **Solution**: Verify your Supabase password

## Testing Your Deployment

1. **Health Check**: Visit `/health` endpoint
2. **API Docs**: Visit `/docs` for interactive API documentation
3. **Database Test**: The app will log database connection status on startup
4. **Configuration Test**: Run `python test_database_config.py` locally

## Monitoring

Check the Hugging Face Spaces logs for:
- ✅ Environment detection successful
- ✅ Supabase database configuration detected
- ✅ Database connection successful
- ✅ Database tables created successfully
- ✅ Application startup complete

## Security Notes

- ✅ Never commit `.env` files to version control
- ✅ Use Hugging Face secrets for all sensitive data
- ✅ Supabase automatically handles SSL connections
- ✅ Database credentials are encrypted in transit

## Support

If you encounter issues:
1. Check the logs in Hugging Face Spaces
2. Run `python test_database_config.py` to verify configuration
3. Verify your Supabase configuration
4. Test the database connection locally first
5. Review the `SUPABASE_SETUP.md` guide for detailed instructions
6. Check `HUGGINGFACE_DEPLOYMENT_FIX.md` for specific deployment fixes 