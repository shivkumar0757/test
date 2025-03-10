/**
 * SuperApp API Gateway Server
 * 
 * This is the main entry point for the API Gateway that routes requests
 * to various microservices based on the request path.
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const dotenv = require('dotenv');
const rateLimit = require('express-rate-limit');
const { connectDatabases } = require('../shared/config/database');

// Load environment variables
dotenv.config();

// Import route handlers (will create these later)
const authRoutes = require('./routes/auth');
const jobPrepRoutes = require('./routes/job-prep');
const chatbotRoutes = require('./routes/chatbot');
const ragRoutes = require('./routes/rag');
const resumeRoutes = require('./routes/resume');

// Create Express app
const app = express();

// Set up middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS
app.use(express.json()); // Parse JSON bodies
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded bodies
app.use(morgan('dev')); // Request logging

// Rate limiting
const apiLimiter = rateLimit({
  windowMs: process.env.RATE_LIMIT_WINDOW_MS || 15 * 60 * 1000, // Default: 15 minutes
  max: process.env.RATE_LIMIT_MAX_REQUESTS || 100, // Default: limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  message: 'Too many requests from this IP, please try again after 15 minutes'
});

// Apply rate limiting to all routes
app.use(apiLimiter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', version: process.env.npm_package_version });
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/job-prep', jobPrepRoutes);
app.use('/api/chat', chatbotRoutes);
app.use('/api/rag', ragRoutes);
app.use('/api/resume', resumeRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';
  
  res.status(statusCode).json({
    status: 'error',
    statusCode,
    message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// Handle 404 - Route not found
app.use((req, res) => {
  res.status(404).json({
    status: 'error',
    statusCode: 404,
    message: 'Route not found'
  });
});

// Connect to databases before starting server
const startServer = async () => {
  try {
    // Connect to MongoDB, PostgreSQL, and Redis
    await connectDatabases();
    
    // Start the server
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
      console.log(`SuperApp API Gateway running on port ${PORT}`);
      console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

// Handle unhandled promise rejections
process.on('unhandledRejection', (err) => {
  console.error('UNHANDLED REJECTION! 💥 Shutting down...');
  console.error(err.name, err.message);
  process.exit(1);
});

// Handle SIGTERM signals (e.g. from Heroku)
process.on('SIGTERM', () => {
  console.log('👋 SIGTERM RECEIVED. Shutting down gracefully');
  process.exit(0);
});

// Start the server
startServer();

// Export app for testing
module.exports = app; 