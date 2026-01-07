import { useState, useEffect } from 'react';
import { LayoutDashboard, Users, MessageSquare, History, Wand2, Settings, LogOut, Flame, Target, Zap, Lightbulb, Clock, Activity, Calendar } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from './api';
import type { HealthState, FullState } from './api';

import { CouncilView } from './views/CouncilView';
import { MakeDecisionView } from './views/MakeDecisionView';
import { ChatView } from './views/ChatView';
import { SimulationView } from './views/SimulationView';

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

interface HomeViewProps {
    fullState: FullState | null;
    streak?: string;
    adherence?: string;
}

const HomeView = ({ fullState, streak = "1 days", adherence = "100%" }: HomeViewProps) => {
    // Derived values
    const metrics = fullState?.current_state.computed_metrics;

    // Fallback safe defaults if metrics aren't computed yet
    const riskScore = metrics?.burnout_risk_score ?? 10;
    const riskLabel = metrics?.burnout_risk_label?.toUpperCase() ?? "LOW RISK";
    const readiness = metrics?.readiness_score ?? 71;

    // Use passed props, defaulting if undefined

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
                    <div className="text-center py-6 text-zinc-500 text-sm">
                        No decisions recorded today.
                    </div>
                )}
            </div>
        </div>
    );
};


export const Dashboard = () => {
    const [activeTab, setActiveTab] = useState('home');

    // Joint State
    const [fullState, setFullState] = useState<FullState | null>(null);
    const [currentStreak, setCurrentStreak] = useState("1 days");
    const [currentAdherence, setCurrentAdherence] = useState("100%");

    const loadState = async () => {
        try {
            const state = await api.getState();
            setFullState(state);
        } catch (error) {
            console.error(error);
        }
    };

    // Load initial state
    useEffect(() => {
        loadState();
    }, []);

    const updateMetrics = async (key: string, value: any) => {
        if (!fullState) return;
        const newState = { ...fullState.current_state, [key]: value };
        try {
            await api.updateMetrics(newState);
            loadState(); // Refresh full state to get calculated metrics
        } catch (e) {
            console.error(e);
        }
    };

    const currentState = fullState?.current_state;

    return (
        <div className="flex min-h-screen bg-black text-white font-sans selection:bg-red-500/30">
            {/* Sidebar */}
            <aside className="w-72 border-r border-zinc-800 p-6 flex flex-col fixed h-full bg-black z-50">
                <div className="flex items-center gap-3 mb-10 pl-2">
                    <div className="w-10 h-10 flex items-center justify-center">
                        <img src="/diamond.png" alt="Equilibra Logo" className="w-full h-full object-contain" />
                    </div>
                    <span className="text-2xl font-bold tracking-tight">Equilibria</span>
                </div>

                <nav className="space-y-2 flex-1">
                    <SidebarItem icon={LayoutDashboard} label="Dashboard" active={activeTab === 'home'} onClick={() => setActiveTab('home')} />
                    <SidebarItem icon={Users} label="Health Council" active={activeTab === 'council'} onClick={() => setActiveTab('council')} />
                    <SidebarItem icon={Wand2} label="Make Decision" active={activeTab === 'make-decision'} onClick={() => setActiveTab('make-decision')} />
                    <SidebarItem icon={Calendar} label="Simulation" active={activeTab === 'simulation'} onClick={() => setActiveTab('simulation')} />
                    <SidebarItem icon={MessageSquare} label="Assistant" active={activeTab === 'chat'} onClick={() => setActiveTab('chat')} />
                    <SidebarItem icon={History} label="History" active={activeTab === 'history'} onClick={() => setActiveTab('history')} />
                    <SidebarItem icon={Settings} label="Settings" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
                </nav>

                <div className="mt-auto pt-6 border-t border-zinc-800 space-y-2">
                    <div className="flex items-center gap-3 px-4 py-3 text-zinc-500 hover:text-zinc-300 cursor-pointer transition-colors"
                        onClick={async () => {
                            await api.resetSession();
                            window.location.reload();
                        }}
                    >
                        <Wand2 size={20} className="rotate-180" />
                        <span className="font-medium">Reset Session</span>
                    </div>
                    <div className="flex items-center gap-3 px-4 py-3 text-zinc-500 hover:text-red-400 cursor-pointer transition-colors"
                        onClick={() => {
                            window.location.href = '/';
                        }}
                    >
                        <LogOut size={20} />
                        <span className="font-medium">Log Out</span>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 ml-72 p-8 md:p-12 max-w-7xl mx-auto w-full">
                <header className="flex justify-between items-center mb-12">
                    <div>
                        <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
                            {activeTab === 'home' ? 'Dashboard' :
                                activeTab === 'council' ? 'Health Council' :
                                    activeTab === 'make-decision' ? 'Make Decision' :
                                        activeTab === 'simulation' ? 'System Simulation' :
                                            activeTab === 'chat' ? 'Assistant Chat' :
                                                activeTab === 'history' ? 'History' : 'Adaptation'}
                        </h1>
                        <p className="text-zinc-400 text-sm">Professional AI Health Balance System</p>
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
                        {activeTab === 'home' && <HomeView fullState={fullState} streak={currentStreak} adherence={currentAdherence} />}
                        {activeTab === 'council' && <CouncilView lastDecision={fullState?.decision_history?.[fullState.decision_history.length - 1]} />}
                        {activeTab === 'make-decision' && <MakeDecisionView
                            currentState={currentState}
                            dailyTasks={fullState?.daily_tasks || []}
                            userProfile={fullState?.user_profile}
                            onDecisionComplete={loadState}
                        />}
                        {activeTab === 'simulation' && <SimulationView onSimulationComplete={(finalState) => {
                            if (finalState) {
                                // Update real metrics
                                // But primarily update the Mocked Stats for display
                                setCurrentStreak("7 days");
                                setCurrentAdherence("98%");

                                api.updateMetrics(finalState).then(() => {
                                    loadState();
                                });
                            }
                        }} />}
                        {activeTab === 'chat' && <ChatView />}
                        {activeTab === 'history' && <div className="p-8 text-center text-zinc-500">History View Coming Soon</div>}
                        {activeTab === 'settings' && <div className="p-8 text-center text-zinc-500">Settings View</div>}
                    </motion.div>
                </AnimatePresence>
            </main>
        </div>
    );
};
