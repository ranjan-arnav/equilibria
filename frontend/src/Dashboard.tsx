import { useState, useEffect } from 'react';
import { LayoutDashboard, Users, MessageSquare, History, Wand2, Settings, LogOut, Flame, Target, Zap, Lightbulb, Clock, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from './api';
import type { HealthState, FullState } from './api';

import { CouncilView } from './views/CouncilView';
import { MakeDecisionView } from './views/MakeDecisionView';
import { ChatView } from './views/ChatView';

// --- Shared Components ---

const SidebarItem = ({ icon: Icon, label, active = false, onClick }: { icon: any, label: string, active?: boolean, onClick?: () => void }) => (
    <div
        onClick={onClick}
        className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-colors ${active
            ? 'bg-red-500/10 text-red-500 border border-red-500/20'
            : 'text-zinc-500 hover:bg-zinc-900 hover:text-zinc-200'
            }`}
    >
        <Icon size={20} />
        <span className="font-medium">{label}</span>
    </div>
);

const StatCard = ({ label, value, subtext, icon: Icon, color }: { label: string, value: string, subtext: string, icon: any, color: string }) => (
    <div className="bg-zinc-900 border border-zinc-800 p-5 rounded-2xl relative overflow-hidden">
        <div className={`absolute top-0 right-0 p-4 opacity-10 text-${color}-500`}>
            <Icon size={64} />
        </div>
        <div className="relative z-10">
            <h3 className="text-zinc-500 text-xs font-bold uppercase tracking-wider mb-2">{label}</h3>
            <div className="text-3xl font-bold text-white mb-2">{value}</div>
            <div className={`text-sm font-medium flex items-center gap-1.5 text-${color}-500`}>
                {subtext}
            </div>
        </div>
    </div>
);

// --- Views ---

const HomeView = ({ fullState }: { fullState: FullState | null }) => {
    // Derived values
    const metrics = fullState?.current_state.computed_metrics;

    // Fallback safe defaults if metrics aren't computed yet
    const riskScore = metrics?.burnout_risk_score ?? 10;
    const riskLabel = metrics?.burnout_risk_label?.toUpperCase() ?? "LOW RISK";
    const readiness = metrics?.readiness_score ?? 71;
    const streak = "1 days"; // Still mocked until streak tracking is added
    const adherence = "100%"; // Still mocked

    const lastDecision = fullState?.decision_history?.[fullState.decision_history.length - 1];

    return (
        <div className="max-w-7xl mx-auto space-y-6">
            {/* Welcome Section */}
            <div>
                <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                    👋 Welcome back, {fullState?.user_profile?.name || "Demo User"}
                </h1>
                <p className="text-zinc-500 mt-1">Here's your daily balance snapshot.</p>
            </div>

            {/* Top Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatCard
                    label="Current Streak"
                    value={streak}
                    subtext="Keep it up! 🔥"
                    icon={Flame}
                    color="orange"
                />
                <StatCard
                    label="Adherence"
                    value={adherence}
                    subtext="On track 🎯"
                    icon={Target}
                    color="green"
                />
                <StatCard
                    label="Readiness"
                    value={readiness + "/100"}
                    subtext="System ready 🚀"
                    icon={Zap}
                    color="red"
                />
            </div>

            {/* Burnout Risk Monitor */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 relative overflow-hidden">
                <div className="flex justify-between items-start relative z-10">
                    <div>
                        <div className="flex items-center gap-2 text-zinc-400 mb-2">
                            <Activity size={20} />
                            <h3 className="font-bold uppercase tracking-wider text-sm">Burnout Risk Monitor</h3>
                        </div>
                        <div className="mt-4">
                            <div className={`text-sm font-bold mb-1 ${riskScore > 70 ? 'text-red-500' : riskScore > 40 ? 'text-yellow-500' : 'text-green-500'}`}>
                                {riskLabel}
                            </div>
                            <div className="text-4xl font-bold text-white">
                                {riskScore}<span className="text-xl text-zinc-600">/100</span>
                            </div>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-zinc-500 text-xs font-bold uppercase mb-1">Primary Factor</div>
                        <div className="text-zinc-300 font-medium max-w-[150px] truncate" title={metrics?.burnout_primary_factor ?? "Insufficient data"}>
                            {metrics?.burnout_primary_factor ?? "Insufficient data"}
                        </div>
                    </div>
                </div>
            </div>

            {/* Today's Focus */}
            <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl flex items-start gap-4">
                <div className="p-3 bg-yellow-500/10 rounded-xl text-yellow-500 shrink-0">
                    <Lightbulb size={24} />
                </div>
                <div>
                    <h3 className="text-yellow-500 font-bold mb-1">Today's Focus</h3>
                    <p className="text-zinc-400 text-sm leading-relaxed">
                        Goal: <span className="font-bold text-white">{fullState?.user_profile?.goal || "Improve overall health"}</span>.
                        Remember, small consistent actions compound over time. Check your Decision tab to stay aligned!
                    </p>
                </div>
            </div>

            {/* Last Decision */}
            <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-2xl">
                <div className="flex items-center gap-2 mb-4 text-zinc-500">
                    <Clock size={16} />
                    <h3 className="font-bold text-sm uppercase tracking-wider">Last Decision</h3>
                </div>
                {lastDecision && new Date(lastDecision.timestamp).toDateString() === new Date().toDateString() ? (
                    <div className="bg-zinc-950/50 rounded-xl p-4 border border-zinc-800/50">
                        <div className="flex justify-between items-start mb-2">
                            <span className="text-white font-medium">{lastDecision.activity}</span>
                            <span className={`text-xs px-2 py-1 rounded-full ${lastDecision.action === 'PROCEED' ? 'bg-green-500/20 text-green-400' :
                                lastDecision.action === 'SKIP' ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'
                                }`}>
                                {lastDecision.action}
                            </span>
                        </div>
                        <p className="text-zinc-400 text-sm">
                            {(lastDecision.decisions?.[0]?.reasoning) || "Decision recorded."}
                        </p>
                        <div className="mt-2 text-xs text-zinc-600">
                            {new Date(lastDecision.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                    </div>
                ) : (
                    <div className="text-zinc-500 italic p-4 text-center bg-zinc-950/30 rounded-xl border border-dashed border-zinc-800">
                        Make your first decision to see the Health Council in action! 🚀
                    </div>
                )}
            </div>
        </div>
    );
};

// Simulation View (Hidden logic for inputs)
const SimulationView = ({ sleep, energy, stress, time, updateMetrics }: any) => {
    return (
        <div className="max-w-2xl mx-auto bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <Wand2 size={24} className="text-red-500" />
                System Simulation
            </h2>
            <p className="text-zinc-500 mb-8">
                Adjust these metrics to simulate different user states and test the system's response in real-time.
            </p>

            <div className="space-y-8">
                <div>
                    <label className="text-sm font-medium text-zinc-400 mb-2 block flex justify-between">
                        <span>Sleep Duration</span>
                        <span className="text-blue-400">{sleep} hr</span>
                    </label>
                    <input
                        type="range" min="3" max="10" step="0.5" value={sleep}
                        onChange={(e) => updateMetrics('sleep_hours', parseFloat(e.target.value))}
                        className="w-full accent-blue-500 h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer"
                    />
                </div>
                <div>
                    <label className="text-sm font-medium text-zinc-400 mb-2 block flex justify-between">
                        <span>Energy Level</span>
                        <span className="text-yellow-400">{energy}/10</span>
                    </label>
                    <input
                        type="range" min="1" max="10" value={energy}
                        onChange={(e) => updateMetrics('energy_level', parseInt(e.target.value))}
                        className="w-full accent-yellow-500 h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer"
                    />
                </div>
                <div>
                    <label className="text-sm font-medium text-zinc-400 mb-3 block">Stress Level</label>
                    <div className="grid grid-cols-3 gap-3">
                        {['Low', 'Medium', 'High'].map((lvl) => (
                            <button
                                key={lvl}
                                onClick={() => updateMetrics('stress_level', lvl)}
                                className={`py-2 text-sm font-medium rounded-lg transition-all border ${stress === lvl
                                    ? 'bg-zinc-800 text-white border-zinc-600 shadow-sm'
                                    : 'text-zinc-600 border-zinc-800 hover:border-zinc-700'
                                    }`}
                            >
                                {lvl}
                            </button>
                        ))}
                    </div>
                </div>
                <div>
                    <label className="text-sm font-medium text-zinc-400 mb-2 block flex justify-between">
                        <span>Available Time</span>
                        <span className="text-green-400">{time} hr</span>
                    </label>
                    <input
                        type="range" min="0.5" max="4.0" step="0.5" value={time}
                        onChange={(e) => updateMetrics('available_time', parseFloat(e.target.value))}
                        className="w-full accent-green-500 h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer"
                    />
                </div>
            </div>
        </div>
    );
};


export const Dashboard = () => {
    const [activeTab, setActiveTab] = useState('home');

    // Joint State
    const [age, setAge] = useState(25);
    const [goal, setGoal] = useState("Improve overall health");
    const [sleep, setSleep] = useState(7.0);
    const [energy, setEnergy] = useState(6);
    const [stress, setStress] = useState<'Low' | 'Medium' | 'High'>("Medium");
    const [time, setTime] = useState(2.0);
    const [fullState, setFullState] = useState<FullState | null>(null);

    const currentState: HealthState = {
        sleep_hours: sleep,
        energy_level: energy,
        stress_level: stress,
        available_time: time
    };

    const loadState = async () => {
        try {
            const state = await api.getState();
            setFullState(state);
            setAge(state.user_profile.age);
            setGoal(state.user_profile.goal);
            setSleep(state.current_state.sleep_hours);
            setEnergy(state.current_state.energy_level);
            setStress(state.current_state.stress_level);
            setTime(state.current_state.available_time);
        } catch (e) {
            console.error("Failed to load backend state", e);
        }
    };

    // Load initial state
    useEffect(() => {
        loadState();
    }, []);

    const updateMetrics = (field: string, value: any) => {
        const newState = { sleep_hours: sleep, energy_level: energy, stress_level: stress, available_time: time, [field]: value };

        if (field === 'sleep_hours') setSleep(value);
        if (field === 'energy_level') setEnergy(value);
        if (field === 'stress_level') setStress(value);
        if (field === 'available_time') setTime(value);

        api.updateMetrics(newState as HealthState).then((updatedState) => {
            // Update fullState with the new computed metrics so UI updates instantly
            if (fullState) {
                setFullState({
                    ...fullState,
                    current_state: updatedState
                });
            }
        }).catch(console.error);
    };

    const sharedProps = {
        age, goal, sleep, energy, stress, time,
        fullState,
        updateMetrics
    };

    return (
        <div className="min-h-screen bg-zinc-950 text-white font-sans flex">
            {/* Sidebar */}
            <aside className="w-64 border-r border-zinc-900 p-6 flex flex-col h-screen fixed top-0 left-0 bg-zinc-950 z-20">
                <div className="flex items-center gap-3 mb-10 pl-2">
                    <div className="w-8 h-8 flex items-center justify-center">
                        <img src="/diamond.png" alt="Equilibra Logo" className="w-full h-full object-contain" />
                    </div>
                    <div className="text-2xl font-bold tracking-tight">Equilibra</div>
                </div>

                <div className="space-y-2 flex-1">
                    <SidebarItem
                        icon={LayoutDashboard}
                        label="Home"
                        active={activeTab === 'home'}
                        onClick={() => setActiveTab('home')}
                    />
                    <SidebarItem
                        icon={Users}
                        label="Council"
                        active={activeTab === 'council'}
                        onClick={() => setActiveTab('council')}
                    />
                    <SidebarItem
                        icon={Wand2}
                        label="Make Decision"
                        active={activeTab === 'make-decision'}
                        onClick={() => setActiveTab('make-decision')}
                    />
                    <SidebarItem
                        icon={Activity}
                        label="Simulation"
                        active={activeTab === 'simulation'}
                        onClick={() => setActiveTab('simulation')}
                    />
                    <SidebarItem
                        icon={MessageSquare}
                        label="Chat"
                        active={activeTab === 'chat'}
                        onClick={() => setActiveTab('chat')}
                    />
                    <SidebarItem
                        icon={History}
                        label="History"
                        active={activeTab === 'history'}
                        onClick={() => setActiveTab('history')}
                    />
                </div>

                <div className="space-y-2 pt-8 border-t border-zinc-900">
                    <SidebarItem icon={Settings} label="Settings" />
                    <SidebarItem
                        icon={LogOut}
                        label="Log Out"
                        onClick={() => {
                            api.resetSession().then(() => {
                                setFullState(null);
                                window.location.href = '/';
                            });
                        }}
                    />
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 ml-64 p-8">
                <header className="flex justify-between items-center mb-10">
                    <div>
                        <h1 className="text-2xl font-bold text-white mb-1">
                            {activeTab === 'home' ? 'Dashboard' :
                                activeTab === 'council' ? 'Health Council' :
                                    activeTab === 'make-decision' ? 'Make Decision' :
                                        activeTab === 'simulation' ? 'System Simulation' :
                                            activeTab === 'chat' ? 'Assistant Chat' :
                                                activeTab === 'history' ? 'History' : 'Adaptation'}
                        </h1>
                        <p className="text-zinc-500 text-sm">Professional AI Health Balance System</p>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 px-4 py-2 bg-zinc-900 rounded-full border border-zinc-800">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                            <span className="text-sm font-medium text-zinc-300">System Active</span>
                        </div>
                    </div>
                </header>

                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                    >
                        {activeTab === 'home' && <HomeView fullState={fullState} />}
                        {activeTab === 'council' && <CouncilView lastDecision={fullState?.decision_history?.[fullState.decision_history.length - 1]} />}
                        {activeTab === 'make-decision' && <MakeDecisionView
                            currentState={currentState}
                            dailyTasks={fullState?.daily_tasks || []}
                            userProfile={fullState?.user_profile}
                            onDecisionComplete={loadState}
                        />}
                        {activeTab === 'simulation' && <SimulationView {...sharedProps} />}
                        {activeTab === 'chat' && <ChatView />}
                        {activeTab === 'history' && <div className="p-8 text-center text-zinc-500">History View Coming Soon</div>}
                        {activeTab === 'settings' && <div className="p-8 text-center text-zinc-500">Settings View</div>}
                    </motion.div>
                </AnimatePresence>
            </main>
        </div>
    );
};
