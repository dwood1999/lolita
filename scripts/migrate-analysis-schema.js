#!/usr/bin/env node

/**
 * Migration script to add new analysis fields to screenplay_analyses table
 */

import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

async function migrateSchema() {
    console.log('🔄 Starting schema migration for enhanced analysis fields...');
    
    let connection;
    
    try {
        // Create database connection
        connection = await mysql.createConnection({
            host: process.env.DB_HOST || 'localhost',
            user: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD,
            database: process.env.DB_NAME || 'lolita',
            port: parseInt(process.env.DB_PORT || '3306')
        });
        
        console.log('✅ Database connection established');
        
        // Check if new columns exist
        const [columns] = await connection.execute(`
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = 'screenplay_analyses'
        `, [process.env.DB_NAME || 'lolita']);
        
        const existingColumns = columns.map(row => row.COLUMN_NAME);
        console.log('📋 Existing columns:', existingColumns.length);
        
        // Define new columns to add
        const newColumns = [
            { name: 'structural_analysis', type: 'TEXT' },
            { name: 'character_analysis', type: 'TEXT' },
            { name: 'thematic_depth', type: 'TEXT' },
            { name: 'craft_evaluation', type: 'TEXT' },
            { name: 'genre_mastery', type: 'TEXT' },
            { name: 'improvement_strategies', type: 'JSON' },
            { name: 'casting_vision', type: 'JSON' },
            { name: 'grok_confidence', type: 'DECIMAL(3,2)' },
            { name: 'grok_cultural_analysis', type: 'JSON' },
            { name: 'grok_brutal_honesty', type: 'JSON' },
            { name: 'grok_controversy_analysis', type: 'JSON' },
            { name: 'grok_movie_poster_url', type: 'TEXT' },
            { name: 'grok_poster_prompt', type: 'TEXT' },
            { name: 'grok_raw_response', type: 'LONGTEXT' },
            // Budget fields
            { name: 'user_proposed_budget', type: 'DECIMAL(12,2)' },
            { name: 'budget_currency', type: "VARCHAR(10) DEFAULT 'USD'" },
            { name: 'budget_category', type: 'VARCHAR(20)' },
            { name: 'ai_budget_min', type: 'DECIMAL(12,2)' },
            { name: 'ai_budget_optimal', type: 'DECIMAL(12,2)' },
            { name: 'ai_budget_max', type: 'DECIMAL(12,2)' },
            { name: 'budget_notes', type: 'JSON' }
        ];
        
        // Add missing columns
        let addedColumns = 0;
        for (const column of newColumns) {
            if (!existingColumns.includes(column.name)) {
                console.log(`➕ Adding column: ${column.name}`);
                await connection.execute(`
                    ALTER TABLE screenplay_analyses 
                    ADD COLUMN ${column.name} ${column.type}
                `);
                addedColumns++;
            } else {
                console.log(`✅ Column already exists: ${column.name}`);
            }
        }
        
        if (addedColumns > 0) {
            console.log(`🎉 Migration completed! Added ${addedColumns} new columns.`);
        } else {
            console.log('✅ Schema is already up to date.');
        }
        
    } catch (error) {
        console.error('❌ Migration failed:', error);
        process.exit(1);
    } finally {
        if (connection) {
            await connection.end();
            console.log('🔌 Database connection closed');
        }
    }
}

// Run migration
migrateSchema();
