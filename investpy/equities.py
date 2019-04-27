#!/usr/bin/env python

# Copyright 2018-2019 Alvaro Bartolome
# See LICENSE for details.

import pandas as pd
import requests
import time
from lxml.html import fromstring
import pkg_resources

from investpy import user_agent as ua


def get_equity_names():
    """
    This function retrieves all the available equities to retrieve data from.
    All the equities available can be found at: https://es.investing.com/equities/spain

    Returns
    -------
        returns a dictionary containing all the equities information
    """

    params = {
        "noconstruct": "1",
        "smlID": "10119",
        "sid": "",
        "tabletype": "price",
        "index_id": "all"
    }

    head = {
        "User-Agent": ua.get_random(),
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "text/html",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    url = "https://es.investing.com/equities/StocksFilter"

    req = requests.get(url, params=params, headers=head)

    if req.status_code != 200:
        raise ConnectionError("ERR#015: error " + req.status_code + ", try again later.")

    root_ = fromstring(req.text)
    path_ = root_.xpath(".//table[@id='cross_rate_markets_stocks_1']/tbody/tr")

    results = list()

    if path_:
        for elements_ in path_:
            id_ = elements_.get('id').replace('pair_', '')

            for element_ in elements_.xpath('.//a'):
                tag_ = element_.get('href').replace('/equities/', '')
                isin_ = get_isin_code(tag_)

                data = {
                    "name": element_.text_content(),
                    "tag": tag_,
                    "isin": isin_,
                    "id": id_
                }

                results.append(data)

    resource_package = __name__
    resource_path = '/'.join(('resources', 'es', 'equities.csv'))
    file = pkg_resources.resource_filename(resource_package, resource_path)

    df = pd.DataFrame(results)
    df.to_csv(file, index=False)

    return results


def get_isin_code(info):
    """
    This is an auxiliar function that adds data to the equities pandas.DataFrame.
    Added data in this case, are the ISIN codes of every company in order to identify it.

    Returns
    -------
        returns a str that contains the ISIN code of the specified equity
    """

    url = "https://es.investing.com/equities/" + info

    head = {
        "User-Agent": ua.get_random(),
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "text/html",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    req = requests.get(url, headers=head, timeout=5)

    if req.status_code != 200:
        # raise ConnectionError("ERR#015: error " + req.status_code + ", try again later.")
        return None

    root_ = fromstring(req.text)
    path_ = root_.xpath("/html/body/div[5]/section/div[4]/div[1]/div[2]/div[3]/span[2]")

    code = None

    if path_:
        try:
            code = path_[0].text_content().rstrip()
            time.sleep(.5)
        except IndexError:
            raise IndexError("ERR#017: isin code unavailable or not found.")

    return code


def list_equities():
    """
    This function retrieves all the available equities and returns a list of each one of them.
    All the available equities can be found at: https://es.investing.com/equities/spain

    Returns
    -------
        returns a list with all the available equities to retrieve data from
    """

    resource_package = __name__
    resource_path = '/'.join(('resources', 'es', 'equities.csv'))
    if pkg_resources.resource_exists(resource_package, resource_path):
        equities = pd.read_csv(pkg_resources.resource_filename(resource_package, resource_path))
    else:
        names = get_equity_names()
        equities = pd.DataFrame(names)

    if equities is None:
        raise IOError("ERR#001: equities list not found or unable to retrieve.")

    return equities['name'].tolist()