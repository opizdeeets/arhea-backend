                                        " MediaAsset "

## MediaAsset
MediaAsset
- id (UUID, PK)
- file_path (text, not null)
- file_name (text, not null)
- mime_type (text, not null)
- file_size (int, not null)
- width (int, nullable)         # если это изображение
- height (int, nullable)
- created_at (timestamptz, default now())

# MediaAsset_i18n
- media_asset_id (FK → media_asset.id on delete cascade)
- locale (enum('en', 'ru', 'tk') not null)
- alt_text (text)
- unique(media_asset_id, locale)                                   
                                        
                                        
                                        
                                        " Project "

## Project
- id (UUID, PK)
- cover_media_id (uuid fk -> media_asset.id) # тут единая таблица для всех видов медиа в проекте, к ней будут привязаны и gallery_images and gallery_drawing.
- slug (text, unique, not null), генерится автоматически из name, остается неизменяемым.
- type_id (FK → project_type.id)
- location_id (FK → location.id)
- year (int)
- created_at (timestamptz)
- updated_at (timestamptz)
- area_m2 (numeric(10,2))
- is_published (bool)
- published_at (timestamptz)
- order_index (int, default 0)


# project_i18n
- project_id (fk -> project.id on delete cascade)
- locale (enum('en', 'ru', 'tk') not null) <- 'en' | 'ru' | 'tk'
- name (text, not null)
- client_name (text)
- subname (text, not null)
- short_description (text)
- full_description (text)
- search_vector (tsvector, generated or stored)
- unique(project_id, locale)

**Indexes**
- unique(slug)
- (is_published, order_index desc)
- (type_id, is_published, order_index desc)
- (location_id, is_published, order_index desc)
- (published_at desc)
- GIN(search_vector)

---

## Projecttype
- id (UUID, PK)
- key (text, unique)
- order_index (int, default 0)
- visible (bool, default true)

# project_type_i18n
- type_id (fk -> project_type.id on delete cascade)
- locale (text not null)
- title (text)
- pk (type_id, locale)
- unique(type_id, locale)

---

## ProjectStyle (modern, minimalist, classic...)
- id (UUID, PK)
- key (text, unique)
- order_index (int, default 0)
- visible (bool, default true)

# project_style_i18n
- style_id(fk -> project_style.id on delete cascade)
- locale (enum('en', 'ru', 'tk') not null)
- title(text not null)
- pk(style_id, locale)
- unique(style_id, locale)

## ProjectStyleLink
- project_id (FK → project.id, on delete cascade)
- style_id (FK → project_style.id, on delete cascade)
- PK (project_id, style_id)

# indexes
- style_id
- project_id

---

## Location
- id (UUID, PK)

# location_i18n
- location_id(fk -> location.id on delete cascade)
- locale (enum('en', 'ru', 'tk') not null)
- country(text)
- city(text)
- pk (location_id, locale)
- unique(location_id, locale)

---

## ProjectMedia
- id (UUID, PK)
- project_id (FK → project.id, on delete cascade)
- media_id (FK → media_asset.id, on delete cascade)
- kind (text, not null, e.g. 'photo' | 'drawing' | 'hero')
- order_index (int, default 0)

# indexes
- (project_id, kind, order_index)
- unique(project_id, media_id, kind)

---

## Person
- id (UUID, PK)
- slug (text, unique)
- order_index (int, default 0)
- created_at (timestamptz)
- updated_at (timestamptz)

# person_i18n
- person_id (fk -> person.id on delete cascade)
- locale (enum('en', 'ru', 'tk') not null)
- full_name(text, not null)
- unique(person_id, locale)


## ProjectPersonRole
- project_id (FK → project.id, on delete cascade)
- person_id (FK → person.id, on delete cascade)
- role_id (FK → person_role.id)
- order_index (int, default 0)
- PK (project_id, person_id, role_id)


## PersonRole
- id (UUID, PK)
- key (text, unique)
- title (text)
- order_index (int, default 0)

# PersonRole_i18n
- role_id (fk -> personrole.id on delete cascade)
- title
- locale (enum('en', 'ru', 'tk') not null)
- pk(role_id, locale)
- unique(role_id, locale)

## PersontypeLink
- person_id (FK → person.id, on delete cascade)
- type_id (FK → person_type.id, on delete cascade)
- PK (person_id, type_id)


## Persontype
- id (UUID, PK)
- key (text, unique)
- title (text)
- order_index (int, default 0)
- visible (bool, default true)

# Persontype_i18n
- persontype_id (fk -> persontype.id on delete cascade)
- title
- locale (enum('en', 'ru', 'tk') not null)
- pk (persontype_id, locale)
- unique(persontype_id, locale)

---


## Career
- id (UUID, PK)
- slug (text, unique)
- is_published (bool, default true)
- order_index (int, default 0)
- created_at (timestamptz)
- updated_at (timestamptz)

# career_i18n
- career_id (fk -> career.id on delete cascade)
- title(text)
- locale (enum('en', 'ru', 'tk') not null)
- description(text)
- unique(career_id, locale)

---

## JobApplication
- id (UUID, PK)
- career_id (FK → career.id)
- first_name (text)
- last_name (text)
- message (text)
- email (citext)
- phone (text)
- portfolio_media_id (FK → media_asset.id)
- created_at (timestamptz)
- status(enum, default "new")
- processed_at (timestamptz)
- unique(email, portfolio_media_id, created_at::date)


---

## ContactMessage
- id (UUID, PK)
- name (text)
- email (citext)
- message (text)
- created_at (timestamptz)
- processed_at (timestamptz)
- source (text)
- status (enum, default "new")
- unique(email, hash(message), created_at::date)



                              "News & Updates"

## News
- id (uuid, pk)
- slug (text, unique, not null) 
- preview_media_id (uuid, fk -> media_asset.id, nullable)
- is_published (bool, default false)
- published_at (timestamptz)
- created_at (timestamptz)
- updated_at (timestamptz)

# news_i18n
- news_id (FK → news.id on delete cascade)
- locale (enum('en', 'ru', 'tk'), not null)
- title (text, not null)
- short_description (text)
- full_description (text)
- search_vector (tsvector generated/stored)
- unique(news_id, locale)

## NewsMedia
- id(uuid, pk)
- news_id (fk -> news.id on delete cascade)
- media_id (fk -> media_asset.id on delete cascade)
- kind (text not null)
- order_index(int, default 0)

# indexes
- (news_id, kind, order_index)
- unique(news_id, media_id, kind)


                                "Contact"
## Contact Message
- id (uuid, pk)
- name (text)
- email (citext)
- message (text)
- source (text)
- status (enum, default "new")
- created_at (timestamptz)
- processed_at (timestamptz)

- unique (email, hash(message), created_at::date)


## Contact Info
- id (UUID, PK)
- key (text, unique)              
- email (text)
- phone (text)
- address (text)

# ContactInfo_i18n
- contact_info_id (FK → contact_info.id on delete cascade)
- locale (enum('en', 'ru', 'tk'), not null)
- address (text)
- unique(contact_info_id, locale)


                             "EmailLog"
## EmailLog                             
- id (UUID, PK)
- to_email (citext, not null)
- subject (text, not null)
- body (text, not null)
- template_name (text, nullable)
- related_object_id (UUID, nullable)
- related_object_type (text, nullable)  # 'application', 'contact_message', etc.
- status (enum('pending', 'sent', 'failed'), default 'pending')
- sent_at (timestamptz, nullable)
- error_message (text, nullable)
- created_at (timestamptz, default now())                  

                             "PageMeta"
## PageMeta
- id (UUID, PK)
- page_slug (text, unique, not null)  # например: 'about-us', 'projects', 'contact-us'
- created_at (timestamptz, default now())

# PageMeta_i18n
- page_meta_id (FK → page_meta.id on delete cascade)
- locale (enum('en', 'ru', 'tk') not null)
- meta_title (text)
- meta_description (text)
- og_title (text)
- og_description (text)
- og_image_id (FK → media_asset.id, nullable)
- unique(page_meta_id, locale)


















## MediaAsset

* id (UUID, PK)
* file_path (text, not null)
* file_name (text, not null)
* mime_type (text, not null)
* file_size (int, not null)
* width (int, nullable)
* height (int, nullable)
* created_at (timestamptz, default now())

### MediaAsset_i18n

* media_asset_id (FK → media_asset.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* alt_text (text)
* unique(media_asset_id, locale)

## Project

* id (UUID, PK)
* cover_media_id (UUID, FK → media_asset.id)
* slug (text, unique, not null)
* type_id (FK → project_type.id)
* location_id (FK → location.id)
* year (int)
* created_at (timestamptz)
* updated_at (timestamptz)
* area_m2 (numeric(10,2))
* is_published (bool)
* published_at (timestamptz)
* order_index (int, default 0)

### project_i18n

* project_id (FK → project.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* name (text, not null)
* client_name (text)
* subname (text, not null)
* short_description (text)
* full_description (text)
* search_vector (tsvector GENERATED ALWAYS AS (...) STORED)
* unique(project_id, locale)
* GIN index on search_vector

## Projecttype

* id (UUID, PK)
* key (text, unique)
* order_index (int, default 0)
* visible (bool, default true)

### project_type_i18n

* type_id (FK → project_type.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* title (text)
* unique(type_id, locale)

## ProjectStyle

* id (UUID, PK)
* key (text, unique)
* order_index (int, default 0)
* visible (bool, default true)

### project_style_i18n

* style_id (FK → project_style.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* title (text, not null)
* unique(style_id, locale)

## ProjectStyleLink

* project_id (FK → project.id on delete cascade)
* style_id (FK → project_style.id on delete cascade)
* PK (project_id, style_id)
* Indexes: style_id, project_id

## Location

* id (UUID, PK)

### location_i18n

* location_id (FK → location.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* country (text)
* city (text)
* unique(location_id, locale)

## ProjectMedia

* id (UUID, PK)
* project_id (FK → project.id on delete cascade)
* media_id (FK → media_asset.id on delete cascade)
* kind (text, not null)
* order_index (int, default 0)
* Indexes: (project_id, kind, order_index), unique(project_id, media_id, kind)

## Person

* id (UUID, PK)
* slug (text, unique)
* order_index (int, default 0)
* created_at (timestamptz)
* updated_at (timestamptz)

### person_i18n

* person_id (FK → person.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* full_name (text, not null)
* unique(person_id, locale)

## ProjectPersonRole

* project_id (FK → project.id on delete cascade)
* person_id (FK → person.id on delete cascade)
* role_id (FK → person_role.id)
* order_index (int, default 0)
* PK (project_id, person_id, role_id)

## PersonRole

* id (UUID, PK)
* key (text, unique)
* title (text)
* order_index (int, default 0)

### person_role_i18n

* role_id (FK → person_role.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* title (text)
* unique(role_id, locale)

## Persontype

* id (UUID, PK)
* key (text, unique)
* title (text)
* order_index (int, default 0)
* visible (bool, default true)

### persontype_i18n

* persontype_id (FK → persontype.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* title (text)
* unique(persontype_id, locale)

## PersontypeLink

* person_id (FK → person.id on delete cascade)
* type_id (FK → persontype.id on delete cascade)
* PK (person_id, type_id)

## Career

* id (UUID, PK)
* slug (text, unique)
* is_published (bool, default true)
* order_index (int, default 0)
* created_at (timestamptz)
* updated_at (timestamptz)

### career_i18n

* career_id (FK → career.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* title (text)
* description (text)
* unique(career_id, locale)

## JobApplication

* id (UUID, PK)
* career_id (FK → career.id)
* first_name (text)
* last_name (text)
* message (text)
* email (citext)
* phone (text)
* portfolio_media_id (FK → media_asset.id)
* created_at (timestamptz)
* status (enum('new', 'reviewed', 'archived'), default 'new')
* processed_at (timestamptz)
* unique(email, portfolio_media_id, created_at::date)

## ContactMessage

* id (UUID, PK)
* name (text)
* email (citext)
* message (text)
* source (text)
* status (enum('new', 'reviewed', 'archived'), default 'new')
* created_at (timestamptz)
* processed_at (timestamptz)
* unique(email, hash(message), created_at::date)

## ContactInfo

* id (UUID, PK)
* key (text, unique)
* email (text)
* phone (text)
* address (text)

### contact_info_i18n

* contact_info_id (FK → contact_info.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* address (text)
* unique(contact_info_id, locale)

## News

* id (UUID, PK)
* slug (text, unique, not null)
* preview_media_id (UUID, FK → media_asset.id, nullable)
* is_published (bool, default false)
* published_at (timestamptz)
* created_at (timestamptz)
* updated_at (timestamptz)

### news_i18n

* news_id (FK → news.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* title (text, not null)
* short_description (text)
* full_description (text)
* search_vector (tsvector GENERATED ALWAYS AS (...) STORED)
* unique(news_id, locale)
* GIN index on search_vector

## NewsMedia

* id (UUID, PK)
* news_id (FK → news.id on delete cascade)
* media_id (FK → media_asset.id on delete cascade)
* kind (text, not null)
* order_index (int, default 0)
* Indexes: (news_id, kind, order_index), unique(news_id, media_id, kind)

## EmailLog

* id (UUID, PK)
* to_email (citext, not null)
* subject (text, not null)
* body (text, not null)
* template_name (text, nullable)
* related_object_id (UUID, nullable)
* related_object_type (text, nullable)
* status (enum('pending', 'sent', 'failed'), default 'pending')
* sent_at (timestamptz, nullable)
* error_message (text, nullable)
* created_at (timestamptz, default now())

## PageMeta

* id (UUID, PK)
* page_slug (text, unique, not null)
* created_at (timestamptz, default now())

### page_meta_i18n

* page_meta_id (FK → page_meta.id on delete cascade)
* locale (enum('en', 'ru', 'tk') not null)
* meta_title (text)
* meta_description (text)
* og_title (text)
* og_description (text)
* og_image_id (FK → media_asset.id, nullable)
* unique(page_meta_id, locale)
