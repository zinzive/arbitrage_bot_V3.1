def sample_prices():
    """Фикстура с примером цен для тестирования"""
    return {
        'quickswap': {
            ('USDT', 'USDC'): 1.01,
            ('USDC', 'USDT'): 0.99,
            ('USDT', 'WETH'): 0.0005,
            ('WETH', 'USDT'): 2000,
            ('USDC', 'WETH'): 0.000495,
            ('WETH', 'USDC'): 2020,
        },
        'sushiswap': {
            ('USDT', 'USDC'): 1.02,
            ('USDC', 'USDT'): 0.98,
            ('USDT', 'WETH'): 0.00051,
            ('WETH', 'USDT'): 1960,
            ('USDC', 'WETH'): 0.000505,
            ('WETH', 'USDC'): 1980,
        }
    }