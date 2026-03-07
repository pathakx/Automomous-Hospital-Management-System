"use client";

import ProfileCard from "./ProfileCard";

export default function Sidebar({ activeTab, setActiveTab }) {
    // Define our navigation menu configurations
    const navItems = [
        { id: "chat", icon: "💬", label: "Chat Assistant" },
        { id: "appointments", icon: "📅", label: "Appointments" },
        { id: "reports", icon: "📋", label: "Lab Reports" },
        { id: "prescriptions", icon: "💊", label: "Prescriptions" },
        { id: "billing", icon: "💰", label: "Billing" },
    ];

    return (
        <div className="w-64 bg-slate-900 h-screen flex flex-col shadow-xl hidden md:flex shrink-0">
            {/* Branding */}
            <div className="p-6">
                <h2 className="text-2xl font-bold text-blue-400 flex items-center gap-2">
                    <span>🏥</span> MediChat
                </h2>
            </div>

            {/* Navigation Links */}
            <div className="flex-1 overflow-y-auto px-4 py-2 space-y-2">
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${activeTab === item.id
                                ? "bg-blue-600 text-white shadow-md font-semibold"
                                : "text-slate-300 hover:bg-slate-800 hover:text-white"
                            }`}
                    >
                        <span className="text-xl">{item.icon}</span>
                        <span>{item.label}</span>
                    </button>
                ))}
            </div>

            {/* Profile Section at the bottom */}
            <ProfileCard />
        </div>
    );
}