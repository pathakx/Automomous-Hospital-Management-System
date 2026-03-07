"use client";

import { useEffect, useState } from "react";
import { getPrescriptions } from "../services/api";

export default function PrescriptionsPage() {
    const [prescriptions, setPrescriptions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchPrescriptions = async () => {
            try {
                const data = await getPrescriptions();
                setPrescriptions(data);
            } catch (err) {
                setError("Failed to load prescriptions.");
            } finally {
                setLoading(false);
            }
        };
        fetchPrescriptions();
    }, []);

    if (loading) return <div className="p-8 text-slate-500 animate-pulse">Loading prescriptions...</div>;
    if (error) return <div className="p-8 text-red-500">{error}</div>;

    return (
        <div className="p-6 sm:p-8 max-w-5xl mx-auto h-full overflow-y-auto">
            <h2 className="text-2xl font-bold text-slate-800 mb-6">My Prescriptions</h2>

            {prescriptions.length === 0 ? (
                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 text-center text-slate-500">
                    No prescriptions found.
                </div>
            ) : (
                <div className="space-y-4">
                    {prescriptions.map((script) => (
                        <div key={script.id} className="bg-white p-5 rounded-lg shadow-sm border border-blue-100 border-l-4 border-l-blue-500">
                            <h3 className="font-bold text-lg text-slate-800">{script.medication}</h3>
                            <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                                <div>
                                    <p className="text-slate-500">Dosage</p>
                                    <p className="font-medium">{script.dosage}</p>
                                </div>
                                <div>
                                    <p className="text-slate-500">Instructions</p>
                                    <p className="font-medium">{script.instructions}</p>
                                </div>
                                <div>
                                    <p className="text-slate-500">Prescribed By</p>
                                    <p className="font-medium">Dr. {script.doctor.user.name}</p>
                                </div>
                                <div>
                                    <p className="text-slate-500">Date</p>
                                    <p className="font-medium">{new Date(script.created_at).toLocaleDateString()}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}