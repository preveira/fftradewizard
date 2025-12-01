import React, { useState } from 'react';
import Layout from './components/Layout';
import RosRankings from './components/RosRankings';
import TradeAnalyzer from './components/TradeAnalyzer';

function App() {
  const [view, setView] = useState('rankings');

  return (
    <Layout selectedView={view} onSelectView={setView}>
      {view === 'rankings' && <RosRankings />}
      {view === 'trade' && <TradeAnalyzer />}
    </Layout>
  );
}

export default App;
