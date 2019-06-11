import html.parser
from collections import UserDict
from datetime import datetime


class Event(UserDict):
    """Event class."""

    def __init__(self, initialdata):
        super().__init__(initialdata)

    def __repr__(self):
        fmt = '%H:%M:%S %d.%m.%Y'
        created_at = datetime.fromtimestamp(self['time']).strftime(fmt)
        return '{subtype} with ID {id}. Created at {time}'.format(
            subtype=self['subtype'],
            id=self['id'],
            time=created_at,
        )

    @classmethod
    def from_html(cls, code: str):
        parser = cls.Parser()
        parser.feed(code)
        event = cls(parser.fields)
        return event

    class Parser(html.parser.HTMLParser):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields = {}

        def handle_starttag(self, tag, attrs):
            fields = {}
            attrs = dict(attrs)
            classes = attrs.get('class', '').split()

            if attrs.get('data-astat'):
                astat = Astat(*attrs['data-astat'].split(':'))
                fields['id'] = astat.id
                fields['time'] = astat.time
                fields['type'] = astat.type
                fields['subtype'] = astat.subtype
                fields['type_name'] = astat.type_name
                fields['likes_count'] = astat.likes_count
                fields['comments_count'] = astat.comments_count

            if 'event_links' in classes:
                fields['is_likeable'] = 1
                fields['is_commentable'] = 1

            if fields:
                self.fields.update(fields)


class Astat:
    def __init__(self, user_world_id, event_type, event_id,
                 owner_world_id, corr_world_id, corr_event_id,
                 likes_count, comments_count, event_time, _, region):
        self.user_world_id = int(user_world_id or '0')
        self.event_type = event_type
        self.event_id = event_id
        self.owner_world_id = owner_world_id
        self.corr_world_id = corr_world_id
        self.corr_event_id = corr_event_id
        self.likes_count = int(likes_count or '0')
        self.comments_count = int(comments_count or '0')
        self.event_time = int(event_time)
        self.region = int(region)

    @property
    def id(self):
        return self.event_id

    @property
    def time(self):
        return self.event_time

    @property
    def type(self):
        return '-'.join(self.event_type.split('-')[:2])

    @property
    def type_name(self):
        return TYPE_NAMES.get(self.type, '')

    @property
    def subtype(self):
        subtype = '-'.join(self.event_type.split('-')[2:])
        return subtype.lower() if subtype else 'event'


TYPE_NAMES = {
    '1-1': 'photo_upload',
    '1-2': 'video_upload',
    '1-7': 'music_add',
    '3-3': 'user_community_actions_enter',
    '3-5': 'user_community_actions_leave',
    '3-23': 'micropost',
    '5-7': 'avatar_change',
    '5-10': 'gift_send',
    '5-11': 'gift_received',
    '5-16': 'app_add',
    '5-26': 'share',
    '5-28': 'app_info2',
    '5-37': 'gift_receive_multi',
    '5-39': 'community_post',
    '5-41': 'user_post',
    '5-44': 'community_video_upload',
    '5-47': 'community_photo_upload',
    #  TODO: add missing types
}
