# TranscribeMe Setup Guide 🚀

This guide will help you set up TranscribeMe with your Twilio account and get it running.

## Prerequisites ✅

- [x] Twilio Account (you have your Account SID)
- [ ] Twilio Auth Token
- [ ] Twilio Phone Number
- [ ] OpenAI API Key
- [ ] Public URL for webhooks (ngrok, Railway, Heroku, etc.)

## Step 1: Get Your Twilio Credentials 🔑

### 1.1 Get Auth Token
1. Go to [Twilio Console](https://console.twilio.com/)
2. Copy your **Auth Token** from the dashboard
3. Keep it secure - you'll need it for the `.env` file

### 1.2 Get a Phone Number
1. In Twilio Console, go to **Phone Numbers** > **Manage** > **Buy a number**
2. Choose a number that supports **Voice** capabilities
3. Purchase the number
4. Note the number (format: `+1234567890`)

## Step 2: Get OpenAI API Key 🤖

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)
4. Keep it secure

## Step 3: Configure Environment 🔧

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   # Twilio Configuration
   TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
   TWILIO_AUTH_TOKEN=your_actual_auth_token_here
   TWILIO_PHONE_NUMBER=+1234567890  # Your purchased number
   
   # OpenAI Configuration
   OPENAI_API_KEY=sk-your_actual_openai_key_here
   
   # Service Configuration
   BASE_URL=https://your-public-url.com  # See Step 4
   ```

## Step 4: Set Up Public URL 🌐

You need a public URL for Twilio webhooks. Choose one option:

### Option A: ngrok (Development)
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Start your app
make dev

# In another terminal, expose port 8000
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update BASE_URL in .env
```

### Option B: Railway (Production)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy to Railway
railway login
railway init
railway up

# Get your deployment URL
railway domain
```

### Option C: Heroku (Production)
```bash
# Install Heroku CLI
# Create Heroku app
heroku create your-transcribeme-app

# Set environment variables
heroku config:set TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
heroku config:set TWILIO_AUTH_TOKEN=your_token
heroku config:set TWILIO_PHONE_NUMBER=+1234567890
heroku config:set OPENAI_API_KEY=sk-your_key
heroku config:set BASE_URL=https://your-transcribeme-app.herokuapp.com

# Deploy
git push heroku main
```

## Step 5: Configure Twilio Webhooks 📞

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Phone Numbers** > **Manage** > **Active numbers**
3. Click on your purchased phone number
4. In the **Voice** section, set:
   - **A call comes in**: Webhook
   - **URL**: `https://your-public-url.com/webhook/voice`
   - **HTTP**: POST
5. Click **Save configuration**

## Step 6: Test Your Setup 🧪

### 6.1 Start the Service
```bash
# Install dependencies
make install

# Run tests
make test

# Start the service
make dev
```

### 6.2 Test the API
```bash
# Check health
curl https://your-public-url.com/health

# Check service info
curl https://your-public-url.com/
```

### 6.3 Test Phone Call
1. Call your Twilio phone number from a mobile phone
2. You should hear: "Welcome to TranscribeMe! Please speak your message..."
3. Record a short message
4. You should receive an SMS with a transcript link

## Step 7: Monitor and Debug 🔍

### Check Logs
```bash
# View application logs
tail -f logs/transcribeme.log

# Or if using Railway/Heroku
railway logs  # or heroku logs --tail
```

### Debug Webhooks
1. Go to [Twilio Console](https://console.twilio.com/) > **Monitor** > **Logs** > **Errors**
2. Check for webhook delivery failures
3. Verify your webhook URLs are accessible

### Test Endpoints
```bash
# List recent calls (admin endpoint)
curl https://your-public-url.com/admin/calls
```

## Troubleshooting 🛠️

### Common Issues

**1. "Sorry, this service is only available for mobile phone numbers"**
- Make sure you're calling from a mobile phone
- Check that your number starts with +1, +44, or +61
- Verify the `allowed_country_codes` in config

**2. Webhook not receiving calls**
- Verify your BASE_URL is correct and publicly accessible
- Check Twilio webhook configuration
- Ensure your service is running and accessible

**3. Transcription fails**
- Verify your OpenAI API key is correct
- Check you have sufficient OpenAI credits
- Look for errors in the logs

**4. SMS not sent**
- Verify your Twilio Auth Token is correct
- Check your Twilio account has SMS capabilities
- Ensure the phone number supports SMS

### Getting Help

1. Check the logs first: `make dev` and look for error messages
2. Test individual components: `make test`
3. Verify your environment variables: `cat .env`
4. Check Twilio Console for webhook errors
5. Open an issue on GitHub with logs and error details

## Next Steps 🎯

Once basic functionality is working:

1. **Add Database**: Replace in-memory storage with PostgreSQL/SQLite
2. **Add Authentication**: User accounts and API keys
3. **Add Monitoring**: Error tracking and analytics
4. **Scale Up**: Load balancing and redundancy
5. **Add Features**: Multiple languages, custom formatting, integrations

## Security Notes 🔒

- Never commit your `.env` file to git
- Rotate your API keys regularly
- Use HTTPS for all webhook URLs
- Monitor your usage and costs
- Set up rate limiting for production

---

**Need help?** Open an issue on GitHub or check the troubleshooting section above.