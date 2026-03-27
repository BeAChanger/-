/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import Welcome from './pages/Welcome';
import Feed from './pages/Feed';
import Profile from './pages/Profile';
import Login from './pages/Login';
import { getAuth } from './api/client';

export default function App() {
  const [currentRoute, setCurrentRoute] = useState(window.location.pathname);

  useEffect(() => {
    const handlePopState = () => {
      setCurrentRoute(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    setCurrentRoute(path);
    window.scrollTo(0, 0);
  };

  const auth = getAuth();
  const isLoggedIn = !!auth;

  // Protected route check
  const requiresAuth = ['/feed', '/search', '/discover'].some(p => currentRoute.startsWith(p))
    || currentRoute.startsWith('/agent/');

  if (requiresAuth && !isLoggedIn) {
    return (
      <div className="font-sans antialiased text-brand-dark bg-brand-pink min-h-screen">
        <Login onNavigate={navigate} />
      </div>
    );
  }

  let content;
  if (currentRoute === '/' || currentRoute === '/welcome') {
    content = <Welcome onNavigate={navigate} />;
  } else if (currentRoute === '/login') {
    content = <Login onNavigate={navigate} />;
  } else if (currentRoute === '/feed') {
    content = <Feed onNavigate={navigate} />;
  } else if (currentRoute.startsWith('/agent/')) {
    const agentId = currentRoute.split('/')[2];
    content = <Profile agentId={agentId} onNavigate={navigate} />;
  } else {
    content = <Welcome onNavigate={navigate} />;
  }

  return (
    <div className="font-sans antialiased text-brand-dark bg-brand-pink min-h-screen">
      {content}
    </div>
  );
}
