from memory.smart_cache import SmartCache

# Initialize cache
cache = SmartCache()
print('SmartCache initialized')
print()

# Test normalization
test_inputs = [
    'Please open Chrome boss',
    'hey friday open chrome',
    'open chrome',
    'OPEN CHROME!!!',
]
print('Testing normalization:')
for inp in test_inputs:
    normalized = cache.normalize(inp)
    print(f'  {inp} -> {normalized}')
print()

# Test set and get
print('Testing set/get:')
cache.set('open chrome', 'Chrome opened successfully', 'open_app', response_ms=120)
cache.set('open firefox', 'Firefox opened', 'open_app', response_ms=115)
cache.set('send message to sai', 'Message sent to Sai', 'whatsapp_flow', response_ms=200)
print(f'Cache size: {cache.get_size()} entries')
print()

# Test exact match
result = cache.get('open chrome')
if result:
    print(f'Exact match found: {result["result"]}')

# Test fuzzy match
result = cache.get('please open chrome boss')
if result:
    print(f'Fuzzy match found: {result["result"]}')
print()

# Test stats
print('Cache Stats:')
print(cache.get_stats())
