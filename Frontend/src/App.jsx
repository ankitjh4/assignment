import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import Chat from './pages/Chat'
import Home from './pages/Home'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Status from './pages/Status'
import Upload from './pages/Upload'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/status" element={<Status />} />
              <Route
                path="/chat"
                element={
                  <ProtectedRoute>
                    <Chat />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/upload"
                element={
                  <ProtectedRoute>
                    <Upload />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </main>

          <footer className="bg-white border-t border-gray-200 py-4 text-center text-sm text-gray-400">
            © 2026 DRINKOO — Smart Beverage Assistant
          </footer>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}
