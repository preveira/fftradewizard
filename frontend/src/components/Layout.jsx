import React, { useState } from 'react';

const Layout = ({ selectedView, onSelectView, children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleNavClick = (view) => {
    onSelectView(view);
    // Auto-close the sidebar on small screens after navigation
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  };

  return (
    <div className="app-shell">
      <aside
        className={`sidebar ${
          sidebarOpen ? 'sidebar--open' : 'sidebar--collapsed'
        }`}
      >
        <div className="sidebar__brand">
          <span className="sidebar__logo">⚡</span>
          <div className="sidebar__title-group">
            <h1 className="sidebar__title">FFTradeWizard</h1>
            <p className="sidebar__subtitle">Fantasy Trade Analyzer</p>
          </div>
        </div>

        <nav className="sidebar__nav">
          <button
            className={`nav-item ${
              selectedView === 'rankings' ? 'nav-item--active' : ''
            }`}
            onClick={() => handleNavClick('rankings')}
          >
            🏆 Rankings
          </button>
          <button
            className={`nav-item ${
              selectedView === 'trade' ? 'nav-item--active' : ''
            }`}
            onClick={() => handleNavClick('trade')}
          >
            🔄 Trade Analyzer
          </button>
        </nav>
      </aside>

      <div className="app-shell__main">
        <header className="topbar">
          <button
            className="hamburger"
            onClick={() => setSidebarOpen((open) => !open)}
            aria-label="Toggle navigation"
          >
            <span />
            <span />
            <span />
          </button>
          <div className="topbar__titles">
            <h2 className="topbar__title">
              {selectedView === 'rankings'
                ? 'Rest-of-Season Rankings'
                : 'Trade Analyzer'}
            </h2>
            <p className="topbar__subtitle">
              Live ESPN player pool · Blue &amp; silver theme
            </p>
          </div>
        </header>

        <main className="main-content">{children}</main>

        <footer className="footer">
          <span>Built with React · FastAPI · ESPN Fantasy API (test mode)</span>
        </footer>
      </div>
    </div>
  );
};

export default Layout;
