# Cấu trúc Dự án như sau:

```
.\
├── Dockerfile
├── eslint.config.js
├── index.html
├── package-lock.json
├── package.json
├── src
│   ├── App.jsx
│   ├── components
│   │   ├── Header.jsx
│   │   ├── Layout.jsx
│   │   └── Sidebar.jsx
│   ├── index.css
│   └── main.jsx
└── vite.config.js
```

# Danh sách chi tiết các file:

## File .\eslint.config.js:
```javascript
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  { ignores: ['dist'] },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  },
]

```

## File .\vite.config.js:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})

```

## File .\src\App.jsx:
```
import Layout from "./components/Layout";

function App() {
  return (
    <Layout>
      <div className="p-6 text-white">
        <h2 className="text-2xl font-semibold">Welcome to CryptoNav</h2>
        <p>Your crypto portfolio management dashboard.</p>
      </div>
    </Layout>
  );
}

export default App;

```

## File .\src\main.jsx:
```
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

```

## File .\src\components\Header.jsx:
```
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

```

## File .\src\components\Layout.jsx:
```
import Sidebar from "./Sidebar";
import Header from "./Header";

export default function Layout({ children }) {
  return (
    <div className="flex flex-col h-screen bg-gray-950">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}

```

## File .\src\components\Sidebar.jsx:
```
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
              Analytics
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

```

