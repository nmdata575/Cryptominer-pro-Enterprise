import React, { useState, useEffect } from 'react';

// ============================================================================
// SAVED POOLS MANAGER COMPONENT
// ============================================================================

const SavedPoolsManager = ({ onUsePool, onClose, currentConfig }) => {
    const [savedPools, setSavedPools] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [editingPool, setEditingPool] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        coin_symbol: 'LTC',
        wallet_address: '',
        pool_address: '',
        pool_port: 3333,
        pool_password: 'x',
        pool_username: '',
        description: ''
    });

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    useEffect(() => {
        fetchSavedPools();
    }, []);

    const fetchSavedPools = async () => {
        try {
            const response = await fetch(`${backendUrl}/api/pools/saved`);
            if (response.ok) {
                const data = await response.json();
                setSavedPools(data.pools || []);
            }
        } catch (error) {
            console.error('Failed to fetch saved pools:', error);
        }
        setLoading(false);
    };

    const handleSave = async () => {
        try {
            const url = editingPool 
                ? `${backendUrl}/api/pools/saved/${editingPool._id}`
                : `${backendUrl}/api/pools/saved`;
            
            const method = editingPool ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                await fetchSavedPools();
                setShowAddForm(false);
                setEditingPool(null);
                resetForm();
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            }
        } catch (error) {
            console.error('Save error:', error);
            alert('Failed to save pool configuration');
        }
    };

    const handleDelete = async (poolId) => {
        if (window.confirm('Are you sure you want to delete this pool configuration?')) {
            try {
                const response = await fetch(`${backendUrl}/api/pools/saved/${poolId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    await fetchSavedPools();
                }
            } catch (error) {
                console.error('Delete error:', error);
            }
        }
    };

    const handleUse = async (pool) => {
        try {
            const response = await fetch(`${backendUrl}/api/pools/saved/${pool._id}/use`, {
                method: 'POST'
            });

            if (response.ok) {
                const data = await response.json();
                onUsePool(data.mining_config, pool);
                onClose();
            }
        } catch (error) {
            console.error('Use pool error:', error);
        }
    };

    const handleEdit = (pool) => {
        setFormData({
            name: pool.name,
            coin_symbol: pool.coin_symbol,
            wallet_address: pool.wallet_address,
            pool_address: pool.pool_address,
            pool_port: pool.pool_port,
            pool_password: pool.pool_password || 'x',
            pool_username: pool.pool_username || '',
            description: pool.description || ''
        });
        setEditingPool(pool);
        setShowAddForm(true);
    };

    const saveCurrentConfig = () => {
        if (currentConfig) {
            setFormData({
                name: `${currentConfig.coin?.symbol || 'Unknown'} Pool Config`,
                coin_symbol: currentConfig.coin?.symbol || 'LTC',
                wallet_address: currentConfig.wallet_address || '',
                pool_address: currentConfig.coin?.custom_pool_address || '',
                pool_port: currentConfig.coin?.custom_pool_port || 3333,
                pool_password: currentConfig.pool_password || 'x',
                pool_username: currentConfig.pool_username || '',
                description: 'Auto-saved from current configuration'
            });
            setShowAddForm(true);
        }
    };

    const resetForm = () => {
        setFormData({
            name: '',
            coin_symbol: 'LTC',
            wallet_address: '',
            pool_address: '',
            pool_port: 3333,
            pool_password: 'x',
            pool_username: '',
            description: ''
        });
    };

    if (loading) {
        return <div className="text-center p-8">Loading saved pools...</div>;
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-green-400">
                        💾 Saved Pool Configurations
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white text-xl"
                    >
                        ✕
                    </button>
                </div>

                {!showAddForm ? (
                    <>
                        <div className="flex gap-3 mb-6">
                            <button
                                onClick={() => setShowAddForm(true)}
                                className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium"
                            >
                                ➕ Add New Pool
                            </button>
                            {currentConfig && (
                                <button
                                    onClick={saveCurrentConfig}
                                    className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg font-medium"
                                >
                                    💾 Save Current Config
                                </button>
                            )}
                        </div>

                        {savedPools.length === 0 ? (
                            <div className="text-center text-gray-400 py-8">
                                <p className="text-lg mb-2">No saved pool configurations yet</p>
                                <p>Save your frequently used pool settings for quick access!</p>
                            </div>
                        ) : (
                            <div className="grid gap-4">
                                {savedPools.map((pool) => (
                                    <div key={pool._id} className="bg-gray-700 rounded-lg p-4">
                                        <div className="flex justify-between items-start">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <h3 className="text-lg font-semibold text-white">
                                                        {pool.name}
                                                    </h3>
                                                    <span className="bg-green-600 px-2 py-1 rounded text-sm">
                                                        {pool.coin_symbol}
                                                    </span>
                                                </div>
                                                
                                                <div className="grid grid-cols-2 gap-4 text-sm text-gray-300">
                                                    <div>
                                                        <span className="text-gray-400">Pool:</span>{' '}
                                                        {pool.pool_address}:{pool.pool_port}
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-400">Wallet:</span>{' '}
                                                        {pool.wallet_address ? 
                                                            `${pool.wallet_address.slice(0, 10)}...${pool.wallet_address.slice(-4)}` 
                                                            : 'Not set'
                                                        }
                                                    </div>
                                                </div>
                                                
                                                {pool.description && (
                                                    <p className="text-gray-400 text-sm mt-2">
                                                        {pool.description}
                                                    </p>
                                                )}
                                                
                                                {pool.last_used && (
                                                    <p className="text-gray-500 text-xs mt-2">
                                                        Last used: {new Date(pool.last_used).toLocaleDateString()}
                                                    </p>
                                                )}
                                            </div>
                                            
                                            <div className="flex gap-2 ml-4">
                                                <button
                                                    onClick={() => handleUse(pool)}
                                                    className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm"
                                                >
                                                    ▶️ Use
                                                </button>
                                                <button
                                                    onClick={() => handleEdit(pool)}
                                                    className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm"
                                                >
                                                    ✏️ Edit
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(pool._id)}
                                                    className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm"
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                ) : (
                    <div>
                        <h3 className="text-xl font-semibold mb-4">
                            {editingPool ? 'Edit Pool Configuration' : 'Add New Pool Configuration'}
                        </h3>
                        
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Configuration Name *
                                </label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="My Pool Config"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Coin Symbol *
                                </label>
                                <select
                                    value={formData.coin_symbol}
                                    onChange={(e) => setFormData({...formData, coin_symbol: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                >
                                    <option value="LTC">Litecoin (LTC)</option>
                                    <option value="DOGE">Dogecoin (DOGE)</option>
                                    <option value="FTC">Feathercoin (FTC)</option>
                                    <option value="EFL">E-Gulden (EFL)</option>
                                </select>
                            </div>
                            
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Wallet Address *
                                </label>
                                <input
                                    type="text"
                                    value={formData.wallet_address}
                                    onChange={(e) => setFormData({...formData, wallet_address: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="Your wallet address"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Pool Address *
                                </label>
                                <input
                                    type="text"
                                    value={formData.pool_address}
                                    onChange={(e) => setFormData({...formData, pool_address: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="pool.example.com"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Pool Port *
                                </label>
                                <input
                                    type="number"
                                    value={formData.pool_port}
                                    onChange={(e) => setFormData({...formData, pool_port: parseInt(e.target.value)})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="3333"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Pool Username
                                </label>
                                <input
                                    type="text"
                                    value={formData.pool_username}
                                    onChange={(e) => setFormData({...formData, pool_username: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="Usually your wallet address"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Pool Password
                                </label>
                                <input
                                    type="text"
                                    value={formData.pool_password}
                                    onChange={(e) => setFormData({...formData, pool_password: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="x"
                                />
                            </div>
                            
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Description (Optional)
                                </label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white h-20"
                                    placeholder="Notes about this pool configuration..."
                                />
                            </div>
                        </div>
                        
                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={handleSave}
                                className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-medium"
                            >
                                💾 Save Configuration
                            </button>
                            <button
                                onClick={() => {
                                    setShowAddForm(false);
                                    setEditingPool(null);
                                    resetForm();
                                }}
                                className="bg-gray-600 hover:bg-gray-700 px-6 py-2 rounded-lg font-medium"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// ============================================================================
// CUSTOM COINS MANAGER COMPONENT
// ============================================================================

const CustomCoinsManager = ({ onSelectCoin, onClose }) => {
    const [customCoins, setCustomCoins] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [editingCoin, setEditingCoin] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        symbol: '',
        algorithm: 'Scrypt',
        block_reward: 25.0,
        block_time: 150,
        difficulty: 1000.0,
        scrypt_params: {
            n: 1024,
            r: 1,
            p: 1
        },
        network_hashrate: 'Unknown',
        wallet_format: 'Standard',
        description: ''
    });

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    useEffect(() => {
        fetchCustomCoins();
    }, []);

    const fetchCustomCoins = async () => {
        try {
            const response = await fetch(`${backendUrl}/api/coins/custom`);
            if (response.ok) {
                const data = await response.json();
                setCustomCoins(data.coins || []);
            }
        } catch (error) {
            console.error('Failed to fetch custom coins:', error);
        }
        setLoading(false);
    };

    const handleSave = async () => {
        try {
            // Validate required fields
            if (!formData.name.trim() || !formData.symbol.trim()) {
                alert('Name and Symbol are required');
                return;
            }

            const url = editingCoin 
                ? `${backendUrl}/api/coins/custom/${editingCoin._id}`
                : `${backendUrl}/api/coins/custom`;
            
            const method = editingCoin ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                await fetchCustomCoins();
                setShowAddForm(false);
                setEditingCoin(null);
                resetForm();
            } else {
                const error = await response.json();
                alert(`Error: ${error.detail}`);
            }
        } catch (error) {
            console.error('Save error:', error);
            alert('Failed to save custom coin');
        }
    };

    const handleDelete = async (coinId) => {
        if (window.confirm('Are you sure you want to delete this custom coin?')) {
            try {
                const response = await fetch(`${backendUrl}/api/coins/custom/${coinId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    await fetchCustomCoins();
                }
            } catch (error) {
                console.error('Delete error:', error);
            }
        }
    };

    const handleSelect = (coin) => {
        // Convert custom coin to CoinConfig format
        const coinConfig = {
            name: coin.name,
            symbol: coin.symbol,
            algorithm: coin.algorithm,
            block_reward: coin.block_reward,
            block_time: coin.block_time,
            difficulty: coin.difficulty,
            scrypt_params: coin.scrypt_params,
            network_hashrate: coin.network_hashrate,
            wallet_format: coin.wallet_format,
            is_custom: true
        };
        
        onSelectCoin(coinConfig);
        onClose();
    };

    const handleEdit = (coin) => {
        setFormData({
            name: coin.name,
            symbol: coin.symbol,
            algorithm: coin.algorithm,
            block_reward: coin.block_reward,
            block_time: coin.block_time,
            difficulty: coin.difficulty,
            scrypt_params: coin.scrypt_params,
            network_hashrate: coin.network_hashrate,
            wallet_format: coin.wallet_format,
            description: coin.description || ''
        });
        setEditingCoin(coin);
        setShowAddForm(true);
    };

    const resetForm = () => {
        setFormData({
            name: '',
            symbol: '',
            algorithm: 'Scrypt',
            block_reward: 25.0,
            block_time: 150,
            difficulty: 1000.0,
            scrypt_params: {
                n: 1024,
                r: 1,
                p: 1
            },
            network_hashrate: 'Unknown',
            wallet_format: 'Standard',
            description: ''
        });
    };

    const algorithmOptions = [
        'Scrypt',
        'SHA-256',
        'X11',
        'Lyra2REv2',
        'Equihash',
        'CryptoNote',
        'Other'
    ];

    if (loading) {
        return <div className="text-center p-8">Loading custom coins...</div>;
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-5xl w-full max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-green-400">
                        🪙 Custom Coin Manager
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white text-xl"
                    >
                        ✕
                    </button>
                </div>

                {!showAddForm ? (
                    <>
                        <div className="flex gap-3 mb-6">
                            <button
                                onClick={() => setShowAddForm(true)}
                                className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-medium"
                            >
                                ➕ Add Custom Coin
                            </button>
                        </div>

                        {customCoins.length === 0 ? (
                            <div className="text-center text-gray-400 py-8">
                                <p className="text-lg mb-2">No custom coins created yet</p>
                                <p>Add custom coins to mine new or unlisted cryptocurrencies!</p>
                            </div>
                        ) : (
                            <div className="grid gap-4">
                                {customCoins.map((coin) => (
                                    <div key={coin._id} className="bg-gray-700 rounded-lg p-4">
                                        <div className="flex justify-between items-start">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <h3 className="text-lg font-semibold text-white">
                                                        {coin.name}
                                                    </h3>
                                                    <span className="bg-purple-600 px-2 py-1 rounded text-sm">
                                                        {coin.symbol}
                                                    </span>
                                                    <span className="bg-gray-600 px-2 py-1 rounded text-xs">
                                                        {coin.algorithm}
                                                    </span>
                                                </div>
                                                
                                                <div className="grid grid-cols-3 gap-4 text-sm text-gray-300">
                                                    <div>
                                                        <span className="text-gray-400">Block Reward:</span>{' '}
                                                        {coin.block_reward} {coin.symbol}
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-400">Block Time:</span>{' '}
                                                        {coin.block_time}s
                                                    </div>
                                                    <div>
                                                        <span className="text-gray-400">Difficulty:</span>{' '}
                                                        {coin.difficulty.toLocaleString()}
                                                    </div>
                                                </div>

                                                {coin.algorithm === 'Scrypt' && (
                                                    <div className="text-sm text-gray-300 mt-2">
                                                        <span className="text-gray-400">Scrypt Params:</span>{' '}
                                                        N={coin.scrypt_params?.n}, R={coin.scrypt_params?.r}, P={coin.scrypt_params?.p}
                                                    </div>
                                                )}
                                                
                                                {coin.description && (
                                                    <p className="text-gray-400 text-sm mt-2">
                                                        {coin.description}
                                                    </p>
                                                )}
                                            </div>
                                            
                                            <div className="flex gap-2 ml-4">
                                                <button
                                                    onClick={() => handleSelect(coin)}
                                                    className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm"
                                                >
                                                    ⚡ Select
                                                </button>
                                                <button
                                                    onClick={() => handleEdit(coin)}
                                                    className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm"
                                                >
                                                    ✏️ Edit
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(coin._id)}
                                                    className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm"
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                ) : (
                    <div>
                        <h3 className="text-xl font-semibold mb-4">
                            {editingCoin ? 'Edit Custom Coin' : 'Add Custom Coin'}
                        </h3>
                        
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Coin Name *
                                </label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="Bitcoin Gold"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Symbol *
                                </label>
                                <input
                                    type="text"
                                    value={formData.symbol}
                                    onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="BTG"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Algorithm
                                </label>
                                <select
                                    value={formData.algorithm}
                                    onChange={(e) => setFormData({...formData, algorithm: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                >
                                    {algorithmOptions.map(algo => (
                                        <option key={algo} value={algo}>{algo}</option>
                                    ))}
                                </select>
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Block Reward
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={formData.block_reward}
                                    onChange={(e) => setFormData({...formData, block_reward: parseFloat(e.target.value)})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Block Time (seconds)
                                </label>
                                <input
                                    type="number"
                                    value={formData.block_time}
                                    onChange={(e) => setFormData({...formData, block_time: parseInt(e.target.value)})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Difficulty
                                </label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={formData.difficulty}
                                    onChange={(e) => setFormData({...formData, difficulty: parseFloat(e.target.value)})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                />
                            </div>

                            {formData.algorithm === 'Scrypt' && (
                                <>
                                    <div className="col-span-2">
                                        <h4 className="text-lg font-medium text-gray-300 mb-3">Scrypt Parameters</h4>
                                        <div className="grid grid-cols-3 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-400 mb-1">N</label>
                                                <input
                                                    type="number"
                                                    value={formData.scrypt_params.n}
                                                    onChange={(e) => setFormData({
                                                        ...formData, 
                                                        scrypt_params: {
                                                            ...formData.scrypt_params,
                                                            n: parseInt(e.target.value)
                                                        }
                                                    })}
                                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-400 mb-1">R</label>
                                                <input
                                                    type="number"
                                                    value={formData.scrypt_params.r}
                                                    onChange={(e) => setFormData({
                                                        ...formData, 
                                                        scrypt_params: {
                                                            ...formData.scrypt_params,
                                                            r: parseInt(e.target.value)
                                                        }
                                                    })}
                                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-400 mb-1">P</label>
                                                <input
                                                    type="number"
                                                    value={formData.scrypt_params.p}
                                                    onChange={(e) => setFormData({
                                                        ...formData, 
                                                        scrypt_params: {
                                                            ...formData.scrypt_params,
                                                            p: parseInt(e.target.value)
                                                        }
                                                    })}
                                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </>
                            )}
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Network Hashrate
                                </label>
                                <input
                                    type="text"
                                    value={formData.network_hashrate}
                                    onChange={(e) => setFormData({...formData, network_hashrate: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="10 MH/s"
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Wallet Format
                                </label>
                                <input
                                    type="text"
                                    value={formData.wallet_format}
                                    onChange={(e) => setFormData({...formData, wallet_format: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                                    placeholder="Standard / Legacy / Bech32"
                                />
                            </div>
                            
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Description (Optional)
                                </label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white h-20"
                                    placeholder="Notes about this custom coin..."
                                />
                            </div>
                        </div>
                        
                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={handleSave}
                                className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-medium"
                            >
                                🪙 Save Custom Coin
                            </button>
                            <button
                                onClick={() => {
                                    setShowAddForm(false);
                                    setEditingCoin(null);
                                    resetForm();
                                }}
                                className="bg-gray-600 hover:bg-gray-700 px-6 py-2 rounded-lg font-medium"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// Export consolidated components
export { SavedPoolsManager, CustomCoinsManager };