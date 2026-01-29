# How to Run Redis Locally on Windows

Since you are strictly on Windows, here are the 3 best ways to run Redis (ordered by recommendation).

## Option 1: Docker (Recommended)
If you have Docker Desktop installed, this is the cleanest method. It keeps your PC clean.

1.  **Open Terminal (cmd/powershell)**
2.  Run this command:
    ```bash
    docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
    ```
3.  **Verify**:
    *   Redis is running on `localhost:6379`.
    *   GUI Dashboard available at `http://localhost:8001` (Bonus!).

---

## Option 2: Memurai (Native Windows)
If you **don't** use Docker, Memurai is the best "native" Redis alternative for Windows developers.

1.  Go to [memurai.com/get-memurai](https://www.memurai.com/get-memurai).
2.  Download the **Developer Edition** (Free).
3.  Install the MSI.
4.  It runs automatically as a Windows Service.
5.  **Verify**: Open cmd and type `redis-cli ping` (if you installed the tools) or just assume it's running on port 6379.

---

## Option 3: WSL (Windows Subsystem for Linux)
If you use Ubuntu on Windows.

1.  Open your Ubuntu terminal.
2.  Run:
    ```bash
    sudo apt-get update
    sudo apt-get install redis-server
    sudo service redis-server start
    ```

---

## Testing Your Connection
Once installed, you can test it with Python in your `risk` folder:

1.  Make sure your `venv` is active.
2.  Run this quick test script:
    ```python
    import redis
    try:
        r = redis.from_url("redis://localhost:6379")
        r.ping()
        print("✅ Redis is Online!")
    except Exception as e:
        print("❌ Redis is Offline. Start it first.")
    ```
