import Layout from "./components/Layout";
import RosRankings from "./components/RosRankings";
import TradeAnalyzer from "./components/TradeAnalyzer";

export default function App() {
  return (
    <Layout>
      <RosRankings />
      <TradeAnalyzer />
    </Layout>
  );
}
