"use client";

import { useState } from "react";

export default function ChatInput({ onSendMessage, isTyping }) {
    const [input, setInput] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim() && !isTyping) {
            onSendMessage(input.trim());
            setInput("");
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-slate-200">
            <div className="flex space-x-2 relative max-w-4xl mx-auto">
                <input
                    className="flex-1 bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-full focus:ring-blue-500 focus:border-blue-500 block w-full p-3 px-5 pr-12 focus:outline-none transition-shadow"
                    placeholder="Type your health-related query here..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isTyping}
                    autoFocus
                />
                <button
                    type="submit"
                    disabled={!input.trim() || isTyping}
                    className="absolute right-2 top-1.5 p-1.5 text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-full disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
                >
                    <svg className="w-5 h-5 translate-x-px translate-y-px" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19V6m0 0l-5 5m5-5l5 5"></path>
                    </svg>
                </button>
            </div>
        </form>
    );
}