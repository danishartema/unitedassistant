# Hugging Face Spaces Deployment Guide

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
- Connect to Supabase on startup
- Create all necessary database tables
- Start the FastAPI server

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_DB_URL` | PostgreSQL connection string | ✅ Yes |
| `ENVIRONMENT` | Set to "production" | ✅ Yes |
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ Yes |
| `SECRET_KEY` | Secret key for JWT tokens | ✅ Yes |
| `HF_API_TOKEN` | Hugging Face API token | Optional |

## Troubleshooting

### Database Connection Issues

If you see `sqlite3.OperationalError: unable to open database file`:

1. **Check Environment Variables**: Ensure `SUPABASE_DB_URL` is set correctly
2. **Verify Supabase**: Make sure your Supabase project is active
3. **Check Network**: Ensure Hugging Face can reach your Supabase instance

### Common Error Messages

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

## Monitoring

Check the Hugging Face Spaces logs for:
- ✅ Database connection successful
- ✅ Database tables created successfully
- ✅ Application startup complete

## Security Notes

- Never commit `.env` files to version control
- Use Hugging Face secrets for all sensitive data
- Supabase automatically handles SSL connections
- Database credentials are encrypted in transit

## Support

If you encounter issues:
1. Check the logs in Hugging Face Spaces
2. Verify your Supabase configuration
3. Test the database connection locally first
4. Review the `SUPABASE_SETUP.md` guide for detailed instructions 