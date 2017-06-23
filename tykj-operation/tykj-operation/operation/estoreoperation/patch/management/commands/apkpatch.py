from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str
from estoreoperation.patch.service import PatchDaemon,queue_single_patch_job


class Command(BaseCommand):
    help = ('Tianyi apk patch')

    def handle(self, *args, **options):
        pidfile = '/var/run/estore-apkpatch.pid'
        cmd = args[0]
        if cmd == "start":
            PatchDaemon(pidfile=pidfile).start()

        elif cmd == "stop":
            PatchDaemon(pidfile=pidfile).stop()

        elif cmd == "patching":
            if len(args)<4:
                print 'args less than 4'
                return
            pname = args[1]
            vcode = args[2]
            phash = args[3]
            #args[0]:package_name,args[1]:version_code,args[3]:package_hash
            queue_single_patch_job(pname, int(vcode), phash)
