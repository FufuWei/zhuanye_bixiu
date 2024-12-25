/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     2023/4/12 12:46:23                           */
/*==============================================================*/


drop table if exists "Order";

drop table if exists User;

drop table if exists manager;

drop table if exists seller;

/*==============================================================*/
/* Table: "Order"                                               */
/*==============================================================*/
create table "Order"
(
   order_id             int not null,
   u_id                 int,
   u_idcard             char(18),
   train_id             char(256),
   ticket_type          char(256),
   price                float,
   order_time           timestamp,
   bill_id              int,
   if_refund            int,
   start_place          char(256),
   end_place            char(256),
   start_time           char(256),
   primary key (order_id)
);

/*==============================================================*/
/* Table: User                                                  */
/*==============================================================*/
create table User
(
   u_id                 int not null,
   u_name               char(256),
   u_password           char(256),
   u_phone              char(256),
   u_idcard             char(18),
   date                 char(256),
   u_authority          char(256),
   u_sex                char(256),
   primary key (u_id)
);

/*==============================================================*/
/* Table: manager                                               */
/*==============================================================*/
create table manager
(
   u_id                 int not null,
   operator_time        datetime,
   primary key (u_id)
);

/*==============================================================*/
/* Table: seller                                                */
/*==============================================================*/
create table seller
(
   u_id                 int not null,
   project              char(256),
   primary key (u_id)
);

alter table "Order" add constraint FK_buy foreign key (u_id)
      references User (u_id);

alter table manager add constraint FK_Inheritance_1 foreign key (u_id)
      references User (u_id);

alter table seller add constraint FK_Inheritance_2 foreign key (u_id)
      references User (u_id);

