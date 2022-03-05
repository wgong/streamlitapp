create table if not exists  t_user (
    id INTEGER PRIMARY KEY,
    username UNIQUE ON CONFLICT REPLACE, 
    password,
    notes,
    is_admin,

    is_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by
);

create table if not exists  t_person (
    id INTEGER PRIMARY KEY,
    full_name UNIQUE ON CONFLICT REPLACE,

    email,
    phone,
    notes,

    twitter_link,
    facebook_link,
    linkedin_link,

    addresses,
    related_persons,

    attachments ,
    is_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by
);

create table if not exists  t_note (
    id INTEGER PRIMARY KEY,
    title UNIQUE ON CONFLICT REPLACE, 
    category,
    sub_category,
    notes,

    blog_link,
    video_link,
    git_link,
    twitter_link,

    attachments ,
    is_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by
);



create table if not exists  t_feedback (
    id INTEGER PRIMARY KEY,
    title UNIQUE ON CONFLICT REPLACE, 
    category,
    notes,

    attachments ,
    is_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by    
);

create table if not exists  t_task (
    id INTEGER PRIMARY KEY,
    title UNIQUE ON CONFLICT REPLACE, 
    category,
    notes,

    priority,
    due_date,
    pct_complete,
    related_tasks,
    related_persons,

    attachments ,
    is_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by 
);

create table if not exists  t_event (
    id INTEGER PRIMARY KEY,
    title UNIQUE ON CONFLICT REPLACE, 
    category,
    notes,

    event_host,
    event_datetime,
    event_location,

    attachments ,
    is_active ,
    added_at ,
    edited_at ,
    added_by ,
    edited_by  
);