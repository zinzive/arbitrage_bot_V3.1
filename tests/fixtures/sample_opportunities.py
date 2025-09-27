def sample_opportunity():
    """Фикстура с примером арбитражной возможности"""
    from datetime import datetime
    
    return {
        'dex': 'quickswap',
        'path': ['USDT', 'USDC', 'USDT'],
        'profit': 0.01,  # 1%
        'timestamp': datetime.now(),
        'estimated_volume': 1000
    }