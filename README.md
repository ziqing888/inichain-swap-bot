# IniChain Bot v1.0

IniChain Bot 是一个用于自动执行每日签到、代币兑换、创建新代币以及管理账户余额的 Python 脚本。该机器人通过与以太坊兼容的区块链（如 INIChain）交互，实现了自动化的区块链操作，帮助用户高效管理其数字资产。

注册：https://candy.inichain.com?invite=JCT01UDJV9CQRJ5RUVTDTS4MV

领水： https://faucet-testnet.inichain.com/
## 目录

- [功能](#功能)
- [先决条件](#先决条件)
- [安装](#安装)
- [配置](#配置)
- [使用指南](#使用指南)
  - [查看账户状态](#查看账户状态)
  - [每日签到](#每日签到)
  - [INI-USDT 兑换](#ini-usdt-兑换)
  - [创建新代币](#创建新代币)
  - [自动执行](#自动执行)
  - [发送 INI 到自身](#发送-ini-到自身)
- [常见问题](#常见问题)
- [贡献](#贡献)
- [许可证](#许可证)

## 功能

- **每日签到**：自动执行每日签到，获取签到奖励。
- **代币兑换**：在 INI 和 USDT 之间进行自动兑换，优化资产配置。
- **创建新代币**：使用指定参数在区块链上创建新代币。
- **账户状态查看**：查看账户的 INI 和 USDT 余额、Gas 价格及交易历史。
- **自动循环**：自动执行每日签到和兑换，并定期发送 INI 到自身地址以优化余额。
- **多账户支持**：支持同时管理多个账户，通过 `privatekey.txt` 文件批量操作。

## 先决条件

在开始之前，请确保您的系统满足以下条件：

- **Python 3.7 或更高版本**。
- **pip**：Python 包管理工具。
- **虚拟环境（推荐）**：如 `venv` 或 `conda`，用于隔离项目依赖。
- **私钥文件**：包含要管理的以太坊账户的私钥，每行一个私钥，存储在项目根目录下的 `privatekey.txt` 文件中。

**注意**：务必妥善保管您的私钥，绝不要将其泄露给他人或上传至公共仓库。

## 安装

1. **克隆仓库**

   ```bash
   git clone https://github.com/ziqing888/inichain-swap-bot.git
   cd inichain-swap-bot
   ```
2.创建并激活虚拟环境（推荐）
```
python3 -m venv venv
source venv/bin/activate  # 对于 Windows 用户使用 `venv\Scripts\activate`
```
3.安装依赖

确保您已经创建了 requirements.txt 文件。运行以下命令安装所需的 Python 库：
```
pip install -r requirements.txt
```
## 配置
在项目根目录下创建一个 privatekey.txt 文件，并将您的以太坊账户私钥逐行添加。例如：
```
0xYOURPRIVATEKEY1
0xYOURPRIVATEKEY2
```
## 运行脚本
```
python3 bot.py
```
