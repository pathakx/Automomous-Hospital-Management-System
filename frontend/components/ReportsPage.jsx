"use client";

import { useEffect, useState } from "react";
import { getReports } from "../services/api";

export default function ReportsPage() {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    useEffect(() => {
        const fetchReports = async () => {
            try {
                const data = await getReports();
                setReports(data);
            } catch (err) {
                setError("Failed to load lab reports.");
            } finally {
                setLoading(false);
            }
        };
        fetchReports();
    }, []);

    if (loading) return <div className="p-8 text-slate-500 animate-pulse">Loading reports...</div>;
    if (error) return <div className="p-8 text-red-500">{error}</div>;

    return (
        <div className="p-6 sm:p-8 max-w-5xl mx-auto h-full overflow-y-auto">
            <h2 className="text-2xl font-bold text-slate-800 mb-6">Lab Reports</h2>

            {reports.length === 0 ? (
                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 text-center text-slate-500">
                    No reports found.
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2">
                    {reports.map((report) => (
                        <div key={report.id} className="bg-white p-5 rounded-lg shadow-sm border border-slate-200">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="font-semibold text-lg text-slate-800">{report.report_type}</h3>
                                    <p className="text-slate-400 text-xs mt-1">
                                        Uploaded: {new Date(report.uploaded_at).toLocaleDateString()}
                                    </p>
                                </div>
                                <span className="text-2xl">📋</span>
                            </div>
                            <a
                                href={`${backendUrl}/${report.file_url}`}
                                target="_blank"
                                rel="noreferrer"
                                className="block w-full text-center bg-slate-100 hover:bg-slate-200 text-blue-600 font-medium py-2 rounded transition-colors text-sm"
                            >
                                View Document
                            </a>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
