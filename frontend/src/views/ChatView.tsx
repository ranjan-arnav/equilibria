import React, { useState } from 'react';
import { Send, User, Bot, Loader } from 'lucide-react';
import { api } from '../api';

export const ChatView = () => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am your Health Balance assistant. How are you feeling today?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input;
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setInput('');
        setLoading(true);

        try {
            const response = await api.chat(userMessage);
            setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', content: "I'm having trouble connecting right now. Please try again later." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-140px)]">
            <div className="flex-1 overflow-y-auto space-y-4 pr-4 custom-scrollbar mb-4">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-zinc-800' : 'bg-red-500/10 text-red-500'}`}>
                            {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                        </div>
                        <div className={`p-4 rounded-2xl max-w-[80%] ${msg.role === 'user' ? 'bg-white text-black' : 'bg-zinc-900 border border-zinc-800 text-zinc-300'}`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-4">
                        <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 bg-red-500/10 text-red-500">
                            <Bot size={20} />
                        </div>
                        <div className="p-4 rounded-2xl bg-zinc-900 border border-zinc-800 text-zinc-300 flex items-center">
                            <Loader size={16} className="animate-spin mr-2" /> Thinking...
                        </div>
                    </div>
                )}
            </div>

            <div className="relative">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Type your health update..."
                    disabled={loading}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl pl-4 pr-12 py-4 focus:outline-none focus:border-zinc-700 transition-colors disabled:opacity-50"
                />
                <button
                    onClick={handleSend}
                    disabled={loading}
                    className="absolute right-2 top-2 p-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors text-white disabled:opacity-50"
                >
                    <Send size={20} />
                </button>
            </div>
        </div>
    );
};
