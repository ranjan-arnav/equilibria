import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Sparkles, User, Target, Activity, Moon, Zap, Clock, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';

const SCENARIOS = [
    { id: 'exhausted', label: '😫 Exhausted', sleep: 5, energy: 3, stress: 'High', time: 1 },
    { id: 'stressed', label: '🤯 Stressed', sleep: 6, energy: 4, stress: 'High', time: 1.5 },
    { id: 'balanced', label: '⚖️ Balanced', sleep: 7.5, energy: 7, stress: 'Medium', time: 2 },
    { id: 'peak', label: '🚀 Peak', sleep: 8, energy: 9, stress: 'Low', time: 3 }
];

export const OnboardingView = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(0);
    const [loading, setLoading] = useState(false);
    const [validating, setValidating] = useState(false);

    // Form Data
    const [name, setName] = useState('');
    const [age, setAge] = useState(30);

    // State Data
    const [sleep, setSleep] = useState(7.0);
    const [energy, setEnergy] = useState(5);
    const [stress, setStress] = useState<'Low' | 'Medium' | 'High'>('Medium');
    const [time, setTime] = useState(2.0);

    // Goal Data
    const [goal, setGoal] = useState('');
    const [customGoal, setCustomGoal] = useState('');
    const [goalRisk, setGoalRisk] = useState<{ status: string, reason: string } | null>(null);

    // Generated Tasks
    const [recommendedTasks, setRecommendedTasks] = useState<any[]>([]);

    const handleScenarioSelect = (scenario: any) => {
        setSleep(scenario.sleep);
        setEnergy(scenario.energy);
        setStress(scenario.stress as any);
        setTime(scenario.time);
    };

    const handleGoalValidation = async () => {
        const targetGoal = customGoal || goal;
        if (!targetGoal) return;

        setValidating(true);
        try {
            const currentState = { sleep_hours: sleep, energy_level: energy, stress_level: stress, available_time: time };
            const result = await api.negotiateGoal(targetGoal, currentState as any);
            setGoalRisk({ status: result.status, reason: result.reasoning });
        } catch (e) {
            console.error(e);
        } finally {
            setValidating(false);
        }
    };

    const handleGeneratePlan = async () => {
        setLoading(true);
        try {
            const currentState = { sleep_hours: sleep, energy_level: energy, stress_level: stress, available_time: time };
            const userProfile = { user_id: "new", name, age, goal: customGoal || goal };

            // 1. Update Profile & Metrics
            await api.updateProfile(userProfile);
            await api.updateMetrics(currentState as any);

            // 2. Generate Tasks
            const result = await api.generateTasks(currentState as any, userProfile, userProfile.goal);
            setRecommendedTasks(result.tasks);
            setStep(4); // Move to Task Review
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleFinalize = async () => {
        navigate('/dashboard');
    };

    const variants = {
        enter: { x: 50, opacity: 0 },
        center: { x: 0, opacity: 1 },
        exit: { x: -50, opacity: 0 }
    };

    const renderStepContent = () => {
        switch (step) {
            case 0: // Welcome
                return (
                    <motion.div variants={variants} initial="enter" animate="center" exit="exit" className="text-center">
                        <div className="w-24 h-24 bg-gradient-to-br from-red-500 to-orange-500 rounded-3xl mx-auto flex items-center justify-center shadow-lg shadow-red-500/20 mb-6">
                            <img src="/diamond.png" alt="Equilibra" className="w-16 h-16" />
                        </div>
                        <h1 className="text-4xl font-bold mb-4">Welcome to Equilibra</h1>
                        <p className="text-zinc-400 mb-8 max-w-sm mx-auto">Your adaptive AI health council. Let's calibrate the system to your current reality.</p>
                        <button onClick={() => setStep(1)} className="w-full py-4 bg-white text-black font-bold rounded-xl hover:bg-zinc-200 transition-all flex items-center justify-center gap-2">
                            Calibrate System <ArrowRight size={18} />
                        </button>
                    </motion.div>
                );

            case 1: // Profile
                return (
                    <motion.div variants={variants} initial="enter" animate="center" exit="exit">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2"><User className="text-red-500" /> Who are you?</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-zinc-400 text-sm mb-2">Name</label>
                                <input value={name} onChange={e => setName(e.target.value)} className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:border-red-500 outline-none" placeholder="Enter name" autoFocus />
                            </div>
                            <div>
                                <label className="block text-zinc-400 text-sm mb-2">Age</label>
                                <input type="number" value={age} onChange={e => setAge(parseInt(e.target.value))} className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:border-red-500 outline-none" />
                            </div>
                        </div>
                        <button onClick={() => setStep(2)} disabled={!name} className="w-full mt-8 py-4 bg-zinc-800 text-white font-bold rounded-xl hover:bg-zinc-700 transition-all disabled:opacity-50">Next</button>
                    </motion.div>
                );

            case 2: // State / Scenarios
                return (
                    <motion.div variants={variants} initial="enter" animate="center" exit="exit">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2"><Activity className="text-orange-500" /> How do you feel today?</h2>

                        {/* Scenarios */}
                        <div className="grid grid-cols-2 gap-3 mb-8">
                            {SCENARIOS.map(s => (
                                <button key={s.id} onClick={() => handleScenarioSelect(s)} className="p-3 rounded-xl border border-zinc-800 bg-zinc-900/50 hover:bg-zinc-800 transition-all text-left group">
                                    <div className="font-bold text-white mb-1 group-hover:text-red-400 transition-colors">{s.label}</div>
                                </button>
                            ))}
                        </div>

                        {/* Fine Tune */}
                        <div className="space-y-4 bg-zinc-900/30 p-4 rounded-xl border border-zinc-800/50">
                            <div className="flex justify-between text-sm"><span className="text-zinc-400 flex gap-2"><Moon size={16} /> Sleep</span> <span className="text-blue-400">{sleep}h</span></div>
                            <input type="range" min="3" max="12" step="0.5" value={sleep} onChange={e => setSleep(parseFloat(e.target.value))} className="w-full accent-blue-500 h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer" />

                            <div className="flex justify-between text-sm"><span className="text-zinc-400 flex gap-2"><Zap size={16} /> Energy</span> <span className="text-yellow-400">{energy}/10</span></div>
                            <input type="range" min="1" max="10" value={energy} onChange={e => setEnergy(parseInt(e.target.value))} className="w-full accent-yellow-500 h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer" />

                            <div className="flex justify-between text-sm"><span className="text-zinc-400 flex gap-2"><Clock size={16} /> Time</span> <span className="text-green-400">{time}h</span></div>
                            <input type="range" min="0.5" max="5" step="0.5" value={time} onChange={e => setTime(parseFloat(e.target.value))} className="w-full accent-green-500 h-1 bg-zinc-800 rounded-lg appearance-none cursor-pointer" />

                            <div className="flex justify-between items-center text-sm">
                                <div className="text-zinc-400 flex gap-2"><AlertTriangle size={16} /> Stress</div>
                                <div className="flex gap-1">
                                    {['Low', 'Medium', 'High'].map(l => (
                                        <button key={l} onClick={() => setStress(l as any)} className={`px-2 py-1 rounded text-xs border ${stress === l ? 'bg-zinc-700 text-white border-zinc-500' : 'border-zinc-800 text-zinc-500'}`}>{l}</button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <button onClick={() => setStep(3)} className="w-full mt-6 py-4 bg-zinc-800 text-white font-bold rounded-xl hover:bg-zinc-700 transition-all">Confirm State</button>
                    </motion.div>
                );

            case 3: // Goal
                return (
                    <motion.div variants={variants} initial="enter" animate="center" exit="exit">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2"><Target className="text-red-500" /> Current Goal</h2>

                        <div className="space-y-2 mb-6">
                            {['Maximize Productivity', 'Recovery & Rest', 'Maintenance', 'High Performance'].map(g => (
                                <button key={g} onClick={() => { setGoal(g); setCustomGoal(''); setGoalRisk(null); }} className={`w-full p-4 rounded-xl border text-left transition-all ${goal === g && !customGoal ? 'bg-red-500/10 border-red-500 text-white' : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:border-zinc-700'}`}>
                                    {g}
                                </button>
                            ))}
                        </div>

                        <div className="relative mb-6">
                            <input
                                value={customGoal}
                                onChange={e => { setCustomGoal(e.target.value); setGoal(''); setGoalRisk(null); }}
                                placeholder="Or enter custom goal..."
                                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:border-red-500 outline-none"
                            />
                            {(customGoal || goal) && !goalRisk && (
                                <button onClick={handleGoalValidation} disabled={validating} className="absolute right-2 top-2 px-3 py-1 bg-zinc-800 rounded-lg text-xs font-bold text-zinc-300 hover:text-white">
                                    {validating ? 'Checking...' : 'Check Safety'}
                                </button>
                            )}
                        </div>

                        {goalRisk && (
                            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`p-4 rounded-xl border mb-6 ${goalRisk.status === 'ACCEPTED' ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
                                <div className={`font-bold text-sm mb-1 ${goalRisk.status === 'ACCEPTED' ? 'text-green-500' : 'text-red-500'}`}>
                                    {goalRisk.status === 'ACCEPTED' ? 'Goal Safe & Aligned' : 'Goal Risky - Adjustment Needed'}
                                </div>
                                <p className="text-xs text-zinc-400">{goalRisk.reason}</p>
                            </motion.div>
                        )}

                        <button onClick={handleGeneratePlan} disabled={(!goal && !customGoal) || loading} className="w-full py-4 bg-gradient-to-r from-red-600 to-orange-600 text-white font-bold rounded-xl hover:opacity-90 transition-all flex items-center justify-center gap-2 disabled:opacity-50">
                            {loading ? 'Generating Plan...' : 'Generate Daily Plan'} <Sparkles size={18} />
                        </button>
                    </motion.div>
                );

            case 4: // Plan Review
                return (
                    <motion.div variants={variants} initial="enter" animate="center" exit="exit">
                        <h2 className="text-2xl font-bold mb-2 flex items-center gap-2"><Sparkles className="text-yellow-500" /> Your Daily Plan</h2>

                        <p className="text-zinc-500 text-sm mb-6">AI generated based on your state & goals. You can later change your decisions in <span className="font-bold text-white">Make Decision &rarr; 📅 Today's Schedule</span></p>

                        <div className="space-y-3 mb-8 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                            {recommendedTasks.map((task, i) => (
                                <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl hover:border-zinc-700 transition-colors group relative">
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="font-bold text-white">{task.title}</div>
                                        <div className="text-xs font-medium px-2 py-1 bg-zinc-800 rounded text-zinc-400">{task.duration}m</div>
                                    </div>
                                    <div className="text-xs text-zinc-500 mb-2 uppercase tracking-wider font-bold">{task.domain}</div>
                                    <p className="text-sm text-zinc-400 italic">"{task.reason}"</p>
                                </motion.div>
                            ))}
                        </div>

                        <button onClick={handleFinalize} className="w-full py-4 bg-white text-black font-bold rounded-xl hover:bg-zinc-200 transition-all">
                            Accept & Start Day
                        </button>
                    </motion.div>
                );
            default: return null;
        }
    };

    return (
        <div className="min-h-screen bg-zinc-950 flex flex-col items-center justify-center p-6 text-white relative overflow-hidden">
            {/* Background Ambience */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-red-600/5 rounded-full blur-[100px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-orange-600/5 rounded-full blur-[100px]" />
            </div>

            <div className="w-full max-w-md relative z-10">
                {/* Progress Dots */}
                {step > 0 && step < 5 && (
                    <div className="flex justify-center gap-2 mb-8">
                        {[1, 2, 3, 4].map(i => (
                            <div key={i} className={`h-1 rounded-full transition-all duration-500 ${i <= step ? 'bg-red-500 w-8' : 'bg-zinc-800 w-2'}`} />
                        ))}
                    </div>
                )}

                <AnimatePresence mode="wait">
                    <motion.div
                        key={step}
                        className="bg-zinc-900/50 border border-zinc-800 backdrop-blur-xl p-8 rounded-3xl shadow-2xl"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                    >
                        {renderStepContent()}
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    );
};
