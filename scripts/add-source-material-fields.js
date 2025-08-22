#!/usr/bin/env node

import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const { DB_HOST, DB_USER, DB_PASSWORD, DB_NAME } = process.env;

async function addSourceMaterialFields() {
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
		
		// Add source material analysis fields
		console.log('Adding source material analysis fields...');
		
		const alterQueries = [
			'ALTER TABLE screenplay_analyses ADD COLUMN source_has_material BOOLEAN DEFAULT FALSE',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_type VARCHAR(50)',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_title TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_author VARCHAR(255)',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_description TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_adaptation_notes TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_commercial_implications TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_legal_considerations TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_market_advantages JSON',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_potential_challenges JSON',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_confidence_score DECIMAL(3,2) DEFAULT 0.0',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_raw_detection_text TEXT',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_processing_time DECIMAL(8,2) DEFAULT 0.0',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_cost DECIMAL(8,4) DEFAULT 0.0',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_success BOOLEAN DEFAULT FALSE',
			'ALTER TABLE screenplay_analyses ADD COLUMN source_error_message TEXT'
		];
		
		for (const query of alterQueries) {
			try {
				await connection.execute(query);
				console.log(`✅ Executed: ${query.substring(0, 60)}...`);
			} catch (error) {
				if (error.code === 'ER_DUP_FIELDNAME') {
					console.log(`⚠️  Field already exists: ${query.substring(0, 60)}...`);
				} else {
					console.error(`❌ Error executing: ${query}`);
					console.error(error.message);
				}
			}
		}
		
		// Add indexes
		console.log('Adding indexes...');
		const indexQueries = [
			'CREATE INDEX idx_screenplay_analyses_source_has_material ON screenplay_analyses(source_has_material)',
			'CREATE INDEX idx_screenplay_analyses_source_type ON screenplay_analyses(source_type)',
			'CREATE INDEX idx_screenplay_analyses_source_success ON screenplay_analyses(source_success)'
		];
		
		for (const query of indexQueries) {
			try {
				await connection.execute(query);
				console.log(`✅ Created index: ${query.substring(0, 60)}...`);
			} catch (error) {
				if (error.code === 'ER_DUP_KEYNAME') {
					console.log(`⚠️  Index already exists: ${query.substring(0, 60)}...`);
				} else {
					console.error(`❌ Error creating index: ${query}`);
					console.error(error.message);
				}
			}
		}
		
		console.log('✅ Source material analysis fields added successfully');
		
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
		console.log('Adding source material analysis fields to database...');
		await addSourceMaterialFields();
		console.log('Migration completed successfully');
		process.exit(0);
	} catch (error) {
		console.error('Migration failed:', error);
		process.exit(1);
	}
}

main();
