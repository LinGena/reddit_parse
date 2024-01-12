import cfscrape
import uuid
from bs4 import BeautifulSoup
import warnings
import json
import base64
from datetime import datetime, timezone
from components.models import ModelComponents
from configs.config import CONFIG_PROXY, proxy_data, DB_TABLE_POSTS, DB_TABLE_WORDS


warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class ScrapeControllers(ModelComponents):
    def __init__(self) -> None:
        super().__init__()


    def get_by_word(self, word: tuple):

        self.db_connection()

        try:
            self.id_word = word[0]

            q = word[1]

            self.last_update = word[2]

            date_update = self.get_datetime()

            self.update_data(q)

            sql = f"UPDATE {DB_TABLE_WORDS} SET last_update={date_update} WHERE id={self.id_word}"

            self.insert(sql)

            self._logger.info(f'Datas according word "{q}" was updated in db table')

        except Exception as ex:
            self._logger.error(ex)

        self.db_close_connection()


    def update_data(self, q: str, subreddit_name: str = None) -> dict:

        domain = 'https://www.reddit.com'

        if subreddit_name:
            # subreddit_name must be like "https://www.reddit.com/r/europe"
            link = subreddit_name + '/search/'

        else:

            link = domain + '/search/'

        params = self.get_params(q)

        src = self.get_request(link, params)

        while True:

            res = self.get_result_from_src(src)

            if not res:
                break
                 
            link_next_page = self.get_next_page_link(src)

            if not link_next_page:
                break
            
            link = domain + link_next_page

            src = self.get_request(link)

    
    def get_next_page_link(self, src) -> str:
        """Get link for next page"""

        soup = BeautifulSoup(src, 'lxml')

        blocks = soup.find_all('faceplate-partial')

        if not blocks:
            return None
        
        for block in blocks:

            try:
            
                loading = block.get('loading')

                if loading and loading == 'lazy':

                    return block.get('src')

            except Exception as ex:
                self._logger.error(ex)

        return None

    def get_result_from_src(self, src) -> list:
        """Get list of results from page"""
        
        soup = BeautifulSoup(src, 'lxml')

        posts = soup.find_all('faceplate-tracker')

        if not posts:
            return None        

        post_images = self.get_post_images_from_src(soup)

        for post in posts:

            try:

                data_testid = post.get('data-testid')

                if data_testid and data_testid == 'search-post':

                    data = post.get('data-faceplate-tracking-context')

                    if data:
                    
                        data = json.loads(data)

                        post_dict = data.get('post')

                        if post_dict:
                            
                            created_timestamp = post_dict.get('created_timestamp')

                            if created_timestamp and self.last_update and created_timestamp < self.last_update:

                                return None

                            url = post_dict.get('url')

                            if url in post_images:

                                image = post_images[url]

                            else:

                                image = None

                            post_dict.update({'image':image})

                            self.add_to_db_table(post_dict)

            except Exception as ex:
                self._logger.error(ex)

        return True
    

    def check_str_text(self, item: str, post_dict: dict) -> str:

        value = post_dict[item]

        if not value:
            return ''
        
        return self.magic_quotes(value)
    

    def check_int_text(self, item: str, post_dict: dict) -> int:
        
        try:

            value = int(post_dict[item])

            return value     
           
        except:
            return 0


    def add_to_db_table(self, post_dict: dict):

        link = self.check_str_text('url', post_dict)

        if not link:
            return

        post_text = self.check_str_text('title', post_dict)

        if not post_text:
            return 
        
        author_name = self.check_str_text('author_id', post_dict)

        community = self.check_str_text('subreddit_name', post_dict)

        if community:

            community = 'https://www.reddit.com/r/' + community

        post_create = self.check_int_text('created_timestamp', post_dict)
        
        number_comments = self.check_int_text('number_comments', post_dict)

        score = self.check_int_text('score', post_dict)

        domain = self.check_str_text('domain', post_dict)

        sql = f"SELECT COUNT(*) FROM {DB_TABLE_POSTS} WHERE link='{link}'"

        row = self.select_one(sql)

        image = post_dict['image']

        if image:

            image = self.convert_image(image)

        if row[0] == 0:

            sql = f"""INSERT INTO {DB_TABLE_POSTS} 
            (
                network,
                post_text,
                author_name,
                link,
                community,
                id_word,
                post_create,
                number_comments,
                score,
                image,
                domain
            ) VALUES 
            (
                'reddit',
                '{post_text}',
                '{author_name}',
                '{link}',
                '{community}',
                {self.id_word},
                {post_create},
                {number_comments},
                {score},
                '{image}',
                '{domain}'
            )"""

            self.insert(sql)
                    


    def get_post_images_from_src(self, soup: BeautifulSoup) -> dict:
        """Get dict of images from pages"""

        result = {}

        posts = soup.find_all('faceplate-tracker') 

        if not posts:
            return result

        for post in posts:

            try:
                is_noun = post.get('noun')

                if is_noun and is_noun == 'post':

                    a_tag = post.find('a')

                    if a_tag and a_tag.get('href'):

                        url = a_tag.get('href')

                        image_post = post.find('faceplate-img')

                        if image_post and image_post.get('data-testid') and image_post.get('data-testid') == 'search_post_thumbnail':

                            src = image_post.get('src')

                            result.update({url:src})

            except Exception as ex:
                self._logger.error(ex)        

        return result
    

    def get_params(self, q: str) -> dict:
        """Generate request params"""

        params = {
            'q': q,
            'type': 'link',
            'cId': str(uuid.uuid4()),
            'iId': str(uuid.uuid4()),
        }
        return params


    def get_request(self, link: str, params: dict = None) -> str:
        """Return content from page"""

        while True:
            try:
                response = self._request(link, params)

                soup = BeautifulSoup(response, 'lxml')

                if soup.find('title'):

                    title = soup.find('title').text.strip()

                    list_exceptions = ['Just a moment...', 'Access denied']

                    if title not in list_exceptions:

                        return response

                else:
                    return response

            except Exception as ex:
                print(ex)


    def _request(self, link: str, params: dict = None) -> str:
        """Get content form page"""

        s = cfscrape.create_scraper()

        if CONFIG_PROXY:
            s.proxies.update(proxy_data)

        s.headers = self.get_headers()

        if params:
            s.params = params

        scraped_data = s.get(url=link, verify=False, timeout=10)

        return scraped_data.text
    

    def get_headers(self) -> dict:
        """Return Headers"""

        return {
            'authority': 'www.reddit.com',
            'accept': 'text/vnd.reddit.partial+html, text/html;q=0.9',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    

    def get_datetime(self) -> int:
        """Return current UTC datetime in unix format with ms"""

        return int(datetime.now(timezone.utc).timestamp() * 1000)
    

    def convert_image(self, link: str) -> str:

        if not link:
            return None

        s = cfscrape.create_scraper()

        scraped_data = s.get(url=link, verify=False, timeout=10)

        if scraped_data.status_code == 200:

            image_base64 = base64.b64encode(scraped_data.content).decode('utf-8')

            return image_base64
        
        return None