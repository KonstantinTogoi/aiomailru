# Objects List

Some objects are used in several methods.

- [User](#User) - user
- [Event](#Event) - event
- [Like](#Like) - event "like"
- [Comment](#Comment) - event comment
- [Attachments](#Attachments) - event attachments



## User

Object contains information about user and contains following fields:

| **fields** | **description** |
| --- | --- |
| **uid** <br><br> ``string`` | User ID. |
| **first_name** <br><br> ``string`` | First name. |
| **last_name** <br><br> ``string`` | Last name. |
| **nick** <br><br> ``string`` | Nickname. |
| **status_text** <br><br> ``string`` | User status. |
| **email** <br><br> ``string`` | Email address. |
| **sex** <br><br> ``integer, [0,1]`` | User sex. Possible values: <br> <ul><li>*0* -male,</li><li>*1*- female</li></ul> |
| **show_age** <br><br> ``integer, [0,1]`` | Information whether the user allows to show the age. |
| **birthday** <br><br> ``string`` <br><br> Returns only if the age is showed. | User's date of birth. Returned as *DD.MM.YYYY*. |
| **has_my** <br><br> ``integer, [0,1]`` | Information whether the user has profile. |
| **has_pic** <br><br> ``integer, [0,1]`` | Information whether the user has profile photo. |
| **pic** <br><br> ``string`` | URL of user's photo. |
| **pic_small** <br><br> ``string`` | URL of user's photo with at most 45 pixels on the longest side. |
| **pic_big** <br><br> ``string`` | URL of user's photo with at most 600 pixels on the longest side. |
| **pic_22** <br><br> ``string`` | URL of square photo of the user photo with 22 pixels in width. |
| **pic_32** <br><br> ``string`` | URL of square photo of the user photo with 32 pixels in width. |
| **pic_40** <br><br> ``string`` | URL of square photo of the user photo with 40 pixels in width. |
| **pic_50** <br><br> ``string`` | URL of square photo of the user photo with 50 pixels in width. |
| **pic_128** <br><br> ``string`` | URL of square photo of the user photo with 128 pixels in width. |
| **pic_180** <br><br> ``string`` | URL of square photo of the user photo with 180 pixels in width. |
| **pic_190** <br><br> ``string`` | URL of square photo of the user photo with 190 pixels in width. |
| **link** <br><br> ``string`` | Returns a website address of a user profile. |
| **referer_type** <br><br> ``string`` | Referrer type. Possible values: <br> <ul>*stream.install*</ul> <ul>*stream.publish*</ul> <ul>*invitation*</ul> <ul>*catalog*</ul> <ul>*suggests*</ul> <ul>*left menu suggest*</ul> <ul>*new apps*</ul> <ul>*guestbook*</ul> <ul>*agent*</ul> |
| **referer_id** <br><br> ``string`` | Identifies where a user came from; see https://api.mail.ru/docs/guides/ref/. |
| **is_online** <br><br> ``integer, [0,1]`` | Information whether the user is online. |
| **is_friend** <br><br> ``integer, [0,1]`` | Information whether the user is a friend of current user. |
| **follower** <br><br> ``integer, [0,1]`` | Information whether the user is a follower of current user. |
| **following** <br><br> ``integer, [0,1]`` | Information whether current user is a follower of the user. |
| **friends_count** <br><br> ``integer`` | Number of friends. |
| **video_count** <br><br> ``integer`` | Number of videos. |
| **is_verified** <br><br> ``integer, [0,1]`` | Information whether the user is verified. |
| **vip** <br><br> ``integer, [0,1]`` | Information whether the user is vip. |
| **app_installed** <br><br> ``integer, [0,1]`` | Information whether the user has installed the current app. |
| **last_visit** <br><br> ``integer`` | Date (in Unixtime) of the last user's visit. |
| **cover** <br><br> ``object`` <br><br> Returns only with a comment. | Information about profile's cover; see [Cover](#Cover). |



## Event

Object describes an event and contains following fields:

| **field** | **description** |
| --- | --- |
| **thread_id** <br><br> ``string`` <br><br> Returns only if current event is commentable. | Comment thread ID in the following format: ``<User's checksum><ID>``. |
| **authors** <br><br> ``array``| Information about authors; see [User](#User). |
| **type_name** <br><br> ``string``| Event type name. |
| **click_url** <br><br> ``string`` <br><br>  Returns only if event type's name is *micropost*.| Event URL. |
| **likes_count** <br><br> ``integer`` <br><br> Returns only if current event is likeable. | Number of "likes". |
| **attachments** <br><br> ``array``| Information about attachments to the event (link, image, video, audio, user, ...), if any; see [Attachments](#Attachments). |
| **time** <br><br> ``integer``| Date (in Unixtime) of the event. |
| **huid** <br><br> ``string`` | Event ID in the following format: ``<User's checksum><Event ID>``. |
| **user_text** <br><br> ``string``| User text. |
| **is_liked_by_me** <br><br> ``integer, [0,1]``| Shows if current user has liked the event. |
| **subtype** <br><br> ``string``| "event". |
| **is_commentable** <br><br> ``integer, [0,1]``| Shows if the event is commentable. |
| **type** <br><br> ``string``| Event type; see [Event types](#Event types). |
| **is_likeable** <br><br> ``integer, [0,1]``| Shows if the event is likeable. |
| **id** <br><br> ``string`` | Event ID. |
| **text_media** <br><br> ``array`` <br><br> Returns only if event's type name is *micropost*. | Information about text; see [Attachments](#Attachments). |
| **comments_count** <br><br> ``integer`` <br><br> Returns only if current event is commentable. | Number of comments. |

### Event types

- 1-1 Photo
- 1-2 Video
- 1-3 Photo mark
- 1-4 Video mark
- 1-6 TYPE_PHOTO_WAS_SELECTED 
- 1-7 Music 
- 1-8 Photo comment
 - 1-9 TYPE_PHOTO_SUBSCRIPTION 
- 1-10 Video comment
- 1-11 TYPE_PHOTO_WAS_MODERATED
 - 1-12 TYPE_VIDEO_WAS_MODERATED
 - 1-13 TYPE_VIDEO_TRANSLATION 
- 1-14 Private photo comment 
- 1-15 Private video comment
 - 1-16 Music comment
- 1-17 TYPE_PHOTO_NEW_COMMENT 
- 1-18 TYPE_VIDEO_NEW_COMMENT 
- 3-1 Blog post
- 3-2 Blog post comment
 - 3-3 Join community
 - 3-4 Community
- 3-5 TYPE_USER_COMMUNITY_LEAVE
 - 3-6 TYPE_BLOG_COMMUNITY_POST 
- 3-7 TYPE_USER_GUESTBOOK 
- 3-8 TYPE_BLOG_CHALLENGE_ACCEPT 
- 3-9 TYPE_BLOG_CHALLENGE_THROW 
- 3-10 TYPE_BLOG_SUBSCRIPTION 
- 3-12 Blog post mark
- 3-13 Community post mark
- 3-23 Post in micro blog
 - 3-25 Private post in micro blog
- 4-1 TYPE_QUESTION
 - 4-2 TYPE_QUESTION_ANSWER
 - 4-6 TYPE_QUESTION_ANSWER_PRIVATE 
- 5-1 TYPE_USER_FRIEND
 - 5-2 TYPE_USER_ANKETA
 - 5-4 TYPE_USER_CLASSMATES
 - 5-5 TYPE_USER_CAREER
 - 5-7 TYPE_USER_AVATAR
 - 5-9 TYPE_USER_PARTNER 
- 5-10 TYPE_GIFT_SENT 
- 5-11 TYPE_GIFT_RECEIVED 
- 5-12 TYPE_USER_MILITARY
 - 5-13 TYPE_USER_PARTNER_APPROVED
 - 5-15 TYPE_USER_ITEM
 - 5-16 App install
 - 5-17 App event
 - 5-18 Community post
- 5-19 Post in community guestbook
- 5-20 Join community
- 5-21 Community video
 - 5-22 Community photo
- 5-24 App event
- 5-24 TYPE_APP_INFO
 - 5-26 Link share
- 5-27 Event like
 - 5-29 Video share
 - 5-30 Comment to link share
 - 5-31 Comment to video share
 - 5-32 Micropost comment



## Like

Object wraps an event that a user liked and contains following fields:

| **field** | **description** |
| --------- | ---------------- |
| **time** <br><br> ``integer``| Date (in Unixtime) of the "like". |
| **author** <br><br> ``object``| Information about the user; see [User](#User). |
| **huid** <br><br> ``string`` | Like ID in the following format: ``<User's checksum><Like ID>``. |
| **subevent** <br><br> ``object``| Information about the event; see [Event](#Event). |
| **subtype** <br><br> ``string``| "like". |
| **is_commentable** <br><br> ``integer``| 0. |
| **id** <br><br> ``string`` | Like ID. |
| **is_likable** <br><br> ``integer``| 0. |



## Comment

Object wraps an event that a user commented and contains following fields:

| **field** | **description** |
| --------- | ---------------- |
| **time** <br><br> ``integer``| Date (in Unixtime) of the comment. |
| **huid** <br><br> ``string`` | Comment ID in the following format: ``<User's checksum><Comment ID>``. |
| **subevent** <br><br> ``object``| Information about the event; see [Event](#Event). |
| **subtype** <br><br> ``string``| "comment". |
| **comment** <br><br> ``object`` | Object with following fields: <br> <ul> <li> **text** ``string`` - Text. </li> <li> **time** ``integer`` - Date (in Unixtime) of the comment. </li> <li> **is_deleted** ``integer`` - Shows if the comment deleted. </li> <li> **id** ``string`` - Comment ID. </li> <li> **author** ``object`` - Information about the user; see [User](#User). </li> <li> **text_media** ``object`` - Object with fields **object** ``string`` and **content** ``string``. </li> </ul> |
| **is_commentable** <br><br> ``integer``| 0. |
| **id** <br><br> ``string`` | Comment ID. |
| **is_likable** <br><br> ``integer``| 0. |



## Attachments

Information about event's media attachments is returned in field
**attachments** and contains an array of objects.
Each object contains field **object** with type name
that defines all other fields.

- [text](#text)
- [tag](#tag)
- [link](#link)
- [avatar](#avatar)
- [image](#image)
- [music](#music)
- [video](#video)
- [app](#app)
- [group](#group)
- [gift](#gift)

### text

contains following fields:

| **field** |
| --- |
| **object** <br><br> ``string, ["text"]`` |
| **content** <br><br> ``string`` |

### tag

contains one additional field **content** with an object with following fields:

| **field** |
| --- |
| **is_blacklist** <br><br> ``integer, [0,1]`` |
| **tag** <br><br> ``string`` |

### link

contains one additional field **content** with an object with following fields:

| **field** |
| --- |
| **type-id** <br><br> ``string, ["text"]`` |
| **contents** <br><br> ``string`` |

or contains following fields:

| **field** |
| --- |
| **object** <br><br> ``string, ["link"]`` |
| **text** <br><br> ``string`` |
| **url** <br><br> ``string`` |

### avatar

contains one additional field **new** with an object with following fields:

| **field** |
| --- |
| **thread_id** <br><br> ``string`` |
| **width** <br><br> ``integer`` |
| **click_url** <br><br> ``string`` |
| **album_id** <br><br> ``string`` |
| **src** <br><br> ``string`` |
| **height** <br><br> ``integer`` |
| **desc** <br><br> ``string`` |
| **src_hires** <br><br> ``string`` |
| **id** <br><br> ``string`` |
| **owner_id** <br><br> ``string`` |

### image

contains following fields:

| **field** |
| --- |
| **likes_count** <br><br> ``integer`` |
| **thread_id** <br><br> ``string`` |
| **width** <br><br> ``string`` |
| **object** <br><br> ``string, ["image"]`` |
| **click_url** <br><br> ``string`` |
| **album_id** <br><br> ``string`` |
| **src** <br><br> ``string`` |
| **resized_src** <br><br> ``string`` |
| **height** <br><br> ``string`` |
| **src_filed** <br><br> ``string`` |
| **src_hires** <br><br> ``string`` |
| **id** <br><br> ``string`` |
| **owner_id** <br><br> ``string`` |
| **comments_count** <br><br> ``integer`` |

All fields but **object** and **src** may not be returned.

### music

contains following fields:

| **field** |
| --- |
| **is_add** <br><br> ``integer`` |
| **click_url** <br><br> ``string`` |
| **object** <br><br> ``string, ["music"]`` |
| **name** <br><br> ``string`` |
| **author** <br><br> ``string`` |
| **duration** <br><br> ``integer`` |
| **file_url** <br><br> ``string`` |
| **uploader** <br><br> ``string`` |
| **mid** <br><br> ``string`` |

### video

contains following fields:

| **field** |
| --- |
| **width** <br><br> ``integer`` |
| **object** <br><br> ``string, ["video"]`` |
| **album_id** <br><br> ``string`` |
| **view_count** <br><br> ``integer`` |
| **desc** <br><br> ``string`` |
| **comments_count** <br><br> ``integer`` |
| **likes_count** <br><br> ``integer`` |
| **thread_id** <br><br> ``string`` |
| **image_filed** <br><br> ``string`` |
| **click_url** <br><br> ``string`` |
| **src** <br><br> ``string`` |
| **duration** <br><br> ``integer`` |
| **height** <br><br> ``integer`` |
| **is_liked_by_me** <br><br> ``integer, [0,1]`` |
| **external_id** <br><br> ``string`` |
| **owner_id** <br><br> ``string`` |
| **title** <br><br> ``string`` |

### app

contains one additional field **content** with an object with following fields:

| **field** |
| --- |
| **PublishStatus** <br><br> ``object`` <br><br> Object with following fields: <br> <ul> <li> **My** ``string`` </li> <li> **Mobile** ``string`` </li> </ul> |
| **ID** <br><br> ``string`` |
| **InstallationsSpaced** <br><br> ``string`` |
| **ShortName** <br><br> ``string`` |
| **Genre** <br><br> ``array`` <br><br> Each object contains following fields: <br> <ul> <li> **name** ``string`` </li> <li> **id** ``string`` </li> <li> **admin_genre** ``integer, [0,1]`` </li> </ul> |
| **Votes** <br><br> ``object`` <br><br> Object with following fields: <br> <ul> <li> **VotesSum** ``string`` </li> <li> **VotesCount** ``string`` </li> <li> **VotesStarsWidth** ``string`` </li> <li> **Votes2IntRounded** ``string`` </li> <li> **Votes2DigitRounded** ``string`` </li> </ul> |
| **Installations** <br><br> ``integer`` |
| **ShortDescription** <br><br> ``string`` |
| **Name** <br><br> ``string`` |
| **Description** <br><br> ``string`` |
| **Pictures** <br><br> ``object`` |

### group

contains one additional field **content** with an object
that is described [in the separate section](#User).

### gift

contains one additional field **content** with an object with following fields:

| **field** |
| --- |
| **is_private** <br><br> ``integer, [0,1]`` |
| **click_url** <br><br> ``string`` |
| **is_anonymous** <br><br> ``integer, [0,1]`` |
| **time** <br><br> ``integer`` |
| **is_read** <br><br> ``integer, [0,1]`` |
| **to** <br><br> ``object`` <br><br> see [User](#User). |
| **gift** <br><br> ``object`` |
| **from** <br><br> ``object`` <br><br> see [User](#User). |
| **text** <br><br> ``string`` |
| **rus_time** <br><br> ``string`` |
| **long_id** <br><br> ``string`` |



## Other

Objects that are not classified.

### Cover

Object contains information about profile's cover.

| **field** |
| --- |
| **cover_position** <br><br> ``string`` |
| **width** <br><br> ``string`` |
| **size** <br><br> ``string`` |
| **aid** <br><br> ``string`` |
| **pid** <br><br> ``string`` |
| **thread_id** <br><br> ``string`` |
| **owner** <br><br> ``string`` |
| **target_album** <br><br> ``object`` <br> Information about target album; see [Target Album](#Target Album). |
| **click_url** <br><br> ``string`` |
| **src** <br><br> ``string`` |
| **height** <br><br> ``string`` |
| **cover_width** <br><br> ``string`` |
| **created** <br><br> ``string`` |
| **comment** <br><br> ``string`` |
| **src_small** <br><br> ``string`` |
| **cover_height** <br><br> ``string`` |
| **title** <br><br> ``string`` |



### Target Album

Object contains information about cover's target album.

| **field** |
| --- |
| **link** <br><br> ``string`` |
| **owner** <br><br> ``string`` |
| **sort_order** <br><br> ``string`` |
| **sort_by** <br><br> ``string`` |
| **description** <br><br> ``string`` |
| **privacy_desc** <br><br> ``string`` |
| **size** <br><br> ``integer`` |
| **aid** <br><br> ``string`` |
| **created** <br><br> ``integer`` |
| **cover_pid** <br><br> ``string`` |
| **cover_url** <br><br> ``string`` |
| **is_commentable** <br><br> ``integer, [0,1]`` |
| **title** <br><br> ``string`` |
| **updated** <br><br> ``integer`` |
| **privacy** <br><br> ``integer`` |
| **can_read_comment** <br><br> ``integer, [0,1]`` |
