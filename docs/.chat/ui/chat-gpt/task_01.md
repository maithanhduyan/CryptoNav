Dưới đây là hướng dẫn chi tiết từng bước để bạn thực hiện Task đầu tiên:

### 🚩 **Task: Thiết lập môi trường**

---

## 📌 **Bước 1: Cài đặt dependencies cần thiết**

Mở Terminal, vào thư mục dự án `../ui`:

```bash
npm install react-router-dom @types/react-router-dom axios
npm install -D tailwindcss postcss autoprefixer @vitejs/plugin-react typescript @types/react eslint prettier @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-react-hooks eslint-plugin-react-refresh
```

---

## 📌 **Bước 2: Cấu hình Tailwind CSS và PostCSS**

**Khởi tạo Tailwind và PostCSS:**

```bash
npx tailwindcss init -p
```

**Thiết lập Tailwind CSS** (`tailwind.config.js`):

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

**Tạo file `src/index.css`:**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Đảm bảo rằng file này được import trong file `main.tsx`:

```tsx
import "./index.css";
```

---

## 📌 **Bước 3: Cấu hình ESLint & Prettier**

### ✅ **Tạo file `.eslintrc.cjs`**:

```js
module.exports = {
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: "module",
    ecmaFeatures: { jsx: true },
  },
  settings: {
    react: { version: "detect" },
  },
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
  ],
  plugins: ["@typescript-eslint", "react-refresh"],
  rules: {
    "react-refresh/only-export-components": [
      "warn",
      { allowConstantExport: true },
    ],
  },
};
```

### ✅ **Tạo file `.prettierrc`**:

```json
{
  "semi": true,
  "singleQuote": true,
  "printWidth": 80,
  "trailingComma": "all",
  "tabWidth": 2
}
```

**Chạy lệnh format và kiểm tra code:**

```bash
npx eslint ./src --ext .js,.jsx,.ts,.tsx
npx prettier --write .
```

---

## 📌 **Bước 4: Cấu hình TypeScript**

Tạo file `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ESNext"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": false,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

---

## 📌 **Bước 5: Cấu hình Vite**

Cập nhật file `vite.config.ts`:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 3000,
  },
});
```

---

## 📌 **Bước 6: Dockerfile & Dev Container (optional)**

### ✅ **Tạo file `Dockerfile`:**

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

### ✅ **Tạo file `.devcontainer/devcontainer.json` (VSCode):**

```json
{
  "name": "CryptoNav DevContainer",
  "dockerFile": "../Dockerfile",
  "appPort": [3000],
  "settings": {
    "terminal.integrated.shell.linux": "/bin/sh"
  },
  "extensions": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss"
  ]
}
```

---

## 📌 **Bước 7: Chạy và kiểm tra dự án**

Khởi động dự án:

```bash
npm run dev
```

Truy cập URL:  
[http://localhost:3000](http://localhost:3000)

Kiểm tra dự án chạy ổn định, cấu trúc và reload tự động hoạt động tốt.

---

**Hoàn thành các bước trên** đồng nghĩa với việc hoàn thành task **Thiết lập môi trường**. Sau khi hoàn thành, bạn đã sẵn sàng tiếp tục sang các bước tiếp theo như xử lý đăng nhập, xây dựng giao diện Dashboard, Portfolio...
