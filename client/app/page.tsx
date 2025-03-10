"use client";

import { useState, useRef, useEffect } from "react";
import { Bot, Send, Loader2, ChevronLeft, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown"; // For rendering Markdown

const sampleQueries = [
  { title: "Chat with AI", query: "Tell me about the different features of PayZoll." },
  { title: "Post on Twitter", query: "Please post the following tweet: 'We are intoducing you to PayZoll, a new player in the Web3 Ecosystem'" },
  {
    title: "Post on Reddit", query: "Post on the CryptoCurrency subreddit with the title 'PayZoll: The Future of Crypto Payroll' and body 'Introducing PayZoll, the ultimate crypto payroll solution designed to revolutionize how businesses handle payments in the digital age! Our system leverages Web3 technology to ensure secure, decentralized transactions across multiple blockchains, making payroll fast and reliable. With AI-driven automation, we eliminate manual errors and streamline processes, saving you time and effort. PayZoll supports stable token swaps and efficient fiat off-ramps, so even non-Web3 users can enjoy a seamless experience akin to traditional payroll systems. Security is at our core—your assets are protected with cutting-edge encryption and smart contract precision. Plus, our automated compliance and reporting tools keep you ahead of regulations effortlessly. Whether you're a startup or an enterprise, PayZoll simplifies crypto payroll, reduces learning curves, and boosts efficiency.Check out our new system and join the future of payroll today!' "
  },
  { title: "Generate Post", query: "Generate a tweet about our new crypto payroll system that focuses on security features." },
  { title: "Employee Details", query: "Retrieve all employee details from the company_employees.csv file." },
  { title: "Analytics", query: "Show me analytics for our employee data including average salary and work hours." },
  { title: "Bulk Transfer", query: "Execute a bulk transfer of ETH to these employees: [{\"accountId\": \"0xF947782C0CB4d3afa57912DA235894563950E2F4\", \"salary\": 0.2},{\"accountId\": \"0x8AA334072b03AB3F4cE4035A16a1Ee5Bde2521f1\", \"salary\": 0.2},{\"accountId\": \"0xe2e1862B5cA1743DF3F616DB927070AEC4c5B4fC\", \"salary\": 0.2}] using the Sonic RPC URL: https://rpc.blaze.soniclabs.com/" },
  { title: "Transaction Insights", query: "Generate insights from our transaction log, focusing on trends in payment amounts." },
];

interface Message {
  type: "user" | "bot";
  content: string;
  timestamp: Date;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // const apiUrl = "https://web-agent-server.onrender.com/api/";
  const apiUrl = "http://127.0.0.1:5000/api";

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatContent = (content: any): string => {
    if (typeof content === "string") {
      // If it looks like Markdown (e.g., contains #, *, numbered lists), treat it as Markdown
      if (content.match(/[#*]|\d+\./)) {
        return content; // Will be rendered by ReactMarkdown
      }
      return content; // Plain text
    }

    if (Array.isArray(content)) {
      // Handle arrays (e.g., employee details, bulk transfer receipts)
      if (content.length === 0) return "No data available.";

      const firstItem = content[0];
      if ("name" in firstItem && "salary" in firstItem) {
        // Employee details
        return content
          .map(
            (emp: any) =>
              `- **${emp.name}** (${emp.position}, ${emp.department})\n  - Account: ${emp.accountId}\n  - Salary: ${emp.salary} ETH\n  - Work Hours: ${emp.work_hours}`
          )
          .join("\n");
      } else if ("tx_hash" in firstItem && "status" in firstItem) {
        // Bulk transfer receipts
        return content
          .map((tx: any) => `- Transaction Hash: ${tx.tx_hash}\n  - Status: ${tx.status === 1 ? "Success" : "Failed"}`)
          .join("\n");
      }
    }

    if (typeof content === "object" && content !== null) {
      // Handle analytics or other JSON objects
      if ("total_employees" in content) {
        return (
          `- Total Employees: ${content.total_employees}\n` +
          `- Total Salary: ${content.total_salary} ETH\n` +
          `- Average Salary: ${content.average_salary.toFixed(2)} ETH\n` +
          `- Total Work Hours: ${content.total_work_hours}\n` +
          `- Average Work Hours: ${content.average_work_hours.toFixed(2)}`
        );
      }
    }

    return JSON.stringify(content); // Fallback for unhandled cases
  };

  const extractRelevantContent = (data: any): string => {
    if (data.function_result) {
      const result = data.function_result;
      if (result.status === "error") {
        return result.message;
      }
      const relevantData = result.response || result.data || result.post || result.message || "Action completed successfully";
      return formatContent(relevantData);
    }
    return formatContent(data.ai_message || "No response available");
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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white flex overflow-hidden">
      {/* Sidebar */}
      <motion.aside
        initial={{ x: -300 }}
        animate={{ x: isSidebarOpen ? 0 : -300 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="fixed left-0 top-0 h-full w-72 bg-gray-900/95 backdrop-blur-xl border-r border-cyan-500/20 z-20 p-6"
      >
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-xl font-bold text-cyan-400">Sample Queries</h2>
          <button onClick={() => setIsSidebarOpen(false)} className="text-gray-400 hover:text-cyan-400">
            <ChevronLeft size={24} />
          </button>
        </div>
        <div className="space-y-4">
          {sampleQueries.map((sample, index) => (
            <motion.button
              key={index}
              whileHover={{ scale: 1.02, x: 5 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleSubmit(sample.query)}
              className="w-full text-left p-3 rounded-lg bg-gradient-to-r from-cyan-900/20 to-blue-900/20 border border-cyan-500/30 hover:border-cyan-400 transition-all"
            >
              <h3 className="text-sm font-semibold text-cyan-300">{sample.title}</h3>
              <p className="text-xs text-gray-400 mt-1 line-clamp-2">{sample.query}</p>
            </motion.button>
          ))}
        </div>
      </motion.aside>

      {/* Sidebar Toggle */}
      {!isSidebarOpen && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed left-4 top-1/2 -translate-y-1/2 z-20 bg-cyan-500/20 p-2 rounded-full hover:bg-cyan-500/30"
          onClick={() => setIsSidebarOpen(true)}
        >
          <ChevronRight size={24} className="text-cyan-400" />
        </motion.button>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col ml-[300px]">
        {/* Header */}
        <motion.header
          initial={{ y: -100 }}
          animate={{ y: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="p-6 border-b border-cyan-500/20 bg-gray-900/50 backdrop-blur-xl fixed w-full top-0 z-10"
        >
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bot className="w-10 h-10 text-cyan-400" />
              <h1 className="text-3xl font-extrabold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 text-transparent bg-clip-text">
                PayZoll AI
              </h1>
            </div>
          </div>
        </motion.header>

        {/* Messages */}
        <main className="flex-1 max-w-5xl w-full mx-auto pt-24 pb-32 px-6 overflow-y-auto">
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -50 }}
                transition={{ type: "spring", stiffness: 300, damping: 25 }}
                className={`flex ${message.type === "user" ? "justify-end" : "justify-start"} mb-6`}
              >
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  className={`max-w-3xl rounded-xl p-5 ${message.type === "user"
                    ? "bg-gradient-to-r from-cyan-600/20 to-blue-600/20 border border-cyan-500/50"
                    : "bg-gradient-to-r from-gray-800/70 to-gray-900/70 border border-gray-700/50"
                    } shadow-lg`}
                >
                  <div className="text-sm text-gray-200 prose prose-invert max-w-none">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                  <div className={`text-xs mt-3 ${message.type === "user" ? "text-cyan-300" : "text-gray-400"}`}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
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
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="fixed bottom-0 left-[300px] right-0 bg-gray-900/50 backdrop-blur-xl border-t border-cyan-500/20 p-6"
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit(input);
            }}
            className="max-w-5xl mx-auto flex gap-4"
          >
            <motion.input
              whileFocus={{ scale: 1.02, borderColor: "#22d3ee" }}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-gray-800/50 border border-cyan-500/30 rounded-xl px-5 py-4 focus:outline-none focus:border-cyan-400 transition-all text-gray-200"
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="submit"
              disabled={isLoading}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white px-6 py-4 rounded-xl flex items-center gap-2 transition-all disabled:opacity-50 disabled:hover:from-cyan-500 disabled:hover:to-blue-500 shadow-lg"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              Send
            </motion.button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}