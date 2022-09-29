# Import libraries

import asyncio
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
from typing import List

import requests
import nest_asyncio

nest_asyncio.apply()


class MultiThreadAPI:
    """Using asyncio this allows for multithreading of api calls, just need to pass in a list of urls that need to be
    read """

    def __init__(self, url_list):
        self.url_list = url_list

    @staticmethod
    def get_set_event_loop():
        try:
            return asyncio.get_event_loop()
        except RuntimeError as e:
            if e.args[0].startswith('There is no current'):
                asyncio.set_event_loop(asyncio.new_event_loop())
                return asyncio.get_event_loop()
            raise e

    @staticmethod
    def fetch(session, url: str):
        """Private method that will run the request to the api call and return json data"""
        base_url = url
        with session.get(base_url) as response:
            data = response.json()
            if response.status_code != 200:
                print("FAILURE::{0}".format(url))

            # Return json data for future consumption
            return data

    async def get_data_asynchronous(self) -> List[str]:
        """This will implement the multithreading"""

        with ThreadPoolExecutor(max_workers=8) as executor:
            with requests.Session() as session:
                # Set any session parameters here before calling `fetch`

                # Initialize the event loop
                loop = self.get_set_event_loop()

                # Set the START_TIME for the `fetch` function
                START_TIME = default_timer()

                # Use list comprehension to create a list of
                # tasks to complete. The executor will run the `fetch`
                # function for each url in the url_to_fetch list
                tasks = [
                    loop.run_in_executor(
                        executor,
                        self.fetch,
                        *(session, string)  # Allows us to pass in multiple arguments to `fetch`
                    )
                    for string in self.url_list
                ]

                # Initializes the tasks to run and awaits their results
                json_data = []
                for response in await asyncio.gather(*tasks):
                    json_data.append(response)
        return json_data

    def run_api_threads(self):
        """This will implement the loop which multithreads and outputs data"""
        loop = self.get_set_event_loop()
        future = asyncio.ensure_future(self.get_data_asynchronous())
        loop.run_until_complete(future)
        data = future.result()

        return data
