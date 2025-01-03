from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

import os
from typing import List, Any, Union

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DRIVER_PATH = None

if os.name == "nt":
    DRIVER_PATH = os.path.join(ROOT_PATH, "driver/chromedriver.exe")
elif os.name == "posix":
    DRIVER_PATH = os.path.join(ROOT_PATH, "driver/chromedriver")


def _get_soup(url: str) -> BeautifulSoup:
    OPTIONS = Options()
    OPTIONS.add_argument("--headless=new")
    OPTIONS.add_argument("--remote-debugging-pipe")
    OPTIONS.add_argument("--incognito")
    OPTIONS.add_argument("--no-sandbox")
    OPTIONS.add_argument("--disable-dev-shm-usage")
    OPTIONS.add_argument("--disable-blink-features=AutomationControlled")
    OPTIONS.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(options=OPTIONS, service=service)
    driver.get(url)
    try: 
        WebDriverWait(driver, 20).until(expected_conditions.visibility_of_any_elements_located((By.ID, 'item-grid')))
    except Exception as e: 
        return None

    soup = BeautifulSoup(driver.page_source, "lxml")
    return soup


class Mercari:

    # def fetch_all_items(
    #         self,
    #         keyword: str = 'clothes',
    #         price_min: Union[None, int] = None,
    #         price_max: Union[None, int] = None,
    #         max_items_to_fetch: Union[None, int] = 100
    # ) -> List[str]:  # list of URLs.
    #     items_list = []
    #     for page_id in range(int(1e9)):
    #         items, search_res_head_tag = self.fetch_items_pagination(keyword, page_id, price_min, price_max)
    #         items_list.extend(items)
    #         # logger.debug(f'Found {len(items_list)} items so far.')
    #         #
    #         # if max_items_to_fetch is not None and len(items_list) > max_items_to_fetch:
    #         #     logger.debug(f'Reached the maximum items to fetch: {max_items_to_fetch}.')
    #         #     break

    #         if search_res_head_tag is None:
    #             break
    #         else:
    #             search_res_head = str(search_res_head_tag.contents[0]).strip()
    #             num_items = re.findall('\d+', search_res_head)
    #             if len(num_items) == 1 and num_items[0] == '0':
    #                 break
    #         sleep(2)
    #     return items_list

    def fetch_items_pagination(
            self,
            keyword: str,
            page_id: int = 1,
            price_min: Union[None, str] = None,
            price_max: Union[None, str] = None,
            e_flag: bool = False,
            c_flag: bool = False,
            p_flag: bool = False
    ) -> Union[List[str], Any]:  # List of URLS and a HTML marker.
        soup = _get_soup(self._fetch_url(page_id, keyword, price_min=price_min, price_max=price_max, e_flag=e_flag, c_flag=c_flag, p_flag=p_flag))
        if soup is None:
            return []

        results = []

        for item in soup.find_all('li', {"data-testid": "item-cell"}):
            price_element = item.find(class_="merPrice")
            price = price_element.text if price_element else "N/A"

            link_element = item.find("a")
            link = link_element.attrs['href'] if link_element else None

            if link:
                full_link = link if link.startswith('http') else 'https://jp.mercari.com' + link
                results.append(
                    {
                        "price": price, 
                        "item": full_link
                    }
                )

        return results

    def _fetch_url(
            self,
            page: int = 1,
            keyword: str = 'bicycle',
            price_min: Union[None, str] = None,
            price_max: Union[None, str] = None,
            e_flag: bool = False,
            c_flag: bool = False,
            p_flag: bool = False
    ):

        #電気・スマホ・カメラ = t1_category_id=7&category_id=7&t2_category_id=undefined
            #PC/タブレット = t1_category_id=7&category_id=96&t2_category_id=96

        url = f'https://www.mercari.com/jp/search/?keyword={keyword}'
        url += f"&page={page}"

        if p_flag:
            url += "&t1_category_id=7&category_id=1156&t2_category_id=96&t3_category_id=1156"
        elif c_flag:
            url += "&t1_category_id=7&category_id=96&t2_category_id=96"
        elif e_flag:
            url += "&t1_category_id=7&category_id=7&t2_category_id=undefined"
        url += "&sort=created_time&order=desc&status=on_sale"
        if price_min is not None:
            url += f'&price_min={price_min}'
        if price_max is not None:
            url += f'&price_max={price_max}'
        return url

    @property
    def name(self) -> str:
        return 'mercari'
