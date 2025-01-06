import logo from './logo.svg';
import React , {useState} from 'react';
import './App.css';

function App(){
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const HTTP= "http://localhost:9020/chat";

  const handleSubmit = async (e) => {
    e.preventDefault();
      setResponse("")
        try {
          const res = await fetch(HTTP, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ prompt })
          });

          const reader = res.body.getReader();
          const decoder = new TextDecoder('utf-8');

          function read() {
              reader.read().then(({ done, value }) => {
                  if (done) {
                      return;
                  }
                  const chunk = decoder.decode(value, { stream: true });
                  setResponse((prev) => prev + chunk);
                  read();
              });
          }

          read();
      } catch (error) {
          console.error("Error:", error);
      }
    setPrompt("");
  };
  const handlePrompt = (e) => setPrompt(e.target.value);
}

export default App;
