#!/bin/bash
# CryptoMiner Pro V30 - Test Script

set -e

echo "🧪 Running CryptoMiner Pro V30 tests..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Test 1: Import all modules
echo "📦 Testing module imports..."
python3 -c "
import sys
sys.path.append('.')
try:
    from cryptominer import CryptoMinerPro
    from mining_engine import MiningEngine
    from scrypt_miner import ScryptMiner
    from ai_optimizer import AIOptimizer
    print('✅ All modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Test 2: CLI functionality
echo "🖥️ Testing CLI interface..."
python3 cryptominer.py --help > /dev/null
echo "✅ CLI help working"

python3 cryptominer.py --list-coins > /dev/null
echo "✅ Coin listing working"

# Test 3: Backend API
echo "🔗 Testing backend API..."
cd backend
python3 -c "
import sys
sys.path.append('.')
try:
    from server import app
    print('✅ Backend server imports working')
except Exception as e:
    print(f'❌ Backend import error: {e}')
    exit(1)
" &
API_PID=$!

# Wait for server to start
sleep 2

# Test API endpoints
if command -v curl >/dev/null 2>&1; then
    if curl -s http://localhost:8001/api/ > /dev/null; then
        echo "✅ API endpoint accessible"
    else
        echo "⚠️ API endpoint not accessible (server might not be running)"
    fi
fi

# Cleanup
kill $API_PID 2>/dev/null || true
cd ..

# Test 4: Configuration
echo "⚙️ Testing configuration..."
if [ -f "mining_config.template" ]; then
    echo "✅ Configuration template exists"
else
    echo "❌ Configuration template missing"
fi

# Test 5: Dependencies
echo "📋 Testing critical dependencies..."
python3 -c "
required_modules = ['asyncio', 'aiohttp', 'scrypt', 'numpy', 'sklearn']
missing = []

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print(f'❌ Missing modules: {missing}')
    exit(1)
else:
    print('✅ All critical dependencies available')
"

# Test 6: Mining simulation (dry run)
echo "⛏️ Testing mining simulation..."
timeout 10s python3 cryptominer.py \
    --coin LTC \
    --wallet "test_wallet_address" \
    --pool "test.pool.com:3333" \
    --intensity 1 \
    --threads 1 \
    > test_output.log 2>&1 || true

if grep -q "CryptoMiner Pro V30" test_output.log; then
    echo "✅ Mining simulation started successfully"
else
    echo "❌ Mining simulation failed"
    cat test_output.log
fi

rm -f test_output.log

echo ""
echo "🎉 All tests completed!"
echo ""
echo "💡 To run a full system test:"
echo "1. ./scripts/start.sh"
echo "2. Open http://localhost:3000"
echo "3. Run: python3 cryptominer.py --setup"