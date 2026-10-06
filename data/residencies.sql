BEGIN TRANSACTION;
CREATE TABLE checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT,
    checked_at TEXT,
    ok INTEGER,
    status TEXT,
    via TEXT,
    n_items INTEGER,
    changed INTEGER
);
INSERT INTO "checks" VALUES(1,'hca-search-new-grad','2026-10-06T22:27:42Z',0,'HTTP 403','browser',0,0);
INSERT INTO "checks" VALUES(2,'dejobs-dfw-residency','2026-10-06T22:27:42Z',1,'HTTP 202','browser',1,0);
INSERT INTO "checks" VALUES(3,'thr-graduate-nurse','2026-10-06T22:27:42Z',1,'HTTP 200','http',3,0);
INSERT INTO "checks" VALUES(4,'thr-search-residency','2026-10-06T22:27:42Z',0,'HTTP 403','http',0,0);
INSERT INTO "checks" VALUES(5,'cook-nurse-residency','2026-10-06T22:27:42Z',1,'HTTP 200','http',7,0);
INSERT INTO "checks" VALUES(6,'bsw-students-graduates','2026-10-06T22:27:42Z',1,'HTTP 200','http',6,0);
INSERT INTO "checks" VALUES(7,'bsw-search-residency','2026-10-06T22:27:42Z',1,'HTTP 200','http',0,0);
INSERT INTO "checks" VALUES(8,'jps-nurse-residency','2026-10-06T22:27:42Z',1,'HTTP 200','http',3,0);
INSERT INTO "checks" VALUES(9,'jps-nurse-residency-application','2026-10-06T22:27:42Z',1,'HTTP 200','http',11,0);
INSERT INTO "checks" VALUES(10,'methodist-nurse-residency','2026-10-06T22:27:42Z',1,'HTTP 200','http',1,0);
INSERT INTO "checks" VALUES(11,'adventhealth-nurse-residency','2026-10-06T22:27:42Z',0,'SSLError: HTTPSConnectionPool(host=''careers.adventhealth.com'', port=443): Max retries exceeded with url: /nurseresidency (Caused by SSLError(SSLCertVerificationError(1, ''[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)'')))','http',0,0);
INSERT INTO "checks" VALUES(12,'adventhealth-search-texas','2026-10-06T22:27:42Z',0,'HTTP 403','http',0,0);
INSERT INTO "checks" VALUES(13,'utsw-nursing-residency','2026-10-06T22:27:42Z',0,'HTTP 403','http',0,0);
INSERT INTO "checks" VALUES(14,'parkland-residency-eligibility','2026-10-06T22:27:42Z',0,'HTTP 404','http',0,0);
INSERT INTO "checks" VALUES(15,'parkland-careers','2026-10-06T22:27:42Z',1,'HTTP 200','browser',0,0);
INSERT INTO "checks" VALUES(16,'childrens-nurse-residency','2026-10-06T22:27:42Z',1,'HTTP 200','http',2,0);
INSERT INTO "checks" VALUES(17,'va-pbrnr','2026-10-06T22:27:42Z',1,'HTTP 200','http',7,0);
INSERT INTO "checks" VALUES(18,'usajobs-nurse-residency-dallas','2026-10-06T22:27:42Z',1,'HTTP 200','browser',0,0);
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    at TEXT,
    source_id TEXT,
    finding_id TEXT,
    type TEXT,            -- new_posting | new_date | now_open | upgraded | removed | page_changed | source_failing | source_recovered
    level TEXT,           -- high | medium | low
    message TEXT,
    url TEXT,
    notified INTEGER DEFAULT 0
);
CREATE TABLE findings (
    id TEXT PRIMARY KEY,
    source_id TEXT,
    system_id TEXT,
    kind TEXT,            -- posting | snippet
    title TEXT,
    url TEXT,
    cohort TEXT,          -- dates mentioned, e.g. "October 2027"
    relevance TEXT,       -- target | maybe | unknown | early | late
    signal TEXT,          -- open | closed | ''
    hospital_id TEXT,
    first_seen TEXT,
    last_seen TEXT,
    active INTEGER DEFAULT 1,
    missed INTEGER DEFAULT 0
);
INSERT INTO "findings" VALUES('dejobs-dfw-residency:4c3a5c351c9f8145','dejobs-dfw-residency','aggregators','posting','Graduate Nurse (GN) Residency- Medical Intensive Care Unit (MICU)-February 2027 Texas Health Resources - Dallas, TX Posted today','https://dejobs.org/dallas-tx/graduate-nurse-gn-residency-medical-intensive-care-unit-micu-february-2027/9BEA007E1FAB4AEF924B9FF911C77097/job/','February 2027','early','','thr-dallas','2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('thr-graduate-nurse:ce028086de20a326','thr-graduate-nurse','thr','posting','Check Out Our GN Positions*','https://jobs.texashealth.org/listjobs/?keyword=(GN%20OR%20%22Graduate%20Nurse%22)%20AND%20Residency&category=RN%2FRegistered%20Nurse','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('thr-graduate-nurse:fcb2286c1fe96db6','thr-graduate-nurse','thr','posting','Opportunities for Graduate Nurses','https://jobs.texashealth.org/professions/graduate-nurse/','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('thr-graduate-nurse:267a9950387e32d7','thr-graduate-nurse','thr','posting','Graduate Nurse Residency Program','https://jobs.texashealth.org/professions/graduate-nurse/','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:11dd1d105de65a6d','cook-nurse-residency','cook','posting','Nurse Residency Program','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program/','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:c0e8b04c74ff2e62','cook-nurse-residency','cook','snippet','February and April 2027 Cohorts','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','April 2027','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:9072fe1f2595db82','cook-nurse-residency','cook','snippet','Please apply if you have graduated with a BSN or entry-level MSN between August and December 2026.','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','December 2026','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:f9ed667543f6ff56','cook-nurse-residency','cook','snippet','October 5, 2026','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','October 5, 2026','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:c482bea85827f816','cook-nurse-residency','cook','snippet','Feb. 8 and April 5, 2027','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','April 5, 2027','early','open',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:d4e20f4f2598a469','cook-nurse-residency','cook','snippet','Feb. 2027: Accepting applications for both clinical tracks (','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','Feb. 2027','early','open',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:05cae3cd90f6e130','cook-nurse-residency','cook','snippet','April 2027: Accepting applications for Medical-Surgical and Subspecialty Nursing track only. Please see the','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','April 2027','early','open',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:8d5c0731e5a093b3','bsw-students-graduates','bsw','snippet','Graduate Nurse Winter 2027 Residency Program','https://jobs.bswhealth.com/us/en/students-graduates','Winter 2027','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:00a46be7999862f8','bsw-students-graduates','bsw','snippet','Beginning September 7, 2026','https://jobs.bswhealth.com/us/en/students-graduates','September 7, 2026','early','open',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:e9d30e4037335fce','bsw-students-graduates','bsw','snippet','September 27, 2026','https://jobs.bswhealth.com/us/en/students-graduates','September 27, 2026','early','open',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:a2cc894f6802bdc2','bsw-students-graduates','bsw','snippet','For current Baylor Scott & White team members, applications open August 17, 2026.','https://jobs.bswhealth.com/us/en/students-graduates','August 17, 2026','early','open',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:96a543b5e77c2786','bsw-students-graduates','bsw','snippet','Beginning in October 2026','https://jobs.bswhealth.com/us/en/students-graduates','October 2026','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:cf41f34ade7dbb56','bsw-students-graduates','bsw','snippet','Beginning January 25, 2027','https://jobs.bswhealth.com/us/en/students-graduates','January 25, 2027','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency:8bffb29dbf007893','jps-nurse-residency','jps','posting','Nurse Residency','https://jpshealthnet.org/nurse-residency#NurseResidencyProgram','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency:19b60efccacfa02a','jps-nurse-residency','jps','posting','Nurse Residency Information','https://jpshealthnet.org/nurse-residency','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency:854b380f3a708ab7','jps-nurse-residency','jps','posting','Nurse Residency Tracks','https://jpshealthnet.org/careers/nurse-residency-tracks#NRTracks','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:8bffb29dbf007893','jps-nurse-residency-application','jps','posting','Nurse Residency','https://jpshealthnet.org/nurse-residency#NurseResidencyProgram','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:2f4f16a5e9e93847','jps-nurse-residency-application','jps','posting','Nurse Residency Information','https://jpshealthnet.org/careers/nurse-residency-application','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:854b380f3a708ab7','jps-nurse-residency-application','jps','posting','Nurse Residency Tracks','https://jpshealthnet.org/careers/nurse-residency-tracks#NRTracks','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:9c2a67f8b7d25dde','jps-nurse-residency-application','jps','snippet','Week of February 9, 2026','https://jpshealthnet.org/careers/nurse-residency-application','February 9, 2026','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:2d6e1b5c3882698f','jps-nurse-residency-application','jps','snippet','July/August 2026','https://jpshealthnet.org/careers/nurse-residency-application','August 2026','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:17232974f1fc6051','jps-nurse-residency-application','jps','snippet','Week of June 15, 2026','https://jpshealthnet.org/careers/nurse-residency-application','June 15, 2026','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:d6900ece7a5f9960','jps-nurse-residency-application','jps','snippet','October 2026','https://jpshealthnet.org/careers/nurse-residency-application','October 2026','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:e3e3fe0c95934bfd','jps-nurse-residency-application','jps','snippet','Week of October 12, 2026','https://jpshealthnet.org/careers/nurse-residency-application','October 12, 2026','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:a5b72ea49cd2b69d','jps-nurse-residency-application','jps','snippet','February/March 2027','https://jpshealthnet.org/careers/nurse-residency-application','March 2027','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:6310f0798e149c24','jps-nurse-residency-application','jps','snippet','Internal January 1, 2026 – January 22, 2026','https://jpshealthnet.org/careers/nurse-residency-application','January 1, 2026, January 22, 2026','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:9531fa5752f6c3af','jps-nurse-residency-application','jps','snippet','External September 1, 2026 – September 8, 2026','https://jpshealthnet.org/careers/nurse-residency-application','September 1, 2026, September 8, 2026','early','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('methodist-nurse-residency:ec51835a1b4f17c9','methodist-nurse-residency','methodist','snippet','Applications for the February 2027 cohort are open!','https://www.methodisthealthsystem.org/careers/nurse-residency','February 2027','early','','methodist-dallas','2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('childrens-nurse-residency:b2b4be75f8e5f30a','childrens-nurse-residency','childrens','posting','Vizient/AACN Nurse Residency','https://www.childrens.com/for-healthcare-professionals/education-training/nurse-residency','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('childrens-nurse-residency:affa27cae3eab506','childrens-nurse-residency','childrens','snippet','February 2027 Nurse Residency Program','https://www.childrens.com/for-healthcare-professionals/education-training/nurse-residency','February 2027','early','open',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('va-pbrnr:a2b264c0f47c40be','va-pbrnr','va','posting','Post-baccalaureate registered nurse residency program','https://www.va.gov/north-texas-health-care/work-with-us/internships-and-fellowships/post-baccalaureate-registered-nurse-residency-program/','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('va-pbrnr:bf65de06466547fa','va-pbrnr','va','posting','PBRNR program goals','https://www.va.gov/north-texas-health-care/work-with-us/internships-and-fellowships/post-baccalaureate-registered-nurse-residency-program/','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('va-pbrnr:91a0ae1712e9ee69','va-pbrnr','va','posting','PBRNR program outcome','https://www.va.gov/north-texas-health-care/work-with-us/internships-and-fellowships/post-baccalaureate-registered-nurse-residency-program/','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('va-pbrnr:3f6af98005106180','va-pbrnr','va','posting','PBRNR program structure','https://www.va.gov/north-texas-health-care/work-with-us/internships-and-fellowships/post-baccalaureate-registered-nurse-residency-program/','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('va-pbrnr:f307bca76aa8c9a9','va-pbrnr','va','posting','PBRNR program minimum qualifications','https://www.va.gov/north-texas-health-care/work-with-us/internships-and-fellowships/post-baccalaureate-registered-nurse-residency-program/','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('va-pbrnr:8f8c2deab6314105','va-pbrnr','va','posting','PBRNR program salary and benefits','https://www.va.gov/north-texas-health-care/work-with-us/internships-and-fellowships/post-baccalaureate-registered-nurse-residency-program/','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
INSERT INTO "findings" VALUES('va-pbrnr:7b5cc80304b5378c','va-pbrnr','va','posting','PBRNR program faculty','https://www.va.gov/north-texas-health-care/work-with-us/internships-and-fellowships/post-baccalaureate-registered-nurse-residency-program/','','unknown','',NULL,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z',1,0);
CREATE TABLE sources (
    id TEXT PRIMARY KEY,
    system_id TEXT,
    url TEXT,
    kind TEXT,
    baseline_done INTEGER DEFAULT 0,
    last_checked TEXT,
    last_ok TEXT,
    last_status TEXT,
    last_error TEXT,
    last_via TEXT,
    last_hash TEXT,
    page_signal TEXT,
    n_items INTEGER DEFAULT 0,
    consecutive_failures INTEGER DEFAULT 0
);
INSERT INTO "sources" VALUES('hca-search-new-grad','medical-city','https://careers.hcahealthcare.com/search/jobs/in/texas?q=new+grad+residency','jobs',0,'2026-10-06T22:27:42Z',NULL,'error','HTTP 403','browser',NULL,NULL,0,1);
INSERT INTO "sources" VALUES('dejobs-dfw-residency','aggregators','https://dejobs.org/jobs/?q=nurse+residency&location=Dallas%2C+TX','jobs',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'browser','b100b47c54833306','',1,0);
INSERT INTO "sources" VALUES('thr-graduate-nurse','thr','https://jobs.texashealth.org/professions/graduateNurse','jobs',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'http','ce1ef4225148e6cd','',3,0);
INSERT INTO "sources" VALUES('thr-search-residency','thr','https://jobs.texashealth.org/search-jobs/graduate%20nurse%20residency','jobs',0,'2026-10-06T22:27:42Z',NULL,'error','HTTP 403','http',NULL,NULL,0,1);
INSERT INTO "sources" VALUES('cook-nurse-residency','cook','https://cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','page',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'http','5b74153c990c3273','open',7,0);
INSERT INTO "sources" VALUES('bsw-students-graduates','bsw','https://jobs.bswhealth.com/us/en/students-graduates','page',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'http','459ca5f0c5c2358c','open',6,0);
INSERT INTO "sources" VALUES('bsw-search-residency','bsw','https://jobs.bswhealth.com/us/en/search-results?keywords=graduate%20nurse%20residency','jobs',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'http','d30f1895b73ca11e','',0,0);
INSERT INTO "sources" VALUES('jps-nurse-residency','jps','https://jpshealthnet.org/node/1188','page',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'http','fe88087dd8a0a137','open',3,0);
INSERT INTO "sources" VALUES('jps-nurse-residency-application','jps','https://jpshealthnet.org/node/1241','page',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'http','9b0eb405dbe2ce54','open',11,0);
INSERT INTO "sources" VALUES('methodist-nurse-residency','methodist','https://www.methodisthealthsystem.org/careers/nurse-residency','page',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'http','cbe8296638d99ac5','',1,0);
INSERT INTO "sources" VALUES('adventhealth-nurse-residency','adventhealth','https://careers.adventhealth.com/nurseresidency','page',0,'2026-10-06T22:27:42Z',NULL,'error','SSLError: HTTPSConnectionPool(host=''careers.adventhealth.com'', port=443): Max retries exceeded with url: /nurseresidency (Caused by SSLError(SSLCertVerificationError(1, ''[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)'')))','http',NULL,NULL,0,1);
INSERT INTO "sources" VALUES('adventhealth-search-texas','adventhealth','https://jobs.adventhealth.com/search-jobs/nurse%20residency/Texas','jobs',0,'2026-10-06T22:27:42Z',NULL,'error','HTTP 403','http',NULL,NULL,0,1);
INSERT INTO "sources" VALUES('utsw-nursing-residency','utsw','https://jobs.utsouthwestern.edu/nursing-residency/','jobs',0,'2026-10-06T22:27:42Z',NULL,'error','HTTP 403','http',NULL,NULL,0,1);
INSERT INTO "sources" VALUES('parkland-residency-eligibility','parkland','https://www.parklandhealth.org/eligibility-requirements','page',0,'2026-10-06T22:27:42Z',NULL,'error','HTTP 404','http',NULL,NULL,0,1);
INSERT INTO "sources" VALUES('parkland-careers','parkland','https://www.parklandcareers.com/','jobs',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'browser','1b2babc9a1f959d8','',0,0);
INSERT INTO "sources" VALUES('childrens-nurse-residency','childrens','https://www.childrens.com/for-healthcare-professionals/education-training/nurse-residency','page',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'http','39fa148f11392bfe','open',2,0);
INSERT INTO "sources" VALUES('va-pbrnr','va','https://www.va.gov/north-texas-health-care/work-with-us/internships-and-fellowships/post-baccalaureate-registered-nurse-residency-program/','page',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'http','549da2c46f2e37c3','',7,0);
INSERT INTO "sources" VALUES('usajobs-nurse-residency-dallas','va','https://www.usajobs.gov/search/results/?k=nurse%20residency&l=Dallas%2C%20Texas','jobs',1,'2026-10-06T22:27:42Z','2026-10-06T22:27:42Z','ok',NULL,'browser','029861c8f68a5922','',0,0);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('checks',18);
COMMIT;
