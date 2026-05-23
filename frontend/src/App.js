import './App.css';
import Navbar from './components/Navbar';
import PlasmaOrb from './components/blob';


function App() {
  return (
    <div className="App">
      <Navbar />
      <div className="app-content" style={{
        '--bg-image': `url(${process.env.PUBLIC_URL}/background.jpeg)`
      }}>
        <PlasmaOrb />
      </div>
    </div>
  );
}

export default App;
