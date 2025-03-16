## Install TailwindCSS

1. Install Tailwind CSS
   Install `tailwindcss` and `@tailwindcss/vite` via npm.

```
npm install -D tailwindcss @tailwindcss/vite
```

2. Configure the Vite plugin
   Add the `@tailwindcss/vite` plugin to your Vite configuration.

```ts
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
export default defineConfig({
  plugins: [tailwindcss()],
});
```

3. Import Tailwind CSS
   Add an `@import` to your CSS file that imports TailwindCSS.

```tsx
@import "tailwindcss";
```

4. Start your build process

```bash
npm run dev
```
