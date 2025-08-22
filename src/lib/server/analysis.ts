import { readFile } from 'fs/promises';
import { getFilePath } from './storage';

export interface AnalysisResult {
	id: string;
	screenplayId: string;
	summary: string;
	strengths: string[];
	weaknesses: string[];
	recommendations: string[];
	scores: {
		structure: number;
		character: number;
		dialogue: number;
		pacing: number;
		marketability: number;
		overall: number;
	};
	createdAt: string;
}

// Basic screenplay analysis (placeholder for AI integration)
export async function analyzeScreenplay(screenplayId: string, filename: string): Promise<AnalysisResult> {
	try {
		// Read the file content
		const filePath = getFilePath(filename);
		const content = await readFile(filePath, 'utf-8');
		
		// Basic analysis metrics
		const wordCount = content.split(/\s+/).length;
		const pageCount = Math.ceil(wordCount / 250); // Rough estimate
		const characterCount = content.length;
		
		// Mock analysis results (in real implementation, this would use AI)
		const analysis: AnalysisResult = {
			id: crypto.randomUUID(),
			screenplayId,
			summary: `This ${pageCount}-page screenplay contains approximately ${wordCount} words. The analysis reveals a ${getGenreGuess(content)} with ${getStructureAssessment(pageCount)}.`,
			strengths: [
				"Clear narrative structure",
				"Engaging opening sequence",
				"Well-defined protagonist",
				"Appropriate length for the genre"
			],
			weaknesses: [
				"Some dialogue could be more distinctive",
				"Pacing issues in the second act",
				"Supporting characters need more development",
				"Some scenes could be more visually dynamic"
			],
			recommendations: [
				"Strengthen character arcs for supporting roles",
				"Add more visual storytelling elements",
				"Tighten dialogue to improve pacing",
				"Consider adding more conflict in the middle section",
				"Review formatting for industry standards"
			],
			scores: {
				structure: Math.floor(Math.random() * 30) + 70, // 70-100
				character: Math.floor(Math.random() * 25) + 65, // 65-90
				dialogue: Math.floor(Math.random() * 25) + 70, // 70-95
				pacing: Math.floor(Math.random() * 30) + 60, // 60-90
				marketability: Math.floor(Math.random() * 35) + 55, // 55-90
				overall: 0 // Will be calculated
			},
			createdAt: new Date().toISOString()
		};
		
		// Calculate overall score
		const scores = analysis.scores;
		analysis.scores.overall = Math.round(
			(scores.structure + scores.character + scores.dialogue + scores.pacing + scores.marketability) / 5
		);
		
		return analysis;
	} catch (error) {
		console.error('Analysis error:', error);
		throw new Error('Failed to analyze screenplay');
	}
}

function getGenreGuess(content: string): string {
	const lowerContent = content.toLowerCase();
	
	if (lowerContent.includes('horror') || lowerContent.includes('scream') || lowerContent.includes('blood')) {
		return 'horror screenplay';
	} else if (lowerContent.includes('love') || lowerContent.includes('romance') || lowerContent.includes('wedding')) {
		return 'romantic screenplay';
	} else if (lowerContent.includes('action') || lowerContent.includes('fight') || lowerContent.includes('explosion')) {
		return 'action screenplay';
	} else if (lowerContent.includes('comedy') || lowerContent.includes('funny') || lowerContent.includes('laugh')) {
		return 'comedy screenplay';
	} else {
		return 'dramatic screenplay';
	}
}

function getStructureAssessment(pageCount: number): string {
	if (pageCount < 90) {
		return 'a concise structure that may benefit from additional development';
	} else if (pageCount > 120) {
		return 'an extended structure that might need tightening';
	} else {
		return 'a well-balanced three-act structure';
	}
}

// Format analysis for display
export function formatAnalysisForDisplay(analysis: AnalysisResult) {
	return {
		...analysis,
		formattedScores: {
			structure: `${analysis.scores.structure}/100`,
			character: `${analysis.scores.character}/100`,
			dialogue: `${analysis.scores.dialogue}/100`,
			pacing: `${analysis.scores.pacing}/100`,
			marketability: `${analysis.scores.marketability}/100`,
			overall: `${analysis.scores.overall}/100`
		},
		scoreColors: {
			structure: getScoreColor(analysis.scores.structure),
			character: getScoreColor(analysis.scores.character),
			dialogue: getScoreColor(analysis.scores.dialogue),
			pacing: getScoreColor(analysis.scores.pacing),
			marketability: getScoreColor(analysis.scores.marketability),
			overall: getScoreColor(analysis.scores.overall)
		}
	};
}

function getScoreColor(score: number): string {
	if (score >= 80) return 'text-green-600';
	if (score >= 70) return 'text-yellow-600';
	if (score >= 60) return 'text-orange-600';
	return 'text-red-600';
}
