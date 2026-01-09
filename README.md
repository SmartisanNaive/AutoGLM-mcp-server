# Open-AutoGLM MCP Server

This is a Model Context Protocol (MCP) server for Open-AutoGLM, allowing you to control phones (Android, HarmonyOS, iOS) via an MCP client (like Claude Desktop or Trae).

## Prerequisites

- [uv](https://github.com/astral-sh/uv) installed
- `adb` installed and configured (for Android)
- `hdc` installed (for HarmonyOS)
- `libimobiledevice` and `WebDriverAgent` (for iOS)
- A running model API endpoint (e.g., vLLM or local inference)

## Installation

This server is managed using `uv`. All dependencies are specified in `pyproject.toml`.

## Usage

Run the server using `uv`:

```bash
cd mcp-server
uv run server.py
```

### Detailed Configuration Guide

You can configure the server using environment variables. Here is a description of all available parameters:

| Environment Variable | Description | Default | Example |
|---------------------|-------------|---------|---------|
| `PHONE_AGENT_BASE_URL` | Model API Base URL | `http://localhost:8000/v1` | `https://api.deepseek.com/v1` |
| `PHONE_AGENT_MODEL` | Model Name | `autoglm-phone-9b` | `deepseek-chat` |
| `PHONE_AGENT_API_KEY` | Model API Key | `EMPTY` | `sk-xxxxxxxx` |
| `PHONE_AGENT_MAX_STEPS` | Max steps per task | `100` | `50` |
| `PHONE_AGENT_LANG` | System Prompt Language (`cn` or `en`) | `cn` | `en` |
| `PHONE_AGENT_DEVICE_ID` | Device ID to control (ADB/UUID) | (empty) | `emulator-5554` or `00008101-001E30590A08001E` |
| `PHONE_AGENT_WDA_URL` | iOS WebDriverAgent URL | `http://localhost:8100` | `http://192.168.1.10:8100` |

### Available Tools

- `run_task(task: str, device_id: str = None)`: Executes a natural language task on the phone.
  - `task`: Task description (e.g., "Open Settings and enable Wi-Fi").
  - `device_id`: (Optional) Specific device ID.

## Android (ADB) Common Commands & Guide

To better use this server for controlling Android devices, you should be familiar with some basic ADB operations.

### 1. Install ADB

- **macOS** (using Homebrew):
  ```bash
  brew install android-platform-tools
  ```

- **Windows**:
  1. Download [SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools).
  2. Unzip and add the folder path to your system's PATH environment variable.

- **Linux** (Ubuntu/Debian):
  ```bash
  sudo apt install android-tools-adb
  ```

### 2. Get Device ID

To configure `PHONE_AGENT_DEVICE_ID`, you need to get the device serial number:

1. Connect phone via USB and ensure **Developer Options** and **USB Debugging** are enabled.
2. Run in terminal:
   ```bash
   adb devices
   ```
3. Output example:
   ```text
   List of devices attached
   emulator-5554   device
   XDR45678901     device
   ```
   The first column is the Device ID (e.g., `emulator-5554` or `XDR45678901`).

### 3. Common Commands Cheat Sheet

| Task | Command | Description |
|------|---------|-------------|
| **View Devices** | `adb devices` | Check connection status. Ensure it shows `device` instead of `offline` or `unauthorized`. |
| **Wireless Connect** | `adb connect <IP>:<PORT>` | Connect remote device. See "Wireless Debugging Guide" below. |
| **Disconnect** | `adb disconnect` | Disconnect all wireless connections. |
| **Install App** | `adb install <path/to.apk>` | Install an APK file. |
| **View Foreground App** | `adb shell dumpsys window \| grep mCurrentFocus` | View the package name and Activity of the current running app. |
| **Restart Server** | `adb kill-server && adb start-server` | Restart ADB server if connection issues occur. |

### 4. Wireless Debugging Guide

If you want to connect an Android device via Wi-Fi, follow these steps:

#### Method 1: Android 11+ (Recommended)
1. Enable **Developer Options** > **Wireless debugging** on your phone.
2. Tap "Pair device with pairing code".
3. Run on computer:
   ```bash
   adb pair <IP>:<PORT>
   ```
   Enter the 6-digit pairing code shown on the phone.
4. After pairing, run the connect command (note that the port may change, check "IP address and Port" on the phone):
   ```bash
   adb connect <IP>:<PORT>
   ```

#### Method 2: General Method (Requires USB for initial setup)
1. Connect phone to computer via USB.
2. Ensure `adb devices` shows the device.
3. Enable TCP/IP mode (default port 5555):
   ```bash
   adb tcpip 5555
   ```
4. Disconnect USB cable.
5. Check phone's Wi-Fi IP address (in Settings > About phone > Status).
6. Connect device:
   ```bash
   adb connect <Phone_IP>:5555
   ```

## Integration with Claude Desktop

Add the following to your `claude_desktop_config.json`. Please adjust the configuration values according to your actual environment:

```json
{
  "mcpServers": {
    "phone-agent": {
      "command": "uv",
      "args": [
        "run",
        "server.py"
      ],
      "cwd": "/absolute/path/to/Open-AutoGLM/mcp-server",
      "env": {
        "PHONE_AGENT_BASE_URL": "http://localhost:8000/v1",
        "PHONE_AGENT_MODEL": "autoglm-phone-9b",
        "PHONE_AGENT_API_KEY": "EMPTY",
        "PHONE_AGENT_MAX_STEPS": "100",
        "PHONE_AGENT_LANG": "cn",
        "PHONE_AGENT_DEVICE_ID": ""
      }
    }
  }
}
```

### Configuration Parameters Explained

Here is a detailed explanation of each environment variable in the configuration:

- **`PHONE_AGENT_BASE_URL`**: The base URL of the model API.
  - Example: `http://localhost:8000/v1` (Local vLLM) or `https://api.deepseek.com/v1` (Cloud API).
- **`PHONE_AGENT_MODEL`**: The model name to use.
  - Example: `autoglm-phone-9b`.
- **`PHONE_AGENT_API_KEY`**: Model API authentication key.
  - Note: Usually `EMPTY` for local deployment; real Key (e.g., `sk-...`) for Cloud API.
- **`PHONE_AGENT_MAX_STEPS`**: Maximum execution steps per task.
  - Note: Used to prevent tasks from entering infinite loops, default `100`.
- **`PHONE_AGENT_LANG`**: System prompt language.
  - Options: `cn` (Chinese) or `en` (English).
- **`PHONE_AGENT_DEVICE_ID`**: Device ID to control.
  - Note: If multiple devices are connected, enter the target device's Serial. Leave empty to auto-select the first one.

Note: Please replace `/absolute/path/to/Open-AutoGLM/mcp-server` with the actual absolute path of your local project.

## Contact

For any questions or support, please contact: jianghanchn@vip.qq.com
