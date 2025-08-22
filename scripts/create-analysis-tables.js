import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const { DB_HOST, DB_USER, DB_PASSWORD, DB_NAME } = process.env;

async function createAnalysisTables() {
	let connection;
	try {
		console.log('Creating database connection...');
		
		connection = await mysql.createConnection({
			host: DB_HOST,
			user: DB_USER,
			password: DB_PASSWORD,
			database: DB_NAME
		});
		
		console.log('Database connection established successfully');
		
		// Create screenplay_analyses table
		await connection.execute(`
			CREATE TABLE IF NOT EXISTS screenplay_analyses (
				id VARCHAR(255) PRIMARY KEY,
				user_id VARCHAR(255) NOT NULL,
				title VARCHAR(500) NOT NULL,
				original_filename VARCHAR(500),
				file_path VARCHAR(1000),
				file_size INT,
				genre VARCHAR(100),
				detected_genre VARCHAR(100),
				
				-- Analysis Results
				overall_score DECIMAL(3,1),
				recommendation ENUM('Pass', 'Consider', 'Recommend', 'Strong Recommend'),
				one_line_verdict TEXT,
				executive_summary TEXT,
				top_strengths JSON,
				key_weaknesses JSON,
				suggestions JSON,
				commercial_viability TEXT,
				target_audience TEXT,
				comparable_films JSON,
				casting_suggestions JSON,
				
				-- Processing Details
				ai_model VARCHAR(100),
				confidence_level DECIMAL(3,2),
				processing_time DECIMAL(8,2),
				cost DECIMAL(10,4),
				
				-- Status and Metadata
				status ENUM('pending', 'processing', 'completed', 'error') DEFAULT 'pending',
				error_message TEXT,
				raw_api_request LONGTEXT,
				raw_api_response LONGTEXT,
				
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
				
				FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
				INDEX idx_user_id (user_id),
				INDEX idx_status (status),
				INDEX idx_created_at (created_at)
			)
		`);
		
		// Create api_usage_tracking table
		await connection.execute(`
			CREATE TABLE IF NOT EXISTS api_usage_tracking (
				id INT AUTO_INCREMENT PRIMARY KEY,
				user_id VARCHAR(255) NOT NULL,
				analysis_id VARCHAR(255),
				api_provider VARCHAR(50) NOT NULL,
				model_name VARCHAR(100) NOT NULL,
				
				-- Usage Metrics
				input_tokens INT DEFAULT 0,
				output_tokens INT DEFAULT 0,
				total_tokens INT DEFAULT 0,
				cost DECIMAL(10,6) NOT NULL,
				
				-- Request Details
				request_type VARCHAR(50) NOT NULL,
				processing_time DECIMAL(8,2),
				success BOOLEAN DEFAULT TRUE,
				error_message TEXT,
				
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				
				FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
				FOREIGN KEY (analysis_id) REFERENCES screenplay_analyses(id) ON DELETE SET NULL,
				INDEX idx_user_id (user_id),
				INDEX idx_api_provider (api_provider),
				INDEX idx_created_at (created_at)
			)
		`);
		
		// Create user_usage_summary table for quick lookups
		await connection.execute(`
			CREATE TABLE IF NOT EXISTS user_usage_summary (
				user_id VARCHAR(255) PRIMARY KEY,
				
				-- Monthly Usage (current month)
				monthly_analyses_count INT DEFAULT 0,
				monthly_cost DECIMAL(10,4) DEFAULT 0,
				monthly_tokens INT DEFAULT 0,
				
				-- All-time Usage
				total_analyses_count INT DEFAULT 0,
				total_cost DECIMAL(10,4) DEFAULT 0,
				total_tokens INT DEFAULT 0,
				
				-- Last Activity
				last_analysis_at TIMESTAMP NULL,
				last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
				
				FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
			)
		`);
		
		// Create file_uploads table to track uploaded files
		await connection.execute(`
			CREATE TABLE IF NOT EXISTS file_uploads (
				id VARCHAR(255) PRIMARY KEY,
				user_id VARCHAR(255) NOT NULL,
				original_filename VARCHAR(500) NOT NULL,
				stored_filename VARCHAR(500) NOT NULL,
				file_path VARCHAR(1000) NOT NULL,
				file_size INT NOT NULL,
				mime_type VARCHAR(100),
				upload_status ENUM('uploading', 'completed', 'error') DEFAULT 'uploading',
				
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				
				FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
				INDEX idx_user_id (user_id),
				INDEX idx_upload_status (upload_status)
			)
		`);
		
		console.log('✅ All analysis tables created successfully');
		
		// Create some indexes for better performance
		try {
			await connection.execute(`
				CREATE INDEX idx_screenplay_analyses_user_created 
				ON screenplay_analyses(user_id, created_at DESC)
			`);
		} catch (e) {
			// Index might already exist
		}
		
		try {
			await connection.execute(`
				CREATE INDEX idx_api_usage_user_date 
				ON api_usage_tracking(user_id, created_at DESC)
			`);
		} catch (e) {
			// Index might already exist
		}
		
		console.log('✅ Performance indexes created');
		
	} catch (error) {
		console.error('Database table creation error:', error);
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
		console.log('Creating screenplay analysis tables...');
		await createAnalysisTables();
		console.log('✅ Database setup completed successfully!');
		process.exit(0);
	} catch (error) {
		console.error('❌ Database setup failed:', error);
		process.exit(1);
	}
}

main();
