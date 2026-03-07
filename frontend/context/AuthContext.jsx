"use client";

import { createContext, useState, useEffect, useContext } from "react";
import { useRouter, usePathname } from "next/navigation";
import { loginUser as apiLogin, registerUser as apiRegister, getProfile } from "../services/api";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        // Check if user is already logged in on mount
        const loadUser = async () => {
            const token = localStorage.getItem("access_token");
            if (token) {
                try {
                    const profile = await getProfile();
                    setUser(profile);
                } catch (error) {
                    console.error("Failed to fetch profile", error);
                    localStorage.removeItem("access_token");
                    localStorage.removeItem("refresh_token");
                }
            }
            setLoading(false);
        };

        loadUser();
    }, []);

    // Protect routes middleware effect
    useEffect(() => {
        if (!loading) {
            const isPublicRoute = pathname === "/login" || pathname === "/register" || pathname === "/";
            if (!user && !isPublicRoute) {
                router.push("/login"); // Redirect unauthenticated users
            } else if (user && isPublicRoute && pathname !== "/") {
                router.push("/dashboard"); // Redirect authenticated users away from public pages
            }
        }
    }, [user, loading, pathname, router]);

    const login = async (email, password) => {
        const data = await apiLogin(email, password);
        localStorage.setItem("access_token", data.access_token);
        if (data.refresh_token) {
            localStorage.setItem("refresh_token", data.refresh_token);
        }
        const profile = await getProfile();
        setUser(profile);
        router.push("/dashboard");
    };

    const register = async (name, email, phone, password) => {
        await apiRegister(name, email, phone, password);
        router.push("/login"); // redirect to login upon successful registration
    };

    const logout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setUser(null);
        router.push("/login");
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);