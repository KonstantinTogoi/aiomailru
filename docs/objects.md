# Objects List

Some objects are used in several methods.

- [User](#User) - user
- [Event](#Event) - event
- [Like](#Like) - event "like"
- [Comment](#Comment) - event comment
- [Attachments](#Attachments) - event attachments



## User

Object contains information about user/group and contains following fields:

| **fields** | **description** |
| --- | --- |
| **uid** <br> ``string`` | User ID. |
| **first_name** <br> ``string`` | First name. |
| **last_name** <br> ``string`` | Last name. |
| **nick** <br> ``string`` | Nickname. |
| **status_text** <br> ``string`` | User status. |
| **email** <br> ``string`` | Email address. |
| **sex** <br> ``integer, [0,1]`` | User sex. Possible values: <br> <ul><li>*0* -male,</li><li>*1*- female</li></ul> |
| **show_age** <br> ``integer, [0,1]`` | Information whether the user allows to show the age. |
| **birthday** <br> ``string`` <br> Returns only if the age is showed. | User's date of birth. Returned as *DD.MM.YYYY*. |
| **has_my** <br> ``integer, [0,1]`` | Information whether the user has profile. |
| **has_pic** <br> ``integer, [0,1]`` | Information whether the user has profile photo. |
| **pic** <br> ``string`` | URL of user's photo. |
| **pic_small** <br> ``string`` | URL of user's photo with at most 45 pixels on the longest side. |
| **pic_big** <br> ``string`` | URL of user's photo with at most 600 pixels on the longest side. |
| **pic_22** <br> ``string`` | URL of square photo of the user photo with 22 pixels in width. |
| **pic_32** <br> ``string`` | URL of square photo of the user photo with 32 pixels in width. |
| **pic_40** <br> ``string`` | URL of square photo of the user photo with 40 pixels in width. |
| **pic_50** <br> ``string`` | URL of square photo of the user photo with 50 pixels in width. |
| **pic_128** <br> ``string`` | URL of square photo of the user photo with 128 pixels in width. |
| **pic_180** <br> ``string`` | URL of square photo of the user photo with 180 pixels in width. |
| **pic_190** <br> ``string`` | URL of square photo of the user photo with 190 pixels in width. |
| **link** <br> ``string`` | Returns a website address of a user profile. |
| **referer_type** <br> ``string`` | Referrer type. Possible values: <br> <ul> <li>*stream.install*</li> <li>*stream.publish*</li> <li>*invitation*</li> <li>*catalog*</li> <li>*suggests*</li> <li>*left menu suggest*</li> <li>*new apps*</li> <li>*guestbook*</li> <li>*agent*</li> </ul> |
| **referer_id** <br> ``string`` | Identifies where a user came from; see https://api.mail.ru/docs/guides/ref/. |
| **is_online** <br> ``integer, [0,1]`` | Information whether the user is online. |
| **is_friend** <br> ``integer, [0,1]`` | Information whether the user is a friend of current user. |
| **friends_count** <br> ``integer`` | Number of friends. |
| **follower** <br> ``integer, [0,1]`` | Information whether the user is a follower of current user. |
| **following** <br> ``integer, [0,1]`` | Information whether current user is a follower of the user. |
| **subscribe** <br> ``integer, [0,1]`` | Information whether current user is a subscriber of the user. |
| **subscribers_count** <br> ``integer`` | Number of subscribers. |
| **video_count** <br> ``integer`` | Number of videos. |
| **is_verified** <br> ``integer, [0,1]`` | Information whether the user is verified. |
| **vip** <br> ``integer, [0,1]`` | Information whether the user is vip. |
| **app_installed** <br> ``integer, [0,1]`` | Information whether the user has installed the current app. |
| **last_visit** <br> ``integer`` | Date (in Unixtime) of the last user's visit. |
| **cover** <br> ``object`` <br> Returns only with a comment and only for users. | Information about profile's cover; see [Cover](#Cover). |
| **group_info** <br> ``object`` <br> Returns only for groups.  | Object with following fields: <br> <ul> <li> **category_id** ``integer`` </li> <li> **short_description** ``string`` </li> <li> **full_description** ``string`` </li> <li> **interests** ``string`` </li> <li> **posts_cnt** ``integer`` </li> <li> **category_name** ``string`` </li> <li> **rules** ``string`` </li> </ul> |
| **location** <br> ``object``  | Object with following fields: <br> <ul> <li> **country** ``object`` <br> <ul> <li>**name** ``string``</li> <li>**id** ``integer``</li></ul> </li> <li> **city** ``object`` <ul> <li>**name** ``string``</li> <li>**id** ``integer``</li></ul> </li> <li> **region** ``string``<ul> <li>**name** ``string``</li> <li>**id** ``integer``</li></ul> </li> </ul> |



## Event

Object describes an event and contains following fields:

| **field** | **description** |
| --- | --- |
| **thread_id** <br> ``string`` <br> Returns only if current event is commentable. | Comment thread ID in the following format: ``<User's checksum><ID>``. |
| **authors** <br> ``array``| Information about authors; see [User](#User). |
| **type_name** <br> ``string``| Event type name. |
| **click_url** <br> ``string`` <br>  Returns only if event type's name is *micropost*.| Event URL. |
| **likes_count** <br> ``integer`` <br> Returns only if current event is likeable. | Number of "likes". |
| **attachments** <br> ``array``| Information about attachments to the event (link, image, video, audio, user, ...), if any; see [Attachments](#Attachments). |
| **time** <br> ``integer``| Date (in Unixtime) of the event. |
| **huid** <br> ``string`` | Event ID in the following format: ``<User's checksum><Event ID>``. |
| **generator** <br> ``object``| Object with following fields: <br> <ul> <li> **icon** ``string`` - URL of app icon. </li> <li> **url** ``string`` - App url. </li> <li> **app_id** ``integer`` - App ID. </li> <li> **type** ``string`` - App type. </li> <li> **title** ``string`` - App title. </li> </ul>. |
| **user_text** <br> ``string``| User text. |
| **is_liked_by_me** <br> ``integer, [0,1]``| Shows if current user has liked the event. |
| **subtype** <br> ``string``| "event". |
| **is_commentable** <br> ``integer, [0,1]``| Shows if the event is commentable. |
| **type** <br> ``string``| Event type; see [Event types](#event-types). |
| **is_likeable** <br> ``integer, [0,1]``| Shows if the event is likeable. |
| **id** <br> ``string`` | Event ID. |
| **text_media** <br> ``array`` <br> Returns only if event's type name is *micropost*. | Information about text; see [Attachments](#Attachments). |
| **comments_count** <br> ``integer`` <br> Returns only if current event is commentable. | Number of comments. |
| **action_links** <br> ``array`` | Each object contains following fields: <br> <ul> <li> **text** ``string`` </li> <li> **href** ``string`` </li> </ul> |

### Event types

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
* 3-10 TYPE_BLOG_SUBSCRIPTION 
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



## Like

Object wraps an event that a user liked and contains following fields:

| **field** | **description** |
| --------- | ---------------- |
| **time** <br> ``integer``| Date (in Unixtime) of the "like". |
| **author** <br> ``object``| Information about the user; see [User](#User). |
| **huid** <br> ``string`` | Like ID in the following format: ``<User's checksum><Like ID>``. |
| **subevent** <br> ``object``| Information about the event; see [Event](#Event). |
| **subtype** <br> ``string``| "like". |
| **is_commentable** <br> ``integer``| 0. |
| **id** <br> ``string`` | Like ID. |
| **is_likeable** <br> ``integer``| 0. |



## Comment

Object wraps an event that a user commented and contains following fields:

| **field** | **description** |
| --------- | ---------------- |
| **time** <br> ``integer``| Date (in Unixtime) of the comment. |
| **huid** <br> ``string`` | Comment ID in the following format: ``<User's checksum><Comment ID>``. |
| **subevent** <br> ``object``| Information about the event; see [Event](#Event). |
| **subtype** <br> ``string``| "comment". |
| **comment** <br> ``object`` | Object with following fields: <br> <ul> <li> **text** ``string`` - Text. </li> <li> **time** ``integer`` - Date (in Unixtime) of the comment. </li> <li> **is_deleted** ``integer`` - Shows if the comment deleted. </li> <li> **id** ``string`` - Comment ID. </li> <li> **author** ``object`` - Information about the user; see [User](#User). </li> <li> **text_media** ``object`` - Object with fields **object** ``string`` and **content** ``string``. </li> </ul> |
| **is_commentable** <br> ``integer``| 0. |
| **id** <br> ``string`` | Comment ID. |
| **is_likeable** <br> ``integer``| 0. |



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
| **object** <br> ``string, ["text"]`` |
| **content** <br> ``string`` |

### tag

contains one additional field **content** with an object with following fields:

| **field** |
| --- |
| **is_blacklist** <br> ``integer, [0,1]`` |
| **tag** <br> ``string`` |

### link

contains one additional field **content** with an object with following fields:

| **field** |
| --- |
| **type-id** <br> ``string, ["text"]`` |
| **contents** <br> ``string`` |

or contains following fields:

| **field** |
| --- |
| **object** <br> ``string, ["link"]`` |
| **text** <br> ``string`` |
| **url** <br> ``string`` |

### avatar

contains one additional field **new** with an object with following fields:

| **field** |
| --- |
| **thread_id** <br> ``string`` |
| **width** <br> ``integer`` |
| **click_url** <br> ``string`` |
| **album_id** <br> ``string`` |
| **src** <br> ``string`` |
| **height** <br> ``integer`` |
| **desc** <br> ``string`` |
| **src_hires** <br> ``string`` |
| **id** <br> ``string`` |
| **owner_id** <br> ``string`` |

### image

contains following fields:

| **field** |
| --- |
| **likes_count** <br> ``integer`` |
| **thread_id** <br> ``string`` |
| **width** <br> ``string`` |
| **object** <br> ``string, ["image"]`` |
| **click_url** <br> ``string`` |
| **album_id** <br> ``string`` |
| **src** <br> ``string`` |
| **resized_src** <br> ``string`` |
| **height** <br> ``string`` |
| **src_filed** <br> ``string`` |
| **src_hires** <br> ``string`` |
| **id** <br> ``string`` |
| **owner_id** <br> ``string`` |
| **comments_count** <br> ``integer`` |

All fields but **object** and **src** may not be returned.

### music

contains following fields:

| **field** |
| --- |
| **is_add** <br> ``integer`` |
| **click_url** <br> ``string`` |
| **object** <br> ``string, ["music"]`` |
| **name** <br> ``string`` |
| **author** <br> ``string`` |
| **duration** <br> ``integer`` |
| **file_url** <br> ``string`` |
| **uploader** <br> ``string`` |
| **mid** <br> ``string`` |

### video

contains following fields:

| **field** |
| --- |
| **width** <br> ``integer`` |
| **object** <br> ``string, ["video"]`` |
| **album_id** <br> ``string`` |
| **view_count** <br> ``integer`` |
| **desc** <br> ``string`` |
| **comments_count** <br> ``integer`` |
| **likes_count** <br> ``integer`` |
| **thread_id** <br> ``string`` |
| **image_filed** <br> ``string`` |
| **click_url** <br> ``string`` |
| **src** <br> ``string`` |
| **duration** <br> ``integer`` |
| **height** <br> ``integer`` |
| **is_liked_by_me** <br> ``integer, [0,1]`` |
| **external_id** <br> ``string`` |
| **owner_id** <br> ``string`` |
| **title** <br> ``string`` |

### app

contains one additional field **content** with an object with following fields:

| **field** |
| --- |
| **PublishStatus** <br> ``object`` <br> Object with following fields: <br> <ul> <li> **My** ``string`` </li> <li> **Mobile** ``string`` </li> </ul> |
| **ID** <br> ``string`` |
| **InstallationsSpaced** <br> ``string`` |
| **ShortName** <br> ``string`` |
| **Genre** <br> ``array`` <br> Each object contains following fields: <br> <ul> <li> **name** ``string`` </li> <li> **id** ``string`` </li> <li> **admin_genre** ``integer, [0,1]`` </li> </ul> |
| **Votes** <br> ``object`` <br> Object with following fields: <br> <ul> <li> **VotesSum** ``string`` </li> <li> **VotesCount** ``string`` </li> <li> **VotesStarsWidth** ``string`` </li> <li> **Votes2IntRounded** ``string`` </li> <li> **Votes2DigitRounded** ``string`` </li> </ul> |
| **Installations** <br> ``integer`` |
| **ShortDescription** <br> ``string`` |
| **Name** <br> ``string`` |
| **Description** <br> ``string`` |
| **Pictures** <br> ``object`` |

### group

contains one additional field **content** with an object
that is described [in the separate section](#User).

### gift

contains one additional field **content** with an object with following fields:

| **field** |
| --- |
| **is_private** <br> ``integer, [0,1]`` |
| **click_url** <br> ``string`` |
| **is_anonymous** <br> ``integer, [0,1]`` |
| **time** <br> ``integer`` |
| **is_read** <br> ``integer, [0,1]`` |
| **to** <br> ``object`` <br> see [User](#User). |
| **gift** <br> ``object`` |
| **from** <br> ``object`` <br> see [User](#User). |
| **text** <br> ``string`` |
| **rus_time** <br> ``string`` |
| **long_id** <br> ``string`` |



## Other

Objects that are not classified.

### Cover

Object contains information about profile's cover.

| **field** |
| --- |
| **cover_position** <br> ``string`` |
| **width** <br> ``string`` |
| **size** <br> ``string`` |
| **aid** <br> ``string`` |
| **pid** <br> ``string`` |
| **thread_id** <br> ``string`` |
| **owner** <br> ``string`` |
| **target_album** <br> ``object`` <br> Information about target album; <br> see [Target Album](#target-album). |
| **click_url** <br> ``string`` |
| **src** <br> ``string`` |
| **height** <br> ``string`` |
| **cover_width** <br> ``string`` |
| **created** <br> ``string`` |
| **comment** <br> ``string`` |
| **src_small** <br> ``string`` |
| **cover_height** <br> ``string`` |
| **title** <br> ``string`` |



### Target Album

Object contains information about cover's target album.

| **field** |
| --- |
| **link** <br> ``string`` |
| **owner** <br> ``string`` |
| **sort_order** <br> ``string`` |
| **sort_by** <br> ``string`` |
| **description** <br> ``string`` |
| **privacy_desc** <br> ``string`` |
| **size** <br> ``integer`` |
| **aid** <br> ``string`` |
| **created** <br> ``integer`` |
| **cover_pid** <br> ``string`` |
| **cover_url** <br> ``string`` |
| **is_commentable** <br> ``integer, [0,1]`` |
| **title** <br> ``string`` |
| **updated** <br> ``integer`` |
| **privacy** <br> ``integer`` |
| **can_read_comment** <br> ``integer, [0,1]`` |
