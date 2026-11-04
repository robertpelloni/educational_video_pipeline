const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: '.',
  testMatch: 'e2e.spec.cjs',
  use: {
    baseURL: 'http://localhost:5173',
  },
  webServer: [
    {
      command: 'npm run dev',
      port: 5173,
      reuseExistingServer: true,
      stdout: 'ignore',
      stderr: 'pipe',
    },
    {
      command: 'cd .. && uvicorn src.api_router:app --port 8000',
      port: 8000,
      reuseExistingServer: true,
      stdout: 'ignore',
      stderr: 'pipe',
      env: {
        API_USERNAME: 'admin',
        API_PASSWORD: 'local_dev_password'
      }
    }
  ],
});
