# PayZoll Agent Documentation

PayZoll is a revolutionary payroll platform that integrates Web3 technology with AI-driven automation. This Flask-based API simplifies crypto payroll management by handling multi-chain transactions, stable token swaps, and efficient fiat off-ramps while maintaining a user-friendly interface similar to traditional payroll systems.

## Installation

First, clone the repository and install dependencies:

```bash
git clone https://github.com/PayZoll/Web-Agent.git
cd server
pip install -r requirements.txt
cd ../client
npm i
```

Create a `.env` file with required environment variables:

```bash
OPENAI_API_KEY=your_openai_key
BEARER_KEY=your_bearer_token
CONSUMER_KEY=your_consumer_key
CONSUMER_SECRET=your_consumer_secret
ACCESS_KEY=your_access_key
ACCESS_SECRET=your_access_secret
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
PRIVATE_KEY=your_ethereum_private_key
```

## System Architecture

The PayZoll API operates as a unified platform integrating multiple services through a single entry point. Here's the high-level architecture:

```mermaid
flowchart TD
    classDef api fill:#00C4B4,color:#fff,stroke:#00C4B4
    classDef service fill:#1E88E5,color:#fff,stroke:#1E88E5
    classDef storage fill:#FFB300,color:#000,stroke:#FFB300
    classDef data fill:#AB47BC,color:#fff,stroke:#AB47BC

    Client[Client UI] --> API[/"PayZoll API"/]:::api
    API --> Processor[Message Processor]:::api
    
    subgraph Services["External Integrations"]
        Sonic["Sonic Blockchain"]:::service
        OpenAI["OpenAI LLM"]:::service
        Twitter["Twitter API"]:::service
        Reddit["Reddit API"]:::service
    end
    
    Processor --> Sonic
    Processor --> OpenAI
    Processor --> Twitter
    Processor --> Reddit
    
    subgraph Storage["Local Storage"]
        Employees["Employee Data CSV"]:::storage
        Logs["Transaction Logs CSV"]:::storage
    end
    
    Processor --> Employees
    Processor --> Logs
    
    subgraph Analytics["AI Analytics"]
        Engine["Analytics Engine"]:::data
        Insights["Insight Generator"]:::data
    end
    
    Processor --> Engine
    Engine --> Insights
    
    %% Legend
    subgraph Legend["Legend"]
        L1[API Core]:::api
        L2[External Services]:::service
        L3[Storage]:::storage
        L4[Analytics]:::data
    end
```

- **API Core**: Routes all requests efficiently.
- **Services**: Sonic for transactions, OpenAI for LLMs, Twitter/Reddit for social.
- **Storage**: Local CSV for employee data and logs.
- **Analytics**: AI-driven insights from payroll data.

---

## 🔄 Request Flow

See how requests travel through the system:

```mermaid
sequenceDiagram
    participant C as Client UI
    participant A as API Endpoint
    participant P as Message Processor
    participant O as OpenAI LLM
    participant S as Sonic Blockchain
    participant T as Twitter API
    participant R as Reddit API
    participant D as CSV Storage

    C->>+A: POST /api {"message": "..."} 

    alt Invalid Request
        A-->>C: {"status": "error", "message": "Invalid input"}
    else Valid Request
        A->>+P: Route Message 

        alt Chat Request
            P->>+O: "Chat with AI"
            O-->>-P: Response Text
            P-->>A: {"status": "success", "data": "..."} 
        else Social Post
            P->>+O: "Generate Post"
            O-->>-P: Post Content

            alt Twitter
                P->>+T: Post to Twitter
                T-->>-P: Success
            else Reddit
                P->>+R: Post to Reddit
                R-->>-P: Success
            end

            P-->>A: {"status": "success", "data": "Posted"}
        else Payroll Transfer
            P->>+O: "Process Payroll"
            O-->>-P: Transfer Instructions
            P->>+S: Execute Sonic Transfers
            S-->>-P: Transaction Hash
            P->>+D: Log Transaction
            D-->>-P: Saved
            P-->>A: {"status": "success", "data": "Transfers complete"} 
        else Analytics Request
            P->>+D: Read employee data
            D-->>-P: Employee records
            P->>+O: Generate insights
            O-->>-P: Analytics report
            P-->>A: {"status": "success", "data": "Analytics Report"}  
        end
    end
    A-->>C: Final Response
```

The sequence diagram above illustrates the complete lifecycle of a request through the PayZoll API, showing how different types of requests (chat, social media posts, payroll processing, and analytics) are handled through distinct paths while maintaining a unified entry point. Each request flows through the Message Processor, which determines the appropriate function to execute based on the message content.

## Usage Examples

Send requests to the API endpoint using JSON format:

```json
{
    "message": "Generate a Twitter post about our new product launch"
}

{
    "message": "Process bulk transfer for employees"
}

{
    "message": "Analyze employee salary trends"
}
```

## Available Functions

1. **Chat with AI**  - Function: `chat_with_ai`

- Purpose: Engage in conversation with the AI assistant
- Example Message: "What are the benefits of blockchain payroll?"

2. **Social Media Posts**  - Function: `generate_post`

- Purpose: Generate social media content for Twitter or Reddit
- Example Message: "Generate a Twitter post about our product launch"

3. **Payroll Processing**  - Function: `silent_bulk_transfer`

- Purpose: Execute bulk Sonic transfers to employees
- Parameters Required:
  - RPC URL for Sonic node
  - JSON string containing employee data and salaries

4. **Analytics**  - Function: `employee_analytics`

- Purpose: Generate insights from employee data
- Returns: Total employees, average salary, work hours analysis

5. **Transaction Insights**  - Function: `transaction_insights`

- Purpose: Analyze transaction logs using OpenAI
- Generates detailed reports on payroll transactions

## Error Handling

All API responses follow a standardized format:

```json
{
    "status": "success/error",
    "message": "Operation result or error description",
    "data": {}  // Optional data payload
}
```

## Security Considerations

1. **Environment Variables**  - All sensitive credentials are stored in `.env` files

- Never commit `.env` files to version control
- Use secure methods to manage environment variables in production

2. **API Security**  - All requests require proper JSON formatting

- Input validation occurs at multiple levels
- Error responses are sanitized to prevent information leakage

3. **Web3 Security**  - Private keys are stored securely in environment variables

- Transaction signing occurs locally
- Gas parameters are optimized for security and efficiency

## Development Notes

To run the development server:

```bash
python web_agent_4o.py
