import { useState } from "react";
import "./App.css";

function App() {
  const [backendUrl, setBackendUrl] = useState("http://192.168.74.17:8000");

  const streamUrl = `${backendUrl}/video`;
  const snapshotUrl = `${backendUrl}/snapshot`;
  const healthUrl = `${backendUrl}/health`;

  const checkBackend = async () => {
    try {
      const response = await fetch(healthUrl);
      const data = await response.json();
      alert(JSON.stringify(data, null, 2));
    } catch (error) {
      alert("Backend not reachable. Check IP address and port 8000.");
      console.error(error);
    }
  };

  return (
      <main className="page">
        <section className="card">
          <h1>Camera Prototype</h1>

          <p className="subtitle">
            Simple USB camera stream from Python backend to React frontend.
          </p>

          <div className="input-row">
            <label>Backend URL</label>
            <input
                value={backendUrl}
                onChange={(event) => setBackendUrl(event.target.value)}
                placeholder="http://192.168.178.xxx:8000"
            />
          </div>

          <div className="buttons">
            <button onClick={checkBackend}>Check backend</button>

            <a href={snapshotUrl} target="_blank">
              Open snapshot
            </a>

            <a href={streamUrl} target="_blank">
              Open raw stream
            </a>
          </div>

          <div className="camera-box">
            <img src={streamUrl} alt="Live camera stream" />
          </div>
        </section>
      </main>
  );
}

export default App;