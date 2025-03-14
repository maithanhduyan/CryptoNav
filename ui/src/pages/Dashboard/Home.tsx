import { useAuth } from "../../context/AuthContext";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="p-6 text-white">
      <h2 className="text-2xl font-semibold mb-4">
        Welcome to CryptoNav, {user?.username || "User"}!
      </h2>
      <p className="text-gray-300 mb-6">
        Your crypto portfolio management dashboard.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: Portfolio Overview */}
        <div className="bg-gray-800 rounded-lg p-4 shadow-md">
          <h3 className="text-lg font-medium text-white">Portfolio Overview</h3>
          <p className="text-gray-400 mt-2">
            Total Value: <span className="text-green-400">$12,345.67</span>
          </p>
          <p className="text-gray-400">
            24h Change: <span className="text-red-400">-2.5%</span>
          </p>
        </div>
        {/* Card 2: Quick Stats */}
        <div className="bg-gray-800 rounded-lg p-4 shadow-md">
          <h3 className="text-lg font-medium text-white">Quick Stats</h3>
          <p className="text-gray-400 mt-2">Assets: 5</p>
          <p className="text-gray-400">Transactions: 12</p>
        </div>
      </div>
    </div>
  );
}