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
    user_agent="script:Payzoll:v1.0"
)

# ----------------------
# Global Data Directory (local CSV files storage)
# ----------------------
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# Default file names
DEFAULT_EMPLOYEE_CSV = "company_employees.csv"
DEFAULT_TRANSACTION_LOG = "bulk_transfer_log.csv"

# ----------------------
# Function: Chat with AI
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
        
        # Submit the post
        submission = subreddit.submit(title, selftext=body)
        
        # Fetch available flairs and match the correct one
        for flair in subreddit.flair.link_templates:
            if flair['text'].lower() == flair_text.lower():
                submission.flair.select(flair['id'])
                break
        else:
            return {"status": "error", "message": f"Flair '{flair_text}' not found in subreddit '{subreddit_name}'."}

        return {"status": "success", "message": "Reddit post submitted successfully with flair!"}
    
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
        
        # Return receipts directly as an array, not as a stringified JSON
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
            
            # Log the transaction details locally
            transaction_data = {
                "tx_hash": tx_hash.hex(),
                "status": receipt.status,
                "recipient": recipients[i],
                "amount": values[i],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            log_bulk_transfer_transaction(log_csv_path, transaction_data)
        
        # Return receipts directly as an array, not as a stringified JSON
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
        
        # Build a summary string from the transaction log
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
# Function: Use AI to identify and execute the appropriate function
# ----------------------
def process_and_execute_message(message):
    """
    Analyzes a message using GPT to determine which function to call, then executes it.
    """
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
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "employee_analytics",
            "description": "Get analytics about employees from the default CSV file",
            "parameters": {
                "type": "object",
                "properties": {}
            }
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
            "description": "Transfer Sonic to all the employees do the complete payroll",
            "parameters": {
                "type": "object",
                "properties": {},
            }
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
        }
    ]
    
    # System prompt for the AI
    system_prompt = {
    "role": "system",
    "content": (
        "You are PayZollBot, the intelligent assistant for PayZoll—a revolutionary payroll platform "
        "that makes payroll fast, secure, and seamless by integrating Web3 technology with AI-driven automation. "
        "PayZoll simplifies the complex world of crypto payroll by handling multi-chain transactions, stable token swaps, "
        "and efficient fiat off-ramps, ensuring non-Web3 users have a smooth, user-friendly experience similar to traditional "
        "payroll systems. Your tasks include managing payroll transactions, generating concise social media posts for Twitter and Reddit, "
        "providing analytics and insights on payroll data, and interacting with users to execute functions that process crypto-based payroll. "
        "Remember, PayZoll addresses key challenges: reducing the steep learning curve, enabling efficient off-ramps, and automating compliance and reporting. "
        "Your responses should always be clear, concise, and aligned with PayZoll's goals: speed, security, automated compliance, and user-friendly interaction. "
        "When a user makes a request, determine which function best fits the query and provide a response that either executes the function or communicates "
        "the next step in a simple, one-liner format."
  )
}

    
    # Call OpenAI API with function calling enabled
    messages = [system_prompt, {"role": "user", "content": message}]
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        functions=functions,
        function_call="auto"
    )
    
    response_message = response.choices[0].message
    
    # Prepare the response for the user
    result = {
        "ai_message": response_message.get("content", "I've processed your request."),
        "function_details": None,
        "function_result": None
    }
    
    # If a function call was identified
    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]
        function_args_str = response_message["function_call"]["arguments"]
        
        try:
            function_args = json.loads(function_args_str)
            result["function_details"] = {
                "name": function_name,
                "arguments": function_args
            }
            
            # Execute the appropriate function based on name
            if function_name == "chat_with_ai":
                result["function_result"] = chat_with_ai(function_args.get("user_message", message))
            
            elif function_name == "post_on_twitter":
                result["function_result"] = post_on_twitter(function_args.get("body"))
            
            elif function_name == "post_on_reddit":
                result["function_result"] = post_on_reddit(
                    function_args.get("subreddit"),
                    function_args.get("title"),
                    function_args.get("body")
                )
            
            elif function_name == "generate_post":
                result["function_result"] = generate_post(
                    function_args.get("platform"),
                    function_args.get("description")
                )
            
            elif function_name == "get_company_details":
                result["function_result"] = get_company_details()
            
            elif function_name == "employee_analytics":
                result["function_result"] = employee_analytics()
            
            elif function_name == "silent_bulk_transfer":
                result["function_result"] = silent_bulk_transfer(
                    function_args.get("rpc_url"),
                    function_args.get("employees_json")
                )
            elif function_name == "complete_bulk_transfer":
                result["function_result"] = complete_bulk_transfer()
            elif function_name == "transaction_insights":
                result["function_result"] = transaction_insights(
                    prompt=function_args.get("prompt", "Generate insights based on the transaction data.")
                )
            
            else:
                result["function_result"] = {
                    "status": "error",
                    "message": f"Unknown function: {function_name}"
                }
                
        except Exception as e:
            result["function_result"] = {
                "status": "error",
                "message": f"Error executing function: {str(e)}"
            }
    
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