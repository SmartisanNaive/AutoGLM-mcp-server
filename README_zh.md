# Open-AutoGLM MCP 服务器

这是一个 Open-AutoGLM 的 Model Context Protocol (MCP) 服务器，允许您通过 MCP 客户端（如 Claude Desktop 或 Trae）控制手机（Android、HarmonyOS、iOS）。

## 前置条件

- 已安装 [uv](https://github.com/astral-sh/uv)
- 已安装并配置 `adb`（用于 Android）
- 已安装 `hdc`（用于 HarmonyOS）
- 已安装 `libimobiledevice` 和 `WebDriverAgent`（用于 iOS）
- 正在运行的模型 API 端点（例如 vLLM 或本地推理）

## 安装

本服务器使用 `uv` 进行管理。所有依赖项均在 `pyproject.toml` 中指定。

## 使用方法

使用 `uv` 运行服务器：

```bash
cd mcp-server
uv run server.py
```

### 详细配置指南

您可以通过环境变量对服务器进行详细配置。以下是所有可用参数的说明：

| 环境变量 | 说明 | 默认值 | 示例 |
|---------|------|-------|------|
| `PHONE_AGENT_BASE_URL` | 模型 API 基础 URL | `http://localhost:8000/v1` | `https://api.deepseek.com/v1` |
| `PHONE_AGENT_MODEL` | 模型名称 | `autoglm-phone-9b` | `deepseek-chat` |
| `PHONE_AGENT_API_KEY` | 模型认证的 API 密钥 | `EMPTY` | `sk-xxxxxxxx` |
| `PHONE_AGENT_MAX_STEPS` | 每个任务的最大执行步数 | `100` | `50` |
| `PHONE_AGENT_LANG` | 系统提示词语言 (`cn` 或 `en`) | `cn` | `en` |
| `PHONE_AGENT_DEVICE_ID` | 指定要控制的设备 ID (ADB/UUID) | (空) | `emulator-5554` 或 `00008101-001E30590A08001E` |

### 可用工具

- `run_task(task: str, device_id: str = None)`: 在手机上执行自然语言任务。
  - `task`: 任务描述（例如：“打开微信发送消息”）。
  - `device_id`: (可选) 指定设备 ID。

## Android (ADB) 常用命令与指南

为了更好地使用本服务器控制 Android 设备，您需要熟悉一些 ADB 基础操作。

### 1. 安装 ADB

- **macOS** (使用 Homebrew):
  ```bash
  brew install android-platform-tools
  ```

- **Windows**:
  1. 下载 [SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)。
  2. 解压并将文件夹路径添加到系统的 PATH 环境变量中。

- **Linux** (Ubuntu/Debian):
  ```bash
  sudo apt install android-tools-adb
  ```

### 2. 获取设备 ID

要配置 `PHONE_AGENT_DEVICE_ID`，您需要获取设备的序列号：

1. 通过 USB 连接手机，并确保已开启**开发者模式**和**USB 调试**。
2. 在终端运行：
   ```bash
   adb devices
   ```
3. 输出示例：
   ```text
   List of devices attached
   emulator-5554   device
   XDR45678901     device
   ```
   第一列即为设备 ID（如 `emulator-5554` 或 `XDR45678901`）。

### 3. 常用命令速查

| 任务 | 命令 | 说明 |
|------|------|------|
| **查看设备** | `adb devices` | 查看当前连接状态，确保显示 `device` 而非 `offline` 或 `unauthorized`。 |
| **无线连接** | `adb connect <IP>:<PORT>` | 连接远程设备。详见下方“无线调试指南”。 |
| **断开连接** | `adb disconnect` | 断开所有无线连接。 |
| **安装应用** | `adb install <path/to.apk>` | 安装 APK 文件。 |
| **查看前台应用** | `adb shell dumpsys window \| grep mCurrentFocus` | 查看当前正在运行的应用包名和 Activity。 |
| **重启服务** | `adb kill-server && adb start-server` | ADB 连接出现问题时尝试重启服务。 |

### 4. 无线调试连接指南

如果您希望通过 Wi-Fi 连接 Android 设备，请按以下步骤操作：

#### 方法一：Android 11+ (推荐)
1. 在手机上启用 **开发者选项** > **无线调试**。
2. 点击“使用配对码配对设备”。
3. 在电脑上运行：
   ```bash
   adb pair <IP地址>:<端口>
   ```
   输入手机上显示的 6 位配对码。
4. 配对成功后，运行连接命令（注意端口可能变动，请看手机显示的“IP地址和端口”）：
   ```bash
   adb connect <IP地址>:<端口>
   ```

#### 方法二：通用方法 (需要 USB 线辅助首次连接)
1. 使用 USB 线将手机连接到电脑。
2. 确保 `adb devices` 能看到设备。
3. 开启 TCP/IP 模式（默认端口 5555）：
   ```bash
   adb tcpip 5555
   ```
4. 断开 USB 线。
5. 查看手机 Wi-Fi 的 IP 地址（在设置 > 关于手机 > 状态信息中）。
6. 连接设备：
   ```bash
   adb connect <手机IP地址>:5555
   ```

## 集成到 Claude Desktop

将以下内容添加到您的 `claude_desktop_config.json` 文件中。请根据您的实际环境修改配置值：

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

### 参数配置说明

以下是配置文件中各环境变量的详细解释：

- **`PHONE_AGENT_BASE_URL`**: 模型 API 的基础 URL。
  - 示例: `http://localhost:8000/v1` (本地 vLLM) 或 `https://api.deepseek.com/v1` (云端 API)。
- **`PHONE_AGENT_MODEL`**: 使用的模型名称。
  - 示例: `autoglm-phone-9b`。
- **`PHONE_AGENT_API_KEY`**: 模型 API 鉴权密钥。
  - 说明: 本地部署通常填 `EMPTY`；云端 API 需填写真实 Key (如 `sk-...`)。
- **`PHONE_AGENT_MAX_STEPS`**: 单次任务的最大执行步数。
  - 说明: 用于防止任务陷入死循环，默认 `100`。
- **`PHONE_AGENT_LANG`**: 系统提示词语言。
  - 选项: `cn` (中文) 或 `en` (英文)。
- **`PHONE_AGENT_DEVICE_ID`**: 指定要控制的设备 ID。
  - 说明: 如果连接了多台设备，在此填入目标设备的 Serial。留空则自动选择第一台。

注意：请将 `/absolute/path/to/Open-AutoGLM/mcp-server` 替换为您本地项目实际的绝对路径。

## 联系方式

如有任何问题或建议，请联系：jianghanchn@vip.qq.com
