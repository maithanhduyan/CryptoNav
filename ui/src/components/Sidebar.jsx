export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800">
      <nav className="mt-4">
        <ul>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Dashboard
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Portfolio
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Transactions
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              AI Analytics
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Settings
            </a>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
