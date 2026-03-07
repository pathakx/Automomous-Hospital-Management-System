"use client";

import { useState } from "react";
import Sidebar from "../../components/Sidebar";
import ChatWindow from "../../components/ChatWindow";


export default function DashboardPage() {
    // State to track which view is active; defaults to "chat"
    const [activeTab, setActiveTab] = useState("chat");

    // Function to render the correct component based on active tab
    const renderContent = () => {
        switch (activeTab) {
            case "chat":
                return <ChatWindow />;
            case "appointments":
                return (
                    <div className="p-8">
                        <h2 className="text-2xl font-bold text-gray-800">My Appointments</h2>
                        <p className="text-gray-500 mt-2">Data will be fetched and shown here in Part 5.</p>
                    </div>
                );
            case "reports":
                return (
                    <div className="p-8">
                        <h2 className="text-2xl font-bold text-gray-800">Lab Reports</h2>
                        <p className="text-gray-500 mt-2">Data will be fetched and shown here in Part 5.</p>
                    </div>
                );
            case "prescriptions":
                return (
                    <div className="p-8">
                        <h2 className="text-2xl font-bold text-gray-800">Prescriptions</h2>
                        <p className="text-gray-500 mt-2">Data will be fetched and shown here in Part 5.</p>
                    </div>
                );
            case "billing":
                return (
                    <div className="p-8">
                        <h2 className="text-2xl font-bold text-gray-800">Billing & Payments</h2>
                        <p className="text-gray-500 mt-2">Data will be fetched and shown here in Part 5.</p>
                    </div>
                );
            default:
                return <div className="p-8 font-bold">Not Found</div>;
        }
    };

    return (
        <div className="flex h-screen overflow-hidden bg-slate-50">
            {/* Desktop Sidebar */}
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col h-full overflow-hidden">

                {/* Mobile Header (Hidden on Desktop) */}
                <header className="md:hidden bg-slate-900 text-white p-4 flex justify-between items-center shadow-md z-10">
                    <h2 className="text-xl font-bold text-blue-400 flex items-center gap-2">
                        <span>🏥</span> MediChat
                    </h2>
                    <select
                        value={activeTab}
                        onChange={(e) => setActiveTab(e.target.value)}
                        className="bg-slate-800 text-white border border-slate-700 py-1 px-2 rounded outline-none"
                    >
                        <option value="chat">💬 Chat</option>
                        <option value="appointments">📅 Appointments</option>
                        <option value="reports">📋 Reports</option>
                        <option value="prescriptions">💊 Prescriptions</option>
                        <option value="billing">💰 Billing</option>
                    </select>
                </header>

                {/* Dynamic Content View Area */}
                <div className="flex-1 overflow-y-auto relative">
                    {renderContent()}
                </div>

            </main>
        </div>
    );
}