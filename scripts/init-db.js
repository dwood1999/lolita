import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const { DB_HOST, DB_USER, DB_PASSWORD, DB_NAME } = process.env;

async function initDatabase() {
	let connection;
	try {
		console.log('Creating database connection...');
		console.log('DB_HOST:', DB_HOST);
		console.log('DB_USER:', DB_USER);
		console.log('DB_NAME:', DB_NAME);
		
		connection = await mysql.createConnection({
			host: DB_HOST,
			user: DB_USER,
			password: DB_PASSWORD,
			database: DB_NAME
		});
		
		console.log('Database connection established successfully');
		
		// Create users table
		await connection.execute(`
			CREATE TABLE IF NOT EXISTS users (
				id VARCHAR(255) PRIMARY KEY,
				email VARCHAR(255) UNIQUE NOT NULL,
				password_hash VARCHAR(255) NOT NULL,
				full_name VARCHAR(255) DEFAULT '',
				is_active BOOLEAN DEFAULT 1,
				is_verified BOOLEAN DEFAULT 1,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		`);
		
		// Create sessions table
		await connection.execute(`
			CREATE TABLE IF NOT EXISTS sessions (
				id VARCHAR(255) PRIMARY KEY,
				user_id VARCHAR(255) NOT NULL,
				expires_at DATETIME NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
			)
		`);
		
		// Create screenplays table
		await connection.execute(`
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
	} catch (error) {
		console.error('Database initialization error:', error);
		throw error;
	} finally {
		if (connection) {
			await connection.end();
			console.log('Database connection closed');
		}
	}
}

async function main() {
	try {
		console.log('Initializing database...');
		await initDatabase();
		console.log('Database initialization completed successfully!');
		process.exit(0);
	} catch (error) {
		console.error('Database initialization failed:', error);
		process.exit(1);
	}
}

main();
