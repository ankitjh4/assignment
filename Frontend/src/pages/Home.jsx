import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const features = [
  {
    icon: '🤖',
    title: 'AI-Powered Chat',
    desc: 'Ask anything about DRINKOO products, ingredients, promotions, and orders. Answers are grounded in real data.',
  },
  {
    icon: '🧃',
    title: '10+ Beverages',
    desc: 'Energy drinks, cold-pressed juices, sparkling water, and coconut water — something for everyone.',
  },
  {
    icon: '🏷️',
    title: 'Live Promotions',
    desc: 'Stay on top of our latest deals and seasonal discounts automatically surfaced by the chatbot.',
  },
  {
    icon: '🖼️',
    title: 'Image Upload',
    desc: 'Share product photos or receipts directly in the chat for a richer support experience.',
  },
]

export default function Home() {
  const { user } = useAuth()

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-drinkoo-600 to-drinkoo-800 text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="text-6xl mb-4">🥤</div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4 leading-tight">
            Meet the DRINKOO<br />Smart Assistant
          </h1>
          <p className="text-drinkoo-100 text-lg mb-8 max-w-2xl mx-auto">
            Get instant answers about our beverages, ingredients, promotions, and support
            policies — powered by a grounded RAG chatbot that only uses DRINKOO data.
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            {user ? (
              <Link to="/chat" className="bg-white text-drinkoo-700 font-semibold px-6 py-3 rounded-lg hover:bg-drinkoo-50 transition-colors">
                Open Chat →
              </Link>
            ) : (
              <>
                <Link to="/signup" className="bg-white text-drinkoo-700 font-semibold px-6 py-3 rounded-lg hover:bg-drinkoo-50 transition-colors">
                  Get started free
                </Link>
                <Link to="/login" className="border border-white text-white font-semibold px-6 py-3 rounded-lg hover:bg-drinkoo-700 transition-colors">
                  Login
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-10">Everything you need</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f) => (
            <div key={f.title} className="card text-center hover:shadow-md transition-shadow">
              <div className="text-4xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-gray-800 mb-2">{f.title}</h3>
              <p className="text-sm text-gray-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Sample questions */}
      <section className="bg-white border-t border-gray-100 py-12 px-4">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-xl font-bold text-gray-800 mb-6 text-center">Try asking the chatbot…</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              'Which DRINKOO products are low sugar?',
              'What ingredients are in the citrus drinks?',
              'Are there active promotions for sparkling beverages?',
              'What should I do if my order arrives damaged?',
              'Which products are available for bulk orders?',
              'How do I cancel my subscription?',
            ].map((q) => (
              <div key={q} className="flex items-start gap-2 p-3 rounded-lg bg-gray-50 border border-gray-200">
                <span className="text-drinkoo-500 mt-0.5">💬</span>
                <span className="text-sm text-gray-700">{q}</span>
              </div>
            ))}
          </div>
          {!user && (
            <p className="text-center mt-8 text-gray-500 text-sm">
              <Link to="/signup" className="text-drinkoo-600 font-medium hover:underline">Sign up free</Link>
              {' '}or{' '}
              <Link to="/login" className="text-drinkoo-600 font-medium hover:underline">login</Link>
              {' '}to start chatting.
            </p>
          )}
        </div>
      </section>
    </div>
  )
}
