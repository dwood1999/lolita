import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';
import { executeQuery } from '$lib/server/db';

const PYTHON_SERVICE_URL = env.PYTHON_SERVICE_URL || 'http://127.0.0.1:8001';

// Simple in-memory cache for public analyses
const publicAnalysisCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 10 * 60 * 1000; // 10 minutes for public analyses

export const GET: RequestHandler = async ({ params }) => {
	try {
		const { token } = params;

		if (!token) {
			return json({ error: 'Share token is required' }, { status: 400 });
		}

		console.log(`🌐 Getting public analysis with token: ${token.substring(0, 8)}...`);

		// Check cache first
		const cached = publicAnalysisCache.get(token);
		if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
			console.log(`🚀 Cache hit for public analysis: ${token.substring(0, 8)}...`);
			return json(cached.data, {
				headers: {
					'Cache-Control': 'public, max-age=600' // 10 minutes
				}
			});
		}

		// Get analysis ID from database using the public share token
		const tokenResults = await executeQuery(`
			SELECT id, title, is_public 
			FROM screenplay_analyses 
			WHERE public_share_token = ? AND is_public = TRUE
		`, [token]) as any[];

		if (tokenResults.length === 0) {
			return json({ error: 'Analysis not found or not publicly shared' }, { status: 404 });
		}

		const analysisId = tokenResults[0].id;
		const title = tokenResults[0].title;

		// Try to get analysis from Python service first, fallback to database
		let result: any = null;
		
		try {
			const response = await fetch(`${PYTHON_SERVICE_URL}/analysis/${analysisId}`);
			
			if (response.ok) {
				result = await response.json();
				console.log(`✅ Got analysis from Python service: ${analysisId}`);
			} else {
				throw new Error(`Python service returned ${response.status}`);
			}
		} catch (pythonError) {
			console.warn(`⚠️ Python service unavailable, fetching from database: ${pythonError}`);
			
			// Fallback: Get analysis directly from database
			const dbResults = await executeQuery(`
				SELECT * FROM screenplay_analyses WHERE id = ? AND is_public = TRUE
			`, [analysisId]) as any[];
			
			if (dbResults.length === 0) {
				return json({ error: 'Analysis not found' }, { status: 404 });
			}
			
			const dbAnalysis = dbResults[0];
			
			// Format the database result to match the expected structure
			result = {
				status: 'completed',
				result: {
					title: dbAnalysis.title,
					genre: dbAnalysis.genre || dbAnalysis.detected_genre,
					overall_score: dbAnalysis.overall_score,
					recommendation: dbAnalysis.recommendation,
					one_line_verdict: dbAnalysis.one_line_verdict,
					executive_summary: dbAnalysis.executive_summary,
					logline: dbAnalysis.logline,
					top_strengths: dbAnalysis.top_strengths,
					key_weaknesses: dbAnalysis.key_weaknesses,
					suggestions: dbAnalysis.suggestions,
					commercial_viability: dbAnalysis.commercial_viability,
					target_audience: dbAnalysis.target_audience,
					comparable_films: dbAnalysis.comparable_films,
					character_analysis: dbAnalysis.character_analysis,
					structural_analysis: dbAnalysis.structural_analysis,
					thematic_depth: dbAnalysis.thematic_depth,
					craft_evaluation: dbAnalysis.craft_evaluation,
					improvement_strategies: dbAnalysis.improvement_strategies,
					genre_mastery: dbAnalysis.genre_mastery,
					director_recommendation: dbAnalysis.director_recommendation,
					perplexity_market_trends: dbAnalysis.perplexity_market_trends,
					perplexity_competitive_analysis: dbAnalysis.perplexity_competitive_analysis,
					perplexity_audience_demographics: dbAnalysis.perplexity_audience_demographics,
					perplexity_distribution_strategy: dbAnalysis.perplexity_distribution_strategy,
					perplexity_industry_reports: dbAnalysis.perplexity_industry_reports,
					perplexity_financial_intelligence: dbAnalysis.perplexity_financial_intelligence,
					perplexity_talent_intelligence: dbAnalysis.perplexity_talent_intelligence,
					casting_suggestions: dbAnalysis.casting_suggestions,
					// DeepSeek Financial Analysis
					deepseek_financial_score: dbAnalysis.deepseek_financial_score,
					deepseek_confidence: dbAnalysis.deepseek_confidence,
					deepseek_recommendation: dbAnalysis.deepseek_recommendation,
					deepseek_budget_optimization: dbAnalysis.deepseek_budget_optimization,
					deepseek_roi_analysis: dbAnalysis.deepseek_roi_analysis,
					deepseek_risk_assessment: dbAnalysis.deepseek_risk_assessment,
					deepseek_platform_analysis: dbAnalysis.deepseek_platform_analysis,
					// GPT-5 Analysis
					gpt5_score: dbAnalysis.gpt5_score,
					gpt5_recommendation: dbAnalysis.gpt5_recommendation,
					gpt5_executive_assessment: dbAnalysis.gpt5_executive_assessment,
					// Genre Analysis
					genre: dbAnalysis.genre,
					detected_genre: dbAnalysis.detected_genre,
					subgenre: dbAnalysis.subgenre,
					genre_mastery: dbAnalysis.genre_mastery,
					// Improvement Strategies
					improvement_strategies: dbAnalysis.improvement_strategies
				}
			};
			
			console.log(`✅ Got analysis from database fallback: ${analysisId}`);
		}

		// Enhance with database metadata for public view
		try {
			const dbResults = await executeQuery(`
				SELECT created_at, updated_at, shared_at, title, genre
				FROM screenplay_analyses 
				WHERE id = ? AND is_public = TRUE
			`, [analysisId]) as any[];
			
			if (dbResults.length > 0) {
				result.created_at = dbResults[0].created_at;
				result.updated_at = dbResults[0].updated_at;
				result.shared_at = dbResults[0].shared_at;
				result.is_public = true;
				result.public_view = true; // Flag to indicate this is a public view
			}
		} catch (dbError) {
			console.warn('Could not fetch database metadata for public analysis:', dbError);
		}

		// Cache the result
		if (result.status === 'completed') {
			publicAnalysisCache.set(token, {
				data: result,
				timestamp: Date.now()
			});
			
			// Clean up old cache entries
			if (publicAnalysisCache.size > 50) {
				const oldestKey = publicAnalysisCache.keys().next().value;
				publicAnalysisCache.delete(oldestKey);
			}
		}

		return json(result, {
			headers: {
				'Cache-Control': 'public, max-age=600' // 10 minutes
			}
		});

	} catch (error) {
		console.error('❌ Get public analysis API error:', error);
		return json({ 
			error: 'Internal server error', 
			detail: error instanceof Error ? error.message : 'Unknown error' 
		}, { status: 500 });
	}
};
