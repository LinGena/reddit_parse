from controllers.scrape import ScrapeControllers
from controllers.words import WordsControllers
from utils.logger import Logger

_logger = Logger().get_logger(__name__)


def main():

    words = WordsControllers().get()

    for word in words:

        try:

            ScrapeControllers().get_by_word(word)

        except Exception as ex:

            _logger.error(f'[{word}] {ex}')
            

if __name__ == '__main__':
    main()
