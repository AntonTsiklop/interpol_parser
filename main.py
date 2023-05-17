from notice_parser import *

red_notices_link = 'https://ws-public.interpol.int/notices/v1/red'
red_notices = NoticesParser(red_notices_link)
red_notices_list = red_notices.parse_notices()
red_notices.json_write(red_notices_list, 'red_notices')

red_notices_details = NoticeDetailsParser(red_notices_link)
red_notices_details.json_write(red_notices_details.parse_details(red_notices_list), 'red_notices_details')

red_notices_thumbnails = NoticesThumbnailsParser(red_notices_link)
red_notices_thumbnails.parse_thumbnails('images_red', red_notices_list)


yellow_notices_link = 'https://ws-public.interpol.int/notices/v1/yellow'
yellow_notices = NoticesParser(yellow_notices_link)
yellow_notices_list = yellow_notices.parse_notices()
yellow_notices.json_write(yellow_notices_list, 'red_notices')

yellow_notices_details = NoticeDetailsParser(yellow_notices_link)
yellow_notices_details.json_write(yellow_notices_details.parse_details(yellow_notices_list), 'red_notices_details')

yellow_notices_thumbnails = NoticesThumbnailsParser(yellow_notices_link)
yellow_notices_thumbnails.parse_thumbnails('images_yellow', yellow_notices_list)

