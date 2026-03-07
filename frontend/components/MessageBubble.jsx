"use client";

import React from "react";

export default function MessageBubble({ message }) {
    const isUser = message.role === "user";
    const isSystem = message.role === "system";

    if (isSystem) {
        return (
            <div className="flex justify-center my-4">
                <span className="bg-slate-200 text-slate-600 text-xs px-3 py-1 rounded-full">
                    {message.text}
                </span>
            </div>
        );
    }

    return (
        <div className={`flex w-full my-2 ${isUser ? "justify-end" : "justify-start"}`}>
            <div
                className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm shadow-sm ${isUser
                        ? "bg-blue-600 text-white rounded-br-sm"
                        : "bg-white text-slate-800 border border-slate-200 rounded-bl-sm"
                    }`}
            >
                <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
                <span className={`text-[10px] mt-1 block ${isUser ? "text-blue-200" : "text-slate-400"}`}>
                    {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
            </div>
        </div>
    );
}