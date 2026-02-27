---
name: setup
description: Set up the Python backtesting environment. Detects OS, creates virtual environment, installs dependencies (openalgo, ta-lib, vectorbt, plotly), and creates the backtesting folder structure.
argument-hint: "[python-version]"
allowed-tools: Bash, Read, Write, Glob, AskUserQuestion
---

Set up the complete Python backtesting environment for VectorBT + OpenAlgo.

## Arguments

- `$0` = Python version (optional, default: `python3`). Examples: `python3.12`, `python3.13`

## Steps

### Step 1: Detect Operating System

Run the following to detect the OS:

```bash
uname -s 2>/dev/null || echo "Windows"
```

Map the result:
- `Darwin` = macOS
- `Linux` = Linux
- `MINGW*` or `CYGWIN*` or `Windows` = Windows

Print the detected OS to the user.

### Step 2: Create Virtual Environment

Create a Python virtual environment in the current working directory:

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
```

If the user specified a Python version argument, use that instead of `python3`:
```bash
$PYTHON_VERSION -m venv venv
```

### Step 3: Install TA-Lib System Dependency

TA-Lib requires a C library installed at the OS level BEFORE `pip install ta-lib`.

**macOS:**
```bash
brew install ta-lib
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install -y build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

**Linux (RHEL/CentOS/Fedora):**
```bash
sudo yum groupinstall -y "Development Tools"
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

**Windows:**
```
pip install ta-lib
```
If that fails, download the appropriate .whl file from https://github.com/cgohlke/talib-build/releases and install with:
```bash
pip install TA_Lib-0.4.32-cp312-cp312-win_amd64.whl
```

### Step 4: Install Python Packages

Install all required packages (latest versions):

```bash
pip install openalgo vectorbt plotly anywidget nbformat ta-lib pandas numpy yfinance python-dotenv tqdm scipy numba nbformat ipywidgets quantstats ccxt
```

### Step 5: Create Backtesting Folder

Create only the top-level backtesting directory. Strategy subfolders are created on-demand when a backtest script is generated (by the `/backtest` skill).

```bash
mkdir -p backtesting
```

Do NOT pre-create strategy subfolders.

### Step 6: Configure .env File

**6a. Check if `.env.sample` exists at the project root.** If it does, use it as a template.

**6b. Ask the user which markets they will be backtesting** using AskUserQuestion:
- Indian Markets (OpenAlgo) — requires OpenAlgo API key
- US Markets (yfinance) — no API key needed
- Crypto Markets (Binance/CCXT) — optional API key for private data

**6c. If the user selected Indian Markets**, ask for their OpenAlgo API key:
- Ask: "Enter your OpenAlgo API key (from the OpenAlgo dashboard):"
- If the user provides a key, store it in `.env`
- If the user skips, write a placeholder

**6d. If the user selected Crypto Markets**, ask if they want to configure Binance API keys:
- Ask: "Do you have Binance API keys for authenticated data? (Optional — public OHLCV data works without keys)"
- If yes, ask for API key and secret key, store in `.env`
- If no, leave them blank in `.env`

**6e. Write the `.env` file** in the project root directory. Use this template, filling in any keys the user provided:

```
# Indian Markets (OpenAlgo)
OPENALGO_API_KEY={user_provided_key or "your_openalgo_api_key_here"}
OPENALGO_HOST=http://127.0.0.1:5000

# Crypto Markets (Binance via CCXT) - Optional
BINANCE_API_KEY={user_provided_key or ""}
BINANCE_SECRET_KEY={user_provided_key or ""}
```

**6f. Add `.env` to `.gitignore`** if it exists (never commit secrets):

Scripts use `find_dotenv()` to automatically walk up and find the single root `.env`, so no copies are needed in subdirectories.

```bash
grep -qxF '.env' .gitignore 2>/dev/null || echo '.env' >> .gitignore
```

### Step 7: Verify Installation

Run a quick verification:

```bash
python -c "
import vectorbt as vbt
import openalgo
import plotly
import talib
import anywidget
import nbformat
import quantstats as qs
from dotenv import load_dotenv
print('All packages installed successfully')
print(f'  vectorbt: {vbt.__version__}')
print(f'  plotly: {plotly.__version__}')
print(f'  nbformat: {nbformat.__version__}')
print(f'  quantstats: {qs.__version__}')
print(f'  TA-Lib: available')
print(f'  python-dotenv: available')
"
```

If TA-Lib import fails, inform the user that the C library needs to be installed first (see Step 3).

### Step 8: Print Summary

Print a summary showing:
- Detected OS
- Python version used
- Virtual environment path
- Installed packages and versions
- Backtesting folder created (strategy subfolders created on-demand by `/backtest`)
- `.env` file status (configured with keys / placeholder) — single file at project root
- Reminder: "Run `cp .env.sample .env` and fill in API keys if you skipped configuration"

## Important Notes

- Never install packages globally — always use the virtual environment
- TA-Lib C library installation requires admin/sudo privileges on Linux
- On macOS, Homebrew must be installed for `brew install ta-lib`
- If the user already has a virtual environment, ask before creating a new one
- The backtesting/ folder is where all generated backtest scripts will be saved
- NEVER commit `.env` files — they contain secrets. Always use `.gitignore`.
- If the user provides an API key during setup, write it directly to `.env` — do not ask them to edit the file manually
- `python-dotenv` is included in the pip install and must be used by all scripts to load `.env`
