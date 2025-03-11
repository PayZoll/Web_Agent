from flask import Flask, request, jsonify
import openai
import json
import os
import tweepy
import praw
from web3 import Web3
from dotenv import load_dotenv
import csv
from datetime import datetime
import re
from flask_cors import CORS
import random

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes by default

# ----------------------
# OpenAI API configuration
# ----------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

# ----------------------
# Twitter API configuration using Tweepy
# ----------------------
twitter_client = tweepy.Client(
    bearer_token=os.getenv("BEARER_KEY"),
    consumer_key=os.getenv("CONSUMER_KEY"),
    consumer_secret=os.getenv("CONSUMER_SECRET"),
    access_token=os.getenv("ACCESS_KEY"),
    access_token_secret=os.getenv("ACCESS_SECRET")
)

# ----------------------
# Reddit API configuration using PRAW
# ----------------------
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# ----------------------
# Global Data Directory (local CSV files storage)
# ----------------------
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Chat history file for conversation memory
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")
if not os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump([], f)

# Default file names
DEFAULT_EMPLOYEE_CSV = "company_employees.csv"
DEFAULT_TRANSACTION_LOG = "bulk_transfer_log.csv"

# ----------------------
# Chat History Functions
# ----------------------
def load_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f)

def append_to_chat_history(role, content):
    history = load_chat_history()
    history.append({"role": role, "content": content})
    save_chat_history(history)

# ----------------------
# Function: Chat with AI (direct prompt)
# ----------------------
def chat_with_ai(user_message):
    """
    Process a user message with GPT.
    """
    messages = [{"role": "system", "content": "You are an AI assistant."}]
    messages.append({"role": "user", "content": user_message})
    
    response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
    ai_response = response["choices"][0]["message"]["content"]
    
    return {"status": "success", "response": ai_response}

# ----------------------
# Function: Post on Twitter
# ----------------------
def post_on_twitter(body):
    """
    Posts a tweet using the Twitter API.
    """
    try:
        twitter_client.create_tweet(text=body)
        return {"status": "success", "message": "Tweet posted successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------
# Function: Post on Reddit
# ----------------------
def post_on_reddit(subreddit_name, title, body):
    """
    Posts on Reddit using the PRAW API.
    """
    try:
        subreddit = reddit.subreddit(subreddit_name)
        submission = subreddit.submit(title, selftext=body)
        return {"status": "success", "message": "Reddit post submitted successfully!"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------
# Function: Generate Social Media Post
# ----------------------
def generate_post(platform, description):
    """
    Generates a one-liner social media post using OpenAI's GPT.
    """
    if platform == "twitter":
        prompt = f"Generate a one-liner tweet about: {description}"
    elif platform == "reddit":
        prompt = f"Generate a one-liner reddit post about: {description}"
    else:
        return {"status": "error", "message": "Platform not supported. Choose 'twitter' or 'reddit'."}
    
    messages = [
        {"role": "system", "content": "You are a creative social media content generator."},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
    generated_post = response["choices"][0]["message"]["content"].strip()
    
    return {"status": "success", "post": generated_post}

# ----------------------
# Function: Get Company Details
# ----------------------
def get_company_details(filename=None):
    """
    Reads employee details from the specified CSV file in the DATA_DIR.
    """
    if filename is None:
        filename = DEFAULT_EMPLOYEE_CSV
        
    file_path = os.path.join(DATA_DIR, filename)
    try:
        employees = []
        with open(file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['salary'] = float(row.get('salary', 0))
                row['work_hours'] = float(row.get('work_hours', 0))
                employees.append(row)
        return {"status": "success", "data": employees}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------
# Function: Employee Analytics
# ----------------------
def employee_analytics(filename=None):
    """
    Returns insights like total employees, average salary, and average work hours.
    """
    if filename is None:
        filename = DEFAULT_EMPLOYEE_CSV
        
    file_path = os.path.join(DATA_DIR, filename)
    try:
        employees = []
        with open(file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['salary'] = float(row.get('salary', 0))
                row['work_hours'] = float(row.get('work_hours', 0))
                employees.append(row)
        if not employees:
            return {"status": "error", "message": "No employee data found."}
        
        total_employees = len(employees)
        total_salary = sum(emp['salary'] for emp in employees)
        avg_salary = total_salary / total_employees
        total_work_hours = sum(emp['work_hours'] for emp in employees)
        avg_work_hours = total_work_hours / total_employees
        
        insights = {
            'total_employees': total_employees,
            'total_salary': total_salary,
            'average_salary': avg_salary,
            'total_work_hours': total_work_hours,
            'average_work_hours': avg_work_hours
        }
        return {"status": "success", "data": insights}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------
# Utility: Log Bulk Transfer Transaction
# ----------------------
def log_bulk_transfer_transaction(log_csv_path, transaction_data):
    """
    Logs a transaction to a CSV file.
    transaction_data: dict with keys: tx_hash, status, recipient, amount, timestamp
    """
    file_exists = os.path.exists(log_csv_path)
    with open(log_csv_path, mode='a', newline='') as file:
        fieldnames = ['tx_hash', 'status', 'recipient', 'amount', 'timestamp']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(transaction_data)
    return True

# ----------------------
# Function: Complete Bulk Transfer with Logging
# ----------------------
def complete_bulk_transfer(log_filename=None):
    """
    Executes bulk transfers and logs each transaction to a local CSV file.
    """
    print("Complete Bulk Transfer")
    if log_filename is None:
        log_filename = DEFAULT_TRANSACTION_LOG
        
    log_csv_path = os.path.join(DATA_DIR, log_filename)

    try:
        w3 = Web3(Web3.HTTPProvider("https://rpc.blaze.soniclabs.com/"))
        if not w3.is_connected():
            return {"status": "error", "message": "Could not connect to Ethereum node"}
        
        PRIVATE_KEY = os.getenv("PRIVATE_KEY")
        account = w3.eth.account.from_key(PRIVATE_KEY)
        sender_address = account.address

        # Read employee data from CSV file
        file_path = os.path.join(DATA_DIR, DEFAULT_EMPLOYEE_CSV)
        employees = []
        with open(file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                employees.append(row)

        recipients = [emp["accountId"] for emp in employees]
        values = [w3.to_wei(str(emp["salary"]), "ether") for emp in employees]

        nonce = w3.eth.get_transaction_count(sender_address, "pending")
        receipts = []
        for i in range(len(recipients)):
            tx = {
                "to": recipients[i],
                "value": values[i],
                "nonce": nonce,
                "gas": 21000,
                "maxPriorityFeePerGas": w3.to_wei("2", "gwei"),
                "maxFeePerGas": w3.to_wei("50", "gwei"),
                "chainId": w3.eth.chain_id
            }
            nonce += 1
            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            receipts.append({"tx_hash": tx_hash.hex(), "status": receipt.status})
            
            # Log the transaction details locally
            transaction_data = {
                "tx_hash": tx_hash.hex(),
                "status": receipt.status,
                "recipient": recipients[i],
                "amount": values[i],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            log_bulk_transfer_transaction(log_csv_path, transaction_data)
        
        return {"status": "success", "data": receipts}
    except Exception as e:
        print(f"Error in bulk transfer: {e}")
        return {"status": "error", "message": f"Error in bulk transfer: {e}"}

# ----------------------
# Function: Silent Bulk Transfer with Logging
# ----------------------
def silent_bulk_transfer(rpc_url, employees_json, log_filename=None):
    """
    Executes bulk transfers and logs each transaction to a local CSV file.
    """
    if log_filename is None:
        log_filename = DEFAULT_TRANSACTION_LOG
        
    log_csv_path = os.path.join(DATA_DIR, log_filename)

    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            return {"status": "error", "message": "Could not connect to Ethereum node"}
        
        PRIVATE_KEY = os.getenv("PRIVATE_KEY")
        account = w3.eth.account.from_key(PRIVATE_KEY)
        sender_address = account.address

        if isinstance(employees_json, str):
            employees = json.loads(employees_json)
        else:
            employees = employees_json

        recipients = [emp["accountId"] for emp in employees]
        values = [w3.to_wei(str(emp["salary"]), "ether") for emp in employees]

        nonce = w3.eth.get_transaction_count(sender_address, "pending")
        receipts = []
        for i in range(len(recipients)):
            tx = {
                "to": recipients[i],
                "value": values[i],
                "nonce": nonce,
                "gas": 21000,
                "maxPriorityFeePerGas": w3.to_wei("2", "gwei"),
                "maxFeePerGas": w3.to_wei("50", "gwei"),
                "chainId": w3.eth.chain_id
            }
            nonce += 1
            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            receipts.append({"tx_hash": tx_hash.hex(), "status": receipt.status})
            
            transaction_data = {
                "tx_hash": tx_hash.hex(),
                "status": receipt.status,
                "recipient": recipients[i],
                "amount": values[i],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            log_bulk_transfer_transaction(log_csv_path, transaction_data)
        
        return {"status": "success", "data": receipts}
    except Exception as e:
        print(f"Error in bulk transfer: {e}")
        return {"status": "error", "message": f"Error in bulk transfer: {e}"}

# ----------------------
# Function: Transaction Insights
# ----------------------
def transaction_insights(log_filename=None, prompt="Generate insights based on the transaction data."):
    """
    Reads the transaction log and generates insights using OpenAI's GPT.
    """
    if log_filename is None:
        log_filename = DEFAULT_TRANSACTION_LOG
        
    log_csv_path = os.path.join(DATA_DIR, log_filename)
    try:
        transactions = []
        with open(log_csv_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                transactions.append(row)
        if not transactions:
            return {"status": "error", "message": "No transactions found for insights."}
        
        summary = f"Transaction Log Summary:\nTotal Transactions: {len(transactions)}\n"
        for tx in transactions:
            summary += f"Tx Hash: {tx['tx_hash']}, Recipient: {tx['recipient']}, Amount: {tx['amount']}, Status: {tx['status']}, Timestamp: {tx['timestamp']}\n"
        
        messages = [
            {"role": "system", "content": "You are an expert analyst."},
            {"role": "user", "content": f"{prompt}\n{summary}"}
        ]
        response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
        insights = response["choices"][0]["message"]["content"]
        return {"status": "success", "data": insights}
    except Exception as e:
        return {"status": "error", "message": f"Error generating insights: {e}"}

# ----------------------
# New Function: Get Current Time
# ----------------------
def get_current_time():
    """
    Returns the current server time.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"status": "success", "current_time": now}

# ----------------------
# New Function: Random Motivational Quote
# ----------------------
def random_quote():
    """
    Returns a random motivational quote.
    """
    quotes = [
        "Believe you can and you're halfway there.",
        "The only way to do great work is to love what you do.",
        "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "Keep your face always toward the sunshine—and shadows will fall behind you."
    ]
    return {"status": "success", "quote": random.choice(quotes)}

# ----------------------
# New Function: Calculate Payroll Savings
# ----------------------
def calculate_payroll_savings(traditional_cost, employee_count):
    """
    Calculate estimated savings when using PayZoll compared to traditional payroll systems.
    """
    try:
        traditional_cost = float(traditional_cost)
        employee_count = int(employee_count)
        
        # PayZoll costs approximately 80% less than traditional systems
        payzoll_cost = traditional_cost * 0.2
        savings = traditional_cost - payzoll_cost
        
        # Monthly maintenance fee
        monthly_fee = employee_count * 5  # $5 per employee per month
        
        result = {
            "traditional_cost": traditional_cost,
            "payzoll_cost": payzoll_cost,
            "monthly_fee": monthly_fee,
            "total_savings": savings - monthly_fee,
            "savings_percentage": ((traditional_cost - (payzoll_cost + monthly_fee)) / traditional_cost) * 100
        }
        
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------
# New Function: Get PayZoll Features
# ----------------------
def get_payzoll_features():
    """
    Returns the key features of the PayZoll platform.
    """
    features = [
        {
            "name": "One-Click Global Payroll",
            "description": "Pay employees worldwide instantly—no borders, no delays."
        },
        {
            "name": "Cost-Saving Blockchain",
            "description": "Reduce fees by 80% with decentralized multi-chain efficiency."
        },
        {
            "name": "Transparent Ledger",
            "description": "Every transaction is verifiable and tamper-proof."
        },
        {
            "name": "Smart Contract Security",
            "description": "Rules are locked in code—unchangeable and trustworthy."
        },
        {
            "name": "AI-Driven Automation",
            "description": "From tax compliance to analytics, our AI agents handle it all."
        },
        {
            "name": "Multi-Chain Support",
            "description": "Operates across multiple blockchains for maximum flexibility and lower costs."
        },
        {
            "name": "Stablecoin Integration",
            "description": "Auto-swaps to stablecoins like USDT to eliminate volatility concerns."
        },
        {
            "name": "Fiat Off-Ramping",
            "description": "Seamless conversion from crypto to traditional currency when needed."
        }
    ]
    return {"status": "success", "data": features}

# ----------------------
# New Function: Get PayZoll FAQ
# ----------------------
def get_payzoll_faq():
    """
    Returns frequently asked questions about PayZoll.
    """
    faqs = [
        {
            "question": "How does PayZoll handle cryptocurrency volatility?",
            "answer": "PayZoll automatically converts to stablecoins like USDT to ensure payment values remain consistent, protecting both employers and employees from market fluctuations."
        },
        {
            "question": "Is PayZoll compliant with international tax regulations?",
            "answer": "Yes, our AI-driven system automatically handles tax compliance across different jurisdictions, making international payments seamless and legally compliant."
        },
        {
            "question": "What blockchains does PayZoll support?",
            "answer": "PayZoll is built with multi-chain architecture, currently supporting Ethereum, BNB Chain, Polygon, and Sonic blockchain networks, with more integrations planned."
        },
        {
            "question": "How secure is PayZoll?",
            "answer": "PayZoll utilizes smart contract security, immutable blockchain records, and enterprise-grade encryption to ensure your payroll data and transactions are completely secure."
        },
        {
            "question": "What are the costs associated with using PayZoll?",
            "answer": "PayZoll charges a $5/employee/month maintenance fee, 3% for fiat off-ramping, and 3% for real-time payroll streaming. Overall, businesses save up to 80% compared to traditional payroll systems."
        }
    ]
    return {"status": "success", "data": faqs}

# ----------------------
# New Function: Get Web3 Payroll Guide
# ----------------------
def get_web3_payroll_guide():
    """
    Returns educational information about Web3 payroll concepts.
    """
    guide = {
        "title": "Understanding Web3 Payroll",
        "introduction": "Web3 payroll leverages blockchain technology to revolutionize how employees are paid, offering greater transparency, lower costs, and global accessibility.",
        "key_concepts": [
            {
                "name": "Blockchain-Based Transactions",
                "description": "Payments occur on decentralized blockchains, eliminating intermediaries and reducing costs."
            },
            {
                "name": "Smart Contracts",
                "description": "Self-executing contracts with predefined rules that automatically process payroll when conditions are met."
            },
            {
                "name": "Cryptocurrency Payments",
                "description": "Employees can be paid in various cryptocurrencies or stablecoins, enabling borderless transactions."
            },
            {
                "name": "Stablecoins",
                "description": "Cryptocurrencies pegged to stable assets like USD, reducing volatility concerns in payroll."
            },
            {
                "name": "Multi-Chain Operations",
                "description": "Using multiple blockchain networks to optimize for speed, cost, and accessibility."
            }
        ],
        "benefits": [
            "Reduced transaction fees (up to 80% savings)",
            "Near-instant global payments",
            "Transparent and verifiable transaction records",
            "Programmable payment schedules and conditions",
            "Elimination of traditional banking delays",
            "Seamless international payments without currency conversion issues"
        ]
    }
    return {"status": "success", "data": guide}

# ----------------------
# New Function: Compare Traditional vs Web3 Payroll
# ----------------------
def compare_payroll_systems():
    """
    Returns a comparison between traditional and Web3 payroll systems.
    """
    comparison = {
        "categories": [
            {
                "category": "Transaction Speed",
                "traditional": "2-5 business days for international payments",
                "web3": "Near-instant (seconds to minutes) regardless of location"
            },
            {
                "category": "Transaction Costs",
                "traditional": "High fees (3-7% for international transfers)",
                "web3": "Low fees (80% less than traditional systems)"
            },
            {
                "category": "Global Accessibility",
                "traditional": "Complex process with multiple intermediaries",
                "web3": "Borderless by design, pay anyone with a wallet address"
            },
            {
                "category": "Transparency",
                "traditional": "Limited visibility into transaction processing",
                "web3": "Complete transparency with blockchain verification"
            },
            {
                "category": "Security",
                "traditional": "Centralized systems vulnerable to single points of failure",
                "web3": "Decentralized, cryptographically secured transactions"
            },
            {
                "category": "Automation",
                "traditional": "Limited, often requires manual intervention",
                "web3": "Highly programmable through smart contracts"
            },
            {
                "category": "Banking Requirements",
                "traditional": "Requires bank accounts and relationships",
                "web3": "Only requires crypto wallet addresses"
            }
        ]
    }
    return {"status": "success", "data": comparison}

# ----------------------
# New Function: Get Case Studies
# ----------------------
def get_case_studies():
    """
    Returns case studies of companies using PayZoll.
    """
    case_studies = [
        {
            "company": "Global Tech Innovations",
            "industry": "Software Development",
            "employees": 250,
            "countries": 15,
            "challenge": "Managing payroll across 15 countries with different banking systems and currencies",
            "solution": "Implemented PayZoll's multi-chain payroll system with stablecoin payments",
            "results": [
                "Reduced payroll processing time from 5 days to 2 hours",
                "Saved $12,000 monthly in banking and transaction fees",
                "Eliminated payment delays and employee complaints",
                "Streamlined compliance across multiple jurisdictions"
            ]
        },
        {
            "company": "Decentralized Finance Corp",
            "industry": "Financial Services",
            "employees": 75,
            "countries": 8,
            "challenge": "Needed a payroll solution aligned with their Web3-first company philosophy",
            "solution": "Adopted PayZoll with direct crypto payments and smart contract automation",
            "results": [
                "Achieved 100% transparent payroll visible on blockchain",
                "Implemented performance-based smart contracts for bonuses",
                "Reduced HR workload by 35% through automation",
                "Attracted top talent with innovative crypto payment options"
            ]
        }
    ]
    return {"status": "success", "data": case_studies}

# ----------------------
# New Function: Get Implementation Guide
# ----------------------
def get_implementation_guide():
    """
    Returns step-by-step guide for implementing PayZoll.
    """
    guide = {
        "title": "PayZoll Implementation Guide",
        "steps": [
            {
                "step": 1,
                "name": "Initial Setup",
                "description": "Create your PayZoll account and connect your organization's wallet",
                "estimated_time": "1 day"
            },
            {
                "step": 2,
                "name": "Employee Onboarding",
                "description": "Add employees and their wallet addresses to the system",
                "estimated_time": "2-3 days"
            },
            {
                "step": 3,
                "name": "Payment Configuration",
                "description": "Set up payment schedules, currencies, and conversion preferences",
                "estimated_time": "1 day"
            },
            {
                "step": 4,
                "name": "Compliance Setup",
                "description": "Configure tax withholding and compliance settings for each jurisdiction",
                "estimated_time": "2-5 days"
            },
            {
                "step": 5,
                "name": "Testing Phase",
                "description": "Run test payments to verify system functionality",
                "estimated_time": "1 week"
            },
            {
                "step": 6,
                "name": "Full Deployment",
                "description": "Transition your payroll fully to PayZoll",
                "estimated_time": "1 pay period"
            }
        ],
        "total_time": "Approximately 2-3 weeks for full implementation"
    }
    return {"status": "success", "data": guide}

# ----------------------
# New Function: Support Crypto Knowledge Query
# ----------------------
def crypto_knowledge_query(query):
    """
    Provides information about cryptocurrency and blockchain concepts related to payroll.
    """
    try:
        prompt = f"Explain the following cryptocurrency or blockchain payroll concept in simple terms: {query}"
        
        messages = [
            {"role": "system", "content": "You are an expert in cryptocurrency, blockchain technology, and Web3 payroll systems. Provide clear, concise explanations without technical jargon."},
            {"role": "user", "content": prompt}
        ]
        
        response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
        explanation = response["choices"][0]["message"]["content"].strip()
        
        return {"status": "success", "data": {
            "query": query,
            "explanation": explanation
        }}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------
# New Function: Generate Payroll Schedule
# ----------------------
def generate_payroll_schedule(start_date, frequency, employees_count):
    """
    Generates a recommended payroll schedule based on parameters.
    """
    try:
        from datetime import datetime, timedelta
        
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        schedule = []
        
        frequencies = {
            "weekly": 7,
            "biweekly": 14,
            "monthly": 30
        }
        
        if frequency not in frequencies:
            return {"status": "error", "message": "Invalid frequency. Please choose weekly, biweekly, or monthly."}
        
        days_increment = frequencies[frequency]
        
        # Generate 6 pay periods
        current_date = start_date
        for i in range(6):
            process_date = current_date - timedelta(days=2)  # Process 2 days before payment
            
            schedule.append({
                "pay_period": i + 1,
                "process_date": process_date.strftime("%Y-%m-%d"),
                "payment_date": current_date.strftime("%Y-%m-%d"),
                "employees": employees_count,
                "estimated_gas_cost": round(0.002 * employees_count, 4),
                "estimated_process_time": "5 minutes"
            })
            
            current_date += timedelta(days=days_increment)
        
        return {"status": "success", "data": {
            "frequency": frequency,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "schedule": schedule
        }}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------
# Function: Use AI to identify and execute the appropriate function with chat history memory
# ----------------------
def process_and_execute_message(message):
    """
    Analyzes a message using GPT to determine which function to call, while including chat history.
    If no function is matched, returns a plain GPT response.
    """
    # Load existing chat history and add the current user message
    chat_history = load_chat_history()

    # Enhanced system prompt with comprehensive PayZoll information
    system_prompt = {
        "role": "system",
        "content": (
            "You are PayZollBot, the intelligent assistant for PayZoll—the revolutionary decentralized payroll platform "
            "that's redefining how businesses pay their workforce globally. PayZoll combines blockchain innovation with "
            "cutting-edge AI to deliver lightning-fast, secure, and scalable payroll solutions—bridging the gap between "
            "Web2 simplicity and Web3 potential.\n\n"
            
            "PayZoll's core capabilities include:\n"
            "• Global Reach: Pay your entire workforce across borders in seconds with one click.\n"
            "• Cost Efficiency: Slash transaction costs by 80% using multi-chain blockchain technology.\n"
            "• Security: Immutable ledger records and smart contracts protect every transaction.\n"
            "• AI Automation: Eliminate errors with seamless, hands-off payroll management.\n"
            "• Scalability: Built for businesses from 10 to 10,000+ employees.\n"
            "• Volatility Protection: Auto-swaps to stablecoins (USDT) ensure payment value stability.\n"
            "• Fiat Integration: Seamless off-ramping from crypto to traditional currencies.\n"
            "• Multi-Chain Architecture: Works across Ethereum, BNB Chain, Polygon, and Sonic networks.\n"
            "• Compliance Management: AI-driven tax and regulatory compliance across jurisdictions.\n\n"
            
            "PayZoll has won first place at ETH India 2024 for pioneering multi-chain payroll architecture and "
            "first place at Binance Web3 Build for Web3 payroll excellence. The platform integrates with Sonic "
            "blockchain for enhanced AI agent capabilities.\n\n"
            
            "As PayZollBot, provide knowledgeable, helpful responses about Web3 payroll concepts, blockchain "
            "technology, cryptocurrency, and PayZoll's features. Use previous chat history for context "
            "and deliver clear, concise, and actionable responses. If a function is available to handle the request, "
            "use it. Otherwise, provide informative answers that showcase PayZoll's expertise."
        )
    }
    
    # Define available functions and their parameters
    functions = [
        {
            "name": "chat_with_ai",
            "description": "Have a conversation with the AI assistant",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_message": {"type": "string", "description": "The message from the user"}
                },
                "required": ["user_message"]
            }
        },
        {
            "name": "post_on_twitter",
            "description": "Post a message on Twitter",
            "parameters": {
                "type": "object",
                "properties": {
                    "body": {"type": "string", "description": "The content of the tweet"}
                },
                "required": ["body"]
            }
        },
        {
            "name": "post_on_reddit",
            "description": "Post a message on Reddit",
            "parameters": {
                "type": "object",
                "properties": {
                    "subreddit": {"type": "string", "description": "The subreddit to post to"},
                    "title": {"type": "string", "description": "The title of the Reddit post"},
                    "body": {"type": "string", "description": "The content of the Reddit post"}
                },
                "required": ["subreddit", "title", "body"]
            }
        },
        {
            "name": "generate_post",
            "description": "Generate a social media post",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "description": "The platform to generate for (twitter or reddit)"},
                    "description": {"type": "string", "description": "Description of what the post should be about"}
                },
                "required": ["platform", "description"]
            }
        },
        {
            "name": "get_company_details",
            "description": "Get details about employees from the default CSV file",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "employee_analytics",
            "description": "Get analytics about employees from the default CSV file",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "silent_bulk_transfer",
            "description": "Transfer Sonic to multiple employees and log to default transaction log",
            "parameters": {
                "type": "object",
                "properties": {
                    "rpc_url": {"type": "string", "description": "RPC URL for the Sonic node"},
                    "employees_json": {"type": "string", "description": "JSON string of employees and salaries"}
                },
                "required": ["rpc_url", "employees_json"]
            }
        },
        {
            "name": "complete_bulk_transfer",
            "description": "Transfer Sonic to all the employees to complete payroll",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "transaction_insights",
            "description": "Get insights from the default transaction logs",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Prompt for generating insights"}
                }
            }
        },
        {
            "name": "get_current_time",
            "description": "Get the current server time",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "random_quote",
            "description": "Get a random motivational quote",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "calculate_payroll_savings",
            "description": "Calculate estimated savings when using PayZoll compared to traditional payroll",
            "parameters": {
                "type": "object",
                "properties": {
                    "traditional_cost": {"type": "number", "description": "Current cost of traditional payroll"},
                    "employee_count": {"type": "integer", "description": "Number of employees"}
                },
                "required": ["traditional_cost", "employee_count"]
            }
        },
        {
            "name": "get_payzoll_features",
            "description": "Get a list of PayZoll platform features",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "get_payzoll_faq",
            "description": "Get frequently asked questions about PayZoll",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "get_web3_payroll_guide",
            "description": "Get educational guide about Web3 payroll concepts",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "compare_payroll_systems",
            "description": "Compare traditional and Web3 payroll systems",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "get_case_studies",
            "description": "Get case studies of companies using PayZoll",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "get_implementation_guide",
            "description": "Get step-by-step guide for implementing PayZoll",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "crypto_knowledge_query",
            "description": "Get information about cryptocurrency and blockchain concepts",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The crypto/blockchain concept to explain"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "generate_payroll_schedule",
            "description": "Generate a recommended payroll schedule",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                    "frequency": {"type": "string", "description": "Frequency (weekly, biweekly, monthly)"},
                    "employees_count": {"type": "integer", "description": "Number of employees"}
                },
                "required": ["start_date", "frequency", "employees_count"]
            }
        }
    ]
    
    # Build messages list including system prompt and previous chat history
    messages = [system_prompt] + chat_history + [{"role": "user", "content": message}]
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        functions=functions,
        function_call="auto"
    )
    
    response_message = response.choices[0].message

    result = {
        "ai_message": response_message.get("content", "I've processed your request."),
        "function_details": None,
        "function_result": None
    }
    
    # If a function call was identified, process it
    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]
        function_args_str = response_message["function_call"]["arguments"]
        
        print(f"Function called: {function_name}")
        
        try:
            function_args = json.loads(function_args_str)
            result["function_details"] = {
                "name": function_name,
                "arguments": function_args
            }
            
            # Original functions
            if function_name == "chat_with_ai":
                print("Executing: chat_with_ai")
                result["function_result"] = chat_with_ai(function_args.get("user_message", message))
            elif function_name == "post_on_twitter":
                print("Executing: post_on_twitter")
                result["function_result"] = post_on_twitter(function_args.get("body"))
            elif function_name == "post_on_reddit":
                print("Executing: post_on_reddit")
                result["function_result"] = post_on_reddit(
                    function_args.get("subreddit"),
                    function_args.get("title"),
                    function_args.get("body")
                )
            elif function_name == "generate_post":
                print("Executing: generate_post")
                result["function_result"] = generate_post(
                    function_args.get("platform"),
                    function_args.get("description")
                )
            elif function_name == "get_company_details":
                print("Executing: get_company_details")
                result["function_result"] = get_company_details()
            elif function_name == "employee_analytics":
                print("Executing: employee_analytics")
                result["function_result"] = employee_analytics()
            elif function_name == "silent_bulk_transfer":
                print("Executing: silent_bulk_transfer")
                result["function_result"] = silent_bulk_transfer(
                    function_args.get("rpc_url"),
                    function_args.get("employees_json")
                )
            elif function_name == "complete_bulk_transfer":
                print("Executing: complete_bulk_transfer")
                result["function_result"] = complete_bulk_transfer()
            elif function_name == "transaction_insights":
                print("Executing: transaction_insights")
                result["function_result"] = transaction_insights(
                    prompt=function_args.get("prompt", "Generate insights based on the transaction data.")
                )
            elif function_name == "get_current_time":
                print("Executing: get_current_time")
                result["function_result"] = get_current_time()
            elif function_name == "random_quote":
                print("Executing: random_quote")
                result["function_result"] = random_quote()
            # New PayZoll-specific functions
            elif function_name == "calculate_payroll_savings":
                print("Executing: calculate_payroll_savings")
                result["function_result"] = calculate_payroll_savings(
                    function_args.get("traditional_cost"),
                    function_args.get("employee_count")
                )
            elif function_name == "get_payzoll_features":
                print("Executing: get_payzoll_features")
                result["function_result"] = get_payzoll_features()
            elif function_name == "get_payzoll_faq":
                print("Executing: get_payzoll_faq")
                result["function_result"] = get_payzoll_faq()
            elif function_name == "get_web3_payroll_guide":
                print("Executing: get_web3_payroll_guide")
                result["function_result"] = get_web3_payroll_guide()
            elif function_name == "compare_payroll_systems":
                print("Executing: compare_payroll_systems")
                result["function_result"] = compare_payroll_systems()
            elif function_name == "get_case_studies":
                print("Executing: get_case_studies")
                result["function_result"] = get_case_studies()
            elif function_name == "get_implementation_guide":
                print("Executing: get_implementation_guide")
                result["function_result"] = get_implementation_guide()
            elif function_name == "crypto_knowledge_query":
                print("Executing: crypto_knowledge_query")
                result["function_result"] = crypto_knowledge_query(function_args.get("query"))
            elif function_name == "generate_payroll_schedule":
                print("Executing: generate_payroll_schedule")
                result["function_result"] = generate_payroll_schedule(
                    function_args.get("start_date"),
                    function_args.get("frequency"),
                    function_args.get("employees_count")
                )
            else:
                print(f"Unknown function: {function_name}")
                result["function_result"] = {
                    "status": "error",
                    "message": f"Unknown function: {function_name}"
                }
                
        except Exception as e:
            print(f"Error executing function {function_name}: {str(e)}")
            result["function_result"] = {
                "status": "error",
                "message": f"Error executing function: {str(e)}"
            }
    # If no function call was matched, use the plain GPT answer
    else:
        result["ai_message"] = response_message.get("content", "I've processed your request.")
    
    # Append the current conversation to chat history (user and assistant messages)
    append_to_chat_history("user", message)
    if "ai_message" in result and result["ai_message"]:
        append_to_chat_history("assistant", result["ai_message"])
    
    return result

# ----------------------
# Single Unified Endpoint
# ----------------------
@app.route("/api", methods=["POST"])
def unified_api():
    """
    Single endpoint that handles all requests by analyzing the message content.
    Expects JSON: { "message": "<user message>" }
    """
    data = request.json
    message = data.get("message", "")
    print(f"Received request at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {data}")
    
    if not message:
        return jsonify({
            "status": "error",
            "message": "No message provided in the request"
        })
    
    result = process_and_execute_message(message)
    return jsonify(result)

# ----------------------
# Main entry point
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
