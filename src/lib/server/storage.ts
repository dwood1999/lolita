import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

const UPLOAD_DIR = path.join(process.cwd(), 'uploads', 'screenplays');

// Ensure upload directory exists
export async function ensureUploadDir() {
	if (!existsSync(UPLOAD_DIR)) {
		await mkdir(UPLOAD_DIR, { recursive: true });
	}
}

// Save uploaded file and return file info
export async function saveUploadedFile(file: File, userId: string): Promise<{
	filename: string;
	originalName: string;
	size: number;
	path: string;
}> {
	await ensureUploadDir();
	
	// Generate unique filename
	const fileExtension = path.extname(file.name);
	const filename = `${userId}_${uuidv4()}${fileExtension}`;
	const filePath = path.join(UPLOAD_DIR, filename);
	
	// Convert File to Buffer
	const arrayBuffer = await file.arrayBuffer();
	const buffer = Buffer.from(arrayBuffer);
	
	// Save file
	await writeFile(filePath, buffer);
	
	return {
		filename,
		originalName: file.name,
		size: file.size,
		path: filePath
	};
}

// Get file path for reading
export function getFilePath(filename: string): string {
	return path.join(UPLOAD_DIR, filename);
}

// Validate file type
export function isValidFileType(filename: string): boolean {
	const allowedExtensions = ['.pdf', '.txt', '.doc', '.docx', '.fountain', '.fdx'];
	const extension = path.extname(filename).toLowerCase();
	return allowedExtensions.includes(extension);
}

// Validate file size (10MB limit)
export function isValidFileSize(size: number): boolean {
	const maxSize = 10 * 1024 * 1024; // 10MB
	return size <= maxSize;
}
