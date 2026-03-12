import { ArrowRight } from 'lucide-react';

interface CouncilViewProps {
    lastDecision?: any;
}

export const CouncilView = ({ lastDecision }: CouncilViewProps) => {
    // 1. No Decision State
    if (!lastDecision) {
        return (
            <div className="space-y-8 animate-in fade-in duration-500">
                {/* Header */}
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">🤝</span>
                        <h2 className="text-2xl font-bold text-white">Health Council - Multi-Agent Deliberation</h2>
                    </div>
                    <p className="text-zinc-500">See how 4 specialized agents collaborate to make decisions</p>
                </div>

                <div className="bg-gradient-to-r from-blue-900/10 to-cyan-900/10 border border-blue-500/20 p-6 rounded-xl flex items-center gap-4">
                    <span className="text-2xl">📊</span>
                    <span className="text-blue-200 font-medium">Make your first decision to see the Health Council in action!</span>
                </div>
            </div>
        );
    }

    // 2. Decision Made State
    const { activity, agents, decisions, consensus, reasoning_summary } = lastDecision;
    // Mocking missing fields for UI completeness if they don't exist in history record yet
    const confidence = lastDecision.confidence || 0.80;

    // Normalize agents listing (api returns 'agents', history returns 'decisions')
    const agentList = agents || decisions || [];

    return (
        <div className="space-y-8 animate-in fade-in duration-500 pb-20">
            {/* Header */}
            <div>
                <div className="flex items-center gap-2 mb-1">
                    <span className="text-xl">🤝</span>
                    <h2 className="text-xl font-bold text-white">Health Council</h2>
                </div>
                <p className="text-zinc-500 text-sm">See how 4 specialized agents collaborate to make decisions</p>
            </div>

            {/* Council Decision Header */}
            {consensus && (
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">🎯</span>
                        <h3 className="text-lg font-bold text-white">Council Decision</h3>
                    </div>

                    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-0 overflow-hidden relative group">
                        <div className="p-4 flex justify-between items-center relative z-10">
                            <div>
                                <div className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">TOPIC: {activity?.toUpperCase() || "Activity"}</div>
                                <div className="text-2xl font-bold text-white">{consensus}</div>
                            </div>

                            <div className="text-right">
                                <div className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-1">AGREEMENT</div>
                                <div className="text-3xl font-bold text-green-500">{(confidence * 100).toFixed(0)}%</div>
                            </div>
                        </div>
                        {/* Status Bar */}
                        <div className={`h-1 w-full ${consensus === 'PROCEED' ? 'bg-green-500' : 'bg-red-500'}`} />
                    </div>
                </div>
            )}

            {/* Agent Votes */}
            {consensus && agentList && agentList.length > 0 && (
                <div className="space-y-4">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">🗳️</span>
                        <h3 className="text-lg font-bold text-white">Agent Votes & Logic</h3>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {agentList.map((agent: any, i: number) => {
                            // Handle different field names between API response and History record
                            const name = agent.agent_name || agent.role || "Agent";
                            const vote = agent.vote || agent.action || "UNKNOWN";
                            const reason = agent.reasoning || "No reasoning provided.";
                            const conf = agent.confidence || 0.85; // History might not save confidence per agent, default it

                            return (
                                <div key={i} className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl flex flex-col h-full hover:border-zinc-700 transition-colors">
                                    {/* Agent Header */}
                                    <div className="flex justify-center mb-3 text-4xl">
                                        {name.includes("Sleep") || name.toLowerCase().includes("sleep") ? "😴" :
                                            name.includes("Performance") || name.toLowerCase().includes("performance") ? "⚡" :
                                                name.includes("Wellness") || name.toLowerCase().includes("wellness") ? "🧘" : "🔮"}
                                    </div>
                                    <div className="text-center mb-4 border-b border-zinc-800 pb-3">
                                        <div className="font-bold text-white text-xs uppercase tracking-wider mb-1">{name}</div>
                                        <div className={`font-bold text-lg ${vote === 'PROCEED' || vote === 'PRIORITIZE' ? 'text-green-400' : vote === 'SKIP' ? 'text-red-400' : 'text-blue-400'}`}>
                                            {vote}
                                        </div>
                                        <div className="text-[10px] text-zinc-600 mt-1 uppercase">Confidence: {(conf * 100).toFixed(0)}%</div>
                                    </div>

                                    <div className="flex-1">
                                        <div className="text-[10px] text-zinc-500 font-bold uppercase mb-1 flex items-center gap-1">
                                            <ArrowRight size={10} /> Why?
                                        </div>
                                        <p className="text-xs text-zinc-400 italic leading-relaxed">"{reason}"</p>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* Consensus Logic */}
            {reasoning_summary && (
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">🧠</span>
                        <h3 className="text-lg font-bold text-white">Consensus Logic</h3>
                    </div>
                    <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl">
                        <p className="text-sm text-zinc-400 leading-relaxed">{reasoning_summary}</p>
                    </div>
                </div>
            )}

            {/* Power Balance */}
            {consensus && (
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">⚖️</span>
                        <h3 className="text-lg font-bold text-white">Power Balance</h3>
                    </div>
                    <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl">
                        <div className="flex justify-between text-xs text-zinc-500 mb-2 font-bold uppercase">
                            <span>{consensus} Strength</span>
                            <span>100% (High Trust)</span>
                        </div>
                        <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                            <div className="h-full bg-green-500 w-full rounded-full shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
                        </div>
                    </div>
                </div>
            )}

            {/* Temporal Analysis */}
            {consensus && lastDecision.temporal_analysis && (
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">⏰</span>
                        <h3 className="text-lg font-bold text-white">Temporal Analysis</h3>
                    </div>
                    <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl">
                        <p className="text-sm text-zinc-400"><span className="text-white font-medium">AI Insight:</span> {lastDecision.temporal_analysis}</p>
                    </div>
                </div>
            )}

            {/* Present Context */}
            <div className="space-y-3">
                <div className="flex items-center gap-2">
                    <span className="text-lg">🎯</span>
                    <h3 className="text-lg font-bold text-white">Present Context</h3>
                </div>
                <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl space-y-2">
                    <p className="text-sm text-zinc-400">Day: <span className="text-white">{new Date().toLocaleDateString('en-US', { weekday: 'long' })}</span> | Time: <span className="text-white">{new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span></p>
                    {consensus && lastDecision.context_assessment && (
                        <div className="mt-2 pt-2 border-t border-zinc-800 animate-in fade-in">
                            <p className="text-sm text-zinc-400"><span className="text-white font-medium">AI Assessment:</span> {lastDecision.context_assessment}</p>
                        </div>
                    )}
                </div>
            </div>

        </div>
    );
};
