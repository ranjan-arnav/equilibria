import { motion } from 'framer-motion';
import {
  Brain,
  ShieldAlert,
  Activity,
  Clock,
  MessageSquare,
  Target,
  Users,
  Zap,
  Mail,
  MapPin,
  Phone,
  Github,
  Linkedin,
  ArrowRight,
  Shield,
  TrendingUp
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
            <a href="#how-it-works" className="hover:text-white transition-colors">How it Works</a>
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
            <motion.button
              onClick={() => navigate('/login')}
              className="group relative px-10 py-4 bg-gradient-to-r from-red-500 to-orange-500 rounded-full font-semibold text-lg flex items-center justify-center gap-3 mx-auto overflow-hidden"
              whileHover={{
                scale: 1.05,
                boxShadow: "0 0 50px rgba(239,68,68,0.6), 0 0 100px rgba(249,115,22,0.3)"
              }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
            >
              {/* Shimmer effect */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full"
                animate={{ translateX: ["100%", "-100%"] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 3, ease: "easeInOut" }}
              />
              <span className="relative z-10">Login</span>
              <motion.span
                className="relative z-10"
                initial={{ x: 0 }}
                whileHover={{ x: 5 }}
                transition={{ type: "spring", stiffness: 400 }}
              >
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </motion.span>
            </motion.button>
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

      {/* How It Works Section */}
      <section id="how-it-works" className="px-6 py-24 relative">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              How <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500">Equilibra</span> Works
            </h2>
            <p className="text-zinc-400 max-w-2xl mx-auto text-lg">
              A 4-step intelligent process that transforms your wellness data into personalized interventions
            </p>
          </motion.div>

          {/* Workflow Steps */}
          <div className="grid lg:grid-cols-4 gap-8 relative">

            <WorkflowStep
              step={1}
              icon={Users}
              title="Log Your State"
              description="Enter your sleep hours, energy level, stress, and daily goal. The system captures your current wellness context."
              delay={0.1}
              color="red"
            />
            <WorkflowStep
              step={2}
              icon={Brain}
              title="Multi-Agent Analysis"
              description="Four AI agents—Sleep Specialist, Performance Coach, Wellness Guardian, and Future Self—independently analyze your data."
              delay={0.2}
              color="orange"
            />
            <WorkflowStep
              step={3}
              icon={Shield}
              title="Risk Evaluation"
              description="The system runs burnout prediction, evaluates goal safety, and applies circuit breaker logic to prevent overexertion."
              delay={0.3}
              color="yellow"
            />
            <WorkflowStep
              step={4}
              icon={TrendingUp}
              title="Get Your Plan"
              description="Receive a personalized daily plan with tasks, recommendations, and activity adjustments based on agent consensus."
              delay={0.4}
              color="green"
            />
          </div>

          {/* Key Differentiators */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            viewport={{ once: true }}
            className="mt-20 p-8 rounded-3xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10"
          >
            <div className="grid md:grid-cols-3 gap-8">
              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center flex-shrink-0">
                  <Zap className="w-6 h-6 text-red-400" />
                </div>
                <div>
                  <h4 className="font-bold text-white mb-1">Proactive, Not Reactive</h4>
                  <p className="text-zinc-400 text-sm">Predicts burnout 3-7 days before it happens</p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-orange-500/20 flex items-center justify-center flex-shrink-0">
                  <MessageSquare className="w-6 h-6 text-orange-400" />
                </div>
                <div>
                  <h4 className="font-bold text-white mb-1">Multi-Agent Consensus</h4>
                  <p className="text-zinc-400 text-sm">Decisions backed by 4 AI perspectives</p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                  <ShieldAlert className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <h4 className="font-bold text-white mb-1">Built-in Safety</h4>
                  <p className="text-zinc-400 text-sm">Automatic circuit breaker prevents overexertion</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Team Section */}
      <section id="team" className="px-6 py-24 bg-zinc-900/30">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <span className="px-4 py-1.5 rounded-full bg-gradient-to-r from-purple-500/20 to-blue-500/20 text-purple-400 text-sm font-medium border border-purple-500/30 inline-block mb-6">
              <Users className="w-4 h-4 inline mr-2" />
              Meet the Team
            </span>
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              Built by <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">Innovators</span>
            </h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              A passionate team from Manipal Institute of Technology, Manipal
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <TeamCard
              name="Arnav Ranjan"
              role="Team Lead"
              github="https://github.com/ranjan-arnav/"
              linkedin="https://www.linkedin.com/in/arnavranjan/"
              delay={0.1}
            />
            <TeamCard
              name="Om Raj"
              role="Developer"
              github="https://github.com/OmRajOnWeb"
              linkedin="https://www.linkedin.com/in/omrajonweb"
              delay={0.2}
            />
            <TeamCard
              name="Kushal Raj"
              role="Developer"
              github="https://github.com/rkushell"
              linkedin="https://www.linkedin.com/in/raj-kushal"
              delay={0.3}
            />
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="px-6 py-24 relative">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <span className="px-4 py-1.5 rounded-full bg-gradient-to-r from-green-500/20 to-emerald-500/20 text-emerald-400 text-sm font-medium border border-emerald-500/30 inline-block mb-6">
              <Mail className="w-4 h-4 inline mr-2" />
              Get in Touch
            </span>
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              Contact <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400">Us</span>
            </h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              Have questions or want to learn more? We'd love to hear from you.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 gap-12 max-w-5xl mx-auto">
            {/* Contact Form */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="p-8 rounded-3xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10"
            >
              <h3 className="text-xl font-bold mb-6">Send us a message</h3>
              <form className="space-y-5">
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Your Name</label>
                  <input
                    type="text"
                    placeholder="John Doe"
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-all text-white placeholder-zinc-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Email Address</label>
                  <input
                    type="email"
                    placeholder="john@example.com"
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-all text-white placeholder-zinc-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Message</label>
                  <textarea
                    rows={4}
                    placeholder="Your message..."
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-all text-white placeholder-zinc-500 resize-none"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-3 bg-gradient-to-r from-emerald-500 to-green-500 rounded-xl font-semibold flex items-center justify-center gap-2 hover:shadow-[0_0_30px_rgba(16,185,129,0.4)] transition-all"
                >
                  Send Message <ArrowRight className="w-4 h-4" />
                </button>
              </form>
            </motion.div>

            {/* Contact Info */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="space-y-8"
            >
              <div className="p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10">
                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                    <Mail className="w-6 h-6 text-emerald-400" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white mb-1">Email</h4>
                    <p className="text-zinc-400">equilibra.team@gmail.com</p>
                  </div>
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10">
                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <MapPin className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white mb-1">Location</h4>
                    <p className="text-zinc-400">Manipal Institute of Technology, Manipal, Karnataka</p>
                  </div>
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10">
                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <Phone className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white mb-1">Phone</h4>
                    <p className="text-zinc-400">+91 XXXXX XXXXX</p>
                  </div>
                </div>
              </div>

              {/* Social Links */}
              <div className="flex gap-4 pt-4">
                <a href="#" className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 hover:border-white/20 transition-all">
                  <Github className="w-5 h-5 text-zinc-400" />
                </a>
                <a href="#" className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 hover:border-white/20 transition-all">
                  <Linkedin className="w-5 h-5 text-zinc-400" />
                </a>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-20 border-t border-white/5 bg-black">
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
                <li><a href="#how-it-works" className="hover:text-red-400 transition-colors">How it Works</a></li>
                <li><a href="#team" className="hover:text-red-400 transition-colors">Team</a></li>
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

const WorkflowStep = ({ step, icon: Icon, title, description, delay, color }: {
  step: number,
  icon: any,
  title: string,
  description: string,
  delay: number,
  color: string
}) => {
  const colorClasses: Record<string, { bg: string, text: string, border: string }> = {
    red: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/30' },
    orange: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/30' },
    yellow: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/30' },
    green: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/30' },
  };

  const colors = colorClasses[color] || colorClasses.red;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      viewport={{ once: true }}
      className="relative"
    >
      <div className={`p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/[0.02] border ${colors.border} hover:border-opacity-60 transition-all duration-300`}>
        {/* Step Number */}
        <div className={`w-14 h-14 rounded-2xl ${colors.bg} flex items-center justify-center mb-5 relative`}>
          <Icon className={`w-7 h-7 ${colors.text}`} />
          <span className={`absolute -top-2 -right-2 w-6 h-6 rounded-full bg-black ${colors.border} border-2 flex items-center justify-center text-xs font-bold ${colors.text}`}>
            {step}
          </span>
        </div>
        <h3 className="text-xl font-bold mb-3 text-white">{title}</h3>
        <p className="text-zinc-400 text-sm leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
};

const TeamCard = ({ name, role, github, linkedin, delay }: { name: string, role: string, github: string, linkedin: string, delay: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    viewport={{ once: true }}
    className="p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 hover:border-purple-500/30 transition-all duration-300 text-center group"
  >
    <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500/30 to-blue-500/30 mx-auto mb-5 flex items-center justify-center group-hover:scale-105 transition-transform">
      <Users className="w-10 h-10 text-purple-400" />
    </div>
    <h3 className="text-lg font-bold text-white mb-1">{name}</h3>
    <p className="text-zinc-400 text-sm">{role}</p>
    <div className="flex justify-center gap-3 mt-4">
      <a href={github} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center hover:bg-white/10 hover:text-white transition-all">
        <Github className="w-4 h-4 text-zinc-400 hover:text-white" />
      </a>
      <a href={linkedin} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center hover:bg-white/10 hover:text-white transition-all">
        <Linkedin className="w-4 h-4 text-zinc-400 hover:text-white" />
      </a>
    </div>
  </motion.div>
);

export default LandingPage;
