<p align="center">
  <a href="" rel="noopener">
 <img height=300px src="https://raw.githubusercontent.com/OniMock/.github/refs/heads/main/.resources/logo/new_logo.svg" alt="Project logo"></a>
</p>

<h3 align="center">Mirror Telegram 2 Discord</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/kylelobo/The-Documentation-Compendium.svg)](https://github.com/OniMock/mirror-telegram-2-discord/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kylelobo/The-Documentation-Compendium.svg)](https://github.com/OniMock/mirror-telegram-2-discord/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> This project mirrors messages from a specified Telegram group to a Discord channel, enabling users to authenticate their Telegram accounts and select groups for seamless cross-platform communication.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [Contributing](../CONTRIBUTING.md)
- [Authors](#authors)
- [Support me](#support_me)

## 🧐 About <a name = "about"></a>

The script serves as a bridge between Telegram and Discord by mirroring messages from a specified Telegram group to a Discord channel. It allows users to authenticate their Telegram accounts using their phone numbers and select which groups they want to monitor. Once authenticated, users can either choose from a list of their Telegram groups or input a specific group ID to begin mirroring messages. The script continuously listens for new messages in the selected group and forwards them to the designated Discord webhook, ensuring real-time communication between the two platforms. This functionality enhances cross-platform interaction and keeps communities connected, regardless of their preferred messaging app.

## 🏁 Getting Started <a name = "getting_started"></a>

To get started with this project, follow the steps below:

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- A Telegram account:
   Create an app telegram in https://my.telegram.org/apps save api_id and api_hash
- A Discord account

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mirror-telegram-2-discord.git
   ```
2. Navigate to the project directory:
    ```bash
   cd mirror-telegram-2-discord
   ```
3. Create a virtual environment:
    ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
    ```bash
   venv\Scripts\activate
   ```
5. Install the required packages:
    ```bash
   pip install -r requirements.txt
   ```
6. Create a ```.env``` file in the root directory and add your Telegram API credentials:
    ```bash
   API_ID=your_api_id
   API_HASH=your_api_hash
   ```
7. in ```config.py``` put your webhook discord url and a session_name (any name)
    ```python
   WEBHOOK_URL='https://your_webhook_url'
   SESSION_NAME='your_session_name'
   ```


## 🎈 Usage <a name="usage"></a>

1. Run the application
    ```bash
   python main.py
    ```
2. Follow the prompts to authenticate with your Telegram account and select the group you wish to mirror to Discord.

## 🚀 Deployment <a name = "deployment"></a>

To deploy the application, you can run it locally or on a server. Make sure you have your .env file properly configured with your API credentials.

## ⛏️ Built Using <a name = "built_using"></a>

- [Python](https://www.python.org/) - Language
- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram client for Python
- [python-dotenv](https://pypi.org/project/python-dotenv/) - For managing environment variables Environment


## ✍️ Authors <a name = "authors"></a>

- [@OniMock](https://github.com/OniMock) - Idea & Initial work

## 🆘 Support me <a name = "support_me"></a>


<p align="center">
<img width="24%" alt="Wallet" src="https://raw.githubusercontent.com/OniMock/.github/main/.resources/crypto_wallet.svg"/>
</p>

<table align="left">
    <thead>
        <tr>
            <th>Logo</th>
            <th>Network</th>
            <th>Wallet</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td align="center"><img alt="Bitcoin" src="https://raw.githubusercontent.com/OniMock/.github/main/.resources/bitcoin_logo.svg"/>
            </td>
            <td><font size="3">Bitcoin</font></td>
            <td><code>bc1p24ya6frpr053dhnhsw8mx46kmecxv4s64udecxc5lrk9qcssgxssf6zkpw</code></td>
        </tr>
         <tr>
            <td align="center"><img alt="Solana" src="https://raw.githubusercontent.com/OniMock/.github/main/.resources/solana_logo.svg"/>
            </td>
            <td><font size="3">Solana</font></td>
            <td><code>EMzhyAkJkV4jM8N99A7xJt8vUEcLxcoGT1ukjYXb8NVa</code></td>
         </tr>
         <tr>
            <td align="center" style="width: 20px;"><img alt="Ethereum" src="https://raw.githubusercontent.com/OniMock/.github/main/.resources/binance_logo.svg"/><img alt="Solana" src="https://raw.githubusercontent.com/OniMock/.github/main/.resources/ethereum_logo.svg"/><img alt="Polygon" src="https://raw.githubusercontent.com/OniMock/.github/main/.resources/polygon_logo.svg"/><img alt="Fantom" src="https://raw.githubusercontent.com/OniMock/.github/main/.resources/fantom_logo.svg"/>
            </td>
            <td style="width: 2px;"><font size="2">Binance, Ethereum, Polygon, Fantom ou outra EVM</font></td>
            <td><code>0xE7402cB0191D1C27c9EA0DB14FE62Db2F183bbDe</code></td>
        </tr>
    </tbody>
</table>
