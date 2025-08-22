import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const { DB_HOST, DB_USER, DB_PASSWORD, DB_NAME } = process.env;

async function resetDatabase() {
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
		
		// Drop existing tables in correct order (foreign keys first)
		console.log('Dropping existing tables...');
		await connection.execute('DROP TABLE IF EXISTS sessions');
		await connection.execute('DROP TABLE IF EXISTS screenplays');
		await connection.execute('DROP TABLE IF EXISTS users');
		
		console.log('Creating fresh tables...');
		
		// Create users table with simple schema
		await connection.execute(`
			CREATE TABLE users (
				id VARCHAR(255) PRIMARY KEY,
				email VARCHAR(255) UNIQUE NOT NULL,
				password_hash VARCHAR(255) NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		`);
		
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
		
		// Create screenplays table
		await connection.execute(`
			CREATE TABLE screenplays (
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
		
		console.log('Database tables reset successfully');
	} catch (error) {
		console.error('Database reset error:', error);
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
		console.log('Resetting database...');
		await resetDatabase();
		console.log('Database reset completed successfully!');
		process.exit(0);
	} catch (error) {
		console.error('Database reset failed:', error);
		process.exit(1);
	}
}

main();
