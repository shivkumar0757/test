/**
 * Authentication Middleware
 * 
 * Middleware functions for handling authentication and authorization
 */

const jwt = require('jsonwebtoken');
const User = require('../../shared/models/user.model');

/**
 * Protect routes - Verifies JWT token and attaches user to request
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
exports.protect = async (req, res, next) => {
  try {
    let token;
    
    // Check if token exists in Authorization header
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
      token = req.headers.authorization.split(' ')[1];
    } 
    // Check if token exists in cookies (for browser-based clients)
    else if (req.cookies && req.cookies.token) {
      token = req.cookies.token;
    }
    
    // If no token found, return error
    if (!token) {
      return res.status(401).json({
        status: 'error',
        message: 'Not authorized to access this route'
      });
    }
    
    try {
      // Verify token
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      
      // Get user from database (excluding password)
      const user = await User.findById(decoded.id);
      
      // Check if user exists
      if (!user) {
        return res.status(401).json({
          status: 'error',
          message: 'User no longer exists'
        });
      }
      
      // Check if user is active
      if (!user.isActive) {
        return res.status(401).json({
          status: 'error',
          message: 'User account is deactivated'
        });
      }
      
      // Add user to request object
      req.user = user;
      next();
    } catch (error) {
      // If token verification fails
      return res.status(401).json({
        status: 'error',
        message: 'Token is invalid or expired'
      });
    }
  } catch (error) {
    next(error);
  }
};

/**
 * Restrict to certain roles
 * @param {...String} roles - Roles to restrict to
 * @returns {Function} - Express middleware function
 */
exports.restrictTo = (...roles) => {
  return (req, res, next) => {
    // Check if user has required role
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        status: 'error',
        message: 'You do not have permission to perform this action'
      });
    }
    
    next();
  };
};

/**
 * Rate limiting middleware
 * @param {Number} maxRequests - Maximum requests in time window
 * @param {Number} windowMs - Time window in milliseconds
 * @returns {Function} - Express middleware function
 */
exports.rateLimit = (maxRequests = 100, windowMs = 15 * 60 * 1000) => {
  const requestCounts = new Map();
  const requestTimestamps = new Map();
  
  return (req, res, next) => {
    // Get user ID or IP address for rate limiting
    const key = req.user ? req.user.id : req.ip;
    
    // Current timestamp
    const now = Date.now();
    
    // Get timestamps for this user/IP
    const timestamps = requestTimestamps.get(key) || [];
    
    // Filter timestamps within the time window
    const recentTimestamps = timestamps.filter(timestamp => (now - timestamp) < windowMs);
    
    // If too many requests, return error
    if (recentTimestamps.length >= maxRequests) {
      return res.status(429).json({
        status: 'error',
        message: 'Too many requests, please try again later'
      });
    }
    
    // Add current timestamp to list
    recentTimestamps.push(now);
    requestTimestamps.set(key, recentTimestamps);
    
    next();
  };
};

/**
 * Generate JWT token for user
 * @param {Object} user - User object
 * @returns {String} - JWT token
 */
exports.generateToken = (user) => {
  return jwt.sign(
    { id: user.id },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRES_IN || '1d' }
  );
};

/**
 * Generate refresh token for user
 * @param {Object} user - User object
 * @returns {String} - Refresh token
 */
exports.generateRefreshToken = (user) => {
  return jwt.sign(
    { id: user.id, type: 'refresh' },
    process.env.JWT_REFRESH_SECRET || process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d' }
  );
}; 