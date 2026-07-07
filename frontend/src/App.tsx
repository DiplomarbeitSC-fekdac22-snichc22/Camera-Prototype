import {useState} from "react";
import "./App.css";

function App() {
    const backendUrl = `http://192.168.74.17:8000`;

    const rawUrl = `${backendUrl}/video`;
    const detectUrl = `${backendUrl}/detect`;

    const [streamUrl, setStreamUrl] = useState(rawUrl);

    return (
        <main className="page">
            <h1>Camera Detection v.1</h1>

            <img className="logo" src="../src/assets/logo.png" alt="Pia Automation logo" />

            <div className="buttons">
                <button onClick={() => setStreamUrl(rawUrl)}>
                    Raw Stream
                </button>

                <button onClick={() => setStreamUrl(detectUrl)}>
                    Detection Stream
                </button>
            </div>

            <p>
                Current stream: <code>{streamUrl}</code>
            </p>

            <div className="camera-box">
                <img key={streamUrl} src={streamUrl} alt="Camera stream"/>
            </div>
        </main>
    );
}

export default App;