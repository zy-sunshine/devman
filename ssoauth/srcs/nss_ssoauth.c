#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pwd.h>
#include <shadow.h>
#include <grp.h>
#include <nss.h>
#include "ssorecords.h"

#ifdef NDEBUG
#define DBGPRINTF(x) ((void)0)
#else
#define DBGPRINTF(x) dbgoutput(__FUNCTION__, __LINE__, dbgprintf x)
static void
dbgoutput(const char *func, unsigned ln, const char *msg)
{
    fprintf(stderr, "%s(#%d): [%s]\n", func, ln, msg);
}
static char msgbuf[256];
static const char *
dbgprintf(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(msgbuf, sizeof(msgbuf), fmt, ap);
    va_end(ap);
    return msgbuf;
}
#endif

static int gid_git = -1;
static ssorecord_t *record_users = NULL;

static const char *ssouser_fname = "/etc/ssoauth/ssousers.txt";
static enum nss_status
init(void)
{
    int rc; struct group grpbuf, *grp; char grpstrs[1024];

    DBGPRINTF((""));
    if (record_users == NULL &&
	!(record_users = ssorecord_open(ssouser_fname, sizeof(ssouser_rec_t), "rb")))
	return NSS_STATUS_TRYAGAIN;
    DBGPRINTF((""));
    if (gid_git < 0) {
	rc = getgrnam_r("git", &grpbuf, grpstrs, sizeof(grpstrs), &grp);
	DBGPRINTF(("rc = %d", rc));
	if (rc < 0) return NSS_STATUS_TRYAGAIN;
	if (grp == NULL) return NSS_STATUS_TRYAGAIN; /* git group is not exists */
	gid_git = (int)grp->gr_gid;
	DBGPRINTF(("gid_git = %d", gid_git));
    }
    return NSS_STATUS_SUCCESS;
}

static const unsigned uid_start_local = 9000;
static const unsigned uid_start_sso = 10000;
static uid_t
get_uid(const ssouser_rec_t *record)
{
    char uidbuf[sizeof(record->uid) + 1];
    ssofield_getstr(uidbuf, record->uid, sizeof(record->uid));
    return (uid_t)atoi(uidbuf) +
	(record->base.type == 'l' ? uid_start_local :
	 record->base.type == 's' ? uid_start_sso : 0);
}

static const char *pw_passwd = "x";
static const char *pw_gecos_local = "auto-generated localauth user";
static const char *pw_gecos_sso = "auto-generated ssoauth user";
static const char *pw_dir = "/home/apache/rtdevman/git";
static const char *pw_shell = "/usr/bin/sso-git-shell.exe";
static enum nss_status
fill_passwd(const ssouser_rec_t *record, struct passwd *result,
	    char *buffer, size_t buflen, int *errnop)
{
    uid_t uid_start;
    const char *gecos;
    char namebuf[sizeof(record->user) + 1];
    char uidbuf[sizeof(record->uid) + 1];

    if (record->base.type == 'l') {
	uid_start = uid_start_local;
	gecos = pw_gecos_local;
    } else if (record->base.type == 's') {
	uid_start = uid_start_sso;
	gecos = pw_gecos_sso;
    } else {
	return NSS_STATUS_NOTFOUND;
    }
    ssofield_getstr(namebuf, record->user, sizeof(record->user));
    ssofield_getstr(uidbuf, record->uid, sizeof(record->uid));

    result->pw_name = buffer;
    snprintf(buffer, buflen, "%s", namebuf);
    result->pw_passwd = (char *)pw_passwd;
    result->pw_uid = atoi(uidbuf) + uid_start;
    result->pw_gid = (gid_t)gid_git;
    result->pw_gecos = (char *)gecos;
    result->pw_dir = (char *)pw_dir;
    result->pw_shell = (char *)pw_shell;
    return NSS_STATUS_SUCCESS;
}

/* ---- For passwd features ---- */
static unsigned iter_passwd;

enum nss_status
_nss_ssoauth_setpwent(void)
{
    enum nss_status rc;
    DBGPRINTF((""));
    if ((rc = init()) != NSS_STATUS_SUCCESS) return rc;
    iter_passwd = 0;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_ssoauth_getpwent_r(struct passwd *result,
			char *buffer, size_t buflen, int *errnop)
{
    enum nss_status rc;
    const ssouser_rec_t *rec;

    DBGPRINTF((""));
    if ((rc = init()) != NSS_STATUS_SUCCESS) return rc;
    rec = (const ssouser_rec_t *)ssorecord_next(record_users, &iter_passwd);
    if (rec == NULL) return NSS_STATUS_RETURN;
    return fill_passwd(rec, result, buffer, buflen, errnop);
}

enum nss_status
_nss_ssoauth_endpwent(void)
{
    enum nss_status rc;
    DBGPRINTF((""));
    if ((rc = init()) != NSS_STATUS_SUCCESS) return rc;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_ssoauth_getpwnam_r(const char *name, struct passwd *result,
			char *buffer, size_t buflen, int *errnop)
{
    enum nss_status rc;
    unsigned iter;
    const ssouser_rec_t *rec;
    char namebuf[sizeof(rec->user) + 1];

    DBGPRINTF(("name = [%s]", name));
    if ((rc = init()) != NSS_STATUS_SUCCESS) return rc;
    for (rec = (const ssouser_rec_t *)ssorecord_first(record_users, &iter);
	 rec;
	 rec = (const ssouser_rec_t *)ssorecord_next(record_users, &iter)) {
	ssofield_getstr(namebuf, rec->user, sizeof(rec->user));
	if (!strcmp(name, namebuf))
	    return fill_passwd(rec, result, buffer, buflen, errnop);
    }
    return NSS_STATUS_NOTFOUND;
}

enum nss_status
_nss_ssoauth_getpwuid_r(uid_t uid, struct passwd *result,
			char *buffer, size_t buflen, int *errnop)
{
    enum nss_status rc;
    unsigned iter;
    const ssouser_rec_t *rec;

    DBGPRINTF(("uid = [%u]\n", (unsigned)uid));
    if ((rc = init()) != NSS_STATUS_SUCCESS) return rc;
    for (rec = (const ssouser_rec_t *)ssorecord_first(record_users, &iter);
	 rec;
	 rec = (const ssouser_rec_t *)ssorecord_next(record_users, &iter)) {
	if (uid == get_uid(rec))
	    return fill_passwd(rec, result, buffer, buflen, errnop);
    }
    return NSS_STATUS_NOTFOUND;
}

/* ---- For shadow features ---- */
static enum nss_status
fill_shadow(const ssouser_rec_t *rec, struct spwd *result,
	    char *buffer, size_t buflen, int *errnop)
{
    char namebuf[sizeof(rec->user) + 1];

    ssofield_getstr(namebuf, rec->user, sizeof(rec->user));
    result->sp_namp = buffer;
    snprintf(buffer, buflen, "%s", namebuf);
    result->sp_pwdp = "*";
    result->sp_lstchg = -1;
    result->sp_min = -1;
    result->sp_max = -1;
    result->sp_warn = -1;
    result->sp_inact = -1;
    result->sp_expire = -1;
    result->sp_flag = ~0;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_ssoauth_getspnam_r(const char *name, struct spwd *result,
			char *buffer, size_t buflen, int *errnop)
{
    unsigned iter;
    const ssouser_rec_t *rec;
    char namebuf[sizeof(rec->user) + 1];

    for (rec = (const ssouser_rec_t *)ssorecord_first(record_users, &iter);
	 rec;
	 rec = (const ssouser_rec_t *)ssorecord_next(record_users, &iter)) {
	ssofield_getstr(namebuf, rec->user, sizeof(rec->user));
	if (!strcmp(namebuf, name))
	    return fill_shadow(rec, result, buffer, buflen, errnop);
    }
    return NSS_STATUS_NOTFOUND;
}

static unsigned iter_shadow;

enum nss_status
_nss_ssoauth_setspent(void)
{
    enum nss_status rc;
    DBGPRINTF((""));
    if ((rc = init()) != NSS_STATUS_SUCCESS) return rc;
    iter_shadow = 0;
    return NSS_STATUS_SUCCESS;
}

enum nss_status
_nss_ssoauth_getspent_r(struct spwd *result,
			char *buffer, size_t buflen, int *errnop)
{
    enum nss_status rc;
    const ssouser_rec_t *rec;

    DBGPRINTF((""));
    if ((rc = init()) != NSS_STATUS_SUCCESS) return rc;
    rec = (const ssouser_rec_t *)ssorecord_next(record_users, &iter_shadow);
    if (rec == NULL) return NSS_STATUS_RETURN;
    return fill_shadow(rec, result, buffer, buflen, errnop);
}

enum nss_status
_nss_ssoauth_endspent(void)
{
    enum nss_status rc;
    DBGPRINTF((""));
    if ((rc = init()) != NSS_STATUS_SUCCESS) return rc;
    return NSS_STATUS_SUCCESS;
}
