# Supabase Setup Guide for Hugging Face Deployment

## Why Supabase?

- **Persistent Database**: Data survives container restarts
- **Production Ready**: Scalable PostgreSQL database
- **Free Tier**: Generous free tier for development
- **Easy Setup**: Managed PostgreSQL with automatic backups
- **Real-time**: Built-in real-time subscriptions (if needed)

## Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Choose organization and project name
5. Set a strong database password
6. Choose a region close to your users
7. Wait for setup to complete (2-3 minutes)

## Step 2: Get Database Connection Details

1. In your Supabase dashboard, go to **Settings** → **Database**
2. Find the **Connection string** section
3. Copy the **URI** (it looks like: `postgresql://postgres:[password]@[host]:5432/postgres`)

## Step 3: Configure Hugging Face Spaces

### Option A: Using Hugging Face Spaces Environment Variables

1. Go to your Hugging Face Space
2. Click **Settings** → **Repository secrets**
3. Add these secrets:

```
SUPABASE_DB_URL=postgresql+asyncpg://postgres:[password]@[host]:5432/postgres
ENVIRONMENT=production
```

### Option B: Using .env file (for local testing)

Create a `.env` file in your project root:

```env
# Supabase Database
SUPABASE_DB_URL=postgresql+asyncpg://postgres:[password]@[host]:5432/postgres
ENVIRONMENT=production

# Other settings
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=your_secret_key_here
```

## Step 4: Database Schema Setup

The application will automatically create all tables on startup. However, if you want to use Alembic for migrations:

1. Install Alembic: `pip install alembic`
2. Initialize: `alembic init alembic`
3. Create migration: `alembic revision --autogenerate -m "Initial migration"`
4. Apply: `alembic upgrade head`

## Step 5: Test the Connection

The application will automatically:
- Connect to Supabase on startup
- Create all necessary tables
- Log the connection status

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_DB_URL` | PostgreSQL connection string | Yes (for production) |
| `ENVIRONMENT` | Set to "production" for Supabase | Yes |
| `DATABASE_URL` | Fallback SQLite URL | No (for development) |

## Troubleshooting

### Connection Issues
- Verify the connection string format
- Check if the database password is correct
- Ensure the host is accessible from Hugging Face

### Permission Issues
- Supabase automatically creates the `postgres` user with full permissions
- No additional setup needed for basic operations

### Performance Issues
- The connection pool is optimized for Hugging Face Spaces
- Pool size reduced to 5 connections to avoid limits

## Security Notes

- Never commit database credentials to version control
- Use Hugging Face secrets for production
- Supabase automatically handles SSL connections
- Database is automatically backed up

## Migration from SQLite

The application automatically detects the environment and switches to Supabase when:
- `ENVIRONMENT=production` is set
- `SUPABASE_DB_URL` is provided

No code changes needed - it's handled automatically by the configuration system. 