# NETCONF API Gateway

## Overview

A Python-based REST API gateway for multi-vendor NETCONF routers (Alcatel, Juniper, and more), with fully config-driven, model-agnostic logic for DB, client, and proxy selection. All mappings and lookups are controlled by user-editable config files—no code changes needed to add new vendors, proxies, or DB tables. Credentials, DB access, and proxy mappings are managed securely via config files and environment variables. All config file paths can be overridden using environment variables for flexible deployment and onboarding.

## Features
- Multi-vendor NETCONF support (Alcatel, Juniper, SROS, IOS, and more)
- Normalized REST API endpoints (e.g., `/{device}/get-config`)
- PostgreSQL integration for device metadata (table/column fully configurable)
- Dynamic, config-driven client and proxy selection (no hardcoded logic)
- Unified `/devices/{device}/...` API endpoints that dispatch to the correct vendor client at runtime
- All mappings (client, proxy, DB) are controlled by config files in `config/`
- Credentials managed via `.env` and `decouple`
- Dockerized for deployment

## Project Structure

```
app/
   clients/      # NETCONF client implementations
   controllers/  # API controllers (router, interface, protocol, MPLS)
   db/           # DB access (model-agnostic)
   factories/    # Factories for client/proxy creation
   errors.py     # Custom error classes
   logging.py    # Logging setup
   main.py       # App entrypoint
   routes.py     # API route definitions
config/
   client_config.json         # Vendor/version-to-client mapping (dynamic, runtime loaded)
   proxy_config.json          # Proxy mapping (dynamic, runtime loaded)
   db_client_config.json      # Table/column for device lookup (dynamic, runtime loaded)
   logging_config.json        # Logging configuration
   *.example.json             # Example config files for onboarding
.env.example  # Environment variable template
requirements.txt
Dockerfile
README.md
```

## Logging & Error Handling

### Logging

This project uses the standard Python logging system, which can be configured for console, file, or remote logging as needed. All major actions and errors are logged for observability and troubleshooting.

### Error Handling
Custom error classes are defined in `app/errors.py` and used throughout the codebase for clear, actionable error messages. All major external interactions (DB, NETCONF, file, proxy) are wrapped in try/except blocks and log errors before raising exceptions.

## Setup
1. Clone the repo
2. Copy `.env.example` to `.env` and fill in values
3. Edit config files in `config/` to define your mappings:
   - `client_config.json`: Map device vendor/version to NETCONF client class
   - `proxy_config.json`: Map device attributes to proxy hosts
   - `db_client_config.json`: Specify which table/column to use for device lookup
   - See `*.example.json` files for structure and onboarding
   - **Config file paths can be overridden via environment variables:**
     - `DB_CLIENT_CONFIG_PATH` (default: `./config/db_client_config.json`)
   - `PROXY_CONFIG_PATH` (default: `./config/proxy_config.json`)
   - `CLIENT_CONFIG_PATH` (default: `./config/client_config.json`)
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
> **Note:** The `config/` directory is mounted into the container for dynamic mapping. Adjust the volume path as needed for your environment.

## API Usage & Extension
- Unified endpoints are available under `/devices/{device}/...` (for example: `/devices/{device}/show-interface`, `/devices/{device}/protocols/bgp`, `/devices/{device}/firewall/rules`).
- Legacy grouped endpoints remain available under `/routers`, `/interfaces`, `/protocols`, and `/mpls`.
- The gateway uses DB info (from any table/column, as configured) to select the correct NETCONF client and proxy, with all mapping logic loaded from config files in `config/`.
- All controllers, factories, and clients are documented with Google-style docstrings and type hints for clarity and onboarding.
- Logging and error handling are consistent and robust across all modules.

## Extending & Onboarding
- Add new vendor clients in `app/clients/`
- Update or extend mappings in `config/client_config.json`, `config/proxy_config.json`, or `config/db_client_config.json` (no code changes needed)
- Add new endpoints in `app/api/`
- Use `.env.example` as a template for onboarding and environment setup
## Config File Reference

**Config file reference:**

- `config/client_config.json`:
   ```json
   {
      "key_columns": ["vendor", "software_version"],
      "map": {
         "juniper:*": "app.clients.nccclient_juniper.JuniperNCCClient",
         "alcatel:*": "app.clients.nccclient_alcatel.AlcatelNCCClient",
         "ios:*": "app.clients.nccclient_ios.IOSNCCClient"
         // ...
      }
   }
   ```
  
  
- `config/proxy_config.json`:
   ```json
   {
      "key_columns": ["owner"],
      "map": {
         "twtc": "geodeal.com",
         "ctl": "jp1.com",
         "gblx": "nocsup.com",
         "nocsup": "nocsup.com",
         "default": "nocsup.com"
      }
   }
   ```
- `config/db_client_config.json`:
   ```json
   {
      "table": "router",
      "search_column": "router"
   }
   ```



All config files are hot-reloadable and can be changed without code edits. Example files are provided for onboarding. Environment variables can be used to override config file paths for flexible deployment.

## License
MIT : ME I'm The best
