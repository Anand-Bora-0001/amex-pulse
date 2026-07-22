/**
 * AmEx Pulse — Main Application
 * ================================
 * Root component with routing, auth state, and theme management.
 */

import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Header from './components/layout/Header';
import LoginPage from './features/auth/LoginPage';
import DashboardPage from './features/dashboard/DashboardPage';
import CustomersPage from './features/customer/CustomersPage';
import CustomerDetailPage from './features/customer/CustomerDetailPage';
import JourneyExplorerPage from './features/journey/JourneyExplorerPage';
import AnalyticsPage from './features/analytics/AnalyticsPage';
import AgentViewPage from './features/agent/AgentViewPage';
import SettingsPage from './features/settings/SettingsPage';
import type { User } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30000,
    },
  },
});

function App() {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('amex_pulse_user');
    return stored ? JSON.parse(stored) : null;
  });

  // Apply theme on mount and change
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', 'light');
  }, []);

  const handleLogin = (user: User, token: string) => {
    setUser(user);
    localStorage.setItem('amex_pulse_token', token);
    localStorage.setItem('amex_pulse_user', JSON.stringify(user));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('amex_pulse_token');
    localStorage.removeItem('amex_pulse_user');
  };

  const isAuthenticated = !!user;

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {isAuthenticated ? (
          <div className="app-layout">
            <Header
              user={user}
              onLogout={handleLogout}
            />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/customers" element={<CustomersPage />} />
                <Route path="/customers/:id" element={<CustomerDetailPage />} />
                <Route path="/journeys" element={<JourneyExplorerPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/agent" element={<AgentViewPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="/login" element={<Navigate to="/" replace />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
        ) : (
          <Routes>
            <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        )}
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
