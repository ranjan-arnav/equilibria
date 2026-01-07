const API_URL = 'http://localhost:8000/api';

// --- Types ---

export interface ComputedMetrics {
    readiness_score: number;
    sleep_score: number;
    burnout_risk_score: number;
    burnout_risk_label: string;
    burnout_primary_factor: string;
}

export interface HealthState {
    sleep_hours: number;
    energy_level: number;
    stress_level: 'Low' | 'Medium' | 'High';
    available_time: number;
    computed_metrics?: ComputedMetrics;
}

export interface DailyProjection {
    day: string;
    stress_load: number;
    energy_level: number;
    readiness_score: number;
    metrics: ComputedMetrics;
}

export interface SimulationResponse {
    projections: DailyProjection[];
    final_state: HealthState;
    insights: string[];
}

export interface GoalNegotiationResponse {
    status: 'ACCEPTED' | 'NEGOTIATE' | 'REJECTED';
    reasoning: string;
    counter_proposal?: string;
    risk_score: number;
}

export interface CouncilAgentVote {
    agent_name: string;
    vote: 'PROCEED' | 'MODIFY' | 'SKIP';
    confidence: number;
    reasoning: string;
}

export interface CouncilDeliberationResponse {
    consensus: 'PROCEED' | 'MODIFY' | 'SKIP';
    confidence: number;
    agents: CouncilAgentVote[];
    reasoning_summary: string;
}


export interface UserProfile {
    user_id: string;
    name: string;
    age: number;
    goal: string;
}

export interface ChatMessage {
    role: string;
    content: string;
    timestamp: string;
}

export interface FullState {
    user_profile: UserProfile;
    current_state: HealthState;
    decision_history: any[]; // Using any[] for simplicity as decision structure is complex
    chat_history: ChatMessage[];
    daily_tasks?: any[];
}

export interface BurnoutPredictionResponse {
    risk_level: string;
    reasoning: string;
}

// --- API Functions ---

export const api = {
    negotiateGoal: async (goal: string, currentState?: HealthState): Promise<GoalNegotiationResponse> => {
        const response = await fetch(`${API_URL}/negotiator`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal, current_state: currentState })
        });
        if (!response.ok) throw new Error('Failed to negotiate goal');
        return response.json();
    },

    deliberate: async (activity: string, state: HealthState, userGoal: string): Promise<CouncilDeliberationResponse> => {
        // decisionHistory is now handled by backend
        const response = await fetch(`${API_URL}/council/deliberate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                activity,
                state,
                user_goal: userGoal,
                decision_history: []
            })
        });
        if (!response.ok) throw new Error('Failed to deliberate');
        return response.json();
    },

    predictBurnout: async (state: HealthState): Promise<BurnoutPredictionResponse> => {
        const response = await fetch(`${API_URL}/burnout/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state)
        });
        if (!response.ok) throw new Error('Failed to predict burnout');
        return response.json();
    },

    runSimulation: async (scenarioId: string, dailyTime: number): Promise<SimulationResponse> => {
        const response = await fetch(`${API_URL}/simulation/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_id: scenarioId, daily_time: dailyTime })
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Simulation failed');
        }
        return response.json();
    },

    // --- State Management ---

    getState: async (): Promise<FullState> => {
        const response = await fetch(`${API_URL}/state`);
        if (!response.ok) throw new Error('Failed to fetch state');
        return response.json();
    },

    updateMetrics: async (state: HealthState) => {
        const response = await fetch(`${API_URL}/state/update_metrics`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state)
        });
        if (!response.ok) throw new Error('Failed to update metrics');
        return response.json();
    },

    updateProfile: async (profile: UserProfile): Promise<UserProfile> => {
        const response = await fetch(`${API_URL}/state/update_profile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profile)
        });
        if (!response.ok) throw new Error('Failed to update profile');
        return response.json();
    },

    chat: async (message: string, context?: HealthState): Promise<{ response: string }> => {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, context }),
        });
        return response.json();
    },


    makeDecision: async (
        activity: string,
        domain: string,
        duration: number,
        state: HealthState
    ): Promise<{
        action: string,
        adjustment?: string,
        reasoning: string,
        constraints: string[]
    }> => {
        const response = await fetch(`${API_URL}/decision`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ activity, domain, duration, state }),
        });
        return response.json();
    },

    generateTasks: async (
        state: HealthState,
        userProfile: UserProfile,
        goal: string
    ): Promise<{ tasks: Array<{ title: string, duration: number, domain: string, reason: string, is_blocked?: boolean, block_reason?: string }> }> => {
        const response = await fetch(`${API_URL}/planning/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state, user_profile: userProfile, goal }),
        });
        if (!response.ok) throw new Error('Failed to generate tasks');
        return response.json();
    },

    updateTasks: async (tasks: any[]): Promise<any[]> => {
        const response = await fetch(`${API_URL}/state/update_tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tasks),
        });
        if (!response.ok) throw new Error('Failed to update tasks');
        return response.json();
    },

    analyzeTask: async (taskTitle: string, state: HealthState): Promise<{ domain: string, is_safe: boolean, reason: string }> => {
        const response = await fetch(`${API_URL}/planning/analyze_task`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_title: taskTitle, state }),
        });
        if (!response.ok) throw new Error('Failed to analyze task');
        return response.json();
    },

    resetSession: async () => {
        await fetch(`${API_URL}/state/reset_session`, {
            method: 'POST'
        });
    }
};
