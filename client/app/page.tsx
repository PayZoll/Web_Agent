"use client";

import { useState, useRef, useEffect } from "react";
import { Bot, Send, Loader2, ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";

const sampleQueries = [
  { title: "Chat with AI", query: "Tell me about the different features of PayZoll." },
  { title: "Post on Twitter", query: "Please post the following tweet: 'We are intoducing you to PayZoll, a new player in the Web3 Ecosystem'" },
  {
    title: "Post on Reddit",
    query: "Post on the CryptoCurrency subreddit with the title 'PayZoll: The Future of Crypto Payroll' and body 'Introducing PayZoll, the ultimate crypto payroll solution designed to revolutionize how businesses handle payments in the digital age! Our system leverages Web3 technology to ensure secure, decentralized transactions across multiple blockchains, making payroll fast and reliable. With AI-driven automation, we eliminate manual errors and streamline processes, saving you time and effort. PayZoll supports stable token swaps and efficient fiat off-ramps, so even non-Web3 users can enjoy a seamless experience akin to traditional payroll systems. Security is at our core—your assets are protected with cutting-edge encryption and smart contract precision. Plus, our automated compliance and reporting tools keep you ahead of regulations effortlessly. Whether you're a startup or an enterprise, PayZoll simplifies crypto payroll, reduces learning curves, and boosts efficiency.Check out our new system and join the future of payroll today!' "
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatContent = (content: any): string => {
    if (typeof content === "string") {
      if (content.match(/[#*]|\d+\./)) return content;
      return content;
    }

    if (Array.isArray(content)) {
      if (content.length === 0) return "No data available.";

      const firstItem = content[0];
      if ("name" in firstItem && "salary" in firstItem) {
        return content
          .map(
            (emp: any) =>
              `- **${emp.name}** (${emp.position}, ${emp.department})\n  - Account: ${emp.accountId}\n  - Salary: ${emp.salary} ETH\n  - Work Hours: ${emp.work_hours}`
          )
          .join("\n");
      } else if ("tx_hash" in firstItem && "status" in firstItem) {
        return content
          .map((tx: any) => `- Transaction Hash: ${tx.tx_hash}\n  - Status: ${tx.status === 1 ? "Success" : "Failed"}`)
          .join("\n");
      }
    }

    if (typeof content === "object" && content !== null) {
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

    return JSON.stringify(content);
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
            className="fixed left-0 top-0 h-full w-80 bg-[#0D1321]/90 backdrop-blur-xl border-r border-indigo-500/20 z-20 p-6"
          >
            <div className="flex items-center justify-between mb-8">
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
            <motion.div
              className="space-y-4"
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