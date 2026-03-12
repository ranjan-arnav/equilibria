import React, { useState } from 'react';
import { Calendar, Play, Lightbulb, Flame, Activity, Zap, Star, TrendingUp, Lock, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../api';
import type { SimulationResponse } from '../api';

const SCENARIOS = [
    { id: 'burnout_recovery', label: '🔥 Burnout → Recovery', desc: 'Rehabilitate from high stress state' },
    { id: 'preventive', label: '📉 Gradual Burnout', desc: 'Preventive intervention demonstration' },
    { id: 'irregular', label: '🏃 Weekend Warrior', desc: 'Optimization for irregular schedules' },
    { id: 'peak', label: '⭐ High Performer', desc: 'Peak performance maintenance' }
];

interface SimulationViewProps {
    onSimulationComplete?: (finalState: any) => void;
}

export const SimulationView = ({ onSimulationComplete }: SimulationViewProps) => {
    const [selectedScenario, setSelectedScenario] = useState(SCENARIOS[0].id);
    const [timeAvailable, setTimeAvailable] = useState(2.0);
    const [isSimulating, setIsSimulating] = useState(false);
    const [simulationData, setSimulationData] = useState<SimulationResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleRunSimulation = async () => {
        setIsSimulating(true);
        setSimulationData(null);
        setError(null);

        try {
            const data = await api.runSimulation(selectedScenario, timeAvailable);
            setSimulationData(data);
            if (onSimulationComplete) {
                // Update global state with final simulation state to reflect in Home tab
                onSimulationComplete(data.final_state);
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsSimulating(false);
        }
    };

    return (
        <div className="p-6 max-w-5xl mx-auto space-y-8 pb-20">
            {/* Header */}
            <div>
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-blue-500/10 rounded-lg">
                        <Calendar className="w-6 h-6 text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold text-white">7-Day Simulation</h1>
                </div>
                <p className="text-zinc-400">Watch the agent make autonomous decisions over a full week</p>
            </div>

            {/* Error / Prerequisite Banner */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 flex items-center gap-3 text-red-200">
                    <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" />
                    <p>{error}</p>
                </div>
            )}

            {/* Info Banner - Only show if no error or results yet */}
            {!error && !simulationData && (
                <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-4 flex items-center gap-3">
                    <Lightbulb className="w-5 h-5 text-yellow-400 shrink-0" />
                    <p className="text-blue-200 text-sm">
                        Select a recovery profile and run the analysis to see the agent adapt. requires at least 3 prior decisions.
                    </p>
                </div>
            )}

            {/* Controls Section */}
            <div className="grid md:grid-cols-3 gap-8">
                {/* Left Column: Inputs */}
                <div className="md:col-span-2 space-y-6">
                    {/* Scenario Dropdown */}
                    <div className="space-y-3">
                        <label className="text-sm font-medium text-zinc-300">Scenario</label>
                        <div className="relative">
                            <select
                                value={selectedScenario}
                                onChange={(e) => { setSelectedScenario(e.target.value); setSimulationData(null); setError(null); }}
                                className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 text-white appearance-none focus:border-blue-500 outline-none transition-colors"
                            >
                                {SCENARIOS.map(s => (
                                    <option key={s.id} value={s.id}>{s.label}</option>
                                ))}
                            </select>
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-zinc-500">
                                ▼
                            </div>
                        </div>
                    </div>

                    {/* Time Slider */}
                    <div className="space-y-4">
                        <div className="flex justify-between">
                            <label className="text-sm font-medium text-zinc-300">Daily Time (hours)</label>
                            <span className="text-sm font-mono text-blue-400">{timeAvailable.toFixed(2)}</span>
                        </div>
                        <input
                            type="range"
                            min="0.5"
                            max="8"
                            step="0.5"
                            value={timeAvailable}
                            onChange={(e) => { setTimeAvailable(parseFloat(e.target.value)); setSimulationData(null); setError(null); }}
                            className="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
                        />
                    </div>

                    {/* Run Button */}
                    <button
                        onClick={handleRunSimulation}
                        disabled={isSimulating}
                        className="w-full py-4 bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white font-bold rounded-xl transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSimulating ? (
                            <>
                                <Activity className="w-5 h-5 animate-spin" /> Running Analysis (Real-time)...
                            </>
                        ) : (
                            <>
                                <Play className="w-5 h-5 fill-current" /> Run 7-Day Simulation
                            </>
                        )}
                    </button>
                </div>

                {/* Right Column: Profiles Legend */}
                <div className="space-y-4">
                    <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">Available Profiles:</h3>
                    <div className="space-y-4 text-sm">
                        <div className="flex items-start gap-2">
                            <Flame className="w-4 h-4 text-orange-500 shrink-0 mt-0.5" />
                            <p className="text-zinc-300">
                                <span className="font-bold text-white">Burnout → Recovery:</span> Rehabilitate from high stress state
                            </p>
                        </div>
                        <div className="flex items-start gap-2">
                            <TrendingUp className="w-4 h-4 text-pink-400 shrink-0 mt-0.5" />
                            <p className="text-zinc-300">
                                <span className="font-bold text-white">Gradual Burnout:</span> Preventive intervention demonstration
                            </p>
                        </div>
                        <div className="flex items-start gap-2">
                            <Zap className="w-4 h-4 text-yellow-500 shrink-0 mt-0.5" />
                            <p className="text-zinc-300">
                                <span className="font-bold text-white">Weekend Warrior:</span> Optimization for irregular schedules
                            </p>
                        </div>
                        <div className="flex items-start gap-2">
                            <Star className="w-4 h-4 text-yellow-400 shrink-0 mt-0.5" />
                            <p className="text-zinc-300">
                                <span className="font-bold text-white">High Performer:</span> Peak performance maintenance
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Results Section */}
            {simulationData && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-6"
                >
                    <div className="flex items-center gap-2 mb-4">
                        <div className="p-2 bg-gradient-to-br from-pink-500/20 to-purple-500/20 rounded-lg">
                            <TrendingUp className="w-6 h-6 text-pink-400" />
                        </div>
                        <h2 className="text-xl font-bold text-white">Predicted Trends</h2>
                    </div>

                    {/* Chart Container */}
                    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 md:p-8">
                        {/* Legend */}
                        <div className="flex justify-end gap-6 mb-8 text-xs font-medium">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-red-900/50 border border-red-500/30 rounded-sm"></div>
                                <span className="text-zinc-300">Stress Load</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-1 bg-blue-500 rounded-full"></div>
                                <span className="text-zinc-300">Energy</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-1 bg-green-500 rounded-full"></div>
                                <span className="text-zinc-300">Readiness</span>
                            </div>
                        </div>

                        {/* Chart Area */}
                        <div className="relative h-64 w-full">
                            {/* Y-Axis Grid */}
                            <div className="absolute inset-0 flex flex-col justify-between text-xs text-zinc-600 pointer-events-none">
                                {[100, 80, 60, 40, 20, 0].map((tick) => (
                                    <div key={tick} className="flex items-center w-full">
                                        <span className="w-6 text-right mr-2">{tick}</span>
                                        <div className="flex-1 h-px bg-zinc-800/50 border-t border-dashed border-zinc-800"></div>
                                    </div>
                                ))}
                            </div>

                            {/* Data Visualization */}
                            <div className="absolute inset-0 left-8 right-0 top-0 bottom-6 flex items-end justify-between px-2 md:px-6 pt-3">
                                {simulationData.projections.map((dayData: any, i: number) => {
                                    return (
                                        <div key={dayData.day} className="relative flex-1 flex flex-col justify-end items-center h-full group">
                                            {/* Bar (Stress) */}
                                            <motion.div
                                                initial={{ height: 0 }}
                                                animate={{ height: `${dayData.stress_load}%` }}
                                                transition={{ duration: 0.5, delay: i * 0.1 }}
                                                className="w-full max-w-[40px] bg-red-900/30 hover:bg-red-900/50 border-t border-red-500/20 rounded-t-sm transition-colors"
                                            />

                                            {/* X-Axis Label */}
                                            <span className="absolute -bottom-8 text-xs text-zinc-500 font-medium">{dayData.day}</span>

                                            {/* Points for Lines (Using real data) */}
                                            <motion.div
                                                initial={{ opacity: 0, scale: 0 }}
                                                animate={{ opacity: 1, scale: 1, bottom: `${dayData.energy_level}%` }}
                                                transition={{ delay: 0.5 + i * 0.1 }}
                                                className="absolute w-2 h-2 bg-blue-500 rounded-full border-2 border-zinc-900 z-10"
                                            />
                                            <motion.div
                                                initial={{ opacity: 0, scale: 0 }}
                                                animate={{ opacity: 1, scale: 1, bottom: `${dayData.readiness_score}%` }}
                                                transition={{ delay: 0.5 + i * 0.1 }}
                                                className="absolute w-2 h-2 bg-green-500 rounded-full border-2 border-zinc-900 z-10"
                                            />
                                        </div>
                                    );
                                })}

                                {/* SVG Lines Overlay */}
                                <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ overflow: 'visible' }}>
                                    {/* Energy Line */}
                                    <motion.path
                                        initial={{ pathLength: 0 }}
                                        animate={{ pathLength: 1 }}
                                        transition={{ duration: 1.5, delay: 0.5 }}
                                        d={`M ${simulationData.projections.map((p: any, i: number) => `${6 + i * 14.6}% ${100 - p.energy_level}%`).join(' L ')}`}
                                        fill="none"
                                        stroke="#3b82f6"
                                        strokeWidth="2"
                                        className="opacity-80"
                                    />
                                    {/* Readiness Line */}
                                    <motion.path
                                        initial={{ pathLength: 0 }}
                                        animate={{ pathLength: 1 }}
                                        transition={{ duration: 1.5, delay: 0.5 }}
                                        d={`M ${simulationData.projections.map((p: any, i: number) => `${6 + i * 14.6}% ${100 - p.readiness_score}%`).join(' L ')}`}
                                        fill="none"
                                        stroke="#22c55e"
                                        strokeWidth="2"
                                        className="opacity-80"
                                    />
                                </svg>
                            </div>
                        </div>
                    </div>

                    {/* Insights Box */}
                    <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6">
                        <h3 className="flex items-center gap-2 text-white font-bold mb-4">
                            <Lightbulb className="w-5 h-5 text-yellow-500" />
                            Forecast Insights
                        </h3>
                        <ul className="space-y-2 text-sm text-zinc-400 pl-2">
                            {simulationData.insights.map((insight, idx) => (
                                <li key={idx} className="flex items-center gap-2">
                                    <div className="w-1.5 h-1.5 bg-zinc-600 rounded-full"></div>
                                    <span>{insight}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </motion.div>
            )}
        </div>
    );
};
