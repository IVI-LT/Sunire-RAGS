/*import logo from './logo.svg';
import './App.css';
import SunireGPT from './components/SunireGPT';

function App() {
  const [showChat, setShowChat] = useState(false);

  const toggleCHAT = () => {
    setShowChat(!showChat);
  };

  return (
    <div className="App">
       <img src="chaticon.png" alt="chat-img"></img>
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <button onClick={toggleChat} className="chat-toggle-button">
          {showChat ? 'Close Chat' : 'Open Chat'}
        </button>
      </header>
      {showChat && <SunireGPT />}
    </div>
  );
}

export default App; */

import logo from './logo.svg';
import './App.css';
import SunireGPT from './components/SunireGPT';

function App() {
  return (
    <div className="App">
      <SunireGPT />
    </div>
  );
}

export default App;
