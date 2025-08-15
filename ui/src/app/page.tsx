import Link from 'next/link'

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Jarvis Dashboard
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI Assistant Management & Monitoring
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <Link href="/overview" className="card hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Overview</h2>
            <p className="text-gray-600">System status and key metrics</p>
          </Link>
          
          <Link href="/logs" className="card hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Logs</h2>
            <p className="text-gray-600">Real-time log streaming and search</p>
          </Link>
          
          <Link href="/selftest" className="card hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Self-Test</h2>
            <p className="text-gray-600">Run diagnostics and health checks</p>
          </Link>
        </div>
        
        <div className="mt-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="flex justify-center gap-4">
            <button className="btn-primary">
              Start Monitoring
            </button>
            <button className="btn-secondary">
              View API Docs
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}
