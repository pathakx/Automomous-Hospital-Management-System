"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
import { sendChatMessage } from "../services/api";

export default function ChatWindow() {
    const [messages, setMessages] = useState([
        { role: "assistant", text: "👋 Welcome! I'm your hospital assistant. How can I help you today?", type: "text" }
    ]);
    const [isTyping, setIsTyping] = useState(false);
    const [conversationId, setConversationId] = useState(null); // Will store ID from backend
    const messagesEndRef = useRef(null);
    const { user } = useAuth(); // Needed to send patient_id to backend

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    const handleSendMessage = async (text) => {
    // 1. Add user message
    const newMessages = [...messages, { role: "user", text, type: "text" }];
    setMessages(newMessages);
    setIsTyping(true);

    try {
        // NOTE: exclude the last item we just pushed (the user message itself)
        // to avoid duplicating it — the current message is already sent as 'message'
        const historyToSend = messages; // all messages in state before the new user message

        // 2. Call backend with full contract
        const response = await sendChatMessage(
            text,
            user?.linked_id,
            conversationId,
            historyToSend
        );

        // 3. Keep track of Conversation ID if backend returns a new one
        if (response.conversation_id && !conversationId) {
            setConversationId(response.conversation_id);
        }

        // 4. Add assistant response (now handles structured data types!)
        setMessages((prev) => [
            ...prev,
            {
                role: "assistant",
                text: response.reply,
                type: response.type || "text",
                data: response.data || null
            }
        ]);
    } catch (error) {
        console.error("Chat error:", error);
        setMessages((prev) => [
            ...prev,
            { role: "system", text: "Connection error. Please try again." }
        ]);
    } finally {
        setIsTyping(false);
    }
    };

    return (
        <div className="flex flex-col h-full bg-slate-50 relative">
            {/* Header */}
            <div className="bg-white border-b border-slate-200 px-6 py-4 flex items-center shadow-sm z-10">
                <div>
                    <h2 className="text-lg font-bold text-slate-800">MediChat AI</h2>
                    <p className="text-xs text-green-600 flex items-center">
                        <span className="w-2 h-2 rounded-full bg-green-500 mr-1.5 animate-pulse"></span>
                        Online
                    </p>
                </div>
            </div>

            {/* Message List */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 pb-4">
                <div className="max-w-4xl mx-auto flex flex-col justify-end min-h-full">
                    {messages.map((msg, idx) => (
                        <MessageBubble key={idx} message={msg} />
                    ))}

                    {/* Typing Indicator */}
                    {isTyping && (
                        <div className="flex justify-start my-2">
                            <div className="bg-white border border-slate-200 text-slate-500 px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm flex items-center space-x-1">
                                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <ChatInput onSendMessage={handleSendMessage} isTyping={isTyping} />
        </div>
    );
}