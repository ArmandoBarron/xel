CREATE TABLE hierarchy(
    keyhierarchy varchar(100),
    acronym varchar(20),
    fullname varchar(200),
    tokenhierarchy varchar(100),    
    father varchar(100) NOT NULL,
    PRIMARY KEY (keyhierarchy),
    UNIQUE(tokenhierarchy)    
);

CREATE TABLE token_mapping(
    keyhierarchy varchar(100),
    tokenorg varchar(100),        
    PRIMARY KEY (keyhierarchy,tokenorg),
    CONSTRAINT Ref_mappint_to_hierarchy FOREIGN KEY (keyhierarchy) REFERENCES hierarchy(keyhierarchy) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT Ref_mappint_to_tokenhierarchy FOREIGN KEY (tokenorg) REFERENCES hierarchy(tokenhierarchy) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "users" (
    "keyuser" varchar(100) COLLATE "default" NOT NULL,
    "username" varchar(100) COLLATE "default",
    "email" varchar(200) NOT NULL,
    "password" varchar(100) COLLATE "default",
    "tokenuser" varchar(100),
    "tokenorg" varchar(100),
    "access_token" varchar(200),
    "apikey" varchar(150) COLLATE "default",
    "isactive" boolean NOT NULL DEFAULT false,
    "isadmin" boolean NOT NULL DEFAULT false,
    "code" varchar(100),
    "created_at" timestamp DEFAULT NOW(),
    "dateexp" timestamp DEFAULT NOW() + INTERVAL '2 hour',
    --"dateexp" timestamp DEFAULT NOW() + time '00:01',
    PRIMARY KEY ("keyuser"),
    UNIQUE (username),
    UNIQUE (email),
    UNIQUE (access_token),
    CONSTRAINT Ref_users_to_hierarchy FOREIGN KEY (tokenorg) REFERENCES hierarchy(tokenhierarchy) ON DELETE CASCADE ON UPDATE CASCADE
    
)WITHOUT OIDS;

ALTER TABLE "users" OWNER TO "postgres";





CREATE TABLE "logs" (
    "id" serial NOT NULL,
    "operation" varchar(100) COLLATE "default",
    "token" varchar(200) COLLATE "default",
    "newtoken" varchar(200) COLLATE "default",
    "ipadress" varchar(100) COLLATE "default",
    "status" varchar(100) COLLATE "default",
    "created_at" timestamp DEFAULT NOW() NOT NULL,
    PRIMARY KEY (id)
)WITHOUT OIDS;

ALTER TABLE "logs" OWNER TO "postgres";


--INSERT INTO hierarchy(keyhierarchy, acronym, fullname,tokenhierarchy, father) VALUES ('7e493e1d2282c9afdf2822bab34ca6e54606aa50','public','public','db194dd4022cac66bcc522a82cfe8cf19bf88f555990a8fce33c32da75444931','/');
--INSERT INTO token_mapping(keyhierarchy,tokenorg) VALUES ('7e493e1d2282c9afdf2822bab34ca6e54606aa50','db194dd4022cac66bcc522a82cfe8cf19bf88f555990a8fce33c32da75444931');
--INSERT INTO users(keyuser,username,email,password,tokenuser,tokenorg,access_token,apikey,isactive,isadmin) VALUES ('ac16d263ae5ae6892d9b1ee5162b3afba5dca3eb','admin','admin@email.com','$2a$10$852f5e6e669b01dfce1d7u07nPnvWEcJF9AMUzoYNXYhEAaLFwc2m','f3cde3d296c8e1bd2239f2772b3569a1483c496f977791644380f5f1463384ec','db194dd4022cac66bcc522a82cfe8cf19bf88f555990a8fce33c32da75444931','f3cde3d296c8e1bd2239f2772b3569a1483c496f977791644380f5f1463384e3','597d7f5f03bb3e724dcc18b65bddd908e1fda20e',true,true);


INSERT INTO hierarchy(keyhierarchy, acronym, fullname,tokenhierarchy, father) VALUES ('5826a284a1e6f364869066976f1ba0ca4a253430','XEL','Muyal-Xelhua','ed4ade2b846402b9ae56c75e1df923c71a1a081a339dccb7fa9d2c22194ddaff','/');
INSERT INTO token_mapping(keyhierarchy,tokenorg) VALUES ('5826a284a1e6f364869066976f1ba0ca4a253430','ed4ade2b846402b9ae56c75e1df923c71a1a081a339dccb7fa9d2c22194ddaff');