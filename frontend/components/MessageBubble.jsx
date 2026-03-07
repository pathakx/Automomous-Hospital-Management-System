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

                {/* Structure response rendering block! */}
                {message.type === "appointment_options" && message.data?.doctors && (
                    <div className="mt-4 space-y-2">
                        <p className="font-semibold text-slate-700 border-b border-slate-200 pb-1 mb-2">Available Doctors:</p>
                        {message.data.doctors.map((doc, idx) => (
                            <div key={idx} className="bg-slate-50 border border-slate-200 p-3 rounded shadow-sm flex justify-between items-center hover:border-blue-300">
                                <div>
                                    <h4 className="font-bold text-slate-800">{doc.name}</h4>
                                    <p className="text-xs text-slate-500">{doc.time}</p>
                                </div>
                                <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded text-xs font-semibold shadow-sm transition-colors">
                                    Book Option
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                <span className={`text-[10px] mt-1 block ${isUser ? "text-blue-200" : "text-slate-400"}`}>
                    {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
            </div>
        </div>
    );
}