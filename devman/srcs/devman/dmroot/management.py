from datetime import datetime
from django.db.models.signals import post_init
from devman.settings import superusers, entityroot_id, topsyslists
import devman.dmroot.models
from devman.dmroot.models import DBIDScope, DBMember, DBEntity, DBMemberPerm,\
    DBPerm
from devman.dmroot.autoid import AutoLocalUID

def initdata(sender, **kwargs):
    if kwargs['db'] != 'default': return
    now = datetime.now()
    if not DBMember.objects.all().exists():
        print('Setup DBIDScope(%u, %u) for %u.' % (0, 1000, DBMember.LOCAL))
        iobj = DBIDScope(idtypeid = DBMember.LOCAL, minval = 0, maxval = 1000)
        iobj.save()
        mobj0 = None
        
        # create three default permission git svn trac
        gpermobj = DBPerm(name = "git")
        spermobj = DBPerm(name = "svn")
        tpermobj = DBPerm(name = "trac")
        gpermobj.save()
        spermobj.save()
        tpermobj.save()
        for su in superusers:
            userid = AutoLocalUID.request()
            print('Setup DBMember(%s) with userid/jobnum %u.' % (su, userid))
            mobj = DBMember(member = su, sourceid = DBMember.LOCAL, name = su,
                            userid = userid, jobnum = userid,
                            email = '%s@unknown' % su, mobile = '',
                            enabled = True)
            mobj.save()
            mobj.UserAddOrEdit(pwd = su)
            if mobj0 is None: mobj0 = mobj

            # assign three default permission to super users
            DBMemberPerm(member=mobj, perm = gpermobj).save()
            DBMemberPerm(member=mobj, perm = spermobj).save()
            DBMemberPerm(member=mobj, perm = tpermobj).save()
            
        print('Setup Root DBEntity.')
        eobj = DBEntity(id = entityroot_id, klass = 'DMRoot', owner = mobj0,
                        create_date = now, lastedit_date = now)
        eobj.save()
    else:
        mobj0 = DBMember.objects.filter(sourceid = entityroot_id)[0]
    sl_eobjs = list(DBEntity.objects.filter(parent = entityroot_id).order_by('id'))
    for idx in range(len(sl_eobjs), len(topsyslists)):
        print('Setup System List(%s).' % (topsyslists[idx]))
        eobj = DBEntity(parent = entityroot_id, klass = 'DMSysList',
                        owner = mobj0, create_date = now, lastedit_date = now)
        eobj.save()
        sl_eobjs.append(eobj)
    print('All init data inserted!')

post_init.connect(initdata, sender = devman.dmroot.models)
