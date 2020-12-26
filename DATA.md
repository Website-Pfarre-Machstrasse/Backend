# Data
## User
- Id(uuid)
- First Name(string)
- Last Name(string)
- E-Mail(string)(uniqe)
- Passwort(string)(hash)
- Role(enum)(Admin/Author)
- Pages(list backref [Permission])

## Category
- Id(string)
- Order(int)
- Name(string)
- Pages(list backref [Page])

## Page
- Id(string)
- Order(int)
- Title(string)
- Content(list backref [Change])
- Category(reference [Category])

## Permission
- User(reference [User])
- Page(reference [Page])

## Change
- Id(uuid)
- Changes(json)
- Timestamp(timestamp)
- Page(reference [Page])
- Author(reference [User])

## Gallery
- Id(uuid)
- Title(string)
- Media(list backref [Media])
- Author(reference [User])

## Gallery Media
- Id(uuid)
- Extension(string)
- Mimetype(string)
- Gallery(reference [Gallery])

## Page Media
- Id(uuid)
- Extension(string)
- Mimetype(string)

## Event
- Id(uuid)
- Name(string)
- Details(string)
- Start(timestamp)
- End(timestamp)
- CreatedBy(reference [User])
