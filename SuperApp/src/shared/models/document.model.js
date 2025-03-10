/**
 * Document Models for RAG
 * 
 * Schema definitions for documents and chunks used in RAG system
 */

const mongoose = require('mongoose');

// Document Chunk Schema (embedded in Document)
const documentChunkSchema = new mongoose.Schema({
  content: {
    type: String,
    required: true
  },
  metadata: {
    startIdx: Number,
    endIdx: Number,
    pageNumber: Number,
    sectionTitle: String
  },
  vectorId: {
    type: String,
    description: 'ID of the vector in the vector database'
  },
  vectorDbProvider: {
    type: String,
    enum: ['pinecone', 'qdrant', 'chroma', 'pgvector', 'other'],
    default: 'pinecone'
  }
});

// Document Schema
const documentSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  title: {
    type: String,
    required: true,
    trim: true
  },
  content: {
    type: String,
    required: true
  },
  metadata: {
    source: String,
    author: String,
    tags: [String],
    createdAt: Date,
    fileType: String,
    fileSize: Number,
    language: {
      type: String,
      default: 'en'
    }
  },
  chunks: [documentChunkSchema],
  isProcessed: {
    type: Boolean,
    default: false
  },
  isPublic: {
    type: Boolean,
    default: false
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

// Virtual for chunk count
documentSchema.virtual('chunkCount').get(function() {
  return this.chunks.length;
});

// Method to process document into chunks
documentSchema.methods.processIntoChunks = async function(chunkSize = 1000, overlap = 200) {
  // Simple chunking strategy based on character count
  const text = this.content;
  const chunks = [];
  
  // Process content into overlapping chunks
  for (let i = 0; i < text.length; i += chunkSize - overlap) {
    const end = Math.min(i + chunkSize, text.length);
    chunks.push({
      content: text.slice(i, end),
      metadata: {
        startIdx: i,
        endIdx: end
      }
    });
    
    // If we've reached the end of the text, break
    if (end === text.length) break;
  }
  
  this.chunks = chunks;
  this.isProcessed = true;
  this.updatedAt = Date.now();
  
  await this.save();
  return this;
};

// Method to update vector IDs after embedding
documentSchema.methods.updateVectorIds = async function(vectorIds, provider = 'pinecone') {
  if (vectorIds.length !== this.chunks.length) {
    throw new Error('Vector IDs array length must match chunk count');
  }
  
  this.chunks.forEach((chunk, index) => {
    chunk.vectorId = vectorIds[index];
    chunk.vectorDbProvider = provider;
  });
  
  this.updatedAt = Date.now();
  await this.save();
  return this;
};

// Method to search within document (text-based)
documentSchema.methods.searchText = function(query) {
  // Simple case-insensitive search
  const regex = new RegExp(query, 'i');
  return this.chunks.filter(chunk => regex.test(chunk.content));
};

// Update timestamp on save
documentSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

const Document = mongoose.model('Document', documentSchema);

module.exports = Document; 