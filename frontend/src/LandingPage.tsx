import { motion } from 'framer-motion';
import {
  Brain,
  ShieldAlert,
  Activity,
  Clock,
  MessageSquare,
  Target,
  Play
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black text-white selection:bg-red-500/30 font-sans overflow-x-hidden">
      {/* Background Glow Effects - Purple/Blue/Orange Gradient */}
      <div className="fixed top-1/3 left-0 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-[150px] pointer-events-none" />
      <div className="fixed top-1/2 left-1/4 w-[500px] h-[500px] bg-blue-600/15 rounded-full blur-[120px] pointer-events-none" />
      <div className="fixed top-1/3 right-0 w-[600px] h-[600px] bg-orange-600/20 rounded-full blur-[150px] pointer-events-none" />
      <div className="fixed bottom-1/4 right-1/4 w-[500px] h-[500px] bg-red-600/15 rounded-full blur-[120px] pointer-events-none" />

      {/* Navigation */}
      <nav className="relative w-full z-50 top-0 bg-transparent">
        <div className="max-w-7xl mx-auto px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/diamond.png" alt="Equilibra" className="w-8 h-8" />
            <span className="font-bold text-xl tracking-tight">Equilibra</span>
          </div>
          <div className="flex gap-10 text-sm font-medium text-zinc-400">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#demo" className="hover:text-white transition-colors">How it Works</a>
            <a href="#team" className="hover:text-white transition-colors">Team</a>
            <a href="#contact" className="hover:text-white transition-colors">Contact</a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-24 pb-16 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-6xl md:text-7xl font-bold tracking-tight mb-6 leading-[1.1]"
          >
            Prevent Burnout with <br />
            AI <span className="relative inline-block">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500">
                Health Balance
              </span>
              <svg
                className="absolute -bottom-2 left-0 w-full"
                viewBox="0 0 400 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M 10 15 Q 200 5, 390 15"
                  stroke="url(#gradient)"
                  strokeWidth="3"
                  fill="none"
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#ef4444" />
                    <stop offset="100%" stopColor="#f97316" />
                  </linearGradient>
                </defs>
              </svg>
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg text-zinc-400 max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            A multi-agent system that predicts crises and optimizes your wellness before problems occur.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <button
              onClick={() => navigate('/onboarding')}
              className="px-10 py-4 bg-gradient-to-r from-red-500 to-orange-500 rounded-full font-semibold text-lg flex items-center justify-center gap-3 mx-auto hover:shadow-[0_0_40px_rgba(239,68,68,0.5)] transition-all"
            >
              <Play className="w-5 h-5 fill-current" /> View Live Demo
            </button>
          </motion.div>
        </div>
      </section>


      {/* Features Grid */}
      <section id="features" className="px-6 py-24 bg-zinc-900/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">Not Just a Tracker. <br />An <span className="text-red-400">Intervention System.</span></h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">Equilibra uses AI to reason about your health data and prevent burnout before it happens.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <FeatureCard
              icon={MessageSquare}
              title="Multi-Agent Council"
              desc="4 specialized AI agents collaborate via LLM to deliberate and make health decisions."
            />
            <FeatureCard
              icon={ShieldAlert}
              title="Burnout Circuit Breaker"
              desc="Automatically blocks high-intensity activities when safety thresholds are exceeded."
            />
            <FeatureCard
              icon={Target}
              title="Goal Negotiator"
              desc="AI evaluates your goals and counters with safer, realistic plans when needed."
            />
            <FeatureCard
              icon={Clock}
              title="Temporal Reasoning"
              desc="Analyzes past patterns, present context, and future trajectories to predict crises."
            />
            <FeatureCard
              icon={Activity}
              title="Crisis Prediction"
              desc="Forecasts burnout probability days in advance, allowing course-correction."
            />
            <FeatureCard
              icon={Brain}
              title="Dynamic Tasks"
              desc="LLMs generate personalized daily tasks based on real-time energy levels."
            />
          </div>
        </div>
      </section>

      {/* Team & Footer */}
      <footer id="team" className="px-6 py-20 border-t border-white/5 bg-black">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start gap-12">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <img src="/diamond.png" alt="Equilibra" className="w-7 h-7" />
              <span className="font-bold text-lg">Equilibra</span>
            </div>
            <p className="text-zinc-500 text-sm max-w-xs mb-6">
              Built with React, FastAPI, and AI.<br />
              Preventing burnout through intelligent intervention.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-12">
            <div>
              <h4 className="font-bold mb-4 text-white">Links</h4>
              <ul className="space-y-2 text-zinc-400 text-sm">
                <li><a href="#features" className="hover:text-red-400 transition-colors">Features</a></li>
                <li><a href="#demo" className="hover:text-red-400 transition-colors">Demo</a></li>
                <li><a href="#contact" className="hover:text-red-400 transition-colors">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4 text-white">Legal</h4>
              <ul className="space-y-2 text-zinc-400 text-sm">
                <li><a href="#" className="hover:text-red-400 transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-red-400 transition-colors">Terms of Service</a></li>
                <li><a href="#contact" className="hover:text-red-400 transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="mt-16 pt-8 border-t border-white/5 text-center text-zinc-600 text-xs">
          © {new Date().getFullYear()} Equilibra. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

// Sub-components for cleaner code

const FeatureCard = ({ icon: Icon, title, desc }: { icon: any, title: string, desc: string }) => (
  <div className="group p-6 rounded-2xl bg-white/5 border border-white/5 hover:border-red-500/30 hover:bg-white/10 transition-all duration-300">
    <div className="w-12 h-12 rounded-lg bg-red-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
      <Icon className="w-6 h-6 text-red-400" />
    </div>
    <h3 className="text-xl font-bold mb-2 text-white group-hover:text-red-400 transition-colors">{title}</h3>
    <p className="text-zinc-400 text-sm leading-relaxed">{desc}</p>
  </div>
);



export default LandingPage;
