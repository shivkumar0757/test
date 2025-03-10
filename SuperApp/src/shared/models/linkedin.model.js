/**
 * LinkedIn Models
 * 
 * Schema definitions for LinkedIn profiles and posts
 */

const mongoose = require('mongoose');

// Experience Schema (embedded in LinkedInProfile)
const experienceSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true
  },
  company: {
    type: String,
    required: true
  },
  location: String,
  startDate: {
    type: Date,
    required: true
  },
  endDate: Date, // null for current positions
  description: String,
  skills: [String]
});

// Education Schema (embedded in LinkedInProfile)
const educationSchema = new mongoose.Schema({
  school: {
    type: String,
    required: true
  },
  degree: String,
  fieldOfStudy: String,
  startDate: Date,
  endDate: Date,
  description: String
});

// Skill Schema (embedded in LinkedInProfile)
const skillSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  endorsements: {
    type: Number,
    default: 0
  }
});

// LinkedIn Profile Schema
const linkedInProfileSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  linkedinId: {
    type: String,
    required: true,
    unique: true
  },
  fullName: {
    type: String,
    required: true
  },
  headline: String,
  summary: String,
  profileUrl: String,
  location: String,
  industry: String,
  experience: [experienceSchema],
  education: [educationSchema],
  skills: [skillSchema],
  // Store the full profile data from LinkedIn API
  profileData: {
    type: Object,
    select: false // Don't return by default to save bandwidth
  },
  lastUpdated: {
    type: Date,
    default: Date.now
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// LinkedIn Post Schema
const linkedInPostSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  linkedinPostId: String, // Only present if the post has been published to LinkedIn
  content: {
    type: String,
    required: true
  },
  mediaUrls: [String],
  publishedAt: Date,
  isPublished: {
    type: Boolean,
    default: false
  },
  engagementData: {
    likes: {
      type: Number,
      default: 0
    },
    comments: {
      type: Number,
      default: 0
    },
    shares: {
      type: Number,
      default: 0
    },
    impressions: {
      type: Number,
      default: 0
    },
    clicks: {
      type: Number,
      default: 0
    }
  },
  // Content embedding for similarity search
  contentEmbedding: {
    type: Object, // Store vector embedding
    select: false // Don't return by default
  },
  aiGenerated: {
    type: Boolean,
    default: false
  },
  generationParams: {
    modelId: String,
    prompt: String,
    temperature: Number
  },
  // Score given by AI for predicted engagement
  aiEngagementPrediction: {
    likes: {
      type: String,
      enum: ['low', 'medium', 'high']
    },
    comments: {
      type: String,
      enum: ['low', 'medium', 'high']
    },
    shares: {
      type: String,
      enum: ['low', 'medium', 'high']
    }
  },
  tags: [String],
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Method to generate post variations using AI
linkedInPostSchema.statics.generateVariations = async function(userId, topic, tone, length, count = 3) {
  // This would be implemented with Gemini API in production
  // For now, return mock variations
  return [
    {
      content: `Here's a professional post about ${topic} (${length} version with ${tone} tone).`,
      aiEngagementPrediction: {
        likes: 'high',
        comments: 'medium',
        shares: 'medium'
      }
    },
    {
      content: `Alternative version discussing ${topic} (${length} format, ${tone} style).`,
      aiEngagementPrediction: {
        likes: 'medium',
        comments: 'high',
        shares: 'low'
      }
    },
    {
      content: `Third variation exploring ${topic} (${length} content with ${tone} approach).`,
      aiEngagementPrediction: {
        likes: 'medium',
        comments: 'medium',
        shares: 'high'
      }
    }
  ];
};

// Method to analyze post for SEO and engagement potential
linkedInPostSchema.methods.analyzeContent = async function() {
  // This would be implemented with AI in production
  // For now, return mock analysis
  return {
    engagementScore: 85,
    seoScore: 78,
    readability: {
      score: 72,
      level: 'Professional',
      suggestions: [
        'Consider breaking up the second paragraph for improved readability',
        'Add one more relevant hashtag to increase discoverability'
      ]
    },
    sentiment: {
      overall: 'positive',
      strength: 'moderate'
    },
    keywords: {
      present: ['AI', 'machine learning', 'recommendations'],
      missing: ['data', 'algorithm', 'improvement'],
      trending: ['AI ethics', 'responsible AI', 'ML ops']
    },
    improvementSuggestions: [
      'Add a call to action at the end of your post',
      'Include a specific achievement or metric for credibility',
      'Consider adding an industry-specific hashtag for better targeting'
    ]
  };
};

// Update timestamp on save
linkedInProfileSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

linkedInPostSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

const LinkedInProfile = mongoose.model('LinkedInProfile', linkedInProfileSchema);
const LinkedInPost = mongoose.model('LinkedInPost', linkedInPostSchema);

module.exports = {
  LinkedInProfile,
  LinkedInPost
}; 