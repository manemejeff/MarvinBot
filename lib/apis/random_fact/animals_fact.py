from aiohttp import request
from random import choice

ANIMALS = ['dog', 'cat', 'panda', 'fox', 'bird', 'koala']


async def rand_animal_fact():
    URL = f'https://some-random-api.ml/facts/{choice(ANIMALS)}'
    async with request("GET", URL, headers={}) as response:
        if response.status == 200:
            data = await response.json()
            return data['fact']
        else:
            return f'Api returned {response.status} status'

if __name__ == '__main__':
    import asyncio
    pr = asyncio.run(rand_animal_fact())
    print(pr)
