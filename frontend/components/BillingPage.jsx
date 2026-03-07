"use client";

import { useEffect, useState } from "react";
import { getBills } from "../services/api";

export default function BillingPage() {
    const [bills, setBills] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [filter, setFilter] = useState("all"); // 'all' or 'pending'

    useEffect(() => {
        const fetchBills = async () => {
            try {
                const data = await getBills();
                setBills(data);
            } catch (err) {
                setError("Failed to load bills.");
            } finally {
                setLoading(false);
            }
        };
        fetchBills();
    }, []);

    const filteredBills = bills.filter(bill => {
        if (filter === "pending") return bill.status === "pending";
        return true;
    });

    if (loading) return <div className="p-8 text-slate-500 animate-pulse">Loading bills...</div>;
    if (error) return <div className="p-8 text-red-500">{error}</div>;

    return (
        <div className="p-6 sm:p-8 max-w-5xl mx-auto h-full overflow-y-auto">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
                <h2 className="text-2xl font-bold text-slate-800">Billing & Payments</h2>
                <div className="bg-slate-200 p-1 rounded-md inline-flex text-sm">
                    <button
                        onClick={() => setFilter("all")}
                        className={`px-4 py-1.5 rounded ${filter === "all" ? "bg-white shadow font-medium text-slate-800" : "text-slate-600 hover:text-slate-800"}`}
                    >
                        All Bills
                    </button>
                    <button
                        onClick={() => setFilter("pending")}
                        className={`px-4 py-1.5 rounded ${filter === "pending" ? "bg-white shadow font-medium text-slate-800" : "text-slate-600 hover:text-slate-800"}`}
                    >
                        Pending Only
                    </button>
                </div>
            </div>

            {filteredBills.length === 0 ? (
                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 text-center text-slate-500">
                    No bills found for this category.
                </div>
            ) : (
                <div className="space-y-4">
                    {filteredBills.map((bill) => (
                        <div key={bill.id} className="bg-white p-5 rounded-lg shadow-sm border border-slate-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:border-slate-300 transition-colors">
                            <div>
                                <h3 className="font-semibold text-lg text-slate-800">Hospital Services</h3>
                                <p className="text-slate-500 text-sm mt-1">{new Date(bill.created_at).toLocaleDateString()}</p>
                            </div>
                            <div className="flex items-center gap-4 w-full sm:w-auto justify-between sm:justify-end">
                                <p className="text-xl font-bold text-slate-800">${parseFloat(bill.amount).toFixed(2)}</p>
                                <span className={`px-3 py-1 text-xs font-medium rounded-full ${bill.status === "paid" ? "bg-green-100 text-green-700" : "bg-orange-100 text-orange-700"
                                    }`}>
                                    {bill.status.toUpperCase()}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
