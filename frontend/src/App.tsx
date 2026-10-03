import { useEffect } from "react";

function App() {
  useEffect(() => {
    console.log("React is running");

    fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Hello from React",
      }),
    })
      .then((res) => {
        console.log("HTTP status:", res.status);
        return res.json();
      })
      .then((data) => {
        console.log("Backend response:", data);
      })
      .catch((error) => {
        console.error("Request failed:", error);
      });
  }, []);

  return <h1>Backend connection test</h1>;
}

export default App;