"use client";

import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { 
  Bot, 
  Send, 
  Sparkles, 
  Wrench, 
  User, 
  HelpCircle, 
  Loader2,
  ArrowRight
} from "lucide-react";
import { apiClient } from "@/lib/api";

interface ToolCallRecord {
  tool_name: string;
  arguments: Record<string, any>;
  result_summary: string;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  tools_called?: ToolCallRecord[];
  suggested_follow_ups?: string[];
  created_at: string;
}

interface AgentChatResponse {
  response: string;
  tools_called: ToolCallRecord[];
  suggested_follow_ups: string[];
}

export default function AgentPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome-msg",
      role: "assistant",
      content:
        "Hello! I am your Nexus Autonomous Career Intelligence Agent. I can query your opportunity database, analyze application deadlines, inspect required technical skills across your matches, and summarize your top resume fits. How can I help you today?",
      suggested_follow_ups: [
        "Which of my saved roles have upcoming deadlines?",
        "What technical skills appear most often in my matches?",
        "Show my top 3 resume matches.",
      ],
      created_at: new Date().toISOString(),
    },
  ]);

  const [inputMessage, setInputMessage] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const chatMutation = useMutation({
    mutationFn: async (messageText: string) => {
      return apiClient<AgentChatResponse>("/agent/chat", {
        method: "POST",
        body: JSON.stringify({ message: messageText }),
      });
    },
    onSuccess: (data) => {
      const assistantMsg: ChatMessage = {
        id: `agent-${Date.now()}`,
        role: "assistant",
        content: data.response,
        tools_called: data.tools_called,
        suggested_follow_ups: data.suggested_follow_ups,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    },
    onError: (err: any) => {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        role: "assistant",
        content: `Error communicating with agent: ${err.message || "Please make sure you are logged in."}`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    },
  });

  const handleSendMessage = (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || chatMutation.isPending) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage("");
    chatMutation.mutate(text);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-canvas py-8 px-4 sm:px-6 flex flex-col justify-between">
      <div className="max-w-4xl mx-auto w-full flex-1 flex flex-col space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-softBorder">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-pill bg-white border border-softBorder text-xs font-semibold text-secondaryText mb-2 shadow-2xs">
              <Sparkles className="w-3.5 h-3.5 text-accentBlue" />
              <span>Autonomous Copilot</span>
            </div>
            <h1 className="font-display text-2xl font-bold tracking-tight text-primaryText">
              Career Intelligence Agent
            </h1>
            <p className="text-xs text-secondaryText mt-0.5">
              Tool-augmented assistant with read-access to your resume, saved listings, and market data.
            </p>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 space-y-5 overflow-y-auto max-h-[60vh] pr-2">
          {messages.map((msg) => {
            const isUser = msg.role === "user";

            return (
              <div
                key={msg.id}
                className={`flex items-start space-x-3 ${
                  isUser ? "flex-row-reverse space-x-reverse" : ""
                }`}
              >
                {/* Avatar */}
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
                    isUser
                      ? "bg-accentBlue text-white shadow-2xs"
                      : "bg-surface border border-softBorder text-primaryText shadow-2xs"
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-accentGreen" />}
                </div>

                {/* Content Bubble */}
                <div
                  className={`max-w-2xl rounded-card p-4 space-y-2.5 shadow-2xs ${
                    isUser
                      ? "bg-accentBlue text-white rounded-tr-none"
                      : "bg-surface border border-softBorder text-primaryText rounded-tl-none"
                  }`}
                >
                  {/* Tool execution badge if tools were called */}
                  {!isUser && msg.tools_called && msg.tools_called.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 pb-2 border-b border-softBorder/60">
                      {msg.tools_called.map((tool, idx) => (
                        <div
                          key={idx}
                          className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-pill bg-canvas border border-softBorder text-[10px] font-semibold text-secondaryText"
                        >
                          <Wrench className="w-3 h-3 text-accentBlue" />
                          <span>Tool: {tool.tool_name}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Body text */}
                  <div
                    className={`text-xs leading-relaxed whitespace-pre-wrap ${
                      isUser ? "text-white" : "text-primaryText"
                    }`}
                  >
                    {msg.content}
                  </div>

                  {/* Suggested follow-ups */}
                  {!isUser && msg.suggested_follow_ups && msg.suggested_follow_ups.length > 0 && (
                    <div className="pt-2 border-t border-softBorder/60 space-y-1.5">
                      <span className="text-[10px] font-bold text-secondaryText uppercase tracking-wider block">
                        Suggested Follow-ups:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.suggested_follow_ups.map((chip, i) => (
                          <button
                            key={i}
                            onClick={() => handleSendMessage(chip)}
                            className="px-2.5 py-1 rounded-pill bg-canvas hover:bg-softBorder/50 border border-softBorder text-[11px] font-medium text-primaryText flex items-center space-x-1 transition-colors"
                          >
                            <span>{chip}</span>
                            <ArrowRight className="w-2.5 h-2.5 text-accentBlue" />
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {chatMutation.isPending && (
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 rounded-xl bg-surface border border-softBorder flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-accentGreen" />
              </div>
              <div className="bg-surface border border-softBorder rounded-card rounded-tl-none p-3.5 flex items-center space-x-2 text-xs text-secondaryText shadow-2xs">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-accentBlue" />
                <span>Agent is analyzing database and executing tools...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <div className="bg-surface rounded-card p-3 border border-softBorder shadow-xs">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask anything about upcoming deadlines, in-demand skills, or matched roles..."
              className="flex-1 px-3.5 py-2 rounded-btn bg-canvas border border-softBorder text-xs text-primaryText placeholder:text-secondaryText/60 focus:outline-none focus:ring-2 focus:ring-accentBlue/20 focus:border-accentBlue transition-all"
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || chatMutation.isPending}
              className="p-2.5 rounded-btn bg-accentBlue hover:bg-accentBlue-hover text-white shadow-2xs transition-all disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
