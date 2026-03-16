"use client";

import React from "react";
import ReactMarkdown from "react-markdown";

/** Custom renderers so ReactMarkdown outputs styled HTML elements.
 *  No Tailwind typography plugin needed — styles are inline via className. */
const markdownComponents = {
    p:      ({ children }) => <p className="my-1 leading-relaxed">{children}</p>,
    strong: ({ children }) => <strong className="font-bold text-slate-900">{children}</strong>,
    em:     ({ children }) => <em className="italic">{children}</em>,
    ul:     ({ children }) => <ul className="list-disc list-inside my-1 space-y-0.5">{children}</ul>,
    ol:     ({ children }) => <ol className="list-decimal list-inside my-1 space-y-0.5">{children}</ol>,
    li:     ({ children }) => <li className="text-slate-700">{children}</li>,
    h1:     ({ children }) => <h1 className="font-bold text-base mt-2 mb-1">{children}</h1>,
    h2:     ({ children }) => <h2 className="font-bold text-sm mt-2 mb-1">{children}</h2>,
    h3:     ({ children }) => <h3 className="font-semibold text-sm mt-1 mb-0.5">{children}</h3>,
    hr:     () => <hr className="my-2 border-slate-200" />,
    code:   ({ children }) => <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded text-xs font-mono">{children}</code>,
    blockquote: ({ children }) => <blockquote className="border-l-4 border-slate-300 pl-3 italic text-slate-600 my-1">{children}</blockquote>,
};

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
                className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm shadow-sm ${
                    isUser
                        ? "bg-blue-600 text-white rounded-br-sm"
                        : "bg-white text-slate-800 border border-slate-200 rounded-bl-sm"
                }`}
            >
                {/* User messages: plain text. Bot messages: rendered markdown. */}
                {isUser ? (
                    <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
                ) : (
                    <div className="text-sm">
                        <ReactMarkdown components={markdownComponents}>
                            {message.text}
                        </ReactMarkdown>
                    </div>
                )}

                {/* Structured response: appointment doctor cards */}
                {message.type === "appointment_options" && message.data?.doctors && (
                    <div className="mt-4 space-y-2">
                        <p className="font-semibold text-slate-700 border-b border-slate-200 pb-1 mb-2">
                            Available Doctors:
                        </p>
                        {message.data.doctors.map((doc, idx) => (
                            <div
                                key={idx}
                                className="bg-slate-50 border border-slate-200 p-3 rounded shadow-sm flex justify-between items-center hover:border-blue-300"
                            >
                                <div>
                                    <h4 className="font-bold text-slate-800">{doc.name}</h4>
                                    <p className="text-xs text-slate-500">
                                        {doc.specialization}{doc.consultation_fee ? ` · $${doc.consultation_fee}` : ""}
                                    </p>
                                </div>
                                <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded text-xs font-semibold shadow-sm transition-colors">
                                    Book
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Structured response: report list */}
                {message.type === "report_list" && message.data?.reports && (
                    <div className="mt-3 space-y-2">
                        {message.data.reports.map((r, idx) => (
                            <div
                                key={idx}
                                className="bg-slate-50 border border-slate-200 p-3 rounded flex justify-between items-center"
                            >
                                <div>
                                    <p className="font-semibold text-slate-800 text-xs">{r.report_name}</p>
                                    <p className="text-xs text-slate-500">{r.report_type} · {r.upload_date}</p>
                                </div>
                                {r.file_url && (
                                    <a
                                        href={r.file_url}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-blue-600 text-xs font-semibold hover:underline"
                                    >
                                        View
                                    </a>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Structured response: bill list */}
                {message.type === "bill_list" && message.data?.bills && (
                    <div className="mt-3 space-y-2">
                        {message.data.bills.map((b, idx) => (
                            <div
                                key={idx}
                                className="bg-slate-50 border border-slate-200 p-3 rounded flex justify-between items-center"
                            >
                                <div>
                                    <p className="font-semibold text-slate-800 text-xs">{b.service_type}</p>
                                    <p className="text-xs text-slate-500">{b.created_at}</p>
                                </div>
                                <span className="font-bold text-slate-800 text-xs">
                                    ${typeof b.amount === "number" ? b.amount.toFixed(2) : b.amount}
                                </span>
                            </div>
                        ))}
                    </div>
                )}

                <span className={`text-[10px] mt-2 block ${isUser ? "text-blue-200" : "text-slate-400"}`}>
                    {new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
            </div>
        </div>
    );
}
