/**
 * API Key Model
 * 
 * Schema definition for API keys in MongoDB
 */

const mongoose = require('mongoose');
const crypto = require('crypto');

const apiKeySchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  service: {
    type: String,
    required: true,
    enum: ['google', 'openai', 'linkedin', 'github', 'other'],
    default: 'other'
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  key: {
    type: String,
    required: true,
    select: false // Don't return actual key by default
  },
  // For displaying a masked version of the key (e.g., "sk-...ABCD")
  maskedKey: {
    type: String,
    required: true
  },
  quotaLimit: {
    type: Number,
    default: 100000 // Default quota limit (can be overridden)
  },
  quotaUsed: {
    type: Number,
    default: 0
  },
  quotaResetDate: {
    type: Date,
    default: () => new Date(new Date().setMonth(new Date().getMonth() + 1)) // Default to 1 month from now
  },
  isActive: {
    type: Boolean,
    default: true
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

// Virtual for quota remaining
apiKeySchema.virtual('quotaRemaining').get(function() {
  return Math.max(0, this.quotaLimit - this.quotaUsed);
});

// Virtual for quota percentage used
apiKeySchema.virtual('quotaPercentageUsed').get(function() {
  return this.quotaLimit > 0 ? Math.min(100, (this.quotaUsed / this.quotaLimit) * 100) : 100;
});

// Method to increment quota usage
apiKeySchema.methods.incrementUsage = async function(amount) {
  this.quotaUsed += amount;
  await this.save();
  return this;
};

// Method to reset quota
apiKeySchema.methods.resetQuota = async function() {
  this.quotaUsed = 0;
  this.quotaResetDate = new Date(new Date().setMonth(new Date().getMonth() + 1));
  await this.save();
  return this;
};

// Pre-save hook to encrypt API key
apiKeySchema.pre('save', function(next) {
  // Only encrypt the key if it's modified or new
  if (!this.isModified('key')) return next();
  
  try {
    // Create masked version for display (e.g., "sk-...ABCD")
    const lastFour = this.key.slice(-4);
    const prefix = this.key.substring(0, 5);
    this.maskedKey = `${prefix}...${lastFour}`;
    
    // Encrypt the key - in a real implementation, we'd use a more secure method
    // This is a simple demonstration using environment variable as encryption key
    const algorithm = 'aes-256-ctr';
    const secretKey = process.env.API_KEY_ENCRYPTION_SECRET || 'default-encryption-secret-key';
    const iv = crypto.randomBytes(16);
    
    const cipher = crypto.createCipheriv(algorithm, secretKey, iv);
    const encrypted = Buffer.concat([cipher.update(this.key), cipher.final()]);
    
    // Store encrypted key with IV
    this.key = `${iv.toString('hex')}:${encrypted.toString('hex')}`;
    
    next();
  } catch (error) {
    next(error);
  }
});

// Method to decrypt and return the actual API key
apiKeySchema.methods.getDecryptedKey = function() {
  try {
    // In a real implementation, we'd handle this more securely
    const algorithm = 'aes-256-ctr';
    const secretKey = process.env.API_KEY_ENCRYPTION_SECRET || 'default-encryption-secret-key';
    
    const [ivHex, encryptedHex] = this.key.split(':');
    const iv = Buffer.from(ivHex, 'hex');
    const encrypted = Buffer.from(encryptedHex, 'hex');
    
    const decipher = crypto.createDecipheriv(algorithm, secretKey, iv);
    const decrypted = Buffer.concat([decipher.update(encrypted), decipher.final()]);
    
    return decrypted.toString();
  } catch (error) {
    console.error('Error decrypting API key:', error);
    return null;
  }
};

// Update timestamp on save
apiKeySchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

const ApiKey = mongoose.model('ApiKey', apiKeySchema);

module.exports = ApiKey; 