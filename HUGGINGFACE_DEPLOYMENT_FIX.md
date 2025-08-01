# Hugging Face Deployment Database Connection Fix

## 🚨 Current Issue: Network Unreachable Error

Your Hugging Face Space is experiencing a database connection error:
```
ERROR:main:❌ Failed to create database tables: [Errno 101] Network is unreachable
```

This indicates that the Hugging Face container cannot reach your Supabase database.

## 🔧 Quick Fixes

### 1. Check Supabase Project Status

1. **Go to your Supabase Dashboard**: https://supabase.com/dashboard
2. **Check if your project is active** (not paused or suspended)
3. **Verify the project is in the correct region**

### 2. Verify Database Credentials

1. **Go to your Supabase project** → Settings → Database
2. **Copy the connection string** from the "Connection string" section
3. **Update your Hugging Face Space secrets** with the correct connection string

### 3. Check IP Restrictions

1. **Go to your Supabase project** → Settings → Database
2. **Check if there are any IP restrictions** that might block Hugging Face
3. **If IP restrictions exist, either:**
   - Remove them temporarily for testing
   - Add Hugging Face's IP ranges to the allowlist

### 4. Update Environment Variables

In your Hugging Face Space → Settings → Repository secrets, ensure you have:

```
SUPABASE_DB_URL=postgresql+asyncpg://postgres:[YOUR_ACTUAL_PASSWORD]@[YOUR_ACTUAL_HOST]:5432/postgres
ENVIRONMENT=production
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
DEBUG=false
HOST=0.0.0.0
PORT=7860
```

## 🔍 Detailed Troubleshooting

### Step 1: Verify Supabase Project

1. **Access your Supabase dashboard**
2. **Check project status** - ensure it's not paused
3. **Verify the connection string** matches what you're using

### Step 2: Test Connection Locally

Run this test script to verify your connection string works:

```bash
python test_supabase_complete.py
```

### Step 3: Check Hugging Face Space Secrets

1. **Go to your Space** → Settings → Repository secrets
2. **Verify all required variables are set**
3. **Check for any typos in the connection string**

### Step 4: Alternative Connection String Format

Try using this format in your Space secrets:

```
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres?sslmode=require
```

## 🚀 Immediate Solutions

### Solution 1: Create New Supabase Project

1. **Create a new Supabase project** in a different region
2. **Use the new connection string** in your Hugging Face Space secrets
3. **Redeploy your Space**

### Solution 2: Use Supabase Edge Functions

If the direct connection continues to fail, consider using Supabase Edge Functions as a proxy.

### Solution 3: Check Region Compatibility

1. **Verify your Supabase project region**
2. **Some regions may have connectivity issues with Hugging Face**
3. **Try creating a project in a different region** (e.g., US East, Europe)

## 📋 Verification Steps

After making changes:

1. **Redeploy your Hugging Face Space**
2. **Check the logs** for connection success
3. **Visit the health endpoint**: `https://your-space.hf.space/health`
4. **Test the API documentation**: `https://your-space.hf.space/docs`

## 🔗 Useful Links

- **Supabase Dashboard**: https://supabase.com/dashboard
- **Hugging Face Spaces**: https://huggingface.co/spaces
- **Connection String Guide**: https://supabase.com/docs/guides/database/connecting-to-postgres

## 📞 Support

If the issue persists:

1. **Check Supabase status**: https://status.supabase.com
2. **Check Hugging Face status**: https://status.huggingface.co
3. **Review the detailed logs** in your Hugging Face Space
4. **Try the connection test scripts** provided in this repository

## 🎯 Expected Success Logs

When the connection works, you should see:

```
INFO:main:✅ Supabase database configuration detected
INFO:main:✅ Database tables created successfully
INFO:main:🚀 Application startup complete
```

And the health endpoint should return:

```json
{
  "status": "healthy",
  "service": "unified-assistant-backend",
  "environment": "production",
  "database": "connected",
  "is_huggingface_deployment": true
}
``` 