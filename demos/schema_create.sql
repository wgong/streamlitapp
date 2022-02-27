create table if not exists  s_user (
    id INTEGER PRIMARY KEY,
    username UNIQUE ON CONFLICT REPLACE, 
    password,
    notes,
    flag_admin,

    flag_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by
);

create table if not exists  s_journal (
    id INTEGER PRIMARY KEY,
    title UNIQUE ON CONFLICT REPLACE, 
    category,
    sub_category,
    notes,

    url_blog,
    url_video,
    url_git,
    url_twit,

    attachments ,
    flag_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by
);

create table if not exists  s_person (
    id INTEGER PRIMARY KEY,
    full_name UNIQUE ON CONFLICT REPLACE,

    email,
    phone,
    notes,

    url_twit,
    url_fb,
    address,
    related_persons,

    attachments ,
    flag_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by
);

create table if not exists  s_feedback (
    id INTEGER PRIMARY KEY,
    title UNIQUE ON CONFLICT REPLACE, 
    category,
    notes,

    attachments ,
    flag_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by    
);

create table if not exists  s_task (
    id INTEGER PRIMARY KEY,
    title UNIQUE ON CONFLICT REPLACE, 
    category
    notes,

    priority,
    due_date,
    pct_complete,
    related_tasks,
    related_persons,

    attachments ,
    flag_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by 
);

create table if not exists  s_event (
    id INTEGER PRIMARY KEY,
    title UNIQUE ON CONFLICT REPLACE, 
    category
    notes,

    event_host,
    event_datetime,
    event_location,

    attachments ,
    flag_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by  
);