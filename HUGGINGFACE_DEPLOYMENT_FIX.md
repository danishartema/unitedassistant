# Hugging Face Deployment Fix Guide

## Problem
The application is failing to start in Hugging Face deployment with the error:
```
sqlite3.OperationalError: unable to open database file
```

This happens because SQLite cannot create or access database files in the containerized Hugging Face environment.

## Solution
The application has been updated to automatically detect Hugging Face deployment and require Supabase database configuration.

## Quick Fix Steps

### 1. Set Environment Variables in Hugging Face Space

Go to your Hugging Face Space and set these **REQUIRED** environment variables:

1. **SUPABASE_DB_URL** (Required)
   - Get this from your Supabase project dashboard
   - Go to Settings → Database → Connection string
   - Copy the URI and add `+asyncpg` after `postgresql`
   - Format: `postgresql+asyncpg://postgres:[password]@[host]:5432/postgres`

2. **ENVIRONMENT** (Required)
   - Set to: `production`

3. **Other Required Variables**
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `SECRET_KEY` - A secure secret key for JWT tokens

### 2. Create Supabase Project (if you don't have one)

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Choose organization and project name
5. Set a strong database password
6. Choose a region close to your users
7. Wait for setup to complete (2-3 minutes)

### 3. Get Database Connection String

1. In your Supabase dashboard, go to **Settings** → **Database**
2. Find the **Connection string** section
3. Copy the **URI** (it looks like: `postgresql://postgres:[password]@[host]:5432/postgres`)
4. Add `+asyncpg` after `postgresql` to make it: `postgresql+asyncpg://postgres:[password]@[host]:5432/postgres`

### 4. Set Hugging Face Space Secrets

In your Hugging Face Space:
1. Go to **Settings** → **Repository secrets**
2. Add these secrets:

```
SUPABASE_DB_URL=postgresql+asyncpg://postgres:[your_password]@[your_host]:5432/postgres
ENVIRONMENT=production
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_super_secret_key_here
```

## What Changed in the Code

### 1. Enhanced Environment Detection
The application now automatically detects Hugging Face deployment environment and requires Supabase.

### 2. Better Error Messages
Clear error messages will guide you to set the required environment variables.

### 3. Automatic Database Type Detection
The application automatically switches between SQLite (development) and PostgreSQL/Supabase (production).

## Verification

After setting the environment variables, the application will:

1. ✅ Detect Hugging Face deployment environment
2. ✅ Use Supabase database connection
3. ✅ Create all necessary tables automatically
4. ✅ Start successfully without SQLite errors

## Troubleshooting

### Error: "SUPABASE_DB_URL environment variable is required"
- **Solution**: Set the `SUPABASE_DB_URL` environment variable in your Hugging Face Space secrets

### Error: "unable to open database file"
- **Solution**: This error should no longer occur with the updated code, but if it does, ensure `SUPABASE_DB_URL` is set

### Connection Issues
- Verify the Supabase connection string format
- Check if the database password is correct
- Ensure the host is accessible from Hugging Face

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SUPABASE_DB_URL` | PostgreSQL connection string | ✅ Yes | `postgresql+asyncpg://postgres:password@host:5432/postgres` |
| `ENVIRONMENT` | Set to "production" | ✅ Yes | `production` |
| `OPENAI_API_KEY` | OpenAI API key | ✅ Yes | `sk-...` |
| `SECRET_KEY` | JWT secret key | ✅ Yes | `your-secret-key` |

## Security Notes

- ✅ Never commit database credentials to version control
- ✅ Use Hugging Face secrets for production
- ✅ Supabase automatically handles SSL connections
- ✅ Database is automatically backed up

## Migration from SQLite

The application automatically detects the environment and switches to Supabase when:
- `ENVIRONMENT=production` is set
- `SUPABASE_DB_URL` is provided
- Running in Hugging Face deployment environment

No code changes needed - it's handled automatically by the configuration system. 