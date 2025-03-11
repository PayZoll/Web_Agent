"use client";

import { useState, useRef, useEffect } from "react";
import { Bot, Send, Loader2, ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";

const sampleQueries = [
  { title: "Chat with AI", query: "Tell me about the different features of PayZoll." },
  { title: "Complete Payroll", query: "Pay the complete payroll for all the employees." },
  { title: "Post on Twitter", query: "Please post the following tweet: 'We are intoducing you to PayZoll, a new player in the Web3 Ecosystem'" },
  { title: "Transaction Insights", query: "Generate insights from our transaction log, focusing on trends in payment amounts." },
  { title: "Generate Post", query: "Generate a tweet about our new crypto payroll system that focuses on security features." },
  { title: "Bulk Transfer", query: "Execute a bulk transfer of ETH to these employees: [{\"accountId\": \"0xF947782C0CB4d3afa57912DA235894563950E2F4\", \"salary\": 0.2},{\"accountId\": \"0x8AA334072b03AB3F4cE4035A16a1Ee5Bde2521f1\", \"salary\": 0.2},{\"accountId\": \"0xe2e1862B5cA1743DF3F616DB927070AEC4c5B4fC\", \"salary\": 0.2}] using the Sonic RPC URL: https://rpc.blaze.soniclabs.com/" },
  { title: "Employee Details", query: "Retrieve all employee details from the company_employees.csv file." },
  { title: "Analytics", query: "Show me analytics for our employee data including average salary and work hours." },
  {
    title: "Post on Reddit",
    query: "Post on the payzoll_test subreddit with the title 'PayZoll: The Future of Crypto Payroll' and body 'Introducing PayZoll, the ultimate crypto payroll solution designed to revolutionize how businesses handle payments in the digital age!"
  },
  { title: "Current Time", query: "What is the current server time?" },
  { title: "Motivational Quote", query: "Show me a random motivational quote." },
  { title: "Calculate Savings", query: "Calculate how much our company would save by switching to PayZoll if our traditional payroll costs $50,000 per month for 120 employees." },
  { title: "PayZoll Features", query: "What are the main features of the PayZoll platform?" },
  { title: "PayZoll FAQ", query: "What are some frequently asked questions about PayZoll?" },
  { title: "Web3 Payroll Guide", query: "Provide me with a guide to understanding Web3 payroll concepts." },
  { title: "Payroll Comparison", query: "Compare traditional payroll systems with Web3 payroll." },
  { title: "Case Studies", query: "Show me case studies of companies that have successfully implemented PayZoll." },
  { title: "Implementation Guide", query: "How do I implement PayZoll in my organization? I need a step-by-step guide." },
  { title: "Crypto Explanation", query: "Can you explain what stablecoins are and how they're used in PayZoll?" },
  { title: "Payroll Schedule", query: "Generate a biweekly payroll schedule starting from 2025-04-01 for our 45 employees." },
  { title: "Volatility Handling", query: "How does PayZoll handle cryptocurrency volatility for regular payroll?" },
  { title: "Multi-Chain Support", query: "Which blockchain networks does PayZoll currently support?" },
  { title: "Off-Ramping Options", query: "What options are available for employees who want to convert their crypto payments to fiat currency?" },
];

interface Message {
  type: "user" | "bot";
  content: string;
  timestamp: Date;
}

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 }
};

const slideIn = {
  initial: { x: -300, opacity: 0 },
  animate: { x: 0, opacity: 1 },
  exit: { x: -300, opacity: 0 },
  transition: { type: "spring", stiffness: 300, damping: 30 }
};

const textReveal = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, delay: 0.2 }
};

const cardHover = {
  rest: { scale: 1, boxShadow: "0 4px 6px -1px rgba(99, 102, 241, 0.1), 0 2px 4px -1px rgba(99, 102, 241, 0.06)" },
  hover: {
    scale: 1.02,
    boxShadow: "0 20px 25px -5px rgba(99, 102, 241, 0.15), 0 10px 10px -5px rgba(99, 102, 241, 0.1)",
    transition: { duration: 0.3, ease: "easeOut" }
  }
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const apiUrl = "https://web-agent-server.onrender.com/api";
  // const apiUrl = "http://127.0.0.1:5000/api";


  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatContent = (content: any): string => {
    if (typeof content === "string") {
      return content;
    }

    if (Array.isArray(content)) {
      if (content.length === 0) return "No data available.";

      const firstItem = content[0];

      // Employee data formatting
      if ("name" in firstItem && "salary" in firstItem) {
        return content
          .map(
            (emp: any) =>
              `### ${emp.name}\n**Position:** ${emp.position}\n**Department:** ${emp.department}\n**Account:** ${emp.accountId}\n**Salary:** ${emp.salary} ETH\n**Hours:** ${emp.work_hours}`
          )
          .join("\n\n---\n\n");
      }

      // Transaction data formatting
      else if ("tx_hash" in firstItem && "status" in firstItem) {
        return content
          .map((tx: any) =>
            `### Transaction ${tx.tx_hash.substring(0, 8)}...${tx.tx_hash.substring(tx.tx_hash.length - 6)}\n` +
            `**Status:** ${tx.status === 1 ? "✅ Success" : "❌ Failed"}\n` +
            `**Recipient:** ${tx.recipient || "N/A"}\n` +
            `**Amount:** ${tx.amount || "N/A"} ETH\n` +
            `**Time:** ${tx.timestamp || "N/A"}`
          )
          .join("\n\n---\n\n");
      }

      // Features list formatting
      else if ("name" in firstItem && "description" in firstItem) {
        return content
          .map((item: any) => `### ${item.name}\n${item.description}`)
          .join("\n\n");
      }

      // FAQ formatting
      else if ("question" in firstItem && "answer" in firstItem) {
        return content
          .map((item: any) => `### ${item.question}\n${item.answer}`)
          .join("\n\n---\n\n");
      }

      // Case studies formatting
      else if ("company" in firstItem && "challenge" in firstItem) {
        return content
          .map((study: any) =>
            `## ${study.company}\n\n` +
            `**Industry:** ${study.industry}\n` +
            `**Employees:** ${study.employees}\n` +
            `**Countries:** ${study.countries}\n\n` +
            `### Challenge\n${study.challenge}\n\n` +
            `### Solution\n${study.solution}\n\n` +
            `### Results\n${study.results.map((r: string) => `- ${r}`).join('\n')}`
          )
          .join("\n\n---\n\n");
      }

      // Default array formatting
      return content.map((item: any) => typeof item === 'object' ? `- ${JSON.stringify(item)}` : `- ${item}`).join('\n');
    }

    if (typeof content === "object" && content !== null) {
      // Employee analytics
      if ("total_employees" in content) {
        return (
          `## Company Analytics\n\n` +
          `**Total Employees:** ${content.total_employees}\n` +
          `**Total Salary:** ${content.total_salary.toFixed(2)} ETH\n` +
          `**Average Salary:** ${content.average_salary.toFixed(2)} ETH\n` +
          `**Total Work Hours:** ${content.total_work_hours.toFixed(2)}\n` +
          `**Average Work Hours:** ${content.average_work_hours.toFixed(2)}`
        );
      }

      // Payroll savings calculation
      else if ("traditional_cost" in content && "payzoll_cost" in content) {
        return (
          `## PayZoll Savings Analysis\n\n` +
          `**Traditional Payroll Cost:** $${content.traditional_cost.toLocaleString()}\n` +
          `**PayZoll Cost:** $${content.payzoll_cost.toLocaleString()}\n` +
          `**Monthly Maintenance:** $${content.monthly_fee.toLocaleString()}\n` +
          `**Total Savings:** $${content.total_savings.toLocaleString()}\n` +
          `**Savings Percentage:** ${content.savings_percentage.toFixed(2)}%`
        );
      }

      // Payroll schedule
      else if ("frequency" in content && "schedule" in content) {
        let result = `## ${content.frequency.charAt(0).toUpperCase() + content.frequency.slice(1)} Payroll Schedule\n\n`;

        if (Array.isArray(content.schedule)) {
          result += content.schedule.map((period: any) =>
            `### Pay Period ${period.pay_period}\n` +
            `**Process Date:** ${period.process_date}\n` +
            `**Payment Date:** ${period.payment_date}\n` +
            `**Employees:** ${period.employees}\n` +
            `**Est. Gas Cost:** ${period.estimated_gas_cost} ETH\n` +
            `**Est. Process Time:** ${period.estimated_process_time}`
          ).join("\n\n");
        }

        return result;
      }

      // Web3 payroll guide
      else if ("title" in content && "key_concepts" in content) {
        let result = `# ${content.title}\n\n${content.introduction}\n\n## Key Concepts\n\n`;

        if (Array.isArray(content.key_concepts)) {
          result += content.key_concepts.map((concept: any) =>
            `### ${concept.name}\n${concept.description}`
          ).join("\n\n");
        }

        if (Array.isArray(content.benefits)) {
          result += "\n\n## Benefits\n\n";
          result += content.benefits.map((benefit: string) => `- ${benefit}`).join("\n");
        }

        return result;
      }

      // Implementation guide
      else if ("steps" in content) {
        let result = `# ${content.title || "Implementation Guide"}\n\n`;

        if (Array.isArray(content.steps)) {
          result += content.steps.map((step: any) =>
            `### Step ${step.step}: ${step.name}\n` +
            `${step.description}\n` +
            `**Time Estimate:** ${step.estimated_time}`
          ).join("\n\n");

          if (content.total_time) {
            result += `\n\n**Total Implementation Time:** ${content.total_time}`;
          }
        }

        return result;
      }

      // Payroll comparison
      else if ("categories" in content) {
        let result = `# Traditional vs Web3 Payroll\n\n`;

        if (Array.isArray(content.categories)) {
          result += content.categories.map((cat: any) =>
            `### ${cat.category}\n` +
            `**Traditional:** ${cat.traditional}\n` +
            `**Web3:** ${cat.web3}`
          ).join("\n\n");
        }

        return result;
      }

      // Crypto knowledge query
      else if ("query" in content && "explanation" in content) {
        return `## ${content.query}\n\n${content.explanation}`;
      }

      // Current time
      else if ("current_time" in content) {
        return `The current server time is: **${content.current_time}**`;
      }

      // Quote
      else if ("quote" in content) {
        return `> ${content.quote}`;
      }
    }

    // Final fallback - try to make any remaining objects readable
    if (typeof content === "object" && content !== null) {
      const formattedEntries = Object.entries(content).map(([key, value]) => {
        const formattedKey = key
          .replace(/_/g, ' ')
          .split(' ')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');

        if (Array.isArray(value)) {
          return `**${formattedKey}**:\n${value.map((item: any) => `- ${item}`).join('\n')}`;
        } else if (typeof value === 'object' && value !== null) {
          return `**${formattedKey}**:\n${JSON.stringify(value, null, 2)}`;
        } else {
          return `**${formattedKey}**: ${value}`;
        }
      });

      return formattedEntries.join('\n\n');
    }

    return String(content);
  };

  const extractRelevantContent = (data: any): string => {
    if (!data) return "No response received";

    if (data.function_result) {
      const result = data.function_result;
      if (result.status === "error") {
        return `⚠️ Error: ${result.message}`;
      }
      const relevantData = result.response || result.data || result.post || result.message || result.quote || "Action completed successfully";
      return formatContent(relevantData);
    }

    // If no function result, use the AI message
    if (data.ai_message) {
      return data.ai_message;
    }

    return "No relevant content found in the response";
  };

  const handleSubmit = async (message: string) => {
    if (!message.trim()) return;

    const newUserMessage = { type: "user" as const, content: message, timestamp: new Date() };
    setMessages((prev) => [...prev, newUserMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data = await response.json();
      const relevantContent = extractRelevantContent(data);
      const botResponse = {
        type: "bot" as const,
        content: relevantContent,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botResponse]);
    } catch (error) {
      const errorMessage = {
        type: "bot" as const,
        content: `Error: ${error instanceof Error ? error.message : "Unknown error occurred"}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0F1C] text-white flex overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-[#0A0F1C] via-[#1A1F2E] to-[#0D1321] z-0">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAwIDYwIEwgNjAgMCIgc3Ryb2tlPSIjMjAyNDJFIiBzdHJva2Utd2lkdGg9IjAuNSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-10"></div>
      </div>

      {/* Sidebar */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.aside
            {...slideIn}
            className="fixed left-0 top-0 h-full w-80 bg-[#0D1321]/90 backdrop-blur-xl border-r border-indigo-500/20 z-20 flex flex-col"
          >
            <div className="p-6 border-b border-indigo-500/20">
              <div className="flex items-center justify-between">
                <motion.h2
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent"
                >
                  Sample Queries
                </motion.h2>
                <motion.button
                  whileHover={{ scale: 1.1, rotate: -90 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setIsSidebarOpen(false)}
                  className="text-indigo-400 hover:text-purple-400 transition-colors"
                >
                  <ChevronLeft size={24} />
                </motion.button>
              </div>
            </div>
            <motion.div
              className="overflow-y-auto flex-1 p-6 pt-4"
              style={{
                scrollbarWidth: 'none',  /* Firefox */
                msOverflowStyle: 'none',  /* IE and Edge */
              }}
              variants={{
                show: {
                  transition: {
                    staggerChildren: 0.1
                  }
                }
              }}
              initial="hidden"
              animate="show"
            >
              <div className="space-y-4">
                {sampleQueries.map((sample, index) => (
                  <motion.button
                    key={index}
                    variants={{
                      hidden: { opacity: 0, x: -20 },
                      show: { opacity: 1, x: 0 }
                    }}
                    whileHover={{
                      scale: 1.02,
                      x: 5,
                      backgroundColor: "rgba(99, 102, 241, 0.1)",
                      borderColor: "rgba(99, 102, 241, 0.5)"
                    }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSubmit(sample.query)}
                    className="w-full text-left p-4 rounded-xl bg-[#151A2A]/50 border border-indigo-500/20 hover:border-indigo-400/50 transition-all duration-300 group"
                  >
                    <h3 className="text-sm font-semibold text-indigo-300 group-hover:text-indigo-200">{sample.title}</h3>
                    <p className="text-xs text-gray-400 mt-1 line-clamp-2 group-hover:text-gray-300">{sample.query}</p>
                  </motion.button>
                ))}
              </div>
              <style jsx global>{`
        div::-webkit-scrollbar {
          display: none;
        }
          `}</style>
            </motion.div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Sidebar Toggle */}
      <AnimatePresence>
        {!isSidebarOpen && (
          <motion.button
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="fixed left-4 top-1/2 -translate-y-1/2 z-20 bg-indigo-500/20 p-3 rounded-full hover:bg-indigo-500/30 transition-colors"
            onClick={() => setIsSidebarOpen(true)}
          >
            <ChevronRight size={24} className="text-indigo-400" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className={`flex-1 flex flex-col ${isSidebarOpen ? 'ml-80' : 'ml-0'} transition-all duration-300`}>
        {/* Header */}
        <motion.header
          initial={{ y: -100 }}
          animate={{ y: 0 }}
          className="p-6 border-b border-indigo-500/20 bg-[#0D1321]/50 backdrop-blur-xl fixed w-full top-0 z-10"
        >
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            <motion.div
              className="flex items-center gap-3"
              whileHover={{ scale: 1.02 }}
            >
              <motion.div
                animate={{
                  rotate: [0, 10, -10, 0],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Sparkles className="w-10 h-10 text-indigo-400" />
              </motion.div>
              <h1 className="text-3xl font-extrabold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 text-transparent bg-clip-text">
                PayZoll AI
              </h1>
            </motion.div>
          </div>
        </motion.header>

        {/* Messages */}
        <main className="flex-1 max-w-5xl w-full mx-auto pt-24 pb-32 px-6 overflow-y-auto">
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={index}
                {...fadeInUp}
                className={`flex ${message.type === "user" ? "justify-end" : "justify-start"} mb-6`}
              >
                <motion.div
                  initial="rest"
                  whileHover="hover"
                  animate="rest"
                  variants={cardHover}
                  className={`max-w-3xl rounded-2xl p-6 ${message.type === "user"
                    ? "bg-gradient-to-r from-indigo-600/20 via-purple-600/20 to-pink-600/20 border border-indigo-500/30 hover:border-indigo-400/50"
                    : "bg-gradient-to-r from-[#151A2A]/70 via-[#1A1F2E]/70 to-[#1F2437]/70 border border-gray-700/30 hover:border-gray-600/50"
                    } shadow-xl backdrop-blur-sm relative overflow-hidden group`}
                >
                  {/* Animated gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000"></div>

                  {/* Message content with staggered animation */}
                  <motion.div
                    variants={textReveal}
                    className="relative z-10"
                  >
                    <div className="text-sm text-gray-200 prose prose-invert max-w-none prose-headings:text-indigo-400 prose-a:text-purple-400 prose-strong:text-pink-400 prose-code:text-cyan-400">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                    <div className={`text-xs mt-3 ${message.type === "user"
                      ? "text-indigo-300/80"
                      : "text-gray-400/80"
                      }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </motion.div>
                </motion.div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </main>

        {/* Input Area */}
        <motion.div
          initial={{ y: 100 }}
          animate={{ y: 0 }}
          className="fixed bottom-0 right-0 left-0 bg-[#0D1321]/50 backdrop-blur-xl border-t border-indigo-500/20 p-6 ml-[320px]"
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit(input);
            }}
            className="max-w-5xl mx-auto flex gap-4"
          >
            <motion.input
              whileFocus={{ scale: 1.01 }}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-[#151A2A]/50 border border-indigo-500/30 rounded-xl px-6 py-4 focus:outline-none focus:border-indigo-400 transition-all text-gray-200 placeholder-gray-400"
            />
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isLoading}
              className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 hover:from-indigo-600 hover:via-purple-600 hover:to-pink-600 text-white px-8 py-4 rounded-xl flex items-center gap-3 transition-all disabled:opacity-50 disabled:hover:from-indigo-500 disabled:hover:to-purple-500 shadow-lg shadow-indigo-500/20"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
              Send
            </motion.button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}