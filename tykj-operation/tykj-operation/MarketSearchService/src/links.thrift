namespace py MarketSearch.gen

enum Status {
  	SUCCEED = 0,
  	FAIL = 1,
  	FOUND = 2,
  	REDIRECT = 3
}

enum LinkType {
	UNKNOWN = 0,
	CATELOG = 1,
	LEAF = 2
}

struct Link {
	1: string url
}

struct LinkPredicate {
	1: string source
}

struct LinkStatus {
	1: string url
	2: string source
	3: Status status
	4: LinkType type
	5: i32 pages
}

struct ApkStatus {
	1: string source_link
	2: string url
	3: string source
	4: i32 status
	5: string vol_id
	6: string file
}

struct ApkFileStatus {
	1: string source_link
	2: string url
	3: string source
	4: i32 status
	5: string vol_id
	6: string package_name
	7: i64 version_code
	8: string signature
	9: string version_name
	10: string apk_size
	11: i32 min_sdk_version
	12: string screen_support
	13: i32 is_break
	14: string file_type
	15: i32 platform
	16: string package_hash
}

struct Apk {
	1: string source_link
	2: string url
	3: string size
}

struct ApkFile {
	1: string source_link
	2: string url
	3: string source
	4: string vol_id
}


service Links {
	list<Link> getLinks(1:LinkPredicate predicate, 2:i32 pendings)
	list<Link> getUpdateLinks(1:LinkPredicate predicate, 2:i32 pendings)
    list<Link> getRefreshLinks(1:LinkPredicate predicate, 2:i32 pendings)
    list<Apk> getApkLinks(1:LinkPredicate predicate, 2:i32 pendings)
	list<Apk> getUpdateApkLinks(1:LinkPredicate predicate, 2:i32 pendings)
	list<ApkFile> getApkFiles(1:LinkPredicate predicate, 2:i32 pendings)
	list<ApkFile> getDupApkFiles(1:LinkPredicate predicate, 2:i32 pendings)
	list<ApkFile> getUniqApkFiles(1:LinkPredicate predicate, 2:i32 pendings)
	void reportStatus(1:list<LinkStatus> statusList)
	void reportUpdateStatus(1:list<LinkStatus> statusList)
    void reportRefreshStatus(1:list<LinkStatus> statusList)
    void reportApkStatus(1:list<ApkStatus> statusList)
	void reportApkFileStatus(1:list<ApkFileStatus> statusList)
	void reportDupApkFileStatus(1:list<ApkFileStatus> statusList)
	void reportUniqApkFileStatus(1:list<ApkFileStatus> statusList)
	void reportInsertApk(1:list<ApkFileStatus> statusList)
	void reportRemoveApk(1:list<ApkFileStatus> statusList)
}