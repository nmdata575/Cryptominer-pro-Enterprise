// MongoDB Initialization Script for CryptoMiner Pro V30

// Create database
db = db.getSiblingDB('cryptominer');

// Create collections with indexes
db.createCollection('status_checks');
db.createCollection('mining_stats');
db.createCollection('mining_configs');
db.createCollection('ai_models');

// Create indexes for better performance
db.status_checks.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 86400 }); // Expire after 24 hours
db.status_checks.createIndex({ "client_name": 1 });

db.mining_stats.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 604800 }); // Expire after 7 days
db.mining_stats.createIndex({ "coin": 1 });
db.mining_stats.createIndex({ "pool_connected": 1 });

db.mining_configs.createIndex({ "coin": 1 });
db.mining_configs.createIndex({ "created_at": 1 });

db.ai_models.createIndex({ "model_type": 1 });
db.ai_models.createIndex({ "created_at": 1 });

// Insert default configuration
db.mining_configs.insertOne({
    "coin": "LTC",
    "intensity": 80,
    "threads": "auto",
    "default": true,
    "created_at": new Date()
});

print("Database initialized successfully!");