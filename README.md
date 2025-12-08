# NETCONF API Gateway

## Overview
A Python-based REST API gateway for multi-vendor NETCONF routers (Alcatel, Juniper), with dynamic proxy support and normalized endpoints. Credentials, DB access, and proxy mappings are managed securely via config files and environment variables.

## Features
- Multi-vendor NETCONF support (Alcatel, Juniper)
- Normalized REST API endpoints (e.g., `/{device}/get-config`)
- PostgreSQL integration for router metadata
- Dynamic proxy client logic based on router owner, loaded from config/proxy_map.json
- Credentials managed via `.env` and `decouple`
- Dockerized for deployment

## Project Structure
```
app/
   api/        # REST API endpoints
   clients/    # NETCONF clients, proxy logic, factories
   db/         # DB models and access
   main.py     # App entrypoint
config/
   proxy_map.json # Proxy owner-to-host mapping (dynamic, runtime loaded)
.env.example  # Environment variable template
requirements.txt
Dockerfile
README.md
```

## Setup
1. Clone the repo
2. Copy `.env.example` to `.env` and fill in values
3. Edit `config/proxy_map.json` to define your proxy owner-to-host mappings (see example in file)
3. Create and activate a virtual environment:
   ```powershell
   python -m venv venv; .\venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Run the app:
   ```powershell
   uvicorn app.main:app --reload
   ```

## Docker Deployment
```
docker build -t netconf-gateway .
docker run -p 8000:8000 --env-file .env -v %cd%/config:/app/config netconf-gateway
```
> **Note:** The `config/proxy_map.json` file is mounted into the container for dynamic proxy mapping. Adjust the volume path as needed for your environment.

## API Usage
- All endpoints are normalized: `/{device}/get-config`, `/{device}/set-config`, etc.
- The gateway uses DB info to select the correct NETCONF client and proxy, with proxy mapping loaded from `config/proxy_map.json`.

## Extending
- Add new vendor clients in `app/clients/`
- Update proxy mapping in `config/proxy_map.json` (no code changes needed)
- Add new endpoints in `app/api/`

## License
MIT
