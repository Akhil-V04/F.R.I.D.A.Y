import './App.css';
import Navbar from './components/Navbar';
import PlasmaOrb from './components/blob';

function App() {
  return (
    <div className="App">
      <Navbar />
      <div className="app-content">
        <PlasmaOrb />
      </div>
    </div>
  );
}

export default App;
