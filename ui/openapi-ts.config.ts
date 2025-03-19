// openapi-ts.config.ts
// Auto
import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://cryptonav.local/api/openapi.json',
  output: 'src/client',
  plugins: ['@hey-api/client-fetch'],
});