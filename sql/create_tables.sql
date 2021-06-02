create table sound_effect (
    id int primary key auto_increment,
	regex varchar(200),
	description varchar(100),
	abbreviation varchar(20),
	filename varchar(100)
);
create table sound_tag (
    id int primary key auto_increment,
    name varchar(100)
);
create table effect_tag (
    sound_effect_id int,
    sound_tag_id int,
    Primary key (sound_effect_id, sound_tag_id),
    constraint constraint_fk_sound_effect
        foreign key fk_sound_effect (sound_effect_id) references sound_effect (id)
        on delete cascade on update cascade,
    constraint constraint_fk_sound_tag
        foreign key fk_sound_tag (sound_tag_id) references sound_tag (id)
        on delete restrict on update cascade
);
create table revision_num (
    id int primary key auto_increment,
    type varchar(20),
    num int
);