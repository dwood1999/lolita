import mysql from 'mysql2/promise';
import { env } from '$env/dynamic/private';

let pool: mysql.Pool | null = null;

export async function getDbConnection() {
	if (!pool) {
		try {
			console.log('Creating database connection pool...');
			console.log('DB_HOST:', env.DB_HOST);
			console.log('DB_USER:', env.DB_USER);
			console.log('DB_NAME:', env.DB_NAME);
			console.log('DB_PASSWORD length:', env.DB_PASSWORD?.length);
			console.log('DB_PASSWORD first 5 chars:', env.DB_PASSWORD?.substring(0, 5));
			console.log('DB_PASSWORD full (SvelteKit):', env.DB_PASSWORD);
			
			pool = mysql.createPool({
				host: env.DB_HOST || 'localhost',
				user: env.DB_USER || 'lolita',
				password: env.DB_PASSWORD,
				database: env.DB_NAME || 'lolita',
				waitForConnections: true,
				connectionLimit: 15,
				maxIdle: 5,
				idleTimeout: 60000,
				queueLimit: 0,
				charset: 'utf8mb4',
				ssl: false,
				acquireTimeout: 60000,
				timeout: 60000
			});
			
			console.log('Database connection pool created successfully');
		} catch (error) {
			console.error('Database connection pool creation failed:', error);
			throw error;
		}
	}
	return pool.getConnection();
}

export async function executeQuery(query: string, params: any[] = []) {
	let conn;
	try {
		conn = await getDbConnection();
		const [results] = await conn.execute(query, params);
		return results;
	} catch (error) {
		console.error('Database query error:', error);
		console.error('Query:', query);
		throw error;
	} finally {
		if (conn) {
			conn.release(); // Return connection to pool
		}
	}
}

// Initialize database tables
export async function initDatabase() {
	const conn = await getDbConnection();
	try {
		// Create users table
		await conn.execute(`
			CREATE TABLE IF NOT EXISTS users (
				id VARCHAR(255) PRIMARY KEY,
				email VARCHAR(255) UNIQUE NOT NULL,
				password_hash VARCHAR(255) NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		`);
		
		// Create sessions table
		await conn.execute(`
			CREATE TABLE IF NOT EXISTS sessions (
				id VARCHAR(255) PRIMARY KEY,
				user_id VARCHAR(255) NOT NULL,
				expires_at DATETIME NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
			)
		`);
		
		// Create screenplays table for future use
		await conn.execute(`
			CREATE TABLE IF NOT EXISTS screenplays (
				id VARCHAR(255) PRIMARY KEY,
				user_id VARCHAR(255) NOT NULL,
				title VARCHAR(500) NOT NULL,
				filename VARCHAR(500),
				original_filename VARCHAR(500),
				file_size INT,
				content LONGTEXT,
				status ENUM('draft', 'analyzing', 'completed', 'error') DEFAULT 'draft',
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
				FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
			)
		`);
		
		console.log('Database tables initialized successfully');
	} finally {
		conn.release(); // Return connection to pool
	}
}

// Get pool status for debugging
export function getPoolStatus() {
	if (!pool) {
		return { status: 'No pool created' };
	}
	
	return {
		allConnections: pool.pool._allConnections.length,
		freeConnections: pool.pool._freeConnections.length,
		connectionQueue: pool.pool._connectionQueue.length,
		acquiringConnections: pool.pool._acquiringConnections.length,
		config: {
			connectionLimit: pool.pool.config.connectionLimit,
			queueLimit: pool.pool.config.queueLimit
		}
	};
}

// Gracefully close the pool
export async function closePool() {
	if (pool) {
		await pool.end();
		pool = null;
		console.log('Database connection pool closed');
	}
}
