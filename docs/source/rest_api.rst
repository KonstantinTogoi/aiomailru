REST API
========

List of all methods is available here: https://api.mail.ru/docs/reference/rest/.

Executing requests
------------------

For executing API requests call an instance of :code:`APIMethod` class.
You can get it as an attribute of :code:`API` class instance or
as an attribute of other :code:`APIMethod` class instance.

.. code-block:: python

    from aiomailru import API

    api = API(session)

    events = await api.stream.get()  # events for current user
    friends = await api.friends.get()  # current user's friends

Under the hood each API request is enriched with parameters to generate signature:

* :code:`method`
* :code:`app_id`
* :code:`session_key`
* :code:`secure`

and with the following parameter after generating signature:

* :code:`sig`, see https://api.mail.ru/docs/guides/restapi/#sig

Objects
-------

.. |br| raw:: html

    <br/>

Some objects are returned in several methods.

User
~~~~

.. list-table::
    :widths: 15 85
    :header-rows: 1

    * - **field**
      - **description**
    * - **uid** |br| :code:`string`
      - User ID.
    * - **first_name** |br| :code:`string`
      - First name.
    * - **last_name** |br| :code:`string`
      - Last name.
    * - **nick** |br| :code:`string`
      - Nickname.
    * - **status_text** |br| :code:`string`
      - User status.
    * - **email** |br| :code:`string`
      - E-mail address.
    * - **sex** |br| :code:`integer, [0,1]`
      - User sex. Possible values: |br| - *0* - male |br| - *1* - female
    * - **show_age** |br| :code:`integer, [0,1]`
      - Information whether the user allows to show the age.
    * - **birthday** |br| :code:`string`
      - User's date of birth. Returned as DD.MM.YYYY.
    * - **has_my** |br| :code:`integer, [0,1]`
      - Information whether the user has profile.
    * - **has_pic** |br| :code:`integer, [0,1]`
      - Information whether the user has profile photo.
    * - **pic** |br| :code:`string`
      - URL of user's photo.
    * - **pic_small** |br| :code:`string`
      - URL of user's photo with at most 45 pixels on the longest side.
    * - **pic_big** |br| :code:`string`
      - URL of user's photo with at most 600 pixels on the longest side.
    * - **pic_22** |br| :code:`string`
      - URL of square photo of the user photo with 22 pixels in width.
    * - **pic_32** |br| :code:`string`
      - URL of square photo of the user photo with 32 pixels in width.
    * - **pic_40** |br| :code:`string`
      - URL of square photo of the user photo with 40 pixels in width.
    * - **pic_50** |br| :code:`string`
      - URL of square photo of the user photo with 50 pixels in width.
    * - **pic_128** |br| :code:`string`
      - URL of square photo of the user photo with 128 pixels in width.
    * - **pic_180** |br| :code:`string`
      - URL of square photo of the user photo with 180 pixels in width.
    * - **pic_190** |br| :code:`string`
      - URL of square photo of the user photo with 190 pixels in width.
    * - **link** |br| :code:`string`
      - Returns a website address of a user profile.
    * - **referer_type** |br| :code:`string`
      - Referer type. Possible values: |br| - *stream.install* |br| - *stream.publish* |br| - *invitation* |br| - *catalog* |br| - *suggests* |br| - *left menu suggest* |br| - *new apps* |br| - *guestbook* |br| - *agent*
    * - **referer_id** |br| :code:`string`
      - Identifies where a user came from; |br| see https://api.mail.ru/docs/guides/ref/.
    * - **is_online** |br| :code:`integer, [0,1]`
      - Information whether the user is online.
    * - **is_friend** |br| :code:`integer, [0,1]`
      - Information whether the user is a friend of current user.
    * - **friends_count** |br| :code:`integer`
      - Number of friends.
    * - **follower** |br| :code:`integer, [0,1]`
      - Information whether the user is a follower of current user.
    * - **following** |br| :code:`integer, [0,1]`
      - Information whether current user is a follower of the user.
    * - **subscribe** |br| :code:`integer, [0,1]`
      - Information whether current user is a subscriber of the user.
    * - **subscribers_count** |br| :code:`integer`
      - Number of subscribers.
    * - **video_count** |br| :code:`integer`
      - Number of videos.
    * - **is_verified** |br| :code:`integer, [0,1]`
      - Information whether the user is verified.
    * - **vip** |br| :code:`integer, [0,1]`
      - Information whether the user is vip.
    * - **app_installed** |br| :code:`integer, [0,1]`
      - Information whether the user has installed the current app.
    * - **last_visit** |br| :code:`integer`
      - Date (in Unixtime) of the last user's visit.
    * - **cover** |br| :code:`object`
      - Information about profile's cover; see :ref:`Cover`.
    * - **group_info** |br| :code:`object`
      - Object with following fields: |br| - **category_id** :code:`integer` |br| - **short_description** :code:`string` |br| - **full_description** :code:`string` |br| - **interests** :code:`string` |br| - **posts_cnt** :code:`integer` |br| - **category_name** :code:`string` |br| - **rules** :code:`string`
    * - **location** |br| :code:`object`
      - Object with following fields: |br| - **country** :code:`object`: {**id** :code:`integer`, **name** :code:`string`} |br| - **city** :code:`object`: {**id** :code:`integer`, **name** :code:`string`} |br| - **region** :code:`object`: {**id** :code:`integer`, **name** :code:`string`}

Event
~~~~~

Object describes an event and contains following fields:

.. list-table::
    :widths: 15 85
    :header-rows: 1

    * - **field**
      - **description**
    * - **thread_id** |br| :code:`string`
      - Comment thread ID in the following format: |br| :code:`<User's checksum><ID>`.
    * - **authors** |br| :code:`array`
      - Information about authors; see :ref:`User`.
    * - **type_name** |br| :code:`string`
      - Event type name.
    * - **click_url** |br| :code:`string` |br| Returns only if current |br| event is likeable.
      - Event URL.
    * - **likes_count** |br| :code:`integer` |br| Returns only if current |br| event is likeable.
      - Number of "likes".
    * - **attachments** |br| :code:`array`
      - Information about attachments to the event |br| (link, image, video, audio, user, ...) if any; |br| see :ref:`Attachments`.
    * - **time** |br| :code:`integer`
      - Date (in Unixtime) of the event.
    * - **huid** |br| :code:`string`
      - Event ID in the following format: |br| :code:`<User's checksum><Event ID>`.
    * - **generator** |br| :code:`object`
      - Object with the following fields: |br| - **icon** :code:`string` - URL of app icon. |br| - **url** :code:`string` - App url. |br| - **app_id** :code:`integer` - App ID. |br| - **type** :code:`string` - App type. |br| - **title** :code:`string` - App title.
    * - **user_text** |br| :code:`string`
      - User text.
    * - **is_liked_by_me** |br| :code:`integer, [0,1]`
      - Shows if current user has liked the event.
    * - **subtype** |br| :code:`string`
      - "event"
    * - **is_commentable** |br| :code:`integer, [0,1]`
      - Shows if the event is commentable.
    * - **type** |br| :code:`string`
      - Event type; see :ref:`Event types`.
    * - **is_likeable** |br| :code:`integer, [0,1]`
      - Shows if the event is likeable.
    * - **id** |br| :code:`string`
      - Event ID.
    * - **text_media** |br| :code:`array` |br| Returns only if event's |br| type name is *micropost*.
      - Information about text; see :ref:`Attachments`.
    * - **comments_count** |br| :code:`integer` |br| Returns only if current |br| event is commentable.
      - Number of comments.
    * - **action_links** |br| :code:`array`
      - Each object contains following fields: |br| - **text** :code:`string` |br| - **href** :code:`string`

Event types
^^^^^^^^^^^

* 1-1 Photo
* 1-2 Video
* 1-3 Photo mark
* 1-4 Video mark
* 1-6 TYPE_PHOTO_WAS_SELECTED 
* 1-7 Music 
* 1-8 Photo comment
* 1-9 TYPE_PHOTO_SUBSCRIPTION 
* 1-10 Video comment
* 1-11 TYPE_PHOTO_WAS_MODERATED
* 1-12 TYPE_VIDEO_WAS_MODERATED
* 1-13 TYPE_VIDEO_TRANSLATION 
* 1-14 Private photo comment 
* 1-15 Private video comment
* 1-16 Music comment
* 1-17 TYPE_PHOTO_NEW_COMMENT 
* 1-18 TYPE_VIDEO_NEW_COMMENT 
* 3-1 Blog post
* 3-2 Blog post comment
* 3-3 Join community
* 3-4 Community
* 3-5 TYPE_USER_COMMUNITY_LEAVE
* 3-6 TYPE_BLOG_COMMUNITY_POST 
* 3-7 TYPE_USER_GUESTBOOK 
* 3-8 TYPE_BLOG_CHALLENGE_ACCEPT 
* 3-9 TYPE_BLOG_CHALLENGE_THROW 
* * 3-10 TYPE_BLOG_SUBSCRIPTION 
* 3-12 Blog post mark
* 3-13 Community post mark
* 3-23 Post in micro blog
* 3-25 Private post in micro blog
* 4-1 TYPE_QUESTION
* 4-2 TYPE_QUESTION_ANSWER
* 4-6 TYPE_QUESTION_ANSWER_PRIVATE 
* 5-1 TYPE_USER_FRIEND
* 5-2 TYPE_USER_ANKETA
* 5-4 TYPE_USER_CLASSMATES
* 5-5 TYPE_USER_CAREER
* 5-7 TYPE_USER_AVATAR
* 5-9 TYPE_USER_PARTNER 
* 5-10 TYPE_GIFT_SENT 
* 5-11 TYPE_GIFT_RECEIVED 
* 5-12 TYPE_USER_MILITARY
* 5-13 TYPE_USER_PARTNER_APPROVED
* 5-15 TYPE_USER_ITEM
* 5-16 App install
* 5-17 App event
* 5-18 Community post
* 5-19 Post in community guestbook
* 5-20 Join community
* 5-21 Community video
* 5-22 Community photo
* 5-24 App event
* 5-24 TYPE_APP_INFO
* 5-26 Link share
* 5-27 Event like
* 5-29 Video share
* 5-30 Comment to link share
* 5-31 Comment to video share
* 5-32 Micropost comment

Like
~~~~

Object wraps an event that a user liked and contains following fields:

.. list-table::
    :widths: 15 85
    :header-rows: 1

    * - **field**
      - **description**
    * - **time** |br| :code:`integer`
      - Date (in Unixtime) of the "like".
    * - **author** |br| :code:`object`
      - Information about the user; see :ref:`User`.
    * - **huid** |br| :code:`string`
      - Like ID in the following format: |br| :code:`<User's checksum><Like ID>`.
    * - **subevent** |br| :code:`object`
      - Information about the event; see :ref:`Event`.
    * - **subtype** |br| :code:`string`
      - "like".
    * - **is_commentable** |br| :code:`integer, [0,1]`
      - 0.
    * - **id** |br| :code:`string`
      - Like ID.
    * - **is_likeable** |br| :code:`integer, [0,1]`
      - 0.

Comment
~~~~~~~

Object wraps an event that a user commented and contains following fields:

.. list-table::
    :widths: 15 85
    :header-rows: 1

    * - **field**
      - **description**
    * - **time** |br| :code:`integer`
      - Date (in Unixtime) of the comment.
    * - **huid** |br| :code:`string`
      - Comment ID in the following format: |br| :code:`<User's checksum><Comment ID>`.
    * - **subevent** |br| :code:`object`
      - Information about the event; see :ref:`Event`.
    * - **subtype** |br| :code:`string`
      - "comment".
    * - **comment** |br| :code:`object`
      - Object with following fields: |br| - **text** :code:`string` - Text. |br| - **time** :code:`integer` - Date (in Unixtime) of the comment. |br| - **is_deleted** :code:`integer [0,1]` - Shows if the comment deleted. |br| - **id** :code:`string` - Comment ID. |br| - **author** :code:`object` - Information about the user; see :ref:`User`. |br| - **text_media** :code:`object` - Object: {**object** :code:`string` and **content** :code:`string`}.
    * - **is_commentable** |br| :code:`integer, [0,1]`
      - 0.
    * - **id** |br| :code:`string`
      - Comment ID.
    * - **is_likeable** |br| :code:`integer, [0,1]`
      - 0.

Attachments
~~~~~~~~~~~

Information about event's media attachments is returned
in field **attachments** and contains an :code:`array` of objects.
Each object contains field **object** with type name that
defines all other fields.

text
^^^^

contains following fields:

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **object** |br| :code:`string, ["text"]`
    * - **content** |br| :code:`string`

tag
^^^

contains one additional field **content** with an object with following fields:

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **is_blacklist** |br| :code:`integer, [0,1]`
    * - **tag** |br| :code:`string`

link
^^^^

contains one additional field content with an object with following fields:

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **type-id** |br| :code:`string, ["text"]`
    * - **contents** |br| :code:`string`

or contains following fields:

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **object** |br| :code:`string, ["link"]`
    * - **text** |br| :code:`string`
    * - **url** |br| :code:`string`

avatar
^^^^^^

contains one additional field **new** with an object with following fields:

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **thread_id** |br| :code:`string`
    * - **width** |br| :code:`integer`
    * - **click_url** |br| :code:`string`
    * - **album_id** |br| :code:`string`
    * - **src** |br| :code:`string`
    * - **height** |br| :code:`integer`
    * - **desc** |br| :code:`string`
    * - **src_hires** |br| :code:`string`
    * - **id** |br| :code:`string`
    * - **owner_id** |br| :code:`string`

image
^^^^^

contains following fields:

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **likes_count** |br| :code:`integer`
    * - **thread_id** |br| :code:`string`
    * - **width** |br| :code:`string`
    * - **object** |br| :code:`string, ["image"]`
    * - **click_url** |br| :code:`string`
    * - **album_id** |br| :code:`string`
    * - **src** |br| :code:`string`
    * - **resized_src** |br| :code:`string`
    * - **height** |br| :code:`string`
    * - **src_filed** |br| :code:`string`
    * - **src_hires** |br| :code:`string`
    * - **id** |br| :code:`string`
    * - **owner_id** |br| :code:`string`
    * - **comments_count** |br| :code:`integer`

All fields but **object** and **src** may not be returned.

music
^^^^^

contains following fields:

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **is_add** |br| :code:`integer`
    * - **click_url** |br| :code:`string`
    * - **object** |br| :code:`string, ["music"]`
    * - **name** |br| :code:`string`
    * - **author** |br| :code:`string`
    * - **duration** |br| :code:`integer`
    * - **file_url** |br| :code:`string`
    * - **uploader** |br| :code:`string`
    * - **mid** |br| :code:`string`

video
^^^^^

contains following fields:

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **width** |br| :code:`integer`
    * - **object** |br| :code:`string, ["video"]`
    * - **album_id** |br| :code:`string`
    * - **view_count** |br| :code:`integer`
    * - **desc** |br| :code:`string`
    * - **comments_count** |br| :code:`integer`
    * - **likes_count** |br| :code:`integer`
    * - **thread_id** |br| :code:`string`
    * - **image_filed** |br| :code:`string`
    * - **click_url** |br| :code:`string`
    * - **src** |br| :code:`string`
    * - **duration** |br| :code:`integer`
    * - **height** |br| :code:`integer`
    * - **is_liked_by_me** |br| :code:`integer`
    * - **external_id** |br| :code:`string`
    * - **owner_id** |br| :code:`string`
    * - **title** |br| :code:`string`

app
^^^

contains one additional field **content** with an object with following fields:

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **PublishStatus** |br| :code:`object` |br| Object with following fields: |br| - **My** :code:`string` |br| - **Mobile** :code:`string`
    * - **ID** |br| :code:`string`
    * - **InstallationsSpaced** |br| :code:`string`
    * - **ShortName** |br| :code:`string`
    * - **Genre** |br| :code:`array` |br| Each object contains following fields: |br| - **name** :code:`string` |br| - **id** :code:`string` |br| - **admin_genre** :code:`integer, [0,1]`
    * - **Votes** |br| :code:`object` |br| Object with following fields: |br| - **VoteSum** :code:`string` |br| - **VotesCount** :code:`string` |br| - **VotesStarsWidth** :code:`string` |br| - **Votes2IntRounded** :code:`string` |br| - **Votes2DigitRounded** :code:`string`
    * - **Installations** |br| :code:`integer`
    * - **ShortDescription** |br| :code:`string`
    * - **Name** |br| :code:`string`
    * - **Description** |br| :code:`string`
    * - **Pictures** |br| :code:`object`

group
^^^^^

contains one additional field **content** with an object; see :ref:`User`.

gift
^^^^

contains one additional field **content** with an object with following fields:

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **is_private** |br| :code:`integer, [0,1]`
    * - **click_url** |br| :code:`string`
    * - **is_anonymous** |br| :code:`integer, [0,1]`
    * - **time** |br| :code:`integer`
    * - **is_read** |br| :code:`integer, [0,1]`
    * - **to** |br| :code:`object` |br| see :ref:`User`.
    * - **gift** |br| :code:`object`
    * - **from** |br| :code:`object` |br| see :ref:`User`.
    * - **text** |br| :code:`string`
    * - **rus_time** |br| :code:`string`
    * - **long_id** |br| :code:`string`

Other
~~~~~

Objects that are not classified.

Cover
^^^^^

Object contains information about profile's cover.

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **cover_position** |br| :code:`string`
    * - **width** |br| :code:`string`
    * - **size** |br| :code:`string`
    * - **aid** |br| :code:`string`
    * - **pid** |br| :code:`string`
    * - **thread_id** |br| :code:`string`
    * - **owner** |br| :code:`string`
    * - **target_album** |br| :code:`object` |br| Information about target album; |br| see :ref:`Target Album`.
    * - **click_url** |br| :code:`string`
    * - **src** |br| :code:`string`
    * - **height** |br| :code:`string`
    * - **cover_width** |br| :code:`string`
    * - **created** |br| :code:`string`
    * - **comment** |br| :code:`string`
    * - **src_small** |br| :code:`string`
    * - **cover_height** |br| :code:`string`
    * - **title** |br| :code:`string`

Target Album
^^^^^^^^^^^^

Object contains information about cover's target album.

.. list-table::
    :widths: 100
    :header-rows: 1

    * - **field**
    * - **link** |br| :code:`string`
    * - **owner** |br| :code:`string`
    * - **sort_order** |br| :code:`string`
    * - **sort_by** |br| :code:`string`
    * - **description** |br| :code:`string`
    * - **privacy_desc** |br| :code:`string`
    * - **size** |br| :code:`integer`
    * - **aid** |br| :code:`string`
    * - **created** |br| :code:`integer`
    * - **cover_pid** |br| :code:`string`
    * - **cover_url** |br| :code:`string`
    * - **is_commentable** |br| :code:`integer, [0,1]`
    * - **title** |br| :code:`string`
    * - **updated** |br| :code:`integer`
    * - **privacy** |br| :code:`integer`
    * - **can_read_comment** |br| :code:`integer, [0,1]`
