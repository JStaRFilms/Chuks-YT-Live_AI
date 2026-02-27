import asyncio
import httpx

async def test_chat():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://127.0.0.1:8000/chat",
                json={"text": "Hello, can you hear me? Say your name."}
            )
            print("Status:", response.status_code)
            print("Response:", response.text)
        except Exception as e:
            print("Error connecting to server:", e)

if __name__ == "__main__":
    asyncio.run(test_chat())
