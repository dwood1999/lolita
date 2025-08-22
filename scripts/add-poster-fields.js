#!/usr/bin/env node

import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const { DB_HOST, DB_USER, DB_PASSWORD, DB_NAME } = process.env;

async function addPosterFields() {
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
		
		// Add poster collection fields
		console.log('Adding poster collection fields...');
		
		const alterQueries = [
			'ALTER TABLE screenplay_analyses ADD COLUMN poster_collection_title TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN poster_collection_genre TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN poster_total_cost DECIMAL(8,4) DEFAULT 0.0',
			'ALTER TABLE screenplay_analyses ADD COLUMN poster_total_time DECIMAL(8,2) DEFAULT 0.0',
			'ALTER TABLE screenplay_analyses ADD COLUMN poster_success_count INTEGER DEFAULT 0',
			'ALTER TABLE screenplay_analyses ADD COLUMN poster_best_url TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN poster_best_source TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN poster_variations_json TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN flux_poster_url TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN flux_poster_prompt TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN flux_poster_cost DECIMAL(8,4) DEFAULT 0.0',
			'ALTER TABLE screenplay_analyses ADD COLUMN flux_poster_success BOOLEAN DEFAULT FALSE',
			'ALTER TABLE screenplay_analyses ADD COLUMN flux_poster_error TEXT'
		];
		
		for (const query of alterQueries) {
			try {
				await connection.execute(query);
				console.log(`✅ Executed: ${query.substring(0, 50)}...`);
			} catch (error) {
				if (error.code === 'ER_DUP_FIELDNAME') {
					console.log(`⚠️  Field already exists: ${query.substring(0, 50)}...`);
				} else {
					console.error(`❌ Error executing: ${query}`);
					console.error(error.message);
				}
			}
		}
		
		// Add indexes
		console.log('Adding indexes...');
		const indexQueries = [
			'CREATE INDEX idx_screenplay_analyses_poster_success ON screenplay_analyses(poster_success_count)',
			'CREATE INDEX idx_screenplay_analyses_poster_source ON screenplay_analyses(poster_best_source)',
			'CREATE INDEX idx_screenplay_analyses_flux_success ON screenplay_analyses(flux_poster_success)'
		];
		
		for (const query of indexQueries) {
			try {
				await connection.execute(query);
				console.log(`✅ Created index: ${query.substring(0, 50)}...`);
			} catch (error) {
				if (error.code === 'ER_DUP_KEYNAME') {
					console.log(`⚠️  Index already exists: ${query.substring(0, 50)}...`);
				} else {
					console.error(`❌ Error creating index: ${query}`);
					console.error(error.message);
				}
			}
		}
		
		console.log('✅ Poster collection fields added successfully');
		
	} catch (error) {
		console.error('❌ Database migration error:', error);
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
		console.log('Adding poster collection fields to database...');
		await addPosterFields();
		console.log('Migration completed successfully');
		process.exit(0);
	} catch (error) {
		console.error('Migration failed:', error);
		process.exit(1);
	}
}

main();
