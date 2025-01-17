from web3 import Web3
from eth_account import Account
import json
import time
import random
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz  # 引入pytz库

# 定义时区
wib = pytz.timezone('Asia/Shanghai')

# 加载环境变量
load_dotenv()

# 网络配置
RPC_URL = "https://rpc-testnet.inichain.com"
CHAIN_ID = 7234

# 合约地址
DAILY_CHECKIN_CONTRACT = "0x73439c32e125B28139823fE9C6C079165E94C6D1"
ROUTER_CONTRACT = "0x4ccB784744969D9B63C15cF07E622DDA65A88Ee7"
WINI_CONTRACT = "0xfbECae21C91446f9c7b87E4e5869926998f99ffe"
USDT_CONTRACT = "0xcF259Bca0315C6D32e877793B6a10e97e7647FdE"

# 代币小数位
USDT_DECIMALS = 18
INI_DECIMALS = 18

# 必需的最小ABI
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    }
]

DAILY_CHECKIN_ABI = [
    {
        "inputs": [{"name": "user", "type": "address"}],
        "name": "userCheckInStatus",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# WINI（Wrapped INI）的ABI
WINI_ABI = [
    {
        "constant": False,
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "wad", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# 创建代币的ABI
TOKEN_FACTORY_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string", "name": "symbol", "type": "string"},
            {"internalType": "uint256", "name": "initialSupply", "type": "uint256"},
            {"internalType": "uint8", "name": "decimals", "type": "uint8"}
        ],
        "name": "createToken",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "token", "type": "address"},
            {"indexed": False, "internalType": "string", "name": "name", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "symbol", "type": "string"},
            {"indexed": False, "internalType": "uint256", "name": "totalSupply", "type": "uint256"},
            {"indexed": False, "internalType": "uint8", "name": "decimals", "type": "uint8"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "name": "TokenCreated",
        "type": "event"
    }
]

# Token Factory 合约地址
TOKEN_FACTORY_CONTRACT = "0x01AA0e004F7e7591f2fc2712384dF9B5FDB759DD"

# 初始化 Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

class IniChainBot:
    def __init__(self, private_key):
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.router_contract = w3.eth.contract(address=ROUTER_CONTRACT, abi=ROUTER_ABI)
        self.checkin_contract = w3.eth.contract(address=DAILY_CHECKIN_CONTRACT, abi=DAILY_CHECKIN_ABI)
        self.wini_contract = w3.eth.contract(address=WINI_CONTRACT, abi=WINI_ABI)
        self.last_checkin = {}

    def get_dynamic_gas_price(self, priority="normal"):
        """根据当前网络状况获取动态Gas价格"""
        base_gas_price = w3.eth.gas_price
        
        multipliers = {
            "low": 1.1,
            "normal": 1.2,
            "high": 1.5
        }
        
        gas_price = int(base_gas_price * multipliers[priority])
        
        # 安全上限 (最大5 Gwei)
        max_gas_price = 5 * 10**9
        return min(gas_price, max_gas_price)

    def get_gas_price(self):
        """获取正常交易的最优Gas价格"""
        return self.get_dynamic_gas_price("normal")
        
    def get_approve_gas_price(self):
        """获取Approve操作的Gas价格，优先级更高"""
        return self.get_dynamic_gas_price("high")

    def format_amount(self, amount, decimals):
        """格式化金额，显示为正确的小数位"""
        return amount / (10 ** decimals)

    def check_daily_checkin_status(self):
        """检查每日签到是否可用"""
        try:
            has_checked_in = self.checkin_contract.functions.userCheckInStatus(self.address).call()
            if not has_checked_in:
                return True
                
            print(f"[{self.address}] 签到仍在冷却中")
            return False
            
        except Exception as e:
            print(f"[{self.address}] 检查签到状态时出错: {str(e)}")
            return False

    def daily_checkin(self, account_info):
        """执行每日签到"""
        try:
            nonce = w3.eth.get_transaction_count(self.address)
            gas_price = self.get_gas_price()
            
            print(f"[{account_info}] 开始每日签到...")
            print(f"[{account_info}] Gas价格: {gas_price / 1e9:.2f} Gwei")
            
            # 估算Gas限制
            try:
                gas_estimate = w3.eth.estimate_gas({
                    'from': self.address,
                    'to': DAILY_CHECKIN_CONTRACT,
                    'value': 0,
                    'data': '0x183ff085',  # Checkin函数签名
                    'gasPrice': gas_price,
                    'nonce': nonce
                })
                print(f"[{account_info}] 估算Gas: {gas_estimate}")
            except Exception as e:
                error_message = str(e)
                if "Today's check-in has been completed" in error_message:
                    print(f"[{account_info}] 今日签到已完成")
                    return False
                else:
                    print(f"[{account_info}] 估算Gas时出错: {error_message}")
                    gas_estimate = 150000  # 回退Gas限制
            
            transaction = {
                'from': self.address,
                'to': DAILY_CHECKIN_CONTRACT,
                'value': 0,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'data': '0x183ff085'  # Checkin函数签名
            }

            signed_txn = w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = self.wait_for_transaction(tx_hash)
            
            if receipt and receipt['status'] == 1:
                self.last_checkin[self.address] = datetime.now(wib)
                print(f"[{account_info}] 签到成功: {tx_hash.hex()}")
                return True
            else:
                if receipt:
                    print(f"[{account_info}] 签到失败! Gas消耗: {receipt.get('gasUsed', '未知')}")
                    try:
                        tx = w3.eth.get_transaction(tx_hash)
                        print(f"[{account_info}] 交易详情:")
                        print(f"  Gas价格: {tx.get('gasPrice', '未知')}")
                        print(f"  Gas限制: {tx.get('gas', '未知')}")
                        print(f"  Nonce: {tx.get('nonce', '未知')}")
                        print(f"  值: {tx.get('value', '未知')}")
                    except Exception as e:
                        print(f"[{account_info}] 获取交易详情时出错: {str(e)}")
                return False
                
        except Exception as e:
            print(f"[{account_info}] 签到时出错: {str(e)}")
            return False

    def get_token_balance(self, token_address):
        """获取代币余额"""
        token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
        balance = token_contract.functions.balanceOf(self.address).call()
        return balance

    def wait_for_transaction(self, tx_hash, timeout=300):
        """等待交易被挖矿并返回回执"""
        start_time = time.time()
        print(f"[{self.address}] 等待交易确认: {tx_hash.hex()}")
        
        while True:
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt is not None:
                    return receipt
            except Exception:
                pass
            
            if time.time() - start_time > timeout:
                print(f"[{self.address}] 等待确认时出错: 交易 {tx_hash.hex()} 在 {timeout} 秒后未被确认")
                return None
            
            print(f"[{self.address}] 仍在等待确认... ({int(time.time() - start_time)} 秒)")
            time.sleep(10)

    def approve_token(self, token_address, amount, account_info):
        """为路由器批准代币"""
        token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
        
        try:
            print(f"[{account_info}] 开始批准流程...")
            current_allowance = token_contract.functions.allowance(self.address, ROUTER_CONTRACT).call()
            formatted_allowance = self.format_amount(current_allowance, USDT_DECIMALS)
            print(f"[{account_info}] 当前允许额度: {formatted_allowance:.6f} USDT")

            if current_allowance >= amount:
                print(f"[{account_info}] 允许额度已足够，无需再次批准")
                return True
            
            nonce = w3.eth.get_transaction_count(self.address)
            gas_price = self.get_approve_gas_price()
            
            print(f"[{account_info}] 发送批准交易，Gas价格: {gas_price / 1e9:.2f} Gwei")
            
            amount = int(amount)
            approve_txn = token_contract.functions.approve(
                ROUTER_CONTRACT,
                amount
            ).build_transaction({
                'from': self.address,
                'gas': 100000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': CHAIN_ID
            })
            
            signed_txn = w3.eth.account.sign_transaction(approve_txn, self.account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = self.wait_for_transaction(tx_hash)
            if receipt and receipt['status'] == 1:
                print(f"[{account_info}] 批准成功!")
                return True
            else:
                print(f"[{account_info}] 批准失败!")
                return False
                
        except Exception as e:
            print(f"[{account_info}] 批准时出错: {str(e)}")
            return False

    def get_token_price(self, token_in, token_out, amount_in):
        """从路由器获取代币价格"""
        try:
            path = [token_in, token_out]
            amount_in_wei = int(amount_in * 1e18)
            
            amounts_out = self.router_contract.functions.getAmountsOut(
                amount_in_wei,
                path
            ).call()
            
            return amounts_out[1] / 1e18
        except Exception as e:
            print(f"[{self.address}] 获取价格时出错: {str(e)}")
            return 0

    # ========== 新增：WINI → INI 的解包函数 ==========
    def withdraw_wini(self, wini_amount, account_info):
        """
        将指定数量的WINI解包为原生INI。
        :param wini_amount: 需要解包的WINI数量（单位：最小单位，int 类型）
        :param account_info: 用于日志打印的账户信息
        """
        try:
            nonce = w3.eth.get_transaction_count(self.address)
            gas_price = self.get_gas_price()

            # 估算Gas
            try:
                gas_estimate = self.wini_contract.functions.withdraw(
                    wini_amount
                ).estimate_gas({
                    'from': self.address,
                    'gasPrice': gas_price,
                    'nonce': nonce
                })
                print(f"[{account_info}] 估算 WINI → INI Gas: {gas_estimate}")
            except Exception as e:
                print(f"[{account_info}] 估算 WINI → INI Gas时出错: {str(e)}")
                gas_estimate = 120000  # 回退Gas限制，可根据实际情况调整

            # 构建 withdraw 交易
            withdraw_txn = self.wini_contract.functions.withdraw(
                wini_amount
            ).build_transaction({
                'from': self.address,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': CHAIN_ID
            })

            # 签名并发送
            signed_txn = w3.eth.account.sign_transaction(withdraw_txn, self.account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            print(f"[{account_info}] 开始执行 WINI → INI，交易哈希: {tx_hash.hex()}")
            receipt = self.wait_for_transaction(tx_hash)
            if receipt and receipt['status'] == 1:
                print(f"[{account_info}] WINI → INI 成功!")
                return True
            else:
                print(f"[{account_info}] WINI → INI 失败!")
                if receipt:
                    print(f"[{account_info}] Gas使用量: {receipt.get('gasUsed', '未知')}")
                return False

        except Exception as e:
            print(f"[{account_info}] WINI → INI 时出错: {str(e)}")
            return False

    # ========== 修改：swap_usdt_to_ini ==========
    def swap_usdt_to_ini(self, amount, account_info):
        """将USDT兑换为原生INI（通过先兑换为WINI，再withdraw）"""
        try:
            print(f"[{account_info}] 正在执行 swap_usdt_to_ini，金额: {amount} USDT")
            
            # 1) 先把 USDT -> WINI
            amount_in_wei = int(amount * (10 ** USDT_DECIMALS))
            print(f"[{account_info}] 转换后的金额 (wei): {amount_in_wei}")
            
            # 获取当前 USDT 余额
            usdt_balance = self.get_token_balance(USDT_CONTRACT)
            formatted_usdt_balance = self.format_amount(usdt_balance, USDT_DECIMALS)
            print(f"[{account_info}] 当前 USDT 余额: {formatted_usdt_balance:.6f} USDT")
            
            if usdt_balance < amount_in_wei:
                print(f"[{account_info}] USDT 余额不足，无法兑换")
                return False
            
            # 获取当前允许额度
            token_contract = w3.eth.contract(address=USDT_CONTRACT, abi=ERC20_ABI)
            current_allowance = token_contract.functions.allowance(self.address, ROUTER_CONTRACT).call()
            formatted_allowance = self.format_amount(current_allowance, USDT_DECIMALS)
            print(f"[{account_info}] 当前允许额度: {formatted_allowance:.6f} USDT")
            
            # Approve
            if current_allowance < amount_in_wei:
                print(f"[{account_info}] 允许额度不足，正在批准...")
                if not self.approve_token(USDT_CONTRACT, amount_in_wei, account_info):
                    print(f"[{account_info}] 批准 USDT 失败")
                    return False
                else:
                    print(f"[{account_info}] 批准 USDT 成功")
            else:
                print(f"[{account_info}] 允许额度足够，无需再次批准")
            
            # 开始 swapExactTokensForTokens
            nonce = w3.eth.get_transaction_count(self.address)
            gas_price = self.get_gas_price()
            deadline = int(time.time()) + 300  # 5分钟截止时间
            
            # 获取预期输出 (USDT->WINI)
            expected_out = self.get_token_price(USDT_CONTRACT, WINI_CONTRACT, amount)
            if expected_out == 0:
                print(f"[{account_info}] 获取价格失败，取消兑换")
                return False
            print(f"[{account_info}] 预期输出: {expected_out:.6f} WINI (暂时)")
            
            min_out = int(expected_out * 1e18 * 0.95)  # 5% 滑点
            print(f"[{account_info}] 最小输出: {min_out / 1e18:.6f} WINI")
            
            path = [USDT_CONTRACT, WINI_CONTRACT]
            print(f"[{account_info}] 交易路径: {path}")
            
            # 估算 Gas
            try:
                gas_estimate = self.router_contract.functions.swapExactTokensForTokens(
                    amount_in_wei,
                    min_out,
                    path,
                    self.address,
                    deadline
                ).estimate_gas({
                    'from': self.address,
                    'gasPrice': gas_price,
                    'nonce': nonce
                })
                print(f"[{account_info}] 估算 Gas: {gas_estimate}")
            except Exception as e:
                print(f"[{account_info}] 估算 Gas 时出错: {str(e)}")
                gas_estimate = 300000  # 根据实际情况调整
                
            swap_txn = self.router_contract.functions.swapExactTokensForTokens(
                amount_in_wei,  # amountIn
                min_out,        # amountOutMin
                path,           # path: USDT->WINI
                self.address,   # to
                deadline        # deadline
            ).build_transaction({
                'from': self.address,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': CHAIN_ID
            })
            
            print(f"[{account_info}] 构建交易完成，发送交易...")
            signed_txn = w3.eth.account.sign_transaction(swap_txn, self.account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"[{account_info}] 发送交易，哈希: {tx_hash.hex()}")
            
            # 等待交易回执
            receipt = self.wait_for_transaction(tx_hash)
            if not receipt or receipt['status'] != 1:
                print(f"[{account_info}] USDT->WINI失败!")
                if receipt:
                    print(f"[{account_info}] Gas使用量: {receipt.get('gasUsed', '未知')}")
                return False
            
            print(f"[{account_info}] USDT->WINI 成功!")
            # 2) WINI → INI
            wini_balance = self.get_token_balance(WINI_CONTRACT)
            wini_balance_ether = self.format_amount(wini_balance, INI_DECIMALS)
            print(f"[{account_info}] 当前 WINI 余额: {wini_balance_ether:.6f} WINI")
            
            if wini_balance > 0:
                print(f"[{account_info}] 正在将 WINI 解包为原生INI...")
                result = self.withdraw_wini(wini_balance, account_info)
                if result:
                    print(f"[{account_info}] 兑换已完成，最终获得原生INI!")
                    return True
                else:
                    print(f"[{account_info}] withdraw 失败，未拿到原生INI!")
                    return False
            else:
                print(f"[{account_info}] WINI 余额为0，不需解包")
                return False
                
        except Exception as e:
            print(f"[{account_info}] 兑换USDT为INI时出错: {str(e)}")
            return False

    def swap_ini_to_usdt(self, amount, account_info):
        """通过swapExactETHForTokens将INI兑换为USDT"""
        try:
            nonce = w3.eth.get_transaction_count(self.address)
            gas_price = self.get_gas_price()
            deadline = int(time.time()) + 300  # 5分钟截止时间
            
            amount_in_wei = w3.to_wei(amount, 'ether')
            
            expected_out = self.get_token_price(WINI_CONTRACT, USDT_CONTRACT, amount)
            if expected_out == 0:
                print(f"[{account_info}] 获取价格失败，取消兑换")
                return
            
            min_out = int(expected_out * 1e18 * 0.95)  # 5% 滑点
            
            print(f"[{account_info}] 开始将INI兑换为USDT...")
            print(f"[{account_info}] Gas价格: {gas_price / 1e9:.2f} Gwei")
            print(f"[{account_info}] 金额: {amount:.6f} INI")
            print(f"[{account_info}] 预期输出: {expected_out:.6f} USDT")
            print(f"[{account_info}] 最小输出: {min_out / 1e18:.6f} USDT")
            
            path = [WINI_CONTRACT, USDT_CONTRACT]
            
            # 估算Gas限制
            try:
                gas_estimate = self.router_contract.functions.swapExactETHForTokens(
                    min_out,  
                    path,     
                    self.address,
                    deadline
                ).estimate_gas({
                    'from': self.address,
                    'value': amount_in_wei,
                    'gasPrice': gas_price,
                    'nonce': nonce
                })
                print(f"[{account_info}] 估算Gas: {gas_estimate}")
            except Exception as e:
                print(f"[{account_info}] 估算Gas时出错: {str(e)}")
                gas_estimate = 201306
            
            swap_txn = self.router_contract.functions.swapExactETHForTokens(
                min_out,
                path,
                self.address,
                deadline
            ).build_transaction({
                'from': self.address,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'value': amount_in_wei,
                'nonce': nonce,
                'chainId': CHAIN_ID
            })
            
            print(f"[{account_info}] 构建交易完成，发送交易...")
            
            signed_txn = w3.eth.account.sign_transaction(swap_txn, self.account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"[{account_info}] 发送交易，哈希: {tx_hash.hex()}")
            
            receipt = self.wait_for_transaction(tx_hash)
            if receipt and receipt['status'] == 1:
                print(f"[{account_info}] INI兑换USDT成功!")
                return True
            else:
                print(f"[{account_info}] INI兑换USDT失败!")
                if receipt:
                    print(f"[{account_info}] Gas使用量: {receipt.get('gasUsed', '未知')}")
                return False
                
        except Exception as e:
            print(f"[{account_info}] 兑换INI为USDT时出错: {str(e)}")
            return False

    def wrap_ini(self, amount):
        """将INI包装为WINI"""
        try:
            nonce = w3.eth.get_transaction_count(self.address)
            gas_price = self.get_gas_price()
            
            amount_in_wei = w3.to_wei(amount, 'ether')
            
            print(f"[{self.address}] 将 {amount:.6f} INI 包装为 WINI...")
            print(f"[{self.address}] Gas价格: {gas_price / 1e9:.2f} Gwei")
            
            try:
                gas_estimate = self.wini_contract.functions.deposit().estimate_gas({
                    'from': self.address,
                    'value': amount_in_wei,
                    'gasPrice': gas_price,
                    'nonce': nonce
                })
                print(f"[{self.address}] 估算Gas: {gas_estimate}")
            except Exception as e:
                print(f"[{self.address}] 估算Gas时出错: {str(e)}")
                gas_estimate = 50000
            
            deposit_txn = self.wini_contract.functions.deposit().build_transaction({
                'from': self.address,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'value': amount_in_wei,
                'nonce': nonce,
                'chainId': CHAIN_ID
            })
            
            signed_txn = w3.eth.account.sign_transaction(deposit_txn, self.account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = self.wait_for_transaction(tx_hash)
            if receipt and receipt['status'] == 1:
                print(f"[{self.address}] INI包装为WINI成功!")
                return True
            else:
                print(f"[{self.address}] INI包装为WINI失败!")
                return False
                
        except Exception as e:
            print(f"[{self.address}] 包装INI时出错: {str(e)}")
            return False

    def perform_swap(self, account_info):
        """在INI和USDT之间随机执行兑换"""
        try:
            ini_balance = w3.eth.get_balance(self.address)
            formatted_balance = w3.from_wei(ini_balance, 'ether')
            
            gas_price = self.get_gas_price()
            estimated_gas = 201306
            gas_cost = gas_price * estimated_gas
            
            safe_balance = ini_balance - int(gas_cost * 1.2)
            
            print(f"[{account_info}] 当前INI余额: {formatted_balance:.6f} INI")
            print(f"[{account_info}] Gas费用: {w3.from_wei(gas_cost, 'ether'):.6f} INI")
            print(f"[{account_info}] 安全余额: {w3.from_wei(safe_balance, 'ether'):.6f} INI")
            
            if safe_balance > gas_cost:
                # 将10-25%的INI兑换为USDT
                swap_percentage = random.uniform(0.10, 0.25)
                amount_to_swap = float(w3.from_wei(int(safe_balance * swap_percentage), 'ether'))
                
                print(f"[{account_info}] 将兑换: {amount_to_swap:.6f} INI ({swap_percentage*100:.1f}% 从安全余额)")
                self.swap_ini_to_usdt(amount_to_swap, account_info)
            else:
                usdt_balance = self.get_token_balance(USDT_CONTRACT)
                formatted_usdt_balance = self.format_amount(usdt_balance, USDT_DECIMALS)
                print(f"[{account_info}] 当前USDT余额: {formatted_usdt_balance:.6f} USDT")
                
                if usdt_balance > 0:
                    swap_percentage = random.uniform(0.80, 0.90)
                    amount_to_swap = formatted_usdt_balance * swap_percentage
                    
                    print(f"[{account_info}] 将兑换: {amount_to_swap:.6f} USDT 到 INI ({swap_percentage*100:.1f}% 从余额)")
                    self.swap_usdt_to_ini(amount_to_swap, account_info)
                else:
                    print(f"[{account_info}] INI余额不足以进行兑换")
                    print(f"[{account_info}] 当前余额: {formatted_balance:.6f} INI")
                    print(f"[{account_info}] 最低Gas费用: {w3.from_wei(gas_cost * 1.2, 'ether'):.6f} INI")
                
        except Exception as e:
            print(f"[{account_info}] 兑换时出错: {str(e)}")

    def create_token(self, name, symbol, total_supply, decimals, account_info):
        """使用指定参数创建新代币"""
        try:
            token_factory = w3.eth.contract(address=TOKEN_FACTORY_CONTRACT, abi=TOKEN_FACTORY_ABI)
            total_supply_wei = int(total_supply * (10 ** decimals))
            
            nonce = w3.eth.get_transaction_count(self.address)
            gas_price = self.get_dynamic_gas_price("normal")
            
            print(f"[{account_info}] 开始创建代币...")
            print(f"[{account_info}] Gas价格: {gas_price / 1e9:.2f} Gwei")
            print(f"[{account_info}] 代币名称: {name}")
            print(f"[{account_info}] 代币符号: {symbol}")
            print(f"[{account_info}] 总供应量: {total_supply_wei}")
            print(f"[{account_info}] 小数位: {decimals}")
            
            gas_limit = 1548128
            estimated_gas_cost = gas_limit * gas_price / 1e18
            print(f"[{account_info}] 估算Gas费用: {estimated_gas_cost:.6f} INI")
            
            balance = w3.eth.get_balance(self.address)
            formatted_balance = w3.from_wei(balance, 'ether')
            print(f"[{account_info}] 当前余额: {formatted_balance:.6f} INI")
            
            if balance < (gas_limit * gas_price):
                print(f"[{account_info}] INI余额不足以支付Gas费用!")
                return False
            
            # 这里是你抓取到的成功交易的data，可根据实际情况更改
            input_data = "0x8ab84b4a000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000186a000000000000000000000000000000000000000000000000000000000000000120000000000000000000000000000000000000000000000000000000000000004757364740000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000047573647400000000000000000000000000000000000000000000000000000000"

            transaction = {
                'from': self.address,
                'to': TOKEN_FACTORY_CONTRACT,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'data': input_data
            }
            
            signed_txn = w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            print(f"[{account_info}] 等待代币创建确认...")
            receipt = self.wait_for_transaction(tx_hash)
            
            if receipt and receipt['status'] == 1:
                print(f"[{account_info}] 代币创建成功!")
                print(f"[{account_info}] 交易哈希: {tx_hash.hex()}")
                return True
            else:
                print(f"[{account_info}] 代币创建失败!")
                if receipt:
                    print(f"[{account_info}] Gas消耗: {receipt.get('gasUsed', '未知')}")
                return False
            
        except Exception as e:
            print(f"[{account_info}] 创建代币时出错: {str(e)}")
            return False

def get_transaction_type(tx, bot_address, bot):
    """获取交易类型及详情"""
    if tx['to'] is None:
        return "合约创建", None
        
    if tx['to'].lower() == DAILY_CHECKIN_CONTRACT.lower():
        return "每日签到", None
        
    if tx['to'].lower() == ROUTER_CONTRACT.lower():
        return "USDT兑换INI", None
            
    if tx['from'].lower() == bot_address.lower():
        return "转出交易", f"{bot.format_amount(tx['value'], INI_DECIMALS):.6f} INI"
    else:
        return "转入交易", f"{bot.format_amount(tx['value'], INI_DECIMALS):.6f} INI"

def show_status(private_key, account_num):
    """显示账户状态"""
    bot = IniChainBot(private_key)
    account_info = f"账户 {account_num} | {bot.address[-4:]}"
    
    ini_balance = w3.eth.get_balance(bot.address) / 10**18
    usdt_balance = bot.get_token_balance(USDT_CONTRACT) / 10**18
    
    gas_price = w3.eth.gas_price / 10**9
    checkin_gas = 150000
    swap_gas = 300000
    
    checkin_fee = (checkin_gas * gas_price) / 10**9
    swap_fee = (swap_gas * gas_price) / 10**9
    
    print(f"\n状态 [{account_info}]")
    print(f"完整地址: {bot.address}")
    print(f"INI余额: {ini_balance:.6f}")
    print(f"USDT余额: {usdt_balance:.6f}")
    print(f"Gas价格: {gas_price:.2f} Gwei")
    print(f"签到估算费用: {checkin_fee:.6f} INI")
    print(f"兑换估算费用: {swap_fee:.6f} INI")
    
    print(f"\n最近的交易历史 [{account_info}]:")
    try:
        latest = w3.eth.block_number
        start_block = max(0, latest - 100)
        
        for block in range(latest, start_block, -1):
            block_data = w3.eth.get_block(block, True)
            for tx in block_data.transactions:
                if tx['from'].lower() == bot.address.lower() or (tx['to'] and tx['to'].lower() == bot.address.lower()):
                    timestamp = datetime.fromtimestamp(block_data.timestamp, wib)
                    
                    tx_type = "未知"
                    if tx['to'] and tx['to'].lower() == DAILY_CHECKIN_CONTRACT.lower():
                        tx_type = "每日签到"
                    elif tx['to'] and tx['to'].lower() == ROUTER_CONTRACT.lower():
                        tx_type = "兑换"
                    
                    print(f"区块 {block} ({timestamp:%Y-%m-%d %H:%M:%S}) - {tx_type} (Gas: {tx['gas']})")
                    print(f"  哈希: {tx['hash'].hex()}")
                    
    except Exception as e:
        print(f"获取交易历史时出错: {str(e)}")
    
    print("\n过程完成!")

def process_accounts(private_keys, action):
    """处理多个账户"""
    for i, private_key in enumerate(private_keys, 1):
        bot = IniChainBot(private_key)
        account_info = f"账户 {i} | {bot.address[-4:]}"
        if action == "checkin":
            bot.daily_checkin(account_info)
        elif action == "swap":
            bot.perform_swap(account_info)
        elif action == "status":
            show_status(private_key, i)
        time.sleep(5)

def auto_daily_and_swap(private_keys):
    """自动每日签到和兑换，循环执行"""
    cycle_count = 1
    while True:
        try:
            print(f"\n{'='*50}")
            print(f"开始第 {cycle_count} 个周期...")
            print(f"{'='*50}")
            
            print("\n开始每日签到...")
            process_accounts(private_keys, "checkin")
            print("每日签到完成!")
            
            print("\n等待5秒后开始兑换...")
            time.sleep(5)
            
            print("\n开始兑换过程...")
            process_accounts(private_keys, "swap")
            print("兑换过程完成!")
    
            print("\n等待5秒后开始发送INI到自身...")
            time.sleep(5)
            
            print("\n开始发送INI到自身的过程...")
            send_ini_to_self(private_keys)
            print("发送INI到自身的过程完成!")
            
            print(f"\n第 {cycle_count} 个周期完成")
            print("等待10分钟后开始下一个周期...")
            
            for i in range(600, 0, -1):
                minutes = i // 60
                seconds = i % 60
                print(f"\r下一个周期开始的时间: {minutes:02d}:{seconds:02d}", end="")
                time.sleep(1)
            
            print("\n")
            cycle_count += 1
            
        except KeyboardInterrupt:
            print("\n停止自动每日签到和兑换...")
            break
        except Exception as e:
            print(f"\n周期中出错: {str(e)}")
            print("尝试继续下一个周期...")
            time.sleep(10)

def show_menu():
    """显示交互菜单"""
    print("\n=== 菜单 ===")
    print("1. 查看状态")
    print("2. 每日签到")
    print("3. INI-USDT兑换")
    print("4. 创建代币")
    print("5. 自动（每日签到 & 兑换 & 发送INI到自身）")
    print("6. 发送INI到自身")
    print("7. 退出")
    return input("请选择菜单 (1-7): ")

def cycle_swap(private_keys):
    """每10分钟执行一次兑换循环"""
    cycle_count = 1
    while True:
        try:
            print(f"\n开始第 {cycle_count} 个兑换周期...")
            process_accounts(private_keys, "swap")
            print(f"\n第 {cycle_count} 个兑换周期完成")
            print("等待10分钟后开始下一个周期...")
            
            for i in range(600, 0, -1):
                minutes = i // 60
                seconds = i % 60
                print(f"\r下一个兑换周期开始的时间: {minutes:02d}:{seconds:02d}", end="")
                time.sleep(1)
            
            print("\n")
            cycle_count += 1
            
        except KeyboardInterrupt:
            print("\n停止兑换周期...")
            break
        except Exception as e:
            print(f"\n兑换周期中出错: {str(e)}")
            print("尝试继续下一个周期...")
            time.sleep(10)

def send_ini_to_self(private_keys):
    """向自身地址发送INI，金额为余额的3-5%"""
    for i, private_key in enumerate(private_keys, 1):
        try:
            bot = IniChainBot(private_key)
            account_info = f"账户 {i} | {bot.address[-4:]}"
            
            balance = w3.eth.get_balance(bot.address)
            formatted_balance = w3.from_wei(balance, 'ether')
            
            gas_price = bot.get_gas_price()
            estimated_gas = 21000
            gas_cost = gas_price * estimated_gas
            safe_balance = balance - gas_cost
            
            if safe_balance <= 0:
                print(f"[{account_info}] 余额不足以进行转账")
                print(f"[{account_info}] 当前余额: {formatted_balance:.6f} INI")
                print(f"[{account_info}] 估算Gas费用: {w3.from_wei(gas_cost, 'ether'):.6f} INI")
                continue
            
            percentage = random.uniform(0.03, 0.05)
            amount_to_send = int(safe_balance * percentage)
            
            if amount_to_send <= 0:
                print(f"[{account_info}] 转账金额过小")
                continue
            
            print(f"\n[{account_info}] 开始向自身转账INI...")
            print(f"[{account_info}] 当前余额: {formatted_balance:.6f} INI")
            print(f"[{account_info}] 转账金额: {w3.from_wei(amount_to_send, 'ether'):.6f} INI ({percentage*100:.2f}%)")
            print(f"[{account_info}] Gas价格: {w3.from_wei(gas_price, 'gwei'):.2f} Gwei")
            
            transaction = {
                'from': bot.address,
                'to': bot.address,
                'value': amount_to_send,
                'gas': estimated_gas,
                'gasPrice': gas_price,
                'nonce': w3.eth.get_transaction_count(bot.address),
                'chainId': CHAIN_ID
            }
            
            signed_txn = w3.eth.account.sign_transaction(transaction, bot.account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = bot.wait_for_transaction(tx_hash)
            
            if receipt and receipt['status'] == 1:
                print(f"[{account_info}] 转账成功!")
                print(f"[{account_info}] 交易哈希: {tx_hash.hex()}")
            else:
                print(f"[{account_info}] 转账失败!")
                
        except Exception as e:
            print(f"[{account_info}] 出错: {str(e)}")
        
        time.sleep(5)

def main():
    try:
        with open("privatekey.txt", "r") as f:
            private_keys = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("错误: 找不到文件 privatekey.txt!")
        return
        
    while True:
        choice = show_menu()
        
        if choice == "1":
            process_accounts(private_keys, "status")
        elif choice == "2":
            process_accounts(private_keys, "checkin")
        elif choice == "3":
            cycle_swap(private_keys)
        elif choice == "4":
            print("\n=== 创建代币 ===")
            name = input("代币全名: ")
            symbol = input("代币简称: ")
            try:
                total_supply = float(input("发行代币数量: "))
                decimals = int(input("代币小数位数 (默认18): ") or "18")
            except ValueError:
                print("错误: 代币数量或小数位数输入无效!")
                continue
                
            for i, private_key in enumerate(private_keys, 1):
                bot = IniChainBot(private_key)
                account_info = f"账户 #{i}"
                bot.create_token(name, symbol, total_supply, decimals, account_info)
        elif choice == "5":
            print("\n=== 自动每日签到与兑换 ===")
            print("机器人将自动执行每日签到和兑换")
            print("按 Ctrl+C 停止")
            auto_daily_and_swap(private_keys)
        elif choice == "6":
            print("\n=== 发送INI到自身 ===")
            print("机器人将发送余额的3-5% INI到自身地址")
            send_ini_to_self(private_keys)
        elif choice == "7":
            print("\n感谢您使用机器人!")
            break
        else:
            print("\n无效的选择!")

if __name__ == "__main__":
    main()
