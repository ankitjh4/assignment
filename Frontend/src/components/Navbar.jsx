import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 font-bold text-xl text-drinkoo-700">
          <span className="text-2xl">🥤</span>
          <span>DRINKOO</span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1 sm:gap-2">
          <Link
            to="/status"
            className="px-3 py-2 text-sm text-gray-600 hover:text-drinkoo-700 rounded-lg hover:bg-drinkoo-50 transition-colors"
          >
            Status
          </Link>

          {user ? (
            <>
              <Link
                to="/chat"
                className="px-3 py-2 text-sm text-gray-600 hover:text-drinkoo-700 rounded-lg hover:bg-drinkoo-50 transition-colors"
              >
                Chat
              </Link>
              <Link
                to="/upload"
                className="px-3 py-2 text-sm text-gray-600 hover:text-drinkoo-700 rounded-lg hover:bg-drinkoo-50 transition-colors"
              >
                Upload
              </Link>
              <span className="hidden sm:block text-sm text-gray-500 px-2">
                {user.full_name.split(' ')[0]}
              </span>
              <button
                onClick={handleLogout}
                className="btn-secondary text-sm"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-secondary text-sm">Login</Link>
              <Link to="/signup" className="btn-primary text-sm">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
