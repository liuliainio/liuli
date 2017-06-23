
namespace py MarketSearch.apkpatch_gen

enum ApkPatchStatus {
  	SUCCEED = 0,
  	FAIL = 1,
}

struct ApkPatchResult {
	1: i32 old_size
	2: i32 new_size
	3: i32 patch_size
	4: string patch_file
	5: ApkPatchStatus status
    6: string patch_hash
}

service ApkPatch {
	ApkPatchResult bsdiff(1:string old_hash, 2:string new_hash, 3:string old_file, 4:string new_file)
}
