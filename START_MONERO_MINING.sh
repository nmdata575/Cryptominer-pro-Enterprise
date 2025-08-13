#!/bin/bash

# CryptoMiner Pro V30 - Start Monero Mining
# Replace YOUR_MONERO_ADDRESS with your actual Monero wallet address

echo "🚀 CryptoMiner Pro V30 - Starting Monero Mining"
echo "=================================================="

# Your Monero wallet address (replace this!)
MONERO_ADDRESS="YOUR_MONERO_ADDRESS_HERE"

if [ "$MONERO_ADDRESS" = "YOUR_MONERO_ADDRESS_HERE" ]; then
    echo "❌ ERROR: Please replace YOUR_MONERO_ADDRESS_HERE with your actual Monero address!"
    echo ""
    echo "📋 STEPS TO GET YOUR MONERO ADDRESS:"
    echo "1. Go to: https://mymonero.com/"
    echo "2. Click 'Create New Wallet'"
    echo "3. Save your seed phrase securely"
    echo "4. Copy your Monero address (starts with '4')"
    echo "5. Replace YOUR_MONERO_ADDRESS_HERE in this script"
    echo ""
    exit 1
fi

echo "💰 Monero Address: ${MONERO_ADDRESS:0:20}...${MONERO_ADDRESS: -10}"
echo "🏊 Pool: SupportXMR (0.6% fee, CPU-optimized)"
echo "⚡ Algorithm: RandomX (CPU-friendly)"
echo ""

# Stop any existing mining
echo "🛑 Stopping existing mining..."
curl -s -X POST http://localhost:8001/api/mining/stop > /dev/null

# Update the saved pool with your address
echo "⚙️ Configuring Monero pool with your address..."
curl -s -X POST http://localhost:8001/api/pools/saved \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"SupportXMR - Your Monero Pool\",
    \"coin_symbol\": \"XMR\",
    \"wallet_address\": \"$MONERO_ADDRESS\",
    \"pool_address\": \"stratum+tcp://pool.supportxmr.com:5555\",
    \"pool_port\": 5555,
    \"username\": \"$MONERO_ADDRESS\",
    \"password\": \"CryptoMinerV30\",
    \"description\": \"Your personal Monero mining - SupportXMR 0.6% fee\"
  }" > /dev/null

echo "✅ Pool configuration updated!"

# Start Monero mining using RandomX miner
echo "🚀 Starting RandomX Monero mining..."
echo ""

cd /app/backend
python3 -c "
import asyncio
import sys
sys.path.append('.')
from randomx_miner import MoneroMiner
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def start_monero_mining():
    print('🚀 Initializing Monero RandomX mining...')
    miner = MoneroMiner()
    
    try:
        success = await miner.start_mining(
            pool_host='pool.supportxmr.com',
            pool_port=5555,
            username='$MONERO_ADDRESS',
            password='CryptoMinerV30'
        )
        
        if success:
            print('✅ Monero mining started successfully!')
            print('💰 Earning XMR to your wallet: ${MONERO_ADDRESS:0:20}...')
            print('📊 Monitor earnings at: https://supportxmr.com/')
            print('')
            print('⏱️  Mining for 300 seconds (5 minutes)...')
            print('Press Ctrl+C to stop earlier')
            
            # Mine for 5 minutes or until interrupted
            await asyncio.sleep(300)
            
        else:
            print('❌ Failed to start Monero mining')
            
    except KeyboardInterrupt:
        print('\n🛑 Mining interrupted by user')
    except Exception as e:
        print(f'❌ Mining error: {e}')
    finally:
        miner.stop_mining()
        stats = miner.get_stats()
        print('')
        print('📊 FINAL MINING RESULTS:')
        print(f'   Hash Rate: {stats[\"hashrate\"]:.1f} H/s')
        print(f'   Shares Found: {stats[\"shares_found\"]}')
        print(f'   Shares Accepted: {stats[\"shares_accepted\"]}')
        print(f'   Efficiency: {stats[\"efficiency\"]:.1f}%')
        print(f'   Mining Time: {stats[\"uptime\"]:.1f} seconds')
        print('')
        print('🎉 Monero mining session completed!')

# Run the mining
asyncio.run(start_monero_mining())
" 

echo ""
echo "🎉 Monero mining session completed!"
echo "📊 Check your earnings at: https://supportxmr.com/"
echo "💰 Enter your address to see balance and payouts"