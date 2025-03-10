/**
 * Database Configuration
 * 
 * Connect to MongoDB and PostgreSQL databases
 */

const mongoose = require('mongoose');
const { Pool } = require('pg');
const redis = require('redis');
const dotenv = require('dotenv');

dotenv.config();

// MongoDB Connection
const connectMongoDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    
    console.log(`MongoDB Connected: ${conn.connection.host}`);
    return conn;
  } catch (error) {
    console.error(`MongoDB Connection Error: ${error.message}`);
    process.exit(1); // Exit with failure
  }
};

// PostgreSQL Connection Pool
const pgPool = new Pool({
  host: process.env.POSTGRES_HOST,
  port: process.env.POSTGRES_PORT,
  database: process.env.POSTGRES_DB,
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  max: 20, // Maximum number of clients in the pool
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Test PostgreSQL connection
const connectPostgreSQL = async () => {
  try {
    const client = await pgPool.connect();
    console.log('PostgreSQL Connected');
    client.release();
    return pgPool;
  } catch (error) {
    console.error(`PostgreSQL Connection Error: ${error.message}`);
    process.exit(1); // Exit with failure
  }
};

// Redis Connection
const redisClient = redis.createClient({
  url: `redis://${process.env.REDIS_HOST}:${process.env.REDIS_PORT}`,
  password: process.env.REDIS_PASSWORD || undefined,
});

// Connect to Redis
const connectRedis = async () => {
  try {
    await redisClient.connect();
    console.log('Redis Connected');
    return redisClient;
  } catch (error) {
    console.error(`Redis Connection Error: ${error.message}`);
    // Don't exit process, as Redis is optional
    return null;
  }
};

// Connect to all databases
const connectDatabases = async () => {
  const mongo = await connectMongoDB();
  const pg = await connectPostgreSQL();
  const redis = await connectRedis();
  
  return { mongo, pg, redis };
};

// Close all database connections
const closeDatabases = async () => {
  try {
    await mongoose.connection.close();
    await pgPool.end();
    if (redisClient.isOpen) {
      await redisClient.quit();
    }
    console.log('All database connections closed');
  } catch (error) {
    console.error(`Error closing database connections: ${error.message}`);
  }
};

module.exports = {
  connectMongoDB,
  connectPostgreSQL,
  connectRedis,
  connectDatabases,
  closeDatabases,
  pgPool,
  redisClient
}; 