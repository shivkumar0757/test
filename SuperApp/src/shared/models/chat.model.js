/**
 * Chat Models
 * 
 * Schema definitions for chat sessions and messages in MongoDB
 */

const mongoose = require('mongoose');

// Message Schema (embedded in ChatSession)
const messageSchema = new mongoose.Schema({
  role: {
    type: String,
    enum: ['user', 'assistant', 'system'],
    required: true
  },
  content: {
    type: String,
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

// Chat Session Schema
const chatSessionSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  title: {
    type: String,
    default: 'New Conversation'
  },
  modelId: {
    type: String,
    required: true
  },
  messages: [messageSchema],
  metadata: {
    tokenCount: {
      type: Number,
      default: 0
    },
    modelVersion: String,
    systemPrompt: String
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

// Virtual for message count
chatSessionSchema.virtual('messageCount').get(function() {
  return this.messages.length;
});

// Method to add a message to the chat session
chatSessionSchema.methods.addMessage = async function(role, content) {
  this.messages.push({ role, content });
  this.updatedAt = Date.now();
  await this.save();
  return this;
};

// Method to update title based on content
chatSessionSchema.methods.updateTitle = async function() {
  // If no title set and we have at least 1 user message, set title based on first message
  if (this.title === 'New Conversation' && this.messages.length > 0) {
    const firstUserMessage = this.messages.find(m => m.role === 'user');
    if (firstUserMessage) {
      // Set title to first 30 chars of first user message
      this.title = firstUserMessage.content.substring(0, 30);
      if (firstUserMessage.content.length > 30) {
        this.title += '...';
      }
      await this.save();
    }
  }
  return this;
};

// Method to summarize context for large conversations
chatSessionSchema.methods.summarizeContext = function(maxMessages = 10) {
  if (this.messages.length <= maxMessages) {
    return this.messages;
  }
  
  // Keep first system message (if any), recent messages, and create a summary
  const systemMessages = this.messages.filter(m => m.role === 'system');
  const recentMessages = this.messages.slice(-maxMessages);
  
  return [
    ...(systemMessages.length > 0 ? [systemMessages[0]] : []),
    {
      role: 'system',
      content: `This conversation has ${this.messages.length} messages. Earlier messages have been summarized.`
    },
    ...recentMessages
  ];
};

// Update timestamp on save
chatSessionSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Model Preferences Schema
const modelPreferencesSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    unique: true
  },
  defaultModel: {
    type: String,
    default: 'gemini-pro'
  },
  temperature: {
    type: Number,
    default: 0.7,
    min: 0,
    max: 2
  },
  maxTokens: {
    type: Number,
    default: 1024,
    min: 1,
    max: 8192
  },
  contextWindow: {
    type: Number,
    default: 10,
    min: 1, 
    max: 100
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

// Update timestamp on save
modelPreferencesSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

const ChatSession = mongoose.model('ChatSession', chatSessionSchema);
const ModelPreferences = mongoose.model('ModelPreferences', modelPreferencesSchema);

module.exports = {
  ChatSession,
  ModelPreferences
}; 