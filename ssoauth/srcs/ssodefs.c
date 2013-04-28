#include  "ssodefs.h"
#include  "md5.h"
#include  "ssorecords.h"
#include  <time.h>

static int ssoenv_default_retarr[] = { 0, 1, 2 };
void
ssoenv_syslog(const ssoenv_t *self, int priority, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    if (self->syslogv_func == NULL)  vsyslog(priority, fmt, ap);
    else self->syslogv_func(self, priority, fmt, ap);
    va_end(ap);
}

int
ssoenv_init(ssoenv_t *self, const char *cachedir, const char *user,
	    const char *rhost, const char *pwd, const char *mode)
{
    char fpath[256];

    memset(self, 0, sizeof(*self));
    self->retarr = ssoenv_default_retarr;
    self->auth = no_auth;
    self->cachedir = cachedir;
    self->username = user;
    self->rhost = rhost;
    ssoenv_set_password(self, pwd);
    snprintf(fpath, sizeof(fpath), "%s/ssousers.txt", self->cachedir);
    if (!(self->ssousers = ssorecord_open(fpath, sizeof(ssouser_rec_t), mode)))
	return SSOENV_SERVICE_ERR(self);
    return SSOENV_SUCCESS(self);
}

void
ssoenv_close(ssoenv_t *self)
{
    if (self->ssousers) ssorecord_close(self->ssousers);
}

static const char *hexchr = "0123456789ABCDEF";
void
ssoenv_set_password(ssoenv_t *self, const char *password)
{
    char *p; unsigned char encpwd[16], *pep;

    md5((unsigned char *)password, strlen(password), encpwd);
    p = self->enchexpwd;
    for (pep = encpwd; pep < encpwd + sizeof(encpwd); ++pep) {
	*p++ = hexchr[(*pep) >> 4];
	*p++ = hexchr[*pep & 0xF];
    }
    *p = 0;
}

static int
open_file(const ssoenv_t *self, FILE **fp, const char *fname, const char *mode)
{
    struct stat st;
    char fpath[256];

    snprintf(fpath, sizeof(fpath), "%s/%s", self->cachedir, fname);
    if (stat(fpath, &st)) {
	ssoenv_syslog(self, LOG_ERR, "Can not stat [%s]: %m", fpath);
	return SSOENV_SERVICE_ERR(self);
    }
    if (!S_ISREG(st.st_mode)) {
	ssoenv_syslog(self, LOG_ERR, "[%s] is not a normal file", fpath);
	return SSOENV_SERVICE_ERR(self);
    }
    if ((st.st_mode & S_IWOTH)) {
	ssoenv_syslog(self, LOG_ERR, "[%s] is world writable", fpath);
	return SSOENV_SERVICE_ERR(self);
    }
    if (!(*fp = fopen(fpath, mode))) {
	ssoenv_syslog(self, LOG_ERR,
		      "fopen([%s], [%s]) failed: %m", fpath, mode);
	return SSOENV_SERVICE_ERR(self);
    }
    return SSOENV_SUCCESS(self);
}

static int
cmpsuffix(const char *fn, const char *suffix)
{
    size_t lfn = strlen(fn);
    size_t lsuffix = strlen(suffix);
    if (lfn <= lsuffix) return 0;
    return !strcmp(fn + lfn - lsuffix, suffix);
}
static int
never_shortcut(const ssoenv_t *self)
{
    if (!strcmp(self->username, "root")) return SSOENV_AUTH_ERR(self);
    if (cmpsuffix(self->username, "-sh")) return SSOENV_AUTH_ERR(self);
    return SSOENV_SUCCESS(self);
}

static void
mknowstr(char *nowstr, size_t sznowstr)
{
    time_t now;
    struct tm tmspace, *tmptr;

    now = time(NULL);
    tmptr = localtime_r(&now, &tmspace);
    strftime(nowstr, sznowstr, "%Y%m%d%H", tmptr);
}
static void
dump_self(ssoenv_t *self)
{
    if (self->syslogv_func)
        ssoenv_syslog(self, LOG_INFO, "self->syslogv_func %p", self->syslogv_func);
    else
        ssoenv_syslog(self, LOG_INFO, "self->syslogv_func NULL");

    if (self->handle)
        ssoenv_syslog(self, LOG_INFO, "self->handle %p", self->handle);
    else
        ssoenv_syslog(self, LOG_INFO, "self->handle NULL");

    if (self->retarr)
        ssoenv_syslog(self, LOG_INFO, "self->retarr %d, %d, %d", self->retarr[0], self->retarr[1], self->retarr[2]);
    else
        ssoenv_syslog(self, LOG_INFO, "self->retarr NULL");

    if (self->auth)
        ssoenv_syslog(self, LOG_INFO, "self->auth %p", self->auth);
    else
        ssoenv_syslog(self, LOG_INFO, "self->auth NULL");

    if (self->cachedir)
        ssoenv_syslog(self, LOG_INFO, "self->cachedir %s", self->cachedir);
    else
        ssoenv_syslog(self, LOG_INFO, "self->cachedir NULL");


    if (self->username)
        ssoenv_syslog(self, LOG_INFO, "self->username %s", self->username);
    else
        ssoenv_syslog(self, LOG_INFO, "self->username NULL");

    if (self->rhost)
        ssoenv_syslog(self, LOG_INFO, "self->rhost %s", self->rhost);
    else
        ssoenv_syslog(self, LOG_INFO, "self->rhost NULL");

    ssoenv_syslog(self, LOG_INFO, "self->uid %d", (int)self->uid);
    if (self->enchexpwd)
        ssoenv_syslog(self, LOG_INFO, "self->enchexpwd %s", self->enchexpwd);
    else
        ssoenv_syslog(self, LOG_INFO, "self->enchexpwd NULL");

    if (self->ssousers)
        ssoenv_syslog(self, LOG_INFO, "self->ssousers %p", self->ssousers);
    else
        ssoenv_syslog(self, LOG_INFO, "self->ssousers NULL");

}
int
ssoenv_shortcut_scan(ssoenv_t *self)
{
    int retval;
    FILE *rfp;
    char nowstr[64];
    char lnbuf[1024], *p0, *p1;

    if ((retval = never_shortcut(self)) != SSOENV_SUCCESS(self)) return retval;
    mknowstr(nowstr, sizeof(nowstr));
    retval = open_file(self, &rfp, "shortcuts.txt", "rt");
    if (retval != SSOENV_SUCCESS(self)) return retval;
    while (fgets(lnbuf, sizeof(lnbuf), rfp) != NULL) {
	if ((p0 = strchr(lnbuf, '\n')) != NULL) *p0 = 0;
	if ((p0 = strchr(lnbuf, '\r')) != NULL) *p0 = 0;
	if ((p0 = strchr(lnbuf, '|')) == NULL) continue;
	*p0++ = 0;
	if ((p1 = strchr(p0, '|')) == NULL) continue;
	*p1++ = 0;
	if (strcmp(lnbuf, nowstr)) continue;
	if (self->rhost == NULL) continue;
	if (strcmp(p0, self->rhost)) continue;

	if (strcmp(p1, self->username)) continue;
	fclose(rfp);
	self->auth = shortcut_auth;
	return SSOENV_SUCCESS(self);
    }
    fclose(rfp);
    return SSOENV_AUTH_ERR(self);
}

int
ssoenv_shortcut_append(const ssoenv_t *self)
{
    int retval;
    char nowstr[64];
    FILE *afp;

    if ((retval = never_shortcut(self)) == SSOENV_SUCCESS(self)) {
	mknowstr(nowstr, sizeof(nowstr));
	retval = open_file(self, &afp, "shortcuts.txt", "at");
	if (retval != SSOENV_SUCCESS(self)) return retval;
	fprintf(afp, "%s|%s|%s\n", nowstr, self->rhost, self->username);
	fclose(afp);
    }
    return SSOENV_SUCCESS(self);
}

int
ssoenv_cache_scan(ssoenv_t *self)
{
    const ssouser_rec_t *rec;
    unsigned iter;
    char pwdbuf[sizeof(rec->enchexpwd) + 1];
    char userbuf[sizeof(rec->user) + 1];

    for (rec = (const ssouser_rec_t *)ssorecord_first(self->ssousers, &iter);
	 rec;
	 rec = (const ssouser_rec_t *)ssorecord_next(self->ssousers, &iter)) {
	ssofield_getstr(pwdbuf, rec->enchexpwd, sizeof(rec->enchexpwd));
	if (strcmp(pwdbuf, self->enchexpwd)) continue;
	ssofield_getstr(userbuf, rec->user, sizeof(rec->user));
	if (strcmp(userbuf, self->username)) continue;
	return SSOENV_SUCCESS(self);
    }
    return SSOENV_AUTH_ERR(self);
}

int
ssoenv_cache_setpwd(ssoenv_t *self)
{
    unsigned iter;
    const ssouser_rec_t *rec;
    ssouser_rec_t recbuf;
    char uidbuf[sizeof(recbuf.uid) + 1], userbuf[sizeof(recbuf.user) + 1];
    int rc;

    if (self->auth != sso_auth) return SSOENV_SUCCESS(self);
    if (strcmp(self->ssousers->mode, "rb+")) {
	ssoenv_syslog(self, LOG_ERR, "ssousers.txt is opened with [%s] mode.\n", self->ssousers->mode);
	return SSOENV_AUTH_ERR(self);
    }
    for (rec = (const ssouser_rec_t *)ssorecord_first(self->ssousers, &iter);
	 rec;
	 rec = (const ssouser_rec_t *)ssorecord_next(self->ssousers, &iter)) {
	if (rec->base.type != 's') continue;
	ssofield_getstr(uidbuf, rec->uid, sizeof(rec->uid));
	if ((uid_t)atoi(uidbuf) != self->uid) continue;
	ssofield_getstr(userbuf, rec->user, sizeof(rec->user));
	if (strcmp(userbuf, self->username)) continue;
	memcpy(&recbuf, rec, sizeof(recbuf));
	memcpy(recbuf.enchexpwd, self->enchexpwd, sizeof(recbuf).enchexpwd);
	rc = ssorecord_modify(self->ssousers, &recbuf.base, ssorec_iter2idx(iter));
	if (rc != 0)
	    ssoenv_syslog(self, LOG_ERR, "ssorecord_modify([%s], ..., [%u]) => %d\n",
			  self->username, ssorec_iter2idx(iter), rc);
	return rc == 0 ? SSOENV_SUCCESS(self) : SSOENV_AUTH_ERR(self);
    }
    ssoenv_syslog(self, LOG_ERR, "ssoenv(uid = %u, user = %s)\n",
		  self->uid, self->username);
    return SSOENV_AUTH_ERR(self);
}

#define MAXLN  1024
int
ssoenv_check_context(const ssoenv_t *self)
{
    const char *context, *uri, *ip;
    char uribuf[256], *atype, *subsys, *p, *p0;
    char fname[256];
    ssorecord_t *ssoaccess;
    const ssoaccess_rec_t *rec;
    unsigned iter;
    char typec;
    char userbuf[sizeof(rec->user) + 1];
    char subsysbuf[sizeof(rec->subsys) + 1];
    char ipbuf[sizeof(rec->ip) + 1];

    /* Passed if CONTEXT is not set. */
    if (!(context = getenv("CONTEXT"))) return SSOENV_SUCCESS(self);
    if (!(uri = getenv("URI"))) {
	ssoenv_syslog(self, LOG_ERR,
		      "No URI is set: username = [%s]\n", self->username);
	return SSOENV_SERVICE_ERR(self);
    }
    if (!(ip = getenv("IP"))) {
	ssoenv_syslog(self, LOG_ERR,
		      "No IP is set: username = [%s]\n", self->username);
	return SSOENV_SERVICE_ERR(self);
    }
    /* Get atype & projbuf. */
    strncpy(uribuf, uri, sizeof(uribuf) - 1); uribuf[sizeof(uribuf) - 1] = 0;
    if (!(p = strstr(uribuf, "/nsprojs/"))) {
	ssoenv_syslog(self, LOG_NOTICE,
		      "No 'nsprojs' in URI[%s]: username = [%s]\n",
		      uri, self->username);
	return SSOENV_AUTH_ERR(self);
    }
    atype = p = p + 9;
    if (!(p0 = strchr(p, '/'))) {
	ssoenv_syslog(self, LOG_NOTICE,
		      "No / after 'nsprojs' in URI[%s]: username = [%s]\n",
		      uri, self->username);
	return SSOENV_AUTH_ERR(self);
    }
    *p0 = 0;
    subsys = p = p0 + 1;
    if ((p0 = strchr(p, '/'))) *p0 = 0;
    if (*subsys == 0) {
	ssoenv_syslog(self, LOG_NOTICE,
		      "No subsystem name in URI[%s]: username = [%s]\n",
		      uri, self->username);
	return SSOENV_AUTH_ERR(self);
    }

    if (!strcmp(atype, "svn")) typec = 's';
    else if (!strcmp(atype, "trac")) typec = 't';
    else typec = ' ';

    snprintf(fname, sizeof(fname), "%s/ssoaccess.txt", self->cachedir);
    if (!(ssoaccess = ssorecord_open(fname, sizeof(ssoaccess_rec_t), "rb"))) {
	ssoenv_syslog(self, LOG_NOTICE, "open [%s] failed\n", fname);
	return SSOENV_AUTH_ERR(self);
    }
    for (rec = (const ssoaccess_rec_t *)ssorecord_first(ssoaccess, &iter);
	 rec;
	 rec = (const ssoaccess_rec_t *)ssorecord_next(ssoaccess, &iter)) {
	if (typec != rec->base.type) continue;
	ssofield_getstr(userbuf, rec->user, sizeof(rec->user));
	if (strcmp(userbuf, self->username)) continue;
	ssofield_getstr(subsysbuf, rec->subsys, sizeof(rec->subsys));
	if (strcmp(subsysbuf, subsys)) continue;
	ssofield_getstr(ipbuf, rec->ip, sizeof(rec->ip));
	if (*ipbuf != 0 && strcmp(ipbuf, ip)) continue;
	ssorecord_close(ssoaccess);
	return SSOENV_SUCCESS(self);
    }
    /* All auth failed. */
    ssoenv_syslog(self, LOG_NOTICE,
		  "All auth failed: username = [%s], URI = [%s], CONTEXT = [%s]\n",
		  self->username, uri, context);
    return SSOENV_AUTH_ERR(self);
}
