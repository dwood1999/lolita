require('dotenv').config();
const mysql = require('mysql2/promise');

(async () => {
  console.log('Testing database connection...');
  console.log('Environment variables loaded:');
  console.log('  DB_HOST:', process.env.DB_HOST);
  console.log('  DB_USER:', process.env.DB_USER);
  console.log('  DB_PASSWORD:', process.env.DB_PASSWORD ? '***' + process.env.DB_PASSWORD.slice(-3) : 'NOT SET');
  console.log('  DB_NAME:', process.env.DB_NAME);
  console.log('  DB_PORT:', process.env.DB_PORT || '3306');
  
  try {
    const conn = await mysql.createConnection({
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT || '3306'),
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME
    });
    
    console.log('✅ Connected successfully!');
    
    const [rows] = await conn.execute('SELECT 1 as test');
    console.log('Query result:', rows);
    
    // Check tables
    const [tables] = await conn.execute('SHOW TABLES');
    console.log('Tables in database:', tables.map(t => Object.values(t)[0]));
    
    await conn.end();
    console.log('Connection closed successfully');
  } catch (err) {
    console.error('❌ Connection failed:', err.message);
    console.error('Error code:', err.code);
    console.error('SQL State:', err.sqlState);
  }
})();
