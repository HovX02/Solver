<p align="center">
  <a href="./README.md"><b>English</b></a> | <a href="./README.id.md">Bahasa Indonesia</a>
</p>

# Turnstile, cf_clearance, Recaptcha & AWS WAF Token Solver

<img width="830" height="494" alt="Screenshot 2026-05-26 045641" src="https://github.com/user-attachments/assets/ee5e5f19-6dfc-4221-aba3-3daa9447df18" />

> ✅ **Status: Confirmed working.** This project is regularly tested and updated.

> Inspired by:
[SGAHSCAJASCJ/Turnstile-Solver](https://github.com/SGAHSCAJASCJ/Turnstile-Solver) (Turnstile) — [verfired8975/recaptcha-v3-solver](https://github.com/verfired8975/recaptcha-v3-solver) (Recaptcha V3)

A high-performance solver for Cloudflare Turnstile CAPTCHA, cf_clearance, Recaptcha V3, and AWS WAF Tokens, built with **FastAPI** and asynchronous browser technology (**Camoufox**), providing a ready-to-use RESTful API service.

---

## ✨ Key Features

- **4 Solver Endpoints**: `/turnstile`, `/clearance`, `/aws-token`, `/recaptchaV3`
- **Auto Install & Fetch**: Python dependencies and Camoufox are installed automatically on first run.
- **Configuration via `config.json`**: All settings can be configured via file or interactive prompt.
- **Worker Mode (On-Demand Browser)**: When enabled (`WORKER_MODE=true`), browser instance is only launched when a request arrives and automatically shut down when idle to conserve RAM/CPU.
- **Proxy Rotation**: Per-browser-instance proxy support with round-robin rotation.
- **Forced Cleanup**: Periodic forced memory cleanup for server stability on low-RAM VPS.
- **Headless & GUI Mode**: Compatible for running via Terminal/VPS (`xvfb`) or RDP.

---

## 🚀 Installation & Setup (For New VPS)

**Note:** *Repeated installation issues (`camoufox fetch` errors or browser dependency issues) on a new VPS are usually caused by incomplete browser cache data.* The latest script version has fixed automatic camoufox version detection.

The **recommended steps** on a new Linux VPS (Ubuntu/Debian):

```bash
# 1. Update system & install browser system dependencies
sudo apt update -y && sudo apt upgrade -y
sudo apt install xvfb -y
sudo apt install libasound2 -y
sudo apt install python3 -y
sudo apt install python3-pip -y
sudo apt install python3-venv -y

# 2. Clone Repository
git clone https://github.com/najibyahya/Turnstile-Solver
cd Turnstile-Solver

# 3. Create & activate virtual environment (highly recommended)
python3 -m venv venv
source venv/bin/activate

# 4. Install base Python dependencies
pip install fastapi==0.95.2 uvicorn "camoufox[fetch]" loguru psutil playwright

# 5. FETCH & INSTALL DEPENDENCIES MANUALLY (DO THIS ONCE)
# This prevents "Version information not found" & "browser dependencies" issues
python3 -m camoufox fetch
python3 -m playwright install-deps
playwright install

# 6. Run the server
python3 api_server.py
```

> **INFO:** If using headless mode (false):
> ```bash
> source venv/bin/activate
> xvfb-run -a python3 api_server.py
> ```

---

## 🐳 Docker Deployment

You can run Turnstile Solver using Docker or Docker Compose without installing Python or browser dependencies on your host.

### Using Docker Compose (Recommended)
```bash
docker-compose up -d --build
```

### Using Docker CLI
```bash
# Build the image
docker build -t turnstile-solver .

# Run container with environment variables
docker run -d \
  -p 8000:8000 \
  -e PROXY_SUPPORT=true \
  -e PROXIES="http://user:pass@1.2.3.4:8080, socks5://5.6.7.8:1080" \
  --name turnstile-solver \
  turnstile-solver
```

---

## ⚙️ Configuration & Environment Variables

All settings in `config.json` can be overridden via environment variables:

| Parameter | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `headless` | `HEADLESS` | bool | `true` | Browser runs without a GUI |
| `thread` | `THREAD` | int | `2` | Number of browser instances |
| `page_count` | `PAGE_COUNT` | int | `1` | Number of tabs/pages per browser |
| `proxy_support` | `PROXY_SUPPORT` | bool | `false` | Enable proxy support (automatically enabled if `PROXIES`/`PROXY` is set) |
| `proxy_file` | `PROXY_FILE` | str | `proxies.txt` | File path for proxy list |
| `host` | `HOST` | str | `0.0.0.0` | Host address |
| `port` | `PORT` | int | `8000` | Port number |
| `debug` | `DEBUG` | bool | `false` | Enable debug logging |
| `cleanup_interval_minutes` | `CLEANUP_INTERVAL_MINUTES` | int | `10` | Interval for refreshing/cleaning up browser memory |
| `worker_mode` | `WORKER_MODE` | bool | `false` | Run browser on-demand (start on request, close when idle) |
| `idle_timeout` | `IDLE_TIMEOUT` | int | `10` | Idle timeout in seconds before closing browser in worker mode |

On first run in an interactive shell, the script will create a `config.json` file. You can edit it directly:

```json
{
    "headless":      true,
    "thread":        2,
    "page_count":    1,
    "proxy_support": false,
    "proxy_file":    "proxies.txt",
    "host":          "0.0.0.0",
    "port":          8000,
    "debug":         false,
    "cleanup_interval_minutes": 10,
    "worker_mode":   false,
    "idle_timeout":  10
}
```

---

## 🌐 Proxy Configuration

Proxies can be supplied via environment variables (`PROXIES` or `PROXY`) or added to `proxies.txt`.

### 1. Via Environment Variable
Separate multiple proxies using commas, newlines, or spaces:
```bash
export PROXIES="http://user:pass@10.0.0.1:8080, socks5://10.0.0.2:1080, 10.0.0.3:3128"
```

### 2. Via `proxies.txt`
Add proxies to `proxies.txt` (one proxy per line).

### Supported Formats
Proxies are automatically normalized (if scheme is missing, `http://` is prepended):
```text
http://ip:port
http://user:pass@ip:port
socks5://user:pass@ip:port
ip:port
user:pass@ip:port
```

## 📖 API Endpoint Documentation

This solver works asynchronously (creating a task queue). Each endpoint blocks until a token is successfully retrieved or returned with a failed status.

### 1. Task Creation Endpoints

| Task | Endpoint | Required Parameters |
|---|---|---|
| Turnstile | `GET /turnstile` | `url` (Target URL), `sitekey` (Turnstile Key) |
| cf_clearance | `GET /clearance` | `url` (Target URL), `timeout` (optional, seconds) |
| AWS WAF | `GET /aws-token` | `url` (Target URL), `timeout` (optional, seconds) |
| reCAPTCHA v3 | `GET or POST` to `/recaptchaV3` | `url` / `domain` (Target URL), `sitekey` / `siteKey` (reCAPTCHA Key), `action` (optional, default: `submit`) |

#### 🌐 Example HTTP Requests (cURL) for Task Creation

##### A. Cloudflare Turnstile (`GET /turnstile`)
```bash
curl -X GET "http://127.0.0.1:8001/turnstile?url=https://target.cc/&sitekey=0x4AAAAAxxxxxxxxETLYn"
```

##### B. Cloudflare cf_clearance (`GET /clearance`)
```bash
curl -X GET "http://127.0.0.1:8001/clearance?url=https://target.cc/&timeout=30"
```

##### C. AWS WAF Token (`GET /aws-token`)
```bash
curl -X GET "http://127.0.0.1:8001/aws-token?url=https://target.cc/waitlist&timeout=30"
```

##### D. Google reCAPTCHA v3 (`GET` or `POST` to `/recaptchaV3`)
* **Using HTTP GET:**
```bash
curl -X GET "http://127.0.0.1:8001/recaptchaV3?url=https://target.cc&sitekey=6Ldqxxxxxxxxxxxxxx19Tpa1XsSZfIW&action=submit"
```
* **Using HTTP POST (JSON Body):**
```bash
curl -X POST "http://127.0.0.1:8001/recaptchaV3" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://target.cc", "sitekey": "6Ldqxxxxxxxxxxxxxx19Tpa1XsSZfIW", "action": "submit"}'
```

**Example Successful Task Creation Response (202 Accepted):**
```json
{
  "task_id": "8a31e3d4-b41e-450f-a63c-94cc8193eb41",
  "status": "accepted"
}
```

---

### 2. Result Polling Endpoint (`GET /result?id=<task_id>`)

You must **poll** this endpoint at least every 1 second using the `task_id` from the task creation above, until `status` is either `success` or `error`.

**Example Polling Request (cURL):**
```bash
curl -X GET "http://127.0.0.1:8001/result?id=8a31e3d4-b41e-450f-a63c-94cc8193eb41"
```

**Example Successful Response from Turnstile / reCAPTCHA v3:**
```json
{
  "status": "success",
  "elapsed_time": 2.431,
  "value": "0.AbCdEf..."
}
```

**Example Successful Response from cf_clearance / AWS WAF:**
```json
{
  "status": "success",
  "elapsed_time": 3.102,
  "user_agent": "Mozilla/5.0 ...",
  "cookies": "cf_clearance=abcdef...;",
  "cf_clearance": "abcdef..."
}
```

**HTTP Status Codes:**
- `200` = Success.
- `202` = Still processing, keep polling `GET /result`.
- `404` = Task ID expired or not found.
- `408` = Timeout (> 5 minutes elapsed).
- `500`/`422` = Internal error or CAPTCHA solving failed.

---

## 📄 License
MIT License — See [LICENSE](LICENSE).

<div align="center">
<b>⚡ High Performance &nbsp;|&nbsp; 🚀 Multi Solver</b>
</div>
