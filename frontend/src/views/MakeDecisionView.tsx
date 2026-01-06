import { useState } from 'react';
import { AlertTriangle, CheckCircle, XCircle, Activity, Zap, TrendingUp, ShieldAlert, Sparkles, Edit3, Save, Plus, Trash2 } from 'lucide-react';
import { RefreshCw } from 'lucide-react';
import { api } from '../api';
import type { HealthState, UserProfile } from '../api';

interface MakeDecisionProps {
    currentState: HealthState;
    dailyTasks: any[];
    userProfile?: UserProfile;
    onDecisionComplete?: () => void;
}

export const MakeDecisionView = ({ currentState, dailyTasks: initialTasks, userProfile, onDecisionComplete }: MakeDecisionProps) => {
    const [loading, setLoading] = useState(false);
    const [regenerating, setRegenerating] = useState(false);
    const [result, setResult] = useState<any | null>(null);
    const [dailyTasks, setDailyTasks] = useState(initialTasks);
    const [isEditing, setIsEditing] = useState(false);
    const [analyzingIndex, setAnalyzingIndex] = useState<number | null>(null);

    // Sync if props change
    if (initialTasks !== dailyTasks && !isEditing && initialTasks.length > 0 && dailyTasks.length === 0) {
        setDailyTasks(initialTasks);
    }

    // Dynamic Projections
    const metrics = currentState.computed_metrics;
    const readinessScore = metrics?.readiness_score ?? 50;
    const burnoutRisk = metrics?.burnout_risk_label ?? "Evaluating...";
    const recIntensity = readinessScore > 70 ? "High" : readinessScore > 40 ? "Moderate" : "Low";

    const handleRegeneratePlan = async () => {
        if (!userProfile) return;
        setRegenerating(true);
        try {
            const response = await api.generateTasks(
                currentState,
                userProfile,
                userProfile.goal
            );
            setDailyTasks(response.tasks);
            if (onDecisionComplete) onDecisionComplete();
        } catch (e) {
            console.error("Failed to regenerate", e);
        } finally {
            setRegenerating(false);
        }
    };


    const handleRunDecision = async () => {
        setLoading(true);
        // Simulate analyzing the ENTIRE daily schedule
        // For this demo, we'll pick the first "fitness" task or just a generic "Day Plan" check
        try {
            // We use the first task or a default activity to trigger the decision engine for now
            // Ideally backend would accept a full schedule
            const targetTask = dailyTasks.find(t => t.domain === 'fitness') || dailyTasks[0] || { title: "General Day Plan", domain: "wellness", duration: 60 };

            const decision = await api.makeDecision(targetTask.title, targetTask.domain, targetTask.duration || 60, currentState);
            setResult(decision);

            // Refresh parent state to update Council View
            if (onDecisionComplete) {
                onDecisionComplete();
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const toggleTask = (index: number) => {
        if (isEditing) return;
        const newTasks = [...dailyTasks];
        newTasks[index].completed = !newTasks[index].completed;
        setDailyTasks(newTasks);
    };

    const handleSaveSchedule = async () => {
        setIsEditing(false);
        try {
            await api.updateTasks(dailyTasks);
        } catch (e) {
            console.error("Failed to save tasks", e);
        }
    };

    const addTask = () => {
        setDailyTasks([...dailyTasks, { title: "New Task", duration: 30, domain: "productivity", reason: "User added task" }]);
    };

    const removeTask = (index: number) => {
        const newTasks = [...dailyTasks];
        newTasks.splice(index, 1);
        setDailyTasks(newTasks);
    };

    const updateTaskField = (index: number, field: string, value: any) => {
        const newTasks = [...dailyTasks];
        newTasks[index] = { ...newTasks[index], [field]: value };
        setDailyTasks(newTasks);
    };

    const handleAILookup = async (index: number) => {
        const task = dailyTasks[index];
        if (!task.title || task.title === "New Task") return;

        setAnalyzingIndex(index);
        try {
            const analysis = await api.analyzeTask(task.title, currentState);
            const newTasks = [...dailyTasks];
            newTasks[index] = {
                ...newTasks[index],
                domain: analysis.domain.toLowerCase(),
                reason: analysis.reason,
                is_unsafe: !analysis.is_safe // Flag for UI
            };
            setDailyTasks(newTasks);
        } catch (e) {
            console.error(e);
        } finally {
            setAnalyzingIndex(null);
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-8 pb-20">

            {/* 1. AI Health Projections */}
            <div>
                <div className="flex items-center gap-2 mb-6">
                    <span className="text-2xl">🔮</span>
                    <h2 className="text-xl font-bold text-white">AI Health Projections</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
                        <div className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-1">Tomorrow's Readiness</div>
                        <div className="text-3xl font-bold text-white">{readinessScore}/100</div>
                        <div className="text-green-500 text-xs font-bold flex items-center gap-1 mt-1"><TrendingUp size={12} /> +0</div>
                    </div>
                    <div className="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
                        <div className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-1">Burnout Risk</div>
                        <div className="text-2xl font-bold text-white">{burnoutRisk}</div>
                        <div className="text-green-500 text-xs font-bold flex items-center gap-1 mt-1"><Activity size={12} /> Stable</div>
                    </div>
                    <div className="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
                        <div className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-1">Rec. Intensity</div>
                        <div className="text-2xl font-bold text-white">{recIntensity}</div>
                        <div className="text-green-500 text-xs font-bold flex items-center gap-1 mt-1"><Sparkles size={12} /> AI Adaptive</div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Transmission */}
                    <div className="bg-green-900/10 border border-green-500/20 p-6 rounded-xl flex flex-col justify-center">
                        <div className="text-[10px] font-bold text-green-500 uppercase tracking-widest mb-2 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" /> INCOMING TRANSMISSION // T-MINUS 7 DAYS
                        </div>
                        <div className="flex items-center gap-2 text-green-400 font-bold text-lg mb-2">
                            ⚓ Holding Steady
                        </div>
                        <p className="text-green-400/70 text-sm font-mono italic">
                            "Smooth sailing this week. Good job keeping the balance."
                        </p>
                    </div>

                    {/* AI Reccommended */}
                    <div className="bg-blue-900/10 border border-blue-500/20 p-6 rounded-xl relative overflow-hidden">
                        <div className="flex justify-between items-start mb-2">
                            <div className="text-[10px] font-bold text-blue-400 uppercase tracking-widest flex items-center gap-2">
                                <Sparkles size={12} /> AI RECOMMENDED
                            </div>
                            <span className="text-xs font-bold text-blue-300 bg-blue-500/10 px-2 py-1 rounded">45 min</span>
                        </div>
                        <div className="text-xl font-bold text-white mb-1">Threshold Run / Cycle</div>
                        <p className="text-blue-400/70 text-sm font-mono italic">
                            "Good capacity for cardiovascular strain."
                        </p>
                    </div>
                </div>
            </div>

            {/* 2. Today's Schedule */}
            <div>
                <div className="flex items-center justify-between mb-4 mt-8">
                    <div className="flex items-center gap-2">
                        <span className="text-xl">📅</span>
                        <h2 className="text-lg font-bold text-white">Today's Schedule</h2>
                    </div>
                    <div className="flex items-center gap-2">
                        {/* Edit Controls */}
                        {isEditing ? (
                            <div className="flex items-center gap-2">
                                <button onClick={handleSaveSchedule} className="flex items-center gap-1 px-3 py-1.5 bg-green-500/10 text-green-400 border border-green-500/20 rounded-lg text-xs font-bold hover:bg-green-500/20 transition-colors">
                                    <Save size={14} /> SAVE
                                </button>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={handleRegeneratePlan}
                                    disabled={regenerating}
                                    className="flex items-center gap-1 px-3 py-1.5 bg-zinc-800 text-zinc-400 border border-zinc-700 rounded-lg text-xs font-bold hover:text-white hover:bg-zinc-700 transition-colors disabled:opacity-50"
                                >
                                    <RefreshCw size={14} className={regenerating ? "animate-spin" : ""} />
                                    {regenerating ? 'PLANNING...' : 'REGENERATE'}
                                </button>
                                <button onClick={() => setIsEditing(true)} className="flex items-center gap-1 px-3 py-1.5 bg-zinc-800 text-zinc-400 border border-zinc-700 rounded-lg text-xs font-bold hover:text-white hover:bg-zinc-700 transition-colors">
                                    <Edit3 size={14} /> EDIT
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Circuit Breaker Status (Only show when not editing) */}
                {!isEditing && (
                    <div className="flex gap-2 mb-4">
                        {result?.action === 'REJECTED' && (
                            <div className="flex items-center gap-2 px-3 py-1 bg-red-500/10 border border-red-500/20 rounded-full">
                                <ShieldAlert size={14} className="text-red-500" />
                                <span className="text-xs font-bold text-red-500 uppercase tracking-wider">CIRCUIT BREAKER ENGAGED</span>
                            </div>
                        )}
                        {result?.action === 'MODIFIED' && (
                            <div className="flex items-center gap-2 px-3 py-1 bg-yellow-500/10 border border-yellow-500/20 rounded-full">
                                <AlertTriangle size={14} className="text-yellow-500" />
                                <span className="text-xs font-bold text-yellow-500 uppercase tracking-wider">MODIFICATIONS APPLIED</span>
                            </div>
                        )}
                    </div>
                )}

                <div className="space-y-2">
                    {dailyTasks.length > 0 ? dailyTasks.map((task, i) => (
                        <div key={i} className={`p-4 rounded-xl border flex items-center justify-between transition-all ${isEditing ? 'bg-zinc-900 border-zinc-800' :
                            task.completed ? 'bg-zinc-900/30 border-zinc-800 opacity-50'
                                : result?.action === 'REJECTED' && task.domain === 'fitness' ? 'bg-red-900/10 border-red-500/20'
                                    : 'bg-zinc-900 border-zinc-800 hover:border-zinc-700'
                            }`}>

                            <div className="flex items-center gap-4 w-full">
                                {!isEditing && <span className="text-xs font-mono text-zinc-500">0{8 + i}:00</span>}
                                <div className="flex-1">
                                    {isEditing ? (
                                        <div className="flex gap-2 w-full items-center">
                                            <div className="relative flex-1">
                                                <input
                                                    value={task.title}
                                                    onChange={(e) => updateTaskField(i, 'title', e.target.value)}
                                                    onBlur={() => handleAILookup(i)} // Auto-analyze on blur
                                                    className={`w-full bg-zinc-950 border ${task.is_unsafe ? 'border-red-500' : 'border-zinc-700'} rounded px-2 py-1 text-sm text-white`}
                                                    placeholder="Task Title"
                                                />
                                                {analyzingIndex === i && (
                                                    <div className="absolute right-2 top-1/2 -translate-y-1/2">
                                                        <Sparkles size={12} className="text-yellow-500 animate-spin" />
                                                    </div>
                                                )}
                                                {task.is_unsafe && (
                                                    <div className="absolute right-2 top-1/2 -translate-y-1/2 text-red-500" title={task.reason || "Unsafe task"}>
                                                        <ShieldAlert size={14} />
                                                    </div>
                                                )}
                                            </div>
                                            <select
                                                value={task.domain}
                                                onChange={(e) => updateTaskField(i, 'domain', e.target.value)}
                                                className="bg-zinc-950 border border-zinc-700 rounded px-2 py-1 text-xs text-zinc-400 capitalize"
                                            >
                                                {['fitness', 'nutrition', 'wellness', 'productivity', 'mindfulness'].map(d => (
                                                    <option key={d} value={d}>{d}</option>
                                                ))}
                                            </select>
                                            <button
                                                onClick={() => handleAILookup(i)}
                                                className="p-1 rounded hover:bg-zinc-800 text-yellow-500"
                                                title="AI Categorize & Check"
                                            >
                                                <Sparkles size={14} />
                                            </button>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <div className={`font-bold transition-all ${task.completed ? 'line-through text-zinc-500' : task.is_blocked ? 'line-through text-red-400 decoration-red-500/50' : 'text-white'}`}>
                                                        {task.title}
                                                    </div>

                                                    {/* Blocked Status */}
                                                    {task.is_blocked && (
                                                        <div className="flex items-center gap-2 mt-2">
                                                            <div className="flex items-center gap-1 text-[10px] font-bold text-red-500 bg-red-500/10 px-2 py-0.5 rounded border border-red-500/20 uppercase tracking-wider">
                                                                <ShieldAlert size={10} />
                                                                Circuit Breaker Engaged
                                                            </div>
                                                            <span className="text-xs text-red-400/70 italic flex-1 truncate" title={task.block_reason}>
                                                                {task.block_reason}
                                                            </span>
                                                        </div>
                                                    )}

                                                    {/* AI Rejection from Council */}
                                                    {!task.is_blocked && result?.action === 'REJECTED' && task.domain === 'fitness' && (
                                                        <div className="text-xs text-red-400 font-bold mt-1">🚫 BLOCKED BY CIRCUIT BREAKER</div>
                                                    )}
                                                </div>

                                                {/* Override Button */}
                                                {task.is_blocked && !task.completed && (
                                                    <button
                                                        onClick={() => {
                                                            const reason = window.prompt("⚠️ SAFETY OVERRIDE\n\nThe AI has blocked this task for your safety.\nTo proceed, please explain why you are overriding this protocol:");
                                                            if (reason && reason.length > 5) {
                                                                const newTasks = [...dailyTasks];
                                                                newTasks[i].is_blocked = false;
                                                                newTasks[i].reason = "OVERRIDE: " + reason;
                                                                setDailyTasks(newTasks);
                                                                handleSaveSchedule(); // Auto-save
                                                            }
                                                        }}
                                                        className="px-2 py-1 ml-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 rounded text-[10px] font-bold text-red-500 uppercase transition-colors"
                                                    >
                                                        Override
                                                    </button>
                                                )}
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>

                            {/* Actions */}
                            {isEditing ? (
                                <button onClick={() => removeTask(i)} className="ml-4 text-zinc-500 hover:text-red-500 transition-colors">
                                    <Trash2 size={16} />
                                </button>
                            ) : (
                                <button onClick={() => toggleTask(i)} className={`ml-4 w-6 h-6 rounded-full border flex items-center justify-center ${task.completed ? 'bg-green-500 border-green-500' : 'border-zinc-600 hover:border-zinc-500'}`}>
                                    {task.completed && <CheckCircle size={14} className="text-black" />}
                                </button>
                            )}
                        </div>
                    )) : (
                        <div className="p-8 text-center border border-dashed border-zinc-800 rounded-xl text-zinc-500">
                            No plan generated. Visit Onboarding to generate a plan.
                        </div>
                    )}

                    {isEditing && (
                        <button onClick={addTask} className="w-full py-3 border border-dashed border-zinc-800 rounded-xl text-zinc-500 hover:text-white hover:border-zinc-600 hover:bg-zinc-900 transition-all flex items-center justify-center gap-2 text-sm font-bold">
                            <Plus size={16} /> Add Task
                        </button>
                    )}
                </div>
            </div>

            {/* 3. Current State & Action */}
            <div>
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                    <div className="flex items-center gap-2 mb-6">
                        <span className="text-xl">📊</span>
                        <h2 className="text-lg font-bold text-white">Current State</h2>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
                        <div>
                            <div className="text-xs font-bold text-zinc-500 uppercase mb-1">SLEEP</div>
                            <div className="text-2xl font-bold text-white">{currentState.sleep_hours}h</div>
                        </div>
                        <div>
                            <div className="text-xs font-bold text-zinc-500 uppercase mb-1">ENERGY</div>
                            <div className="text-2xl font-bold text-white">{currentState.energy_level}/10</div>
                        </div>
                        <div>
                            <div className="text-xs font-bold text-zinc-500 uppercase mb-1">STRESS</div>
                            <div className="text-2xl font-bold text-white">{currentState.stress_level}</div>
                        </div>
                        <div>
                            <div className="text-xs font-bold text-zinc-500 uppercase mb-1">TIME AVAILABLE</div>
                            <div className="text-2xl font-bold text-white">{currentState.available_time}h</div>
                        </div>
                    </div>

                    <button
                        onClick={handleRunDecision}
                        disabled={loading}
                        className="w-full py-4 bg-blue-500 hover:bg-blue-600 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2"
                    >
                        {loading ? 'Consulting Council...' : <><Zap size={18} fill="currentColor" /> Run Agent Decision</>}
                    </button>
                </div>

                {/* Tips */}
                {!result && (
                    <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-8 text-sm">
                        <div className="bg-zinc-900/30 border border-zinc-800/50 p-4 rounded-xl">
                            <div className="flex items-center gap-2 text-yellow-500 font-bold mb-2">
                                <Sparkles size={14} /> Adjust your inputs
                            </div>
                            <p className="text-zinc-500">Adjust your inputs in the Simulation tab and click 'Run Agent Decision' to see the agent in action!</p>
                        </div>
                        <div>
                            <h4 className="flex items-center gap-2 text-white font-bold mb-2"><Sparkles size={14} className="text-orange-500" /> How it works</h4>
                            <ul className="space-y-1 text-zinc-500">
                                <li>1. <strong className="text-zinc-400">State Analyzer</strong> reads your data.</li>
                                <li>2. <strong className="text-zinc-400">Council</strong> debates trade-offs.</li>
                                <li>3. <strong className="text-zinc-400">Plan Adjuster</strong> modifies your schedule.</li>
                            </ul>
                        </div>
                    </div>
                )}
            </div>

            {/* 4. Agent Decision Results (Conditional) */}
            {result && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                    <div className="flex items-center gap-2 mt-8">
                        <span className="text-xl">🤖</span>
                        <h2 className="text-lg font-bold text-white">Agent Decision Results</h2>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-zinc-900 border border-zinc-800 p-6 rounded-2xl">
                        <div>
                            <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">READINESS SCORE</div>
                            <div className="text-2xl font-bold text-white">{readinessScore}/100</div>
                        </div>
                        <div>
                            <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">SLEEP QUALITY</div>
                            <div className="text-2xl font-bold text-white">77/100</div>
                        </div>
                        <div>
                            <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">ACTIVE CONSTRAINTS</div>
                            <div className="text-2xl font-bold text-white">{result.constraints?.length || 0}</div>
                        </div>
                        <div>
                            <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">CONFIDENCE</div>
                            <div className="text-2xl font-bold text-white">95%</div>
                        </div>
                    </div>

                    {/* Domain Decisions */}
                    <div>
                        <h3 className="text-sm font-bold text-zinc-400 mb-4">Domain Decisions</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {['Recovery', 'Fitness', 'Nutrition', 'Mindfulness'].map(domain => {
                                const isAffected = result.domain?.toLowerCase() === domain.toLowerCase() || (result.action === 'REJECTED' && domain === 'Fitness');
                                let status = 'MAINTAIN';
                                if (isAffected) status = result.action === 'REJECTED' ? 'SKIP' : result.action === 'MODIFIED' ? 'MODIFY' : 'PROCEED';
                                if (domain === 'Fitness' && result.action === 'REJECTED') status = 'SKIP';

                                const borderColor = status === 'SKIP' ? 'border-red-500' : status === 'MODIFY' ? 'border-yellow-500' : 'border-blue-500/30';
                                const bgColor = status === 'SKIP' ? 'bg-red-500/5' : status === 'MODIFY' ? 'bg-yellow-500/5' : 'bg-blue-500/5';
                                const textColor = status === 'SKIP' ? 'text-red-500' : status === 'MODIFY' ? 'text-yellow-500' : 'text-white';

                                return (
                                    <div key={domain} className={`p-4 rounded-xl border ${isAffected ? borderColor + ' ' + bgColor : 'border-zinc-800 bg-zinc-900/50'}`}>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className={`font-bold ${isAffected ? textColor : 'text-blue-400'}`}>{domain}</span>
                                            <span className={`text-xs font-bold flex items-center gap-1 ${status === 'SKIP' ? 'text-red-500' : 'text-white'}`}>
                                                {status === 'SKIP' && <XCircle size={12} />}
                                                {status === 'MAINTAIN' && <CheckCircle size={12} />}
                                                {status}
                                            </span>
                                        </div>
                                        <div className="text-xs text-zinc-500">
                                            {isAffected ? result.reasoning.slice(0, 50) + "..." : `${domain} as planned`}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Reasoning Summary */}
                    <div>
                        <h3 className="text-sm font-bold text-zinc-400 mb-2 flex items-center gap-2"><Activity size={16} /> Reasoning Summary</h3>
                        <div className="bg-blue-900/20 border border-blue-500/20 p-4 rounded-xl text-blue-200 text-sm italic">
                            {result.reasoning}
                        </div>
                    </div>

                    {/* Detailed Explanation */}
                    <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
                        <div className="bg-zinc-800/50 px-4 py-2 border-b border-zinc-700 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-pink-500">
                            <Sparkles size={12} /> Detailed AI Explanation
                        </div>
                        <div className="p-4 text-zinc-400 text-sm leading-relaxed">
                            I totally get that you're feeling a bit drained today, and with {currentState.stress_level} stress levels, it's amazing you're taking care of yourself as much as you are. Given your limited time and energy, we've prioritized recovery, nutrition, and mindfulness to help you feel more grounded and focused - these are all smart choices to support your well-being right now.
                            {result.action === 'REJECTED' && " Skipping fitness today might feel like a setback, but it's actually a thoughtful decision to conserve your energy for more important things."}
                            Looking ahead, let's aim to add some light activity to your routine tomorrow if your energy levels improve.
                        </div>
                    </div>

                </div>
            )}
        </div>
    );
};
