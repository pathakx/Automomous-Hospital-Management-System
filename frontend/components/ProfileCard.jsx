"use client";

import { useAuth } from "../context/AuthContext";

export default function ProfileCard() {
    const { user, logout } = useAuth();

    return (
        <div className="p-4 border-t border-slate-700 bg-slate-800 text-slate-200">
            <div className="flex items-center space-x-3">
                {/* Placeholder Avatar */}
                <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold shrink-0">
                    {user?.name?.charAt(0) || user?.email?.charAt(0)?.toUpperCase() || "U"}
                </div>

                {/* Details - hidden if too small */}
                <div className="overflow-hidden">
                    <p className="text-sm font-medium truncate">{user?.name || "Patient"}</p>
                    <p className="text-xs text-slate-400 truncate">{user?.email}</p>
                </div>
            </div>

            {/* Logout Action */}
            <button
                onClick={logout}
                className="mt-4 w-full py-2 bg-red-500/10 text-red-500 hover:bg-red-500/20 text-sm font-medium rounded transition-colors"
            >
                Sign Out
            </button>
        </div>
    );
}