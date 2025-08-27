import { marked } from 'marked';

/**
 * Parse markdown text to HTML
 * @param {string} text - The markdown text to parse
 * @returns {string} - The parsed HTML
 */
export function parseMarkdown(text) {
	if (!text) return '';
	
	// Configure marked options for security and formatting
	marked.setOptions({
		breaks: true, // Convert line breaks to <br>
		gfm: true, // Enable GitHub Flavored Markdown
		sanitize: false, // We trust our analysis content
		smartypants: true // Enable smart quotes and dashes
	});
	
	return marked.parse(text);
}

/**
 * Check if text contains markdown formatting
 * @param {string} text - The text to check
 * @returns {boolean} - True if text appears to contain markdown
 */
export function hasMarkdown(text) {
	if (!text) return false;
	
	// Check for common markdown patterns
	const markdownPatterns = [
		/\*\*.*?\*\*/, // Bold **text**
		/\*.*?\*/, // Italic *text*
		/^#{1,6}\s/, // Headers # ## ###
		/^-\s/, // Unordered lists
		/^\d+\.\s/, // Ordered lists
		/`.*?`/, // Inline code
		/```[\s\S]*?```/, // Code blocks
		/\[.*?\]\(.*?\)/, // Links
		/!\[.*?\]\(.*?\)/ // Images
	];
	
	return markdownPatterns.some(pattern => pattern.test(text));
}
