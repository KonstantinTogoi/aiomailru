from collections import UserDict


class Event(UserDict):
    """Event."""

    class Scripts:
        class Selectors:
            event_class = 'b-history_event_active-area_shift'
            subevent_class = 'b-history_event_active-area'
            event = f'div.{event_class}'
            subevent = f'div.{subevent_class}:not(.{event_class})'

            head = 'div.b-history-event_head'
            controls = f'{head} div.b-history-event__controls'
            action = f'{head} div.b-history-event__action'
            author = f'{controls} span.ui-tooltip-action'
            time = f'{action} div.b-history-event_time'
            url = f'{time} a'

            text = (
                'div.b-history-event__body '
                'div.b-history-event__event-textbox2 '
            )
            status = (
                'div.b-history-event__body '
                'div.b-history-event__event-textbox_status '
            )
            links = f'{status} a'

            comments = 'div.b-comments__history'

        astat = 'n => n.getAttribute("data-astat")'
        author = 'n => n.getAttribute("data-event-control-dir")'
        url = 'n => n.getAttribute("href")'

        links = (
            'ns => ns.map(n => {'
            'return { href: n.getAttribute("href"), text: n.innerText };'
            '})'
        )
        text = 'n => n.innerText'
        status = 'n => n.innerText'

    class Types:
        clickable = ['1-1', '3-23', '5-39', '5-41']
        status = '3-23'

    s = Scripts
    ss = Scripts.Selectors
    t = Types

    def __init__(self, initialdata):
        super().__init__(initialdata)

    def __repr__(self):
        return repr(self.data)

    @classmethod
    async def from_element(cls, element):
        """Creates a new event from a DOM element.

        Args:
            element (pyppeteer.element_handle.ElementHandle): the element.

        Returns:
            event (Event): new instance of this class.

        """

        ctx = element.executionContext
        astat = await ctx.evaluate(cls.s.astat, element)
        astat = Astat(*astat.split(':'))
        comments = await element.J(cls.ss.comments)

        if astat.subtype in ['comment', 'like']:
            data = {
                'time': astat.time,
                'author': {},  # fixed below
                # TODO: scrape like/comment 'huid'
                'subevent': {
                    # TODO: scrape subevent 'thread_id'
                    'authors': [],  # fixed below
                    'type_name': astat.corr_type_name,
                    # skip 'click_url', added below if present
                    'likes_count': astat.likes_count,
                    # skip 'attachments', added below if present
                    # TODO: scrape subevent 'time'
                    # TODO: scrape subevent 'huid'
                    # TODO: scrape subevent 'generator'
                    'user_text': '',  # fixed below if present
                    # TODO: scrape subevent 'is_liked_by_me'
                    'subtype': 'event',
                    'is_commentable': 1 if comments else 0,
                    'type': astat.corr_type,
                    'is_likeable': 1 if comments else 0,
                    'id': astat.corr_event_id,
                    # skip 'text_media', added below if present
                    'comments_count': astat.comments_count,
                    # TODO: scrape subevent 'action_links'
                },
                'subtype': astat.subtype,
                'is_commentable': 0,
                'id': astat.id,
                'is_likeable': 0,
            }

            element = await element.J(cls.ss.subevent)
            element_type = astat.corr_type
            element_body = await cls._from_element(element, element_type)
            data['subevent'].update(element_body)

        else:
            data = {
                # TODO: scrape event 'thread_id'
                'authors': [],  # fixed below
                'type_name': astat.type_name,
                # skip 'click_url', added below if present
                'likes_count': astat.likes_count,
                # skip 'attachments', added below if present
                'time': astat.time,
                # TODO: scrape event 'huid'
                # TODO: scape event 'generator'
                'user_text': '',  # fixed below if present
                # TODO: scrape event 'is_liked_by_me'
                'subtype': astat.subtype,
                'is_commentable': 1 if comments else 0,
                'type': astat.type,
                'is_likeable': 1 if comments else 0,
                'id': astat.id,
                # skip 'text_media', added below if present
                'comments_count': astat.comments_count,
                # TODO: scrape event 'action_links'
            }

            element = await element.J(cls.ss.event)
            element_type = astat.type
            element_body = await cls._from_element(element, element_type)
            data.update(element_body)

        event = cls(initialdata=data)

        return event

    @classmethod
    async def _from_element(cls, element, element_type):
        body = {}

        # scrape 'authors'
        controls = await element.J(cls.ss.controls)
        if controls:
            author_ref = await element.Jeval(cls.ss.author, cls.s.author) or ''
        else:
            author_ref = ''
        author = {'link': author_ref}
        body['authors'] = [author]

        # scrape 'click_url'
        if element_type in cls.t.clickable:
            body['click_url'] = await element.Jeval(cls.ss.url, cls.s.url)

        # scrape 'user_text' and 'text_media'
        if element_type == cls.t.status:
            status = await element.J(cls.ss.status)
            ctx = status.executionContext
            text = await ctx.evaluate(cls.s.status, status)
            links = await status.JJeval(cls.ss.links, cls.s.links)

            for link in links:
                text = text.replace(link['text'], link['href'])
            body['user_text'] = text

            medias = []
            for link in links:
                medias.append({
                    'object': 'link',
                    'content': {'type-id': 'text', 'contents': text},
                })
            body['text_media'] = medias + [{'object': 'text', 'content': text}]
        else:
            text = await element.J(cls.ss.text)
            if text:
                ctx = text.executionContext
                body['user_text'] = await ctx.evaluate(cls.s.text, text)

        return body


class Astat:
    def __init__(self, user_world_id, event_type, event_id,
                 owner_world_id, corr_world_id, corr_event_id,
                 likes_count, comments_count, event_time, *_):
        self.user_world_id = int(user_world_id or '0')

        self.event_type = event_type
        self.event_id = event_id
        self.event_time = int(event_time)
        self.owner_world_id = owner_world_id

        self.corr_world_id = corr_world_id
        self.corr_event_id = corr_event_id

        self.likes_count = int(likes_count or '0')
        self.comments_count = int(comments_count or '0')

    @property
    def id(self):
        return self.event_id.lower()

    @property
    def time(self):
        return self.event_time

    @property
    def type(self):
        """Event type."""
        if self.subtype == 'event':
            return '-'.join(self.event_type.split('-')[:2])
        else:
            raise AttributeError()

    @property
    def corr_type(self):
        """Type of liked/commented subevent."""
        if self.subtype == 'event':
            raise AttributeError()
        else:
            return '-'.join(self.event_type.split('-')[:2])

    @property
    def type_name(self):
        return TYPE_NAMES.get(self.type, '')

    @property
    def corr_type_name(self):
        return TYPE_NAMES[self.corr_type]

    @property
    def subtype(self):
        type_code = self.event_type.split('-')
        if len(type_code) < 3:
            return 'event'
        else:
            return type_code[2].lower()


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
    '5-50': '',  # TODO: add name
    #  TODO: add missing types
}
