import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-8 max-w-5xl mx-auto">
      <div className="flex gap-8 mb-8">
        <a 
          href="https://vite.dev" 
          target="_blank" 
          className="transition-all duration-300 hover:drop-shadow-[0_0_2rem_#646cffaa]"
        >
          <img 
            src={viteLogo} 
            className="h-24 p-6 transition-all duration-300 will-change-transform" 
            alt="Vite logo" 
          />
        </a>
        <a 
          href="https://react.dev" 
          target="_blank"
          className="transition-all duration-300 hover:drop-shadow-[0_0_2rem_#61dafbaa]"
        >
          <img 
            src={reactLogo} 
            className="h-24 p-6 logo-animate transition-all duration-300 will-change-transform hover:drop-shadow-[0_0_2rem_#61dafbaa]" 
            alt="React logo" 
          />
        </a>
      </div>
      
      <h1 className="text-5xl font-bold leading-tight mb-8 text-center">
        Vite + React
      </h1>
      
      <div className="bg-gray-800 rounded-lg p-8 mb-6 shadow-lg">
        <button 
          onClick={() => setCount((count) => count + 1)}
          className="bg-gray-700 hover:bg-gray-600 border border-transparent hover:border-blue-500 
                     rounded-lg px-6 py-3 text-base font-medium transition-all duration-200 
                     focus:outline-none focus:ring-4 focus:ring-blue-500/50 cursor-pointer mb-4"
        >
          count is {count}
        </button>
        <p className="text-gray-300 text-center">
          Edit <code className="bg-gray-700 px-2 py-1 rounded text-sm">src/App.tsx</code> and save to test HMR
        </p>
      </div>
      
      <p className="text-gray-500 text-center">
        Click on the Vite and React logos to learn more
      </p>
    </div>
  )
}

export default App
