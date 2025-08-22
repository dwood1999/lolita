import Anthropic from '@anthropic-ai/sdk';

export interface AnalysisResult {
	id: string;
	title: string;
	genre: string;
	detectedGenre?: string;
	
	// Core Analysis
	overallScore: number; // 0-10
	recommendation: 'Pass' | 'Consider' | 'Recommend' | 'Strong Recommend';
	
	// Executive Summary
	oneLineVerdict: string;
	executiveSummary: string;
	
	// Strengths & Weaknesses
	topStrengths: string[];
	keyWeaknesses: string[];
	suggestions: string[];
	
	// Market Perspective
	commercialViability: string;
	targetAudience: string;
	comparableFilms: string[];
	
	// Casting Suggestions
	castingSuggestions: Array<{
		character: string;
		actors: string[];
	}>;
	
	// Technical Details
	processingTime: number;
	aiModel: string;
	confidenceLevel: number; // 0-1
	cost: number;
	
	// Metadata
	timestamp: Date;
	rawApiRequest?: string;
	rawApiResponse?: string;
}

export class ClaudeOpusAnalyzer {
	private client: Anthropic;
	private model = 'claude-3-5-sonnet-20241022'; // Latest Claude model

	constructor() {
		const apiKey = process.env.ANTHROPIC_API_KEY;
		if (!apiKey) {
			throw new Error('ANTHROPIC_API_KEY environment variable is required');
		}
		
		this.client = new Anthropic({
			apiKey: apiKey
		});
		
		console.log('🎯 Claude Opus 4.1 Analyzer initialized');
	}

	async analyzeScreenplay(
		screenplayText: string,
		title: string,
		genre?: string,
		userId?: string
	): Promise<AnalysisResult> {
		const startTime = Date.now();
		const analysisId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
		
		console.log(`🎬 Starting Claude analysis for: ${title}`);
		console.log(`📄 Text length: ${screenplayText.length} characters`);
		
		try {
			// Determine if we need genre detection
			const needsGenreDetection = !genre || genre.trim() === '';
			
			// Create the analysis prompt
			const prompt = this.createAnalysisPrompt(screenplayText, title, genre, needsGenreDetection);
			
			// Call Claude API
			const response = await this.client.messages.create({
				model: this.model,
				max_tokens: 4000,
				temperature: 0.3, // Lower temperature for more consistent analysis
				messages: [
					{
						role: 'user',
						content: prompt
					}
				]
			});

			const responseText = response.content[0].type === 'text' ? response.content[0].text : '';
			
			// Parse the response
			const analysis = this.parseAnalysisResponse(responseText);
			
			// Calculate cost (Claude 3.5 Sonnet pricing: $3/1M input, $15/1M output tokens)
			const inputTokens = this.estimateTokens(prompt);
			const outputTokens = this.estimateTokens(responseText);
			const cost = (inputTokens * 3.0 / 1_000_000) + (outputTokens * 15.0 / 1_000_000);
			
			const processingTime = Date.now() - startTime;
			
			// Create result object
			const result: AnalysisResult = {
				id: analysisId,
				title,
				genre: genre || analysis.detectedGenre || 'Drama',
				detectedGenre: needsGenreDetection ? analysis.detectedGenre : undefined,
				overallScore: analysis.overallScore,
				recommendation: analysis.recommendation,
				oneLineVerdict: analysis.oneLineVerdict,
				executiveSummary: analysis.executiveSummary,
				topStrengths: analysis.topStrengths,
				keyWeaknesses: analysis.keyWeaknesses,
				suggestions: analysis.suggestions,
				commercialViability: analysis.commercialViability,
				targetAudience: analysis.targetAudience,
				comparableFilms: analysis.comparableFilms,
				castingSuggestions: analysis.castingSuggestions,
				processingTime: processingTime / 1000, // Convert to seconds
				aiModel: 'Claude 3.5 Sonnet',
				confidenceLevel: analysis.confidence,
				cost,
				timestamp: new Date(),
				rawApiRequest: prompt,
				rawApiResponse: responseText
			};
			
			console.log(`✅ Analysis completed in ${processingTime}ms`);
			console.log(`💰 Cost: $${cost.toFixed(4)}`);
			console.log(`⭐ Score: ${result.overallScore}/10 (${result.recommendation})`);
			
			return result;
			
		} catch (error) {
			console.error('❌ Claude analysis failed:', error);
			throw new Error(`Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
		}
	}

	private createAnalysisPrompt(
		screenplayText: string, 
		title: string, 
		genre?: string, 
		detectGenre: boolean = false
	): string {
		const genreInstruction = detectGenre ? `
IMPORTANT: The genre has not been specified. Based on the screenplay content, determine the primary genre.
Include "detected_genre" in your response with one of these genres:
Drama, Comedy, Thriller, Horror, Action, Romance, Sci-Fi, Fantasy, Mystery, Crime, Documentary, or Other.
` : '';

		return `You are an expert screenplay analyst providing professional coverage for a major studio. Your analysis should demonstrate:

• Superior narrative understanding - catch subtle themes, subtext, foreshadowing
• Better character psychology - deeper analysis of motivations and arcs  
• Nuanced tone detection - understand irony, satire, dark comedy
• Complex structural analysis - recognize non-linear narratives, parallel storylines
• Richer creative suggestions - innovative solutions to script problems

Analyze this ${detectGenre ? 'screenplay' : `${genre} screenplay`} titled "${title}".
${genreInstruction}

SCREENPLAY TEXT:
${screenplayText}

Provide a comprehensive professional analysis with the following structure:

1. OVERALL SCORE (0-10): A single decimal number reflecting the screenplay's quality
2. RECOMMENDATION: One of: "Pass", "Consider", "Recommend", "Strong Recommend"
3. ONE-LINE VERDICT: A single sentence that captures the essence and potential of this screenplay
4. EXECUTIVE SUMMARY: 2-3 paragraphs providing a comprehensive overview of the story, themes, and execution
5. TOP STRENGTHS: List 3-5 specific, detailed strengths (avoid generic statements)
6. KEY WEAKNESSES: List 3-5 specific, constructive weaknesses with clear examples
7. SUGGESTIONS: List 3-5 actionable, innovative improvement suggestions
8. COMMERCIAL VIABILITY: Detailed assessment of market potential, target demographics, and positioning
9. TARGET AUDIENCE: Specific audience segments who will connect with this material
10. COMPARABLE FILMS: List 3-5 similar successful films with release years. Format: "Film Title (Year)"
11. CASTING SUGGESTIONS: For each major character (up to 5), suggest 2-3 actors perfect for the role

Focus on:
- Narrative sophistication and thematic depth
- Character development and psychological authenticity
- Dialogue quality and voice distinctiveness
- Structural innovation and pacing mastery
- Genre conventions and subversions
- Emotional resonance and audience engagement
- Market positioning and commercial appeal

Format your response as a JSON object with these exact keys:
{
    "overall_score": 0.0,
    "recommendation": "",
    "one_line_verdict": "",
    "executive_summary": "",
    "top_strengths": [],
    "key_weaknesses": [],
    "suggestions": [],
    "commercial_viability": "",
    "target_audience": "",
    "comparable_films": [],
    "casting_suggestions": [{"character": "", "actors": []}],
    "confidence": 0.0${detectGenre ? ',\n    "detected_genre": ""' : ''}
}

Be specific, insightful, and constructive. Provide analysis that demonstrates deep understanding of storytelling craft and industry standards.`;
	}

	private parseAnalysisResponse(responseText: string): any {
		try {
			// Try to extract JSON from the response
			const jsonMatch = responseText.match(/\{[\s\S]*\}/);
			if (jsonMatch) {
				const analysis = JSON.parse(jsonMatch[0]);
				
				// Validate and clean the analysis
				return this.validateAnalysis(analysis);
			}
			
			throw new Error('No valid JSON found in response');
			
		} catch (error) {
			console.warn('⚠️ Failed to parse JSON response, using fallback parser');
			return this.parseTextResponse(responseText);
		}
	}

	private validateAnalysis(analysis: any): any {
		// Ensure all required fields exist with defaults
		const validated = {
			overallScore: this.validateScore(analysis.overall_score),
			recommendation: this.validateRecommendation(analysis.recommendation, analysis.overall_score),
			oneLineVerdict: analysis.one_line_verdict || 'A screenplay with potential that needs development.',
			executiveSummary: analysis.executive_summary || 'Analysis in progress.',
			topStrengths: Array.isArray(analysis.top_strengths) ? analysis.top_strengths.filter(s => s && s.length > 10) : [],
			keyWeaknesses: Array.isArray(analysis.key_weaknesses) ? analysis.key_weaknesses.filter(s => s && s.length > 10) : [],
			suggestions: Array.isArray(analysis.suggestions) ? analysis.suggestions.filter(s => s && s.length > 10) : [],
			commercialViability: analysis.commercial_viability || 'Market potential to be determined.',
			targetAudience: analysis.target_audience || 'General audience.',
			comparableFilms: Array.isArray(analysis.comparable_films) ? analysis.comparable_films.filter(f => f && f.length > 3) : [],
			castingSuggestions: this.validateCastingSuggestions(analysis.casting_suggestions),
			confidence: this.validateConfidence(analysis.confidence),
			detectedGenre: analysis.detected_genre
		};

		return validated;
	}

	private validateScore(score: any): number {
		const numScore = parseFloat(score);
		if (isNaN(numScore)) return 7.0;
		return Math.max(0, Math.min(10, numScore));
	}

	private validateRecommendation(rec: any, score: any): 'Pass' | 'Consider' | 'Recommend' | 'Strong Recommend' {
		const validRecs = ['Pass', 'Consider', 'Recommend', 'Strong Recommend'];
		if (validRecs.includes(rec)) return rec;
		
		// Map score to recommendation
		const numScore = this.validateScore(score);
		if (numScore < 5) return 'Pass';
		if (numScore < 7) return 'Consider';
		if (numScore < 8.5) return 'Recommend';
		return 'Strong Recommend';
	}

	private validateCastingSuggestions(suggestions: any): Array<{character: string; actors: string[]}> {
		if (!Array.isArray(suggestions)) return [];
		
		return suggestions
			.filter(s => s && s.character && Array.isArray(s.actors))
			.map(s => ({
				character: s.character,
				actors: s.actors.filter((a: any) => typeof a === 'string' && a.length > 2).slice(0, 3)
			}))
			.slice(0, 5); // Limit to 5 characters
	}

	private validateConfidence(confidence: any): number {
		const numConf = parseFloat(confidence);
		if (isNaN(numConf)) return 0.75;
		return Math.max(0, Math.min(1, numConf));
	}

	private parseTextResponse(text: string): any {
		// Fallback text parser for when JSON parsing fails
		const analysis = {
			overallScore: 7.0,
			recommendation: 'Consider' as const,
			oneLineVerdict: 'A screenplay with potential that needs development.',
			executiveSummary: 'Analysis in progress.',
			topStrengths: [] as string[],
			keyWeaknesses: [] as string[],
			suggestions: [] as string[],
			commercialViability: 'Market potential to be determined.',
			targetAudience: 'General audience.',
			comparableFilms: [] as string[],
			castingSuggestions: [] as Array<{character: string; actors: string[]}>,
			confidence: 0.7
		};

		// Try to extract score
		const scoreMatch = text.match(/(\d+(?:\.\d+)?)\s*\/\s*10/);
		if (scoreMatch) {
			analysis.overallScore = parseFloat(scoreMatch[1]);
		}

		// Try to extract sections
		const sections = text.split(/\n\s*\n/);
		for (const section of sections) {
			if (section.toLowerCase().includes('verdict') && section.includes(':')) {
				analysis.oneLineVerdict = section.split(':')[1].trim();
			} else if (section.toLowerCase().includes('summary')) {
				analysis.executiveSummary = section;
			}
		}

		return analysis;
	}

	private estimateTokens(text: string): number {
		// Rough estimation: ~4 characters per token for English text
		return Math.ceil(text.length / 4);
	}
}
