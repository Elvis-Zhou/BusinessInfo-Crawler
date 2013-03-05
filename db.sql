DROP TABLE "main"."Urls_Amarillas";
CREATE TABLE "Urls_Amarillas" (
"Keyword"  TEXT,
"Title"  TEXT,
"Url"  TEXT,
"Country"  TEXT,
"Dealed"  TEXT DEFAULT 0,
PRIMARY KEY ("Url" ASC)
);
DROP TABLE "main"."Information";
CREATE TABLE "Information" (
"Keyword"  TEXT,
"Url"  TEXT,
"Name"  TEXT,
"Country"  TEXT,
"Email"  TEXT,
"Address"  TEXT,
"Tel"  TEXT,
"RawInformation"  TEXT,
PRIMARY KEY ("Name" ASC, "Email" ASC)
);
DROP TABLE "main"."Urls";
CREATE TABLE "Urls" (
"Keyword"  TEXT,
"Title"  TEXT,
"Url"  TEXT,
"Country"  TEXT,
"Dealed"  TEXT,
PRIMARY KEY ("Url" ASC)
);