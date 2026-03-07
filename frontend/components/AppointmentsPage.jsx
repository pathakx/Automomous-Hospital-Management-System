"use client";

import { useEffect, useState } from "react";
import { getAppointments } from "../services/api";

export default function AppointmentsPage() {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchAppointments = async () => {
            try {
                const data = await getAppointments();
                setAppointments(data);
            } catch (err) {
                setError("Failed to load appointments.");
            } finally {
                setLoading(false);
            }
        };
        fetchAppointments();
    }, []);

    if (loading) return <div className="p-8 text-slate-500 animate-pulse">Loading appointments...</div>;
    if (error) return <div className="p-8 text-red-500">{error}</div>;

    return (
        <div className="p-6 sm:p-8 max-w-5xl mx-auto h-full overflow-y-auto">
            <h2 className="text-2xl font-bold text-slate-800 mb-6">My Appointments</h2>

            {appointments.length === 0 ? (
                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 text-center text-slate-500">
                    No appointments found.
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-2">
                    {appointments.map((apt) => (
                        <div key={apt.id} className="bg-white p-5 rounded-lg shadow-sm border border-slate-200 flex justify-between items-start hover:shadow-md transition-shadow">
                            <div>
                                <h3 className="font-semibold text-lg text-slate-800">Dr. {apt.doctor.user.name}</h3>
                                <p className="text-slate-500 text-sm mt-1">{apt.appointment_date} at {apt.appointment_time}</p>
                                {apt.reason && <p className="text-slate-600 text-sm mt-2 italic">"{apt.reason}"</p>}
                            </div>
                            <span className={`px-3 py-1 text-xs font-medium rounded-full ${apt.status === "scheduled" ? "bg-green-100 text-green-700" :
                                    apt.status === "cancelled" ? "bg-red-100 text-red-700" :
                                        "bg-yellow-100 text-yellow-700"
                                }`}>
                                {apt.status.charAt(0).toUpperCase() + apt.status.slice(1)}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
