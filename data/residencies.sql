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
INSERT INTO "checks" VALUES(1,'hca-dejobs-new-grad','2026-10-06T22:46:53Z',1,'HTTP 202','browser',1,0);
INSERT INTO "checks" VALUES(2,'dejobs-dallas','2026-10-06T22:46:53Z',1,'HTTP 202','browser',1,0);
INSERT INTO "checks" VALUES(3,'dejobs-fort-worth','2026-10-06T22:46:53Z',1,'HTTP 202','browser',0,0);
INSERT INTO "checks" VALUES(4,'dejobs-new-grad-texas','2026-10-06T22:46:53Z',1,'HTTP 202','browser',0,0);
INSERT INTO "checks" VALUES(5,'thr-gn-residency-search','2026-10-06T22:46:53Z',1,'HTTP 200','browser',2,0);
INSERT INTO "checks" VALUES(6,'cook-nurse-residency','2026-10-06T22:46:53Z',1,'HTTP 200','http',6,0);
INSERT INTO "checks" VALUES(7,'bsw-students-graduates','2026-10-06T22:46:53Z',1,'HTTP 200','http',6,0);
INSERT INTO "checks" VALUES(8,'bsw-search-residency','2026-10-06T22:46:53Z',1,'HTTP 200','browser',0,0);
INSERT INTO "checks" VALUES(9,'jps-nurse-residency','2026-10-06T22:46:53Z',1,'HTTP 200','http',0,0);
INSERT INTO "checks" VALUES(10,'jps-nurse-residency-application','2026-10-06T22:46:53Z',1,'HTTP 200','http',8,0);
INSERT INTO "checks" VALUES(11,'methodist-nurse-residency','2026-10-06T22:46:53Z',1,'HTTP 200','http',1,0);
INSERT INTO "checks" VALUES(12,'adventhealth-workday','2026-10-06T22:46:53Z',1,'HTTP 200','api',1,0);
INSERT INTO "checks" VALUES(13,'utsw-nursing-residency','2026-10-06T22:46:53Z',1,'HTTP 200','http',9,0);
INSERT INTO "checks" VALUES(14,'parkland-bridge-program','2026-10-06T22:46:53Z',1,'HTTP 200','http',0,0);
INSERT INTO "checks" VALUES(15,'parkland-workday','2026-10-06T22:46:53Z',1,'HTTP 200','api',0,0);
INSERT INTO "checks" VALUES(16,'childrens-nurse-residency','2026-10-06T22:46:53Z',1,'HTTP 200','http',1,0);
INSERT INTO "checks" VALUES(17,'va-pbrnr','2026-10-06T22:46:53Z',1,'HTTP 200','http',0,0);
INSERT INTO "checks" VALUES(18,'usajobs-nurse-residency-dallas','2026-10-06T22:46:53Z',1,'HTTP 200','browser',0,0);
INSERT INTO "checks" VALUES(19,'hca-dejobs-new-grad','2026-10-07T06:09:41Z',1,'HTTP 202','browser',1,1);
INSERT INTO "checks" VALUES(20,'dejobs-dallas','2026-10-07T06:09:41Z',1,'HTTP 202','browser',1,0);
INSERT INTO "checks" VALUES(21,'dejobs-fort-worth','2026-10-07T06:09:41Z',1,'HTTP 202','browser',0,0);
INSERT INTO "checks" VALUES(22,'dejobs-new-grad-texas','2026-10-07T06:09:41Z',1,'HTTP 202','browser',0,1);
INSERT INTO "checks" VALUES(23,'thr-gn-residency-search','2026-10-07T06:09:41Z',1,'HTTP 200','browser',2,0);
INSERT INTO "checks" VALUES(24,'cook-nurse-residency','2026-10-07T06:09:41Z',1,'HTTP 200','http',6,0);
INSERT INTO "checks" VALUES(25,'bsw-students-graduates','2026-10-07T06:09:41Z',1,'HTTP 200','http',6,0);
INSERT INTO "checks" VALUES(26,'bsw-search-residency','2026-10-07T06:09:41Z',1,'HTTP 200','browser',0,1);
INSERT INTO "checks" VALUES(27,'jps-nurse-residency','2026-10-07T06:09:41Z',1,'HTTP 200','http',0,0);
INSERT INTO "checks" VALUES(28,'jps-nurse-residency-application','2026-10-07T06:09:41Z',1,'HTTP 200','http',8,0);
INSERT INTO "checks" VALUES(29,'methodist-nurse-residency','2026-10-07T06:09:41Z',1,'HTTP 200','http',1,0);
INSERT INTO "checks" VALUES(30,'hca-dejobs-new-grad','2026-10-07T13:35:22Z',1,'HTTP 202','browser',1,0);
INSERT INTO "checks" VALUES(31,'dejobs-dallas','2026-10-07T13:35:22Z',1,'HTTP 202','browser',1,0);
INSERT INTO "checks" VALUES(32,'dejobs-fort-worth','2026-10-07T13:35:22Z',1,'HTTP 202','browser',0,0);
INSERT INTO "checks" VALUES(33,'dejobs-new-grad-texas','2026-10-07T13:35:22Z',1,'HTTP 202','browser',0,0);
INSERT INTO "checks" VALUES(34,'thr-gn-residency-search','2026-10-07T13:35:22Z',1,'HTTP 200','browser',2,0);
INSERT INTO "checks" VALUES(35,'cook-nurse-residency','2026-10-07T13:35:22Z',1,'HTTP 200','http',6,0);
INSERT INTO "checks" VALUES(36,'bsw-students-graduates','2026-10-07T13:35:22Z',1,'HTTP 200','http',6,0);
INSERT INTO "checks" VALUES(37,'bsw-search-residency','2026-10-07T13:35:22Z',1,'HTTP 200','browser',0,0);
INSERT INTO "checks" VALUES(38,'jps-nurse-residency','2026-10-07T13:35:22Z',1,'HTTP 200','http',0,0);
INSERT INTO "checks" VALUES(39,'jps-nurse-residency-application','2026-10-07T13:35:22Z',1,'HTTP 200','http',8,0);
INSERT INTO "checks" VALUES(40,'methodist-nurse-residency','2026-10-07T13:35:22Z',1,'HTTP 200','http',1,0);
INSERT INTO "checks" VALUES(41,'adventhealth-workday','2026-10-07T13:35:22Z',1,'HTTP 200','api',1,0);
INSERT INTO "checks" VALUES(42,'utsw-nursing-residency','2026-10-07T13:35:22Z',1,'HTTP 200','http',9,0);
INSERT INTO "checks" VALUES(43,'parkland-bridge-program','2026-10-07T13:35:22Z',1,'HTTP 200','http',0,0);
INSERT INTO "checks" VALUES(44,'parkland-workday','2026-10-07T13:35:22Z',1,'HTTP 200','api',0,0);
INSERT INTO "checks" VALUES(45,'childrens-nurse-residency','2026-10-07T13:35:22Z',1,'HTTP 200','http',1,0);
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
INSERT INTO "events" VALUES(1,'2026-10-07T06:09:41Z','hca-dejobs-new-grad','hca-dejobs-new-grad:8b99d986e93b1712','new_posting','medium','Medical City Lewisville (23.1 mi): New Grad Nurse Residency Lewisville, TX Posted 21 days ago','https://hcahealthcare.dejobs.org/lewisville-tx/new-grad-nurse-residency/67B83593570E45229763B32190358986/job/',1);
INSERT INTO "events" VALUES(2,'2026-10-07T13:35:22Z','hca-dejobs-new-grad','hca-dejobs-new-grad:b79ee927465afbf2','new_posting','medium','Medical City Lewisville (23.1 mi): New Grad Nurse Residency Lewisville, TX Posted 22 days ago','https://hcahealthcare.dejobs.org/lewisville-tx/new-grad-nurse-residency/67B83593570E45229763B32190358986/job/',1);
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
INSERT INTO "findings" VALUES('hca-dejobs-new-grad:128bcbcb91d2bd60','hca-dejobs-new-grad','medical-city','posting','New Grad Nurse Residency Fort Worth, TX Posted 21 days ago','https://hcahealthcare.dejobs.org/fort-worth-tx/new-grad-nurse-residency/B44253129AC049FEAF21C0ADA08F789F/job/','','unknown','','mc-fort-worth','2026-10-06T22:46:53Z','2026-10-06T22:46:53Z',0,2);
INSERT INTO "findings" VALUES('dejobs-dallas:4c3a5c351c9f8145','dejobs-dallas','aggregators','posting','Graduate Nurse (GN) Residency- Medical Intensive Care Unit (MICU)-February 2027 Texas Health Resources - Dallas, TX Posted today','https://dejobs.org/dallas-tx/graduate-nurse-gn-residency-medical-intensive-care-unit-micu-february-2027/9BEA007E1FAB4AEF924B9FF911C77097/job/','February 2027','early','','thr-dallas','2026-10-06T22:46:53Z','2026-10-06T22:46:53Z',0,2);
INSERT INTO "findings" VALUES('thr-gn-residency-search:60931890fe8fed6a','thr-gn-residency-search','thr','posting','Graduate Nurse (GN) Residency— Medical Intensive Care Unit (MICU)—February 2027','https://jobs.texashealth.org/job/23843780/graduate-nurse-gn-residency-medical-intensive-care-unit-micu-february-2027-dallas-tx/','February 2027','early','','thr-dallas','2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('thr-gn-residency-search:83343490c03ef6ae','thr-gn-residency-search','thr','posting','GN Residency February 2027 - Mother/Baby','https://jobs.texashealth.org/job/23913806/gn-residency-february-2027-mother-baby-rockwall-tx/','February 2027','early','','thr-rockwall','2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:799c9e4aef5e6c6c','cook-nurse-residency','cook','snippet','Important! You may only apply to one of the above tracks.: February and April 2027 Cohorts','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','April 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:9072fe1f2595db82','cook-nurse-residency','cook','snippet','Please apply if you have graduated with a BSN or entry-level MSN between August and December 2026.','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','December 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:5de273addfafbab2','cook-nurse-residency','cook','snippet','Selection notification date:: October 5, 2026','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','October 5, 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:4688840a9e8cb129','cook-nurse-residency','cook','snippet','Start date:: Feb. 8 and April 5, 2027','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','April 5, 2027','early','open',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:d4e20f4f2598a469','cook-nurse-residency','cook','snippet','Feb. 2027: Accepting applications for both clinical tracks (','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','Feb. 2027','early','open',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('cook-nurse-residency:05cae3cd90f6e130','cook-nurse-residency','cook','snippet','April 2027: Accepting applications for Medical-Surgical and Subspecialty Nursing track only. Please see the','https://www.cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','April 2027','early','open',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:8d5c0731e5a093b3','bsw-students-graduates','bsw','snippet','Graduate Nurse Winter 2027 Residency Program','https://jobs.bswhealth.com/us/en/students-graduates','Winter 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:bec9528a10511a08','bsw-students-graduates','bsw','snippet','Application: Beginning September 7, 2026','https://jobs.bswhealth.com/us/en/students-graduates','September 7, 2026','early','open',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:e9d30e4037335fce','bsw-students-graduates','bsw','snippet','September 27, 2026','https://jobs.bswhealth.com/us/en/students-graduates','September 27, 2026','early','open',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:a2cc894f6802bdc2','bsw-students-graduates','bsw','snippet','For current Baylor Scott & White team members, applications open August 17, 2026.','https://jobs.bswhealth.com/us/en/students-graduates','August 17, 2026','early','open',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:ce788e884acf4992','bsw-students-graduates','bsw','snippet','Interview: Beginning in October 2026','https://jobs.bswhealth.com/us/en/students-graduates','October 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('bsw-students-graduates:e155d6a3a7f9048a','bsw-students-graduates','bsw','snippet','Get started: Beginning January 25, 2027','https://jobs.bswhealth.com/us/en/students-graduates','January 25, 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:9f394fd84178baf6','jps-nurse-residency-application','jps','snippet','Interviews: Week of February 9, 2026','https://jpshealthnet.org/careers/nurse-residency-application','February 9, 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:b3741853097470f3','jps-nurse-residency-application','jps','snippet','Start: July/August 2026','https://jpshealthnet.org/careers/nurse-residency-application','August 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:4a27c40d9f8128c9','jps-nurse-residency-application','jps','snippet','Interviews: Week of June 15, 2026','https://jpshealthnet.org/careers/nurse-residency-application','June 15, 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:68db25882651de88','jps-nurse-residency-application','jps','snippet','Start: October 2026','https://jpshealthnet.org/careers/nurse-residency-application','October 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:cc6401989c759537','jps-nurse-residency-application','jps','snippet','Interviews: Week of October 12, 2026','https://jpshealthnet.org/careers/nurse-residency-application','October 12, 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:edc213598aba7391','jps-nurse-residency-application','jps','snippet','Start: February/March 2027','https://jpshealthnet.org/careers/nurse-residency-application','March 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:6310f0798e149c24','jps-nurse-residency-application','jps','snippet','Internal January 1, 2026 – January 22, 2026','https://jpshealthnet.org/careers/nurse-residency-application','January 1, 2026, January 22, 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('jps-nurse-residency-application:9531fa5752f6c3af','jps-nurse-residency-application','jps','snippet','External September 1, 2026 – September 8, 2026','https://jpshealthnet.org/careers/nurse-residency-application','September 1, 2026, September 8, 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('methodist-nurse-residency:ec51835a1b4f17c9','methodist-nurse-residency','methodist','snippet','Applications for the February 2027 cohort are open!','https://www.methodisthealthsystem.org/careers/nurse-residency','February 2027','early','','methodist-dallas','2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('adventhealth-workday:6520b63b92e17134','adventhealth-workday','adventhealth','posting','Fort Worth, TX Heritage Nurse Residency FALL','https://adventhealth.wd12.myworkdayjobs.com/en-US/AH_External_Career_Site/job/HU-TEXAS-HUGULEY-MEM-MED-CNTR/Fort-Worth--TX-Heritage-Nurse-Residency-FALL_R-0390418','','unknown','','adventhealth-burleson','2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('utsw-nursing-residency:b55df400a9feb32b','utsw-nursing-residency','utsw','snippet','Cohort starts:: February 8, 2027','https://jobs.utsouthwestern.edu/nursing-residency/','February 8, 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('utsw-nursing-residency:8966d9d9e76d84fc','utsw-nursing-residency','utsw','snippet','Cohort starts:: July 12, 2027','https://jobs.utsouthwestern.edu/nursing-residency/','July 12, 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('utsw-nursing-residency:d1b119739c9c8404','utsw-nursing-residency','utsw','snippet','Cohort starts:: January 11, 2027','https://jobs.utsouthwestern.edu/nursing-residency/','January 11, 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('utsw-nursing-residency:e19cd460b900d032','utsw-nursing-residency','utsw','snippet','Application dates:: Oct. 26 – Nov. 6, 2026','https://jobs.utsouthwestern.edu/nursing-residency/','Nov. 6, 2026','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('utsw-nursing-residency:a5742bfe27d957d5','utsw-nursing-residency','utsw','snippet','Cohort starts:: June 7, 2027','https://jobs.utsouthwestern.edu/nursing-residency/','June 7, 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('utsw-nursing-residency:fdfa32d267835c07','utsw-nursing-residency','utsw','snippet','Application dates:: Feb. 22 – March 5, 2027','https://jobs.utsouthwestern.edu/nursing-residency/','March 5, 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('utsw-nursing-residency:6406847bbb62b5a6','utsw-nursing-residency','utsw','snippet','Cohort starts:: Jan 4, 2027','https://jobs.utsouthwestern.edu/nursing-residency/','Jan 4, 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('utsw-nursing-residency:303dcee7ba9170fc','utsw-nursing-residency','utsw','snippet','Cohort starts:: June 21, 2027','https://jobs.utsouthwestern.edu/nursing-residency/','June 21, 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('utsw-nursing-residency:2f894fba926f491c','utsw-nursing-residency','utsw','snippet','Application dates:: March 1 – March 12, 2027','https://jobs.utsouthwestern.edu/nursing-residency/','March 12, 2027','early','',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('childrens-nurse-residency:270cffe3532d6549','childrens-nurse-residency','childrens','snippet','Eligibility Requirements/Application Process: February 2027 Nurse Residency Program','https://www.childrens.com/for-healthcare-professionals/education-training/nurse-residency','February 2027','early','open',NULL,'2026-10-06T22:46:53Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('hca-dejobs-new-grad:8b99d986e93b1712','hca-dejobs-new-grad','medical-city','posting','New Grad Nurse Residency Lewisville, TX Posted 21 days ago','https://hcahealthcare.dejobs.org/lewisville-tx/new-grad-nurse-residency/67B83593570E45229763B32190358986/job/','','unknown','','mc-lewisville','2026-10-07T06:09:41Z','2026-10-07T06:09:41Z',1,1);
INSERT INTO "findings" VALUES('dejobs-dallas:a3a32f9996b19e65','dejobs-dallas','aggregators','posting','Graduate Nurse (GN) Residency- Medical Intensive Care Unit (MICU)-February 2027 Texas Health Resources - Dallas, TX Posted yesterday','https://dejobs.org/dallas-tx/graduate-nurse-gn-residency-medical-intensive-care-unit-micu-february-2027/9BEA007E1FAB4AEF924B9FF911C77097/job/','February 2027','early','','thr-dallas','2026-10-07T06:09:41Z','2026-10-07T13:35:22Z',1,0);
INSERT INTO "findings" VALUES('hca-dejobs-new-grad:b79ee927465afbf2','hca-dejobs-new-grad','medical-city','posting','New Grad Nurse Residency Lewisville, TX Posted 22 days ago','https://hcahealthcare.dejobs.org/lewisville-tx/new-grad-nurse-residency/67B83593570E45229763B32190358986/job/','','unknown','','mc-lewisville','2026-10-07T13:35:22Z','2026-10-07T13:35:22Z',1,0);
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
INSERT INTO "sources" VALUES('hca-dejobs-new-grad','medical-city','https://hcahealthcare.dejobs.org/jobs/?q=new+grad&location=Texas&sort=date','jobs',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'browser','33bedc69050682a1','',1,0);
INSERT INTO "sources" VALUES('dejobs-dallas','aggregators','https://dejobs.org/jobs/?q=nurse+residency&location=Dallas%2C+TX&sort=date','jobs',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'browser','b100b47c54833306','',1,0);
INSERT INTO "sources" VALUES('dejobs-fort-worth','aggregators','https://dejobs.org/jobs/?q=nurse+residency&location=Fort+Worth%2C+TX&sort=date','jobs',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'browser','c5c580a23306a355','',0,0);
INSERT INTO "sources" VALUES('dejobs-new-grad-texas','aggregators','https://dejobs.org/jobs/?q=new+grad+residency&location=Texas&sort=date','jobs',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'browser','e1b47a3da34dc4a0','',0,0);
INSERT INTO "sources" VALUES('thr-gn-residency-search','thr','https://jobs.texashealth.org/listjobs/?keyword=(GN%20OR%20%22Graduate%20Nurse%22)%20AND%20Residency&category=RN%2FRegistered%20Nurse','jobs',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'browser','548981b261deb933','',2,0);
INSERT INTO "sources" VALUES('cook-nurse-residency','cook','https://cookchildrens.org/healthcare-professionals/nursing/nurse-residency-program','page',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'http','5b74153c990c3273','open',6,0);
INSERT INTO "sources" VALUES('bsw-students-graduates','bsw','https://jobs.bswhealth.com/us/en/students-graduates','page',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'http','459ca5f0c5c2358c','open',6,0);
INSERT INTO "sources" VALUES('bsw-search-residency','bsw','https://jobs.bswhealth.com/us/en/search-results?keywords=graduate%20nurse%20residency','jobs',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'browser','8c113a145bc40daf','',0,0);
INSERT INTO "sources" VALUES('jps-nurse-residency','jps','https://jpshealthnet.org/node/1188','page',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'http','fe88087dd8a0a137','open',0,0);
INSERT INTO "sources" VALUES('jps-nurse-residency-application','jps','https://jpshealthnet.org/node/1241','page',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'http','9b0eb405dbe2ce54','open',8,0);
INSERT INTO "sources" VALUES('methodist-nurse-residency','methodist','https://www.methodisthealthsystem.org/careers/nurse-residency','page',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'http','cbe8296638d99ac5','',1,0);
INSERT INTO "sources" VALUES('adventhealth-workday','adventhealth','https://adventhealth.wd12.myworkdayjobs.com/en-US/AH_External_Career_Site','workday',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'api','e3f23da17e62cba3','',1,0);
INSERT INTO "sources" VALUES('utsw-nursing-residency','utsw','https://jobs.utsouthwestern.edu/nursing-residency/','page',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'http','d34fafbb379135c6','',9,0);
INSERT INTO "sources" VALUES('parkland-bridge-program','parkland','https://www.parklandhealth.org/the-bridge-nurse-residency-program','page',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'http','c4a5a972994aa189','open',0,0);
INSERT INTO "sources" VALUES('parkland-workday','parkland','https://wd12.myworkdaysite.com/en-US/recruiting/parklandhospital/Parkland_Careers','workday',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'api','da39a3ee5e6b4b0d','',0,0);
INSERT INTO "sources" VALUES('childrens-nurse-residency','childrens','https://www.childrens.com/for-healthcare-professionals/education-training/nurse-residency','page',1,'2026-10-07T13:35:22Z','2026-10-07T13:35:22Z','ok',NULL,'http','39fa148f11392bfe','open',1,0);
INSERT INTO "sources" VALUES('va-pbrnr','va','https://www.va.gov/north-texas-health-care/work-with-us/internships-and-fellowships/post-baccalaureate-registered-nurse-residency-program/','page',1,'2026-10-06T22:46:53Z','2026-10-06T22:46:53Z','ok',NULL,'http','549da2c46f2e37c3','',0,0);
INSERT INTO "sources" VALUES('usajobs-nurse-residency-dallas','va','https://www.usajobs.gov/search/results/?k=nurse%20residency&l=Dallas%2C%20Texas','jobs',1,'2026-10-06T22:46:53Z','2026-10-06T22:46:53Z','ok',NULL,'browser','029861c8f68a5922','',0,0);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('checks',45);
INSERT INTO "sqlite_sequence" VALUES('events',2);
COMMIT;
