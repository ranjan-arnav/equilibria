import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './LandingPage';
import { Dashboard } from './Dashboard';
import { OnboardingView } from './views/OnboardingView';
import { LoginView } from './views/LoginView';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginView />} />
                <Route path="/onboarding" element={<OnboardingView />} />
                <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
        </Router>
    );
}

export default App;
