import { Link } from "react-router-dom";

export default function AppSidebar() {
  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800">
      <nav className="mt-4">
        <ul>
          <li>
            <Link to="/" className="block px-4 py-2 text-gray-300 hover:bg-gray-800">
              Dashboard
            </Link>
          </li>
          <li>
            <Link to="/portfolio" className="block px-4 py-2 text-gray-300 hover:bg-gray-800">
              Portfolio
            </Link>
          </li>
          <li>
            <Link to="/transactions" className="block px-4 py-2 text-gray-300 hover:bg-gray-800">
              Transactions
            </Link>
          </li>
          <li>
            <Link to="/analytics" className="block px-4 py-2 text-gray-300 hover:bg-gray-800">
              AI Analytics
            </Link>
          </li>
          <li>
            <Link to="/settings" className="block px-4 py-2 text-gray-300 hover:bg-gray-800">
              Settings
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
