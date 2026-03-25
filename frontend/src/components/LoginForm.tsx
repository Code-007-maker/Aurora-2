'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, Mail, User, Shield, ArrowRight, Loader2, AlertCircle } from 'lucide-react';

interface LoginFormProps {
    onLoginSuccess: (token: string, role: string, ward: string | null) => void;
}

export default function LoginForm({ onLoginSuccess }: LoginFormProps) {
    const [mode, setMode] = useState<'login' | 'register'>('login');
    const [identifier, setIdentifier] = useState('');
    const [email, setEmail] = useState('');
    const [fullName, setFullName] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMsg, setSuccessMsg] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setSuccessMsg('');

        try {
            if (mode === 'login') {
                const formData = new URLSearchParams();
                formData.append('username', identifier);
                formData.append('password', password);

                const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                const res = await fetch(`${apiUrl}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData,
                });

                if (!res.ok) {
                    const data = await res.json();
                    throw new Error(data.detail || 'Invalid credentials');
                }

                const data = await res.json();
                onLoginSuccess(data.access_token, data.role, data.ward);
            } else {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                const res = await fetch(`${apiUrl}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, full_name: fullName, password }),
                });

                if (!res.ok) {
                    const data = await res.json();
                    throw new Error(data.detail || 'Registration failed');
                }

                setSuccessMsg('Account created! You can now login.');
                setMode('login');
                setIdentifier(email);
            }
        } catch (err: any) {
            setError(err.message || 'Connection failed.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#020617] flex items-center justify-center p-4">
            {/* Background elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-600/10 blur-[120px] rounded-full" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md relative"
            >
                {/* Logo / Header */}
                <div className="text-center mb-8">
                    <motion.div
                        initial={{ scale: 0.8 }}
                        animate={{ scale: 1 }}
                        className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 p-0.5 mb-4 shadow-xl shadow-blue-500/20"
                    >
                        <div className="w-full h-full bg-[#020617] rounded-[14px] flex items-center justify-center">
                            <Shield className="w-8 h-8 text-blue-500" />
                        </div>
                    </motion.div>
                    <h1 className="text-3xl font-black text-white tracking-tight">AURORA</h1>
                    <p className="text-slate-400 text-sm mt-2 font-medium">Urban Flood Intelligence & Response</p>
                </div>

                {/* Form Card */}
                <div className="bg-[#0f172a]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl relative">
                    {/* Mode Toggle */}
                    <div className="flex bg-slate-900/80 p-1 rounded-xl mb-8 border border-white/5">
                        <button
                            onClick={() => setMode('login')}
                            className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${mode === 'login' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            Log In
                        </button>
                        <button
                            onClick={() => setMode('register')}
                            className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${mode === 'register' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            Sign Up
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        {mode === 'login' ? (
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Username or Email</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                        <User className="w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                                    </div>
                                    <input
                                        type="text"
                                        required
                                        value={identifier}
                                        onChange={(e) => setIdentifier(e.target.value)}
                                        className="w-full bg-slate-900/50 border border-white/5 rounded-xl py-3.5 pl-11 pr-4 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 transition-all font-medium"
                                        placeholder="Identification code"
                                    />
                                </div>
                            </div>
                        ) : (
                            <>
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Full Name</label>
                                    <div className="relative group">
                                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                            <User className="w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                                        </div>
                                        <input
                                            type="text"
                                            required
                                            value={fullName}
                                            onChange={(e) => setFullName(e.target.value)}
                                            className="w-full bg-slate-900/50 border border-white/5 rounded-xl py-3.5 pl-11 pr-4 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 transition-all font-medium"
                                            placeholder="Enter your name"
                                        />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Email Address</label>
                                    <div className="relative group">
                                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                            <Mail className="w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                                        </div>
                                        <input
                                            type="email"
                                            required
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            className="w-full bg-slate-900/50 border border-white/5 rounded-xl py-3.5 pl-11 pr-4 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 transition-all font-medium"
                                            placeholder="you@email.com"
                                        />
                                    </div>
                                </div>
                            </>
                        )}

                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">{mode === 'login' ? 'Passcode' : 'Create Password'}</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <Lock className="w-4 h-4 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                                </div>
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-slate-900/50 border border-white/5 rounded-xl py-3.5 pl-11 pr-4 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/10 transition-all font-medium"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <AnimatePresence>
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-[10px] font-bold uppercase tracking-wider"
                                >
                                    <AlertCircle className="w-4 h-4 shrink-0" />
                                    {error}
                                </motion.div>
                            )}
                            {successMsg && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="flex items-center gap-2 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider"
                                >
                                    <div className="w-4 h-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
                                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                    </div>
                                    {successMsg}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-black uppercase tracking-[0.2em] text-[10px] py-4 rounded-xl shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2 group transition-all active:scale-[0.98] disabled:opacity-70"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <>
                                    {mode === 'login' ? 'Initiate Session' : 'Create Citizen Account'}
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-8 pt-6 border-t border-white/5 text-center">
                        <p className="text-[10px] text-slate-500 uppercase tracking-[0.2em]">
                            System Security Notice
                        </p>
                        <p className="text-[10px] text-slate-600 mt-2 italic px-4">
                            Authorized personnel only. All access attempts are monitored and logged for audit purposes.
                        </p>
                    </div>
                </div>

                {/* Footer Info */}
                <div className="mt-8 flex justify-center gap-6">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        Auth Service Online
                    </span>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                        <Shield className="w-3 h-3" />
                        AES-256 Encryption
                    </span>
                </div>
            </motion.div>
        </div>
    );
}
