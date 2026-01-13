# 🚀 Render Deployment Instructions

## 📋 Prerequisites
1. GitHub account
2. Render account (free tier available)
3. Supabase account (optional - for advanced features)

## 🔧 Setup Steps

### 1. Fork/Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/coinex-dashboard.git
cd coinex-dashboard
```

### 2. Environment Variables Setup
In Render dashboard, add these environment variables:

**Required:**
- `PORT`: 8080 (Render sets this automatically)

**Optional (for advanced features):**
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `DEEPSEEK_API_KEY`: Your DeepSeek API key

### 3. Deploy to Render
1. Connect your GitHub repository to Render
2. Select "Web Service"
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start.py`
   - **Environment**: Python 3.9+

### 4. Access Your Dashboard
Your dashboard will be available at: `https://your-app-name.onrender.com`

## 🎯 Features
- Real-time CoinEx market monitoring
- Professional trading metrics
- Anomaly detection
- Cross-market analysis
- User-friendly interface

## 🔒 Security Notes
- Never commit API keys or sensitive data
- Use environment variables for all secrets
- Keep .env files local only
