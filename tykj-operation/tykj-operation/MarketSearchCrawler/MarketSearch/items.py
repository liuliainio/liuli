# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from MarketSearch.utils import strip_space
from scrapy.contrib.loader.processor import MapCompose, Join, TakeFirst
from scrapy.item import Item, Field
from scrapy.utils.markup import remove_comments, unquote_markup, \
    replace_escape_chars, remove_tags


class CrawledItem(Item):
    name = Field(input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    icon_link = Field(input_processor=MapCompose(strip_space), output_processor=TakeFirst(),)
    source = Field(output_processor=TakeFirst(),)
    source_link = Field(output_processor=TakeFirst(),)
    rating = Field(output_processor=Join(),)
#    rating = Field()
    version = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    developer = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   strip_space),
        output_processor=TakeFirst(),
    )
    sdk_support = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=Join(),)
    category = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    screen_support = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   strip_space),
        output_processor=Join(),
    )
    apk_size = Field(default='', input_processor=MapCompose(strip_space), output_processor=TakeFirst(),)
    language = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    publish_date = Field(output_processor=TakeFirst(),)
    downloads = Field(default=0, input_processor=MapCompose(strip_space), output_processor=TakeFirst(),)
#    downloads = Field()
    description = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   remove_comments,
                                   replace_escape_chars,
                                   strip_space),
        output_processor=Join(),
    )
    images = Field(default='', output_processor=Join(),)
    qr_link = Field(default='', output_processor=TakeFirst(),)
    download_link = Field(default='', input_processor=MapCompose(strip_space), output_processor=TakeFirst(),)


class AppItem(CrawledItem):
    update_note = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   remove_comments,
                                   replace_escape_chars,
                                   strip_space),
        output_processor=Join(),
    )
    labels = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   remove_comments,
                                   replace_escape_chars,
                                   strip_space),
        output_processor=Join(separator=u','),
    )
    icon_path = Field()
    images_path = Field()
    last_crawl = Field()


class FinalAppItem(AppItem):
    package_name = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   remove_comments,
                                   replace_escape_chars,
                                   strip_space),
        output_processor=Join(),
    )
    is_break = Field(default=-1)
    platform = Field(default=1)
    file_type = Field(default='apk')
    avail_download_links = Field(default='')
    error = Field(default='')
    min_sdk_version = Field(default=0)
    vol_id = Field(default=0)
    status = Field(default=0)
    created_at = Field()
    version_code = Field()
    images_path = Field(default='')
    icon_path = Field(default='')


class AppleItem(CrawledItem):
    icon_path = Field()
    images_path = Field()
    last_crawl = Field()
    price = Field(default=0, input_processor=MapCompose(strip_space), output_processor=TakeFirst(),)
    app_id = Field()
    apple_id = Field()


class TripAdvisorItem(Item):
    source = Field(output_processor=TakeFirst(),)
    source_link = Field(output_processor=TakeFirst(),)
    name = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    rating = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    category = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    reviews = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    price = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    city = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    address = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=Join(),)
    phone = Field()
    hotel_class = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   strip_space),
        output_processor=TakeFirst(),
    )
    rank_of_city = Field()
    longitude_latitude = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   strip_space),
        output_processor=TakeFirst(),
    )
    owner_website = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   strip_space),
        output_processor=TakeFirst(),
    )
    last_crawl = Field()


class YelpItem(Item):
    source = Field(output_processor=TakeFirst(),)
    source_link = Field(output_processor=TakeFirst(),)
    name = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    rating = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    category = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=Join(','),)
    reviews = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    price = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    city = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    address = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=Join(),)
    owner_website = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   strip_space),
        output_processor=TakeFirst(),
    )
    phone = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    longitude_latitude = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   strip_space),
        output_processor=TakeFirst(),
    )
    last_crawl = Field()


class YoutubeItem(Item):
    source = Field(output_processor=TakeFirst(),)
    source_link = Field(output_processor=TakeFirst(),)
    name = Field(input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    likes = Field(default=0, input_processor=MapCompose(strip_space), output_processor=TakeFirst(),)
    dislikes = Field(default=0, input_processor=MapCompose(strip_space), output_processor=TakeFirst(),)
    duration = Field(input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    view_count = Field(default=0, input_processor=MapCompose(strip_space), output_processor=TakeFirst(),)
    author = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    category = Field(default='', input_processor=MapCompose(unquote_markup, strip_space), output_processor=TakeFirst(),)
    publish_date = Field(output_processor=TakeFirst(),)
    comments = Field(default=0, input_processor=MapCompose(strip_space), output_processor=TakeFirst(),)
    description = Field(
        default='',
        input_processor=MapCompose(unquote_markup,
                                   remove_comments,
                                   replace_escape_chars,
                                   strip_space),
        output_processor=Join(),
    )
    last_crawl = Field()


class UserNameItem(Item):
    name = Field()


class DownloadLinkItem(Item):
    url = Field()


