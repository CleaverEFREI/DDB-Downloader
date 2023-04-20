#Author : Plantim
#Contributors : Iooray, Cleaver
#Version : 1.4
#Description : Ce script télécharge la base de données de Dofusdb.fr

import json
import configparser
from utils import * #permet de faire des opérations sur les fichiers
import aiohttp
import asyncio
from tqdm.asyncio import tqdm as async_tqdm

async def async_progress_bar(coros, *args, **kwargs):
    tasks = [asyncio.create_task(coro) for coro in coros]
    for f in async_tqdm(asyncio.as_completed(tasks), *args, total=len(tasks), **kwargs):
        await f
    return [task.result() for task in tasks]


async def run(categorie):
    url = "https://api.dofusdb.fr/" + categorie + "?$limit=50&$skip="
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            donnees = await response.json()
        nb_element_max = donnees["total"]
        semaphore = asyncio.Semaphore(100)  # Adjust the concurrency level according to your needs.
        finaljson = await download_json_async(session, url, nb_element_max, donnees, semaphore)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with open(f"{output_path}/{categorie}.json", "w+") as f:
        f.write(json.dumps(finaljson))

    return len(finaljson['data'])

async def main(categories, category):
    if category not in categories and category != "all":
        category = check_categorie(categories)

    if category != "all":
        len_finaljson = await run(category)
        message_fin(len_finaljson, category)
    else:
        len_finaljsons = await async_progress_bar([run(cat) for cat in categories], desc="Downloading categories")
        for i, len_finaljson in enumerate(len_finaljsons):
            message_fin(len_finaljson, categories[i], len(categories))


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    CAT = config['dofusdb.fr']['categories'].split(',') #Liste des catégories
    output_path = config['DEFAULT']['output_path'] #Chemin du dossier output
    categorie = config['DEFAULT']['categorie'] #Catégorie à extraire
    asyncio.run(main(CAT, categorie))
