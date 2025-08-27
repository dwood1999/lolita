#!/usr/bin/env node

// Debug script to test authentication and database connectivity
const mysql = require('mysql2/promise');
require('dotenv').config();

async function debugAuth() {
    console.log('🔍 Debugging Authentication Issues...\n');
    
    // Test database connection
    console.log('1. Testing Database Connection:');
    console.log('   DB_HOST:', process.env.DB_HOST);
    console.log('   DB_USER:', process.env.DB_USER);
    console.log('   DB_NAME:', process.env.DB_NAME);
    console.log('   DB_PASSWORD length:', process.env.DB_PASSWORD?.length);
    
    try {
        const connection = await mysql.createConnection({
            host: process.env.DB_HOST || 'localhost',
            user: process.env.DB_USER || 'lolita',
            password: process.env.DB_PASSWORD,
            database: process.env.DB_NAME || 'lolita'
        });
        
        console.log('   ✅ Database connection successful');
        
        // Check if users table exists and has correct structure
        console.log('\n2. Checking Users Table:');
        const [tables] = await connection.execute("SHOW TABLES LIKE 'users'");
        if (tables.length === 0) {
            console.log('   ❌ Users table does not exist');
            
            // Create users table
            await connection.execute(`
                CREATE TABLE users (
                    id VARCHAR(255) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255) DEFAULT '',
                    is_active BOOLEAN DEFAULT TRUE,
                    is_verified BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            `);
            console.log('   ✅ Users table created');
        } else {
            console.log('   ✅ Users table exists');
            
            // Check table structure
            const [columns] = await connection.execute("DESCRIBE users");
            console.log('   Table structure:', columns.map(col => col.Field));
        }
        
        // Check if sessions table exists
        console.log('\n3. Checking Sessions Table:');
        const [sessionTables] = await connection.execute("SHOW TABLES LIKE 'sessions'");
        if (sessionTables.length === 0) {
            console.log('   ❌ Sessions table does not exist');
            
            // Create sessions table
            await connection.execute(`
                CREATE TABLE sessions (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    expires_at DATETIME NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            `);
            console.log('   ✅ Sessions table created');
        } else {
            console.log('   ✅ Sessions table exists');
        }
        
        // Check for existing users
        console.log('\n4. Checking Existing Users:');
        const [users] = await connection.execute("SELECT id, email, created_at FROM users LIMIT 5");
        console.log(`   Found ${users.length} users`);
        if (users.length > 0) {
            console.log('   Sample users:', users.map(u => ({ id: u.id, email: u.email })));
        }
        
        // Check for active sessions
        console.log('\n5. Checking Active Sessions:');
        const [sessions] = await connection.execute("SELECT id, user_id, expires_at FROM sessions WHERE expires_at > NOW() LIMIT 5");
        console.log(`   Found ${sessions.length} active sessions`);
        
        await connection.end();
        console.log('\n✅ Database debugging complete!');
        
    } catch (error) {
        console.error('   ❌ Database connection failed:', error.message);
        
        if (error.code === 'ER_ACCESS_DENIED_ERROR') {
            console.log('\n💡 Suggestions:');
            console.log('   - Check DB_USER and DB_PASSWORD in .env file');
            console.log('   - Verify MySQL user has proper permissions');
        } else if (error.code === 'ECONNREFUSED') {
            console.log('\n💡 Suggestions:');
            console.log('   - Check if MySQL server is running');
            console.log('   - Verify DB_HOST and port settings');
        } else if (error.code === 'ER_BAD_DB_ERROR') {
            console.log('\n💡 Suggestions:');
            console.log('   - Database does not exist, create it first');
            console.log('   - Check DB_NAME in .env file');
        }
    }
}

debugAuth().catch(console.error);
