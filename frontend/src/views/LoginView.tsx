import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, Mail, ArrowRight, AlertTriangle, Eye, EyeOff } from 'lucide-react';
import { LoginCharacters } from './LoginCharacters';

export const LoginView = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [lookAway, setLookAway] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (email === 'demo@equilibra.com' && password === '123456') {
            navigate('/onboarding');
        } else {
            setError('Invalid credentials. Please try again.');
        }
    };

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center relative overflow-hidden font-sans selection:bg-red-500/30">
            {/* Background Glow Effects */}
            <div className="fixed top-1/4 left-1/4 w-[500px] h-[500px] bg-red-600/10 rounded-full blur-[120px] pointer-events-none" />
            <div className="fixed bottom-1/4 right-1/4 w-[500px] h-[500px] bg-orange-600/10 rounded-full blur-[120px] pointer-events-none" />

            <div className="flex w-full max-w-6xl mx-auto items-center justify-center gap-20 p-8 z-10">

                {/* Left Side: Animated Characters */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6 }}
                    className="hidden lg:block scale-110"
                >
                    <LoginCharacters lookAway={lookAway} />
                </motion.div>

                {/* Right Side: Login Form */}
                <motion.div
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="w-full max-w-md bg-zinc-900/40 backdrop-blur-xl border border-zinc-800/50 p-10 rounded-3xl shadow-2xl shadow-black/50"
                >
                    <div className="text-center mb-10">
                        <div className="flex justify-center mb-6">
                            <div className="w-14 h-14 bg-gradient-to-br from-red-600 to-orange-600 rounded-xl flex items-center justify-center shadow-lg shadow-red-900/40 p-2">
                                <img src="/diamond.png" alt="Equilibra" className="w-full h-full object-contain" />
                            </div>
                        </div>
                        <h1 className="text-4xl font-extrabold text-white tracking-tight">
                            Welcome Back.
                        </h1>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-6">
                        <div>
                            <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Username</label>
                            <div className="relative">
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="block w-full px-5 py-4 bg-black border-2 border-zinc-800 rounded-2xl focus:border-red-500 focus:ring-0 text-white placeholder-zinc-600 transition-all outline-none font-medium"
                                    placeholder="Enter username"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Password</label>
                            <div className="relative">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    onFocus={() => {
                                        setLookAway(showPassword);
                                    }}
                                    onBlur={() => setLookAway(false)}
                                    className="block w-full px-5 py-4 bg-black border-2 border-zinc-800 rounded-2xl focus:border-red-500 focus:ring-0 text-white placeholder-zinc-600 transition-all outline-none font-medium"
                                    placeholder="••••••••"
                                    required
                                />
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowPassword(!showPassword);
                                        setLookAway(!showPassword); // Inverted: if switching to visible, look away
                                    }}
                                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-zinc-500 hover:text-white transition-colors"
                                >
                                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                className="bg-red-500/10 border border-red-500/20 text-red-500 px-4 py-3 rounded-xl text-sm font-medium flex items-center gap-2"
                            >
                                <AlertTriangle size={16} />
                                {error}
                            </motion.div>
                        )}

                        <button
                            type="submit"
                            className="w-full py-4 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 rounded-2xl font-bold text-lg text-white shadow-lg shadow-red-900/20 hover:shadow-red-900/40 transition-all transform hover:-translate-y-0.5 active:translate-y-0"
                        >
                            Sign In
                        </button>
                    </form>

                    <div className="mt-8 text-center text-sm text-zinc-600">
                        <p className="font-mono bg-zinc-950/50 inline-block px-3 py-1 rounded-lg border border-zinc-800/50">
                            demo@equilibra.com / 123456
                        </p>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};
