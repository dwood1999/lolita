import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { executeQuery } from '$lib/server/db';
import { saveUploadedFile, isValidFileType, isValidFileSize } from '$lib/server/storage';
import { v4 as uuidv4 } from 'uuid';

export const POST: RequestHandler = async ({ request, locals }) => {
	try {
		// Check authentication
		if (!locals.user) {
			return json({ error: 'Not authenticated' }, { status: 401 });
		}

		const formData = await request.formData();
		const title = formData.get('title') as string;
		const file = formData.get('file') as File;

		// Validate input
		if (!title || !title.trim()) {
			return json({ error: 'Title is required' }, { status: 400 });
		}

		if (!file || file.size === 0) {
			return json({ error: 'File is required' }, { status: 400 });
		}

		// Validate file type
		if (!isValidFileType(file.name)) {
			return json({ 
				error: 'Invalid file type. Please upload PDF, TXT, DOC, DOCX, Fountain, or FDX files.' 
			}, { status: 400 });
		}

		// Validate file size
		if (!isValidFileSize(file.size)) {
			return json({ error: 'File size must be less than 10MB' }, { status: 400 });
		}

		// Save file to disk
		const fileInfo = await saveUploadedFile(file, locals.user.id);

		// Create screenplay record in database
		const screenplayId = uuidv4();
		await executeQuery(
			'INSERT INTO screenplays (id, user_id, title, filename, original_filename, file_size, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
			[screenplayId, locals.user.id, title.trim(), fileInfo.filename, fileInfo.originalName, fileInfo.size, 'draft']
		);

		return json({
			success: true,
			message: 'Screenplay uploaded successfully',
			screenplay: {
				id: screenplayId,
				title: title.trim(),
				filename: fileInfo.filename,
				originalName: fileInfo.originalName,
				size: fileInfo.size,
				status: 'draft'
			}
		});
	} catch (error) {
		console.error('Upload error:', error);
		return json({ error: 'Internal server error' }, { status: 500 });
	}
};
