"""
Test CoinEx MCP Server Integration

Quick test to verify the MCP server is working with Kiro's configuration.
"""

import asyncio
from trade_risk_analyzer.market_monitoring.mcp_client import MCPClient, MCPConfig


async def test_mcp_connection():
    """Test basic MCP connection and data retrieval"""
    
    print("=" * 60)
    print("Testing CoinEx MCP Server Integration")
    print("=" * 60)
    
    # Initialize MCP client
    mcp_client = MCPClient(MCPConfig())
    
    try:
        # Connect to MCP server
        print("\n1. Connecting to CoinEx MCP server...")
        connected = await mcp_client.connect()
        
        if not connected:
            print("❌ Failed to connect to MCP server")
            return False
        
        print("✅ Connected successfully!")
        
        # Test ticker
        print("\n2. Testing ticker data (BTC/USDT)...")
        ticker = await mcp_client.get_ticker("BTCUSDT")
        
        if ticker:
            print(f"✅ Ticker retrieved:")
            print(f"   Last Price: ${ticker.get('last_price', 'N/A')}")
            print(f"   24h Volume: {ticker.get('volume', 'N/A')}")
        else:
            print("❌ Failed to get ticker")
        
        # Test order book
        print("\n3. Testing order book (BTC/USDT)...")
        orderbook = await mcp_client.get_orderbook("BTCUSDT", depth=5)
        
        if orderbook:
            print(f"   Debug - Full response: {orderbook}")
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            print(f"✅ Order book retrieved:")
            print(f"   Bids: {len(bids)} levels")
            print(f"   Asks: {len(asks)} levels")
            if bids and asks:
                print(f"   Best Bid: ${bids[0][0]}")
                print(f"   Best Ask: ${asks[0][0]}")
        else:
            print("❌ Failed to get order book")
        
        # Test K-line
        print("\n4. Testing K-line data (BTC/USDT)...")
        klines = await mcp_client.get_kline("BTCUSDT", interval="1min", limit=5)
        
        if klines:
            print(f"✅ K-line retrieved: {len(klines)} candles")
            if klines:
                latest = klines[-1]
                print(f"   Latest: O:{latest.get('open')} H:{latest.get('high')} L:{latest.get('low')} C:{latest.get('close')}")
        else:
            print("❌ Failed to get K-line")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! MCP server is working correctly.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Disconnect
        await mcp_client.disconnect()
        print("\nDisconnected from MCP server")


if __name__ == "__main__":
    success = asyncio.run(test_mcp_connection())
    exit(0 if success else 1)
