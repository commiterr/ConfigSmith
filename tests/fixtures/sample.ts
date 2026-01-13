// Sample TypeScript file for testing ConfigSmith scanner
// This file demonstrates various patterns for accessing environment variables

// Direct access patterns
const dbUrl = process.env.DATABASE_URL || 'postgresql://localhost/db';
const apiKey = process.env.API_KEY;

// Destructuring with defaults
const { PORT = '3000', NODE_ENV = 'development' } = process.env;

// Bracket notation
const secretKey = process.env["SECRET_KEY"];
const debug = process.env["DEBUG"] || 'false';

// Framework patterns (Next.js)
const publicApiUrl = process.env.NEXT_PUBLIC_API_URL;

// React pattern
const reactAppName = process.env.REACT_APP_NAME || 'MyApp';

// Configuration object pattern
const config = {
  database: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432', 10),
  ssl: process.env.DB_SSL === 'true',
};

export { dbUrl, apiKey, config };
