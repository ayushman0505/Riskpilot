# Beginner's Guide to Deploying RiskPilot on Render.com

This guide is designed for absolute beginners. We will use **Render.com** because it is free and allows us to deploy both the Backend (API) and Frontend (Streamlit) in one go using the `render.yaml` file I created for you.

## Prerequisites
1.  **GitHub Account**: You must have your code pushed to GitHub (we did this in step 180).
2.  **Render Account**: Sign up at [render.com](https://render.com/) (Login with GitHub is easiest).
3.  **API Keys**: Have your `.env` file open or keys handy (`SUPABASE_URL`, `SUPABASE_KEY`, `GROQ_API_KEY`).

---

## Step 1: Push your latest code
Make sure the `render.yaml` file is in your GitHub repository.
If you haven't pushed it yet, run this in your terminal:
```bash
git add render.yaml
git commit -m "Add render blueprint"
git push origin main
```

## Step 2: Create "Blueprint" on Render
1.  Go to the [Render Dashboard](https://dashboard.render.com).
2.  Click the **"New +"** button (top right).
3.  Select **"Blueprint"**.
4.  Connect your GitHub repository (e.g., `ayushman0505/Riskpilot`).
5.  Render will automatically find the `render.yaml` file.

## Step 2.5: Get Free Redis (Crucial!)
Since your app is now in the cloud, it can't use the Redis on your laptop. You need a cloud Redis.

1.  Go to [Redis Cloud](https://redis.com/try-free/) and sign up (Free 30MB tier).
2.  Create a **New Subscription** (Select "Fixed" -> "Free" -> "AWS/Google" typically).
3.  Create a **Database**.
4.  Copy the **Public Endpoint** (e.g., `redis-12345.c1.us-east-1-2.ec2.cloud.redislabs.com:12345`).
5.  Copy the **Password**.
6.  **Construct your URL:** `redis://default:YOUR_PASSWORD@YOUR_ENDPOINT`
    *   *Example:* `redis://default:xyZ123@redis-12345...com:10000`
    *   Save this URL!

## Step 3: Configure Variables
Render will ask you to fill in the "Environment Variables" defined in the YAML file.
You will see input boxes for these. **Copy-paste them from your `.env` file** (and the Redis URL from above):

*   `SUPABASE_URL`: Paste your Supabase URL.
*   `SUPABASE_KEY`: Paste your `service_role` key.
*   `GROQ_API_KEY`: Paste your Groq API key.
*   `REDIS_URL`: Paste the **Redis Cloud URL** you just made (Step 2.5).


## Step 4: Deploy
1.  Click **"Apply"** or **"Create Blueprint"**.
2.  Render will now create TWO services for you:
    *   `riskpilot-backend`: The AI and Database logic.
    *   `riskpilot-frontend`: The Streamlit Dashboard.
3.  Wait about 3-5 minutes. You will see logs scrolling.

## Step 5: Access Your App
Once the status says **Live** (green dot):
1.  Click on the `riskpilot-frontend` service.
2.  Click the URL at the top (it will look like `https://riskpilot-frontend.onrender.com`).
3.  **Success!** Your app is now on the internet.

---

## Common Issues & Fixes

**Issue: "Deploy Failed"**
*   **Fix:** Click on the failed service to see the logs.
*   If it says `ModuleNotFoundError`, check that your file structure on GitHub matches your local computer.
*   If it says `Memory Limit Exceeded`, restart the deploy (the free tier is 512MB, sometimes it hiccups installing libraries).

**Issue: "Frontend cannot connect to Backend"**
*   **Fix:** Ensure the backend service is actually "Live". The `render.yaml` automatically links them, so this typically just means the backend is still booting up (it takes a minute longer than the frontend).
