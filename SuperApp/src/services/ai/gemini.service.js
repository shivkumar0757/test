/**
 * Gemini API Service
 * 
 * Service for interacting with Google's Gemini API
 */

const { GoogleGenerativeAI } = require('@google/generative-ai');
const ApiKey = require('../../shared/models/api-key.model');

class GeminiService {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.modelName = 'gemini-pro';
    this.model = this.genAI.getGenerativeModel({ model: this.modelName });
  }

  /**
   * Initialize the service with user's API key
   * @param {string} userId - User ID to fetch API key for
   * @returns {GeminiService} - Initialized service
   */
  static async initialize(userId) {
    try {
      // Find user's Google API key
      const apiKeyDoc = await ApiKey.findOne({ 
        userId,
        service: 'google',
        isActive: true
      }).select('+key');

      if (!apiKeyDoc) {
        throw new Error('No active Google API key found for user');
      }

      // Get the decrypted key
      const decryptedKey = apiKeyDoc.getDecryptedKey();
      if (!decryptedKey) {
        throw new Error('Failed to decrypt API key');
      }

      return new GeminiService(decryptedKey);
    } catch (error) {
      console.error('Failed to initialize Gemini service:', error);
      throw error;
    }
  }

  /**
   * Get a completion from Gemini
   * @param {string} prompt - The prompt to send to Gemini
   * @param {Object} options - Additional options
   * @returns {Object} - Completion response
   */
  async getCompletion(prompt, options = {}) {
    try {
      const startTime = Date.now();
      
      // Set default options
      const {
        temperature = 0.7,
        topK = 40,
        topP = 0.95,
        maxOutputTokens = 1024,
        safetySettings = []
      } = options;

      // Generate content
      const result = await this.model.generateContent({
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
        generationConfig: {
          temperature,
          topK,
          topP,
          maxOutputTokens,
        },
        safetySettings
      });

      const response = result.response;
      const text = response.text();
      
      // Calculate API usage metrics
      const endTime = Date.now();
      const latency = endTime - startTime;
      
      // Return formatted response
      return {
        text,
        usage: {
          promptTokens: 0, // Gemini API doesn't provide token counts yet
          completionTokens: 0,
          totalTokens: 0,
          latencyMs: latency
        },
        model: this.modelName,
        finishReason: null // Gemini API doesn't provide finish reason yet
      };
    } catch (error) {
      console.error('Gemini API error:', error);
      throw error;
    }
  }

  /**
   * Get a chat completion from Gemini
   * @param {Array} messages - Array of message objects {role, content}
   * @param {Object} options - Additional options
   * @returns {Object} - Chat completion response
   */
  async getChatCompletion(messages, options = {}) {
    try {
      const startTime = Date.now();
      
      // Set default options
      const {
        temperature = 0.7,
        topK = 40,
        topP = 0.95,
        maxOutputTokens = 1024,
        safetySettings = []
      } = options;

      // Create a chat session
      const chat = this.model.startChat({
        generationConfig: {
          temperature,
          topK,
          topP,
          maxOutputTokens,
        },
        safetySettings,
        history: messages.map(msg => ({
          role: msg.role === 'assistant' ? 'model' : msg.role,
          parts: [{ text: msg.content }]
        }))
      });

      // Get response to the last message (which should already be in history)
      const result = await chat.sendMessage("");
      const text = result.response.text();
      
      // Calculate API usage metrics
      const endTime = Date.now();
      const latency = endTime - startTime;
      
      // Return formatted response
      return {
        text,
        usage: {
          promptTokens: 0, // Gemini API doesn't provide token counts yet
          completionTokens: 0,
          totalTokens: 0,
          latencyMs: latency
        },
        model: this.modelName,
        finishReason: null // Gemini API doesn't provide finish reason yet
      };
    } catch (error) {
      console.error('Gemini Chat API error:', error);
      throw error;
    }
  }

  /**
   * Generate LinkedIn post variations
   * @param {Object} params - Parameters for generating posts
   * @returns {Array} - Array of post variations
   */
  async generateLinkedInPosts(params) {
    const { topic, tone, length, keywords, audience } = params;
    
    // Construct a prompt for LinkedIn post generation
    const prompt = `
Generate ${tone} LinkedIn posts about ${topic} in ${length} length format.
${keywords ? `Include these keywords if relevant: ${keywords.join(', ')}.` : ''}
${audience ? `Target audience: ${audience}.` : ''}

Create 3 variations of LinkedIn posts, each with a different style and approach.
Each post should be engaging, professional, and optimized for LinkedIn's algorithm.
Include relevant hashtags at the end of each post.

Format the response as three distinct posts labeled as "Variation 1:", "Variation 2:", and "Variation 3:".
    `;

    // Get completion from Gemini
    const completion = await this.getCompletion(prompt, {
      temperature: 0.8, // Higher temperature for creativity
      maxOutputTokens: 2048 // More tokens for multiple variations
    });

    // Parse completion into variations
    const text = completion.text;
    const variations = [];
    
    // Simple parsing by "Variation" keyword
    const regex = /Variation \d+:([\s\S]*?)(?=Variation \d+:|$)/g;
    let match;
    
    while ((match = regex.exec(text)) !== null) {
      if (match[1].trim()) {
        variations.push({
          content: match[1].trim(),
          aiEngagementPrediction: this._predictEngagement() // Mock engagement prediction
        });
      }
    }
    
    return variations;
  }
  
  /**
   * Analyze LinkedIn profile and suggest optimizations
   * @param {Object} profile - LinkedIn profile
   * @param {string} targetRole - Target role to optimize for
   * @returns {Object} - Profile optimization suggestions
   */
  async optimizeLinkedInProfile(profile, targetRole) {
    // Construct a prompt for profile optimization
    const prompt = `
Analyze this LinkedIn profile and provide optimization suggestions for the target role of ${targetRole}.

Current LinkedIn Profile:
- Headline: ${profile.headline || 'Not provided'}
- Summary: ${profile.summary || 'Not provided'}
- Experience: ${profile.experience ? JSON.stringify(profile.experience) : 'Not provided'}
- Skills: ${profile.skills ? profile.skills.join(', ') : 'Not provided'}

Provide specific suggestions to improve:
1. The headline (make it more attention-grabbing and specific)
2. The summary (highlight relevant achievements and skills for ${targetRole})
3. Skills to add, remove, or prioritize for ${targetRole}

Format the response as a JSON object with these sections: headline, summary, skills.
The skills section should include three arrays: add, remove, prioritize.
For each suggestion, include both the suggested change and an explanation for why.
    `;

    // Get completion from Gemini
    const completion = await this.getCompletion(prompt, {
      temperature: 0.3, // Lower temperature for more focused responses
      maxOutputTokens: 2048
    });
    
    // Parse response - in a real implementation, we would parse proper JSON
    // For now, return a mock structured response
    return {
      headline: {
        current: profile.headline || 'Not provided',
        suggestion: `Senior ${targetRole} specializing in AI-driven applications`,
        explanation: `This headline directly mentions your seniority level and specialization, making it more targeted for ${targetRole} roles.`
      },
      summary: {
        current: profile.summary || 'Not provided',
        suggestion: `Results-driven professional with extensive experience in ${targetRole} roles. Specializing in AI applications and innovative solutions.`,
        explanation: `The revised summary emphasizes your experience with roles relevant to ${targetRole} and highlights key technologies.`
      },
      skills: {
        add: ['Machine Learning', 'TensorFlow', 'API Design', 'System Architecture'],
        remove: [],
        prioritize: ['AI', 'Machine Learning', 'Cloud Architecture']
      }
    };
  }
  
  /**
   * Mock method to generate engagement predictions
   * @private
   * @returns {Object} - Engagement prediction object
   */
  _predictEngagement() {
    const levels = ['low', 'medium', 'high'];
    return {
      likes: levels[Math.floor(Math.random() * 3)],
      comments: levels[Math.floor(Math.random() * 3)],
      shares: levels[Math.floor(Math.random() * 3)]
    };
  }
}

module.exports = GeminiService; 