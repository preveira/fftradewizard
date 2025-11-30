export default function Layout({ children }) {
  return (
    <div style={{ maxWidth: "960px", margin: "0 auto", padding: "1.5rem" }}>
      <header>
        <h1>FFTradeWizard</h1>
        <p>Fantasy Football Trade & Rest-of-Season Analyzer</p>
        <hr />
      </header>
      <main>{children}</main>
      <footer style={{ marginTop: "2rem", fontSize: "0.8rem", opacity: 0.7 }}>
        Built with React, FastAPI, and Docker.
      </footer>
    </div>
  );
}
