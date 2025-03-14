export default function Header() {
  return (
    <header className="bg-gray-900 border-b border-gray-800 px-4 py-3 flex items-center justify-between">
      <h1 className="text-white text-xl font-semibold">CryptoNav</h1>
      <nav>
        <a href="#" className="text-gray-300 hover:text-white px-3">
          Dashboard
        </a>
        <a href="#" className="text-gray-500 hover:text-white ml-4">
          Portfolio
        </a>
        <a href="#" className="text-gray-500 hover:text-white ml-4">
          Settings
        </a>
      </nav>
    </header>
  );
}
