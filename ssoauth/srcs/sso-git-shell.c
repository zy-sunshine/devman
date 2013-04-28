/* -*- c-basic-offset: 4 -*- */
#include <sys/types.h>
#include <sys/stat.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <pwd.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include "ssorecords.h"

#define  WITH_LOG

static const char *access_fn = "/etc/ssoauth/ssoaccess.txt";

#define  GIT_COMMAND        "/usr/bin/git"
#define  PERL_COMMAND       "/usr/bin/perl"
#define  GL_AUTH_COMMAND    "/usr/bin/gl-auth-command"
#define  GITOLITE_HTTP_HOME "/var/lib/gitolite"

static void die(const char *fmt, ...);
static void die_errno(const char *fmt, ...);
static int prefixcmp(const char *str, const char *prefix);
static char *sq_dequote(char *);

typedef enum {
    ct_gitshell, ct_gitolite
}  cmd_type_t;

static cmd_type_t
check_access(const char *arg, char *userbuf, size_t szuserbuf);

static int do_generic_cmd(const char *me, char *arg)
{
    cmd_type_t ct;
    char user[256];
    char cmd[1024];

    /*setup_path();*/
    if (!arg) die("bad argument: NULL");

    if (!(arg = sq_dequote(arg))) die("bad argument");
    if (prefixcmp(me, "git-")) die("bad command");
    if (*arg == '/') ++arg;
    switch ((ct = check_access(arg, user, sizeof(user)))) {
    case ct_gitshell:
	fprintf(stderr, "%s %s %s\n", GIT_COMMAND, me + 4, arg);
	return execl(GIT_COMMAND, GIT_COMMAND, me + 4, arg, NULL);
    case ct_gitolite:
	snprintf(cmd, sizeof(cmd), "git-%s '%s'", me + 4, arg);
	setenv("SSH_ORIGINAL_COMMAND", cmd, !0);
	setenv("GITOLITE_HTTP_HOME", GITOLITE_HTTP_HOME, !0);
	fprintf(stderr, "gitolite: user = [%s] cmd = [%s]\n", user, cmd);
	return execl(PERL_COMMAND, PERL_COMMAND, GL_AUTH_COMMAND, user, NULL);
    }
    die("Unknown command type: %u", ct);
    return -1;
}

static int do_cvs_cmd(const char *me, char *arg)
{
    char *cvsserver_argv[4] = {
	"git", "cvsserver", "server", NULL
    };

    if (!arg || strcmp(arg, "server"))
	die("git-cvsserver only handles server: %s", arg);

    /*setup_path();*/
    return execvp("git", cvsserver_argv);
}


static struct commands {
    const char *name;
    int (*exec)(const char *me, char *arg);
} cmd_list[] = {
    { "git-receive-pack", do_generic_cmd },
    { "git-upload-pack", do_generic_cmd },
    { "git-upload-archive", do_generic_cmd },
    { "cvs", do_cvs_cmd },
    { NULL },
};

#ifdef WITH_LOG
static const char *logfn = "/tmp/git-shell.log";
#endif
int main(int argc, char **argv)
{
    char *prog;
    struct commands *cmd;
    int devnull_fd;
#ifdef WITH_LOG
    time_t tv;
    struct tm tmv;
    char tmbuf[64];
    FILE *logfp; int idx;
#endif

    /*
     * Always open file descriptors 0/1/2 to avoid clobbering files
     * in die().  It also avoids not messing up when the pipes are
     * dup'ed onto stdin/stdout/stderr in the child processes we spawn.
     */
    devnull_fd = open("/dev/null", O_RDWR);
    while (devnull_fd >= 0 && devnull_fd <= 2)
	devnull_fd = dup(devnull_fd);
    if (devnull_fd == -1)
	die_errno("opening /dev/null failed");
    close (devnull_fd);

    umask(0007);

#ifdef WITH_LOG
    tv = time(NULL);
    localtime_r(&tv, &tmv);
    strftime(tmbuf, sizeof(tmbuf), "%Y/%m/%d %H:%M:%S", &tmv);
    if (!(logfp = fopen(logfn, "at"))) {
	idx = errno;
	die_errno("Can not open [%s]: %d(%s)", logfn, idx, strerror(idx));
    }
    fprintf(logfp, "[%u(%s): ", (unsigned)getuid(), tmbuf);
    for (idx = 0; idx < argc; ++idx)
	fprintf(logfp, "%s ", argv[idx]);
    fprintf(logfp, "]\n");
    fclose(logfp);
#endif

    /*
     * Special hack to pretend to be a CVS server
     */
    if (argc == 2 && !strcmp(argv[1], "cvs server"))
	argv--;

    /*
     * We do not accept anything but "-c" followed by "cmd arg",
     * where "cmd" is a very limited subset of git commands.
     */
    else if (argc != 3 || strcmp(argv[1], "-c"))
	die("What do you think I am? A shell?");

    prog = argv[2];
    if (!strncmp(prog, "git", 3) && isspace(prog[3]))
	/* Accept "git foo" as if the caller said "git-foo". */
	prog[3] = '-';

    for (cmd = cmd_list ; cmd->name ; cmd++) {
	int len = strlen(cmd->name);
	char *arg;
	if (strncmp(cmd->name, prog, len))
	    continue;
	arg = NULL;
	switch (prog[len]) {
	case '\0':
	    arg = NULL;
	    break;
	case ' ':
	    arg = prog + len + 1;
	    break;
	default:
	    continue;
	}
	exit(cmd->exec(cmd->name, arg));
    }
    die("unrecognized command '%s'", prog);
    return 0;
}

static void
die(const char *fmt, ...)
{
    va_list ap;

    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fprintf(stderr, "\n");
    exit(-1);
}

static void
die_errno(const char *fmt, ...)
{
    int en; char enbuf[256];
    va_list ap;

    en = errno; strerror_r(en, enbuf, sizeof(enbuf));
    fprintf(stderr, "ERRNO[(%d)%s]: ", en, enbuf);
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fprintf(stderr, "\n");
    exit(-1);
}

static int
prefixcmp(const char *str, const char *prefix)
{
    for (; ; str++, prefix++)
	if (!*prefix) return 0;
	else if (*str != *prefix)
	    return (unsigned char)*prefix - (unsigned char)*str;
}

/* Help to copy the thing properly quoted for the shell safety.
 * any single quote is replaced with '\'', any exclamation point
 * is replaced with '\!', and the whole thing is enclosed in a
 *
 * E.g.
 *  original     sq_quote     result
 *  name     ==> name      ==> 'name'
 *  a b      ==> a b       ==> 'a b'
 *  a'b      ==> a'\''b    ==> 'a'\''b'
 *  a!b      ==> a'\!'b    ==> 'a'\!'b'
 */
static inline int
need_bs_quote(char c)
{
    return (c == '\'' || c == '!');
}

static char *
sq_dequote_step(char *arg, char **next)
{
	char *dst = arg;
	char *src = arg;
	char c;

	if (*src != '\'')
		return NULL;
	for (;;) {
		c = *++src;
		if (!c)
			return NULL;
		if (c != '\'') {
			*dst++ = c;
			continue;
		}
		/* We stepped out of sq */
		switch (*++src) {
		case '\0':
			*dst = 0;
			if (next)
				*next = NULL;
			return arg;
		case '\\':
			c = *++src;
			if (need_bs_quote(c) && *++src == '\'') {
				*dst++ = c;
				continue;
			}
		/* Fallthrough */
		default:
			if (!next || !isspace(*src))
				return NULL;
			do {
				c = *++src;
			} while (isspace(c));
			*dst = 0;
			*next = src;
			return arg;
		}
	}
}

static char *
sq_dequote(char *arg)
{
    return sq_dequote_step(arg, NULL);
}

static const char *
getprefix(const char *value, char sep, char *buf, size_t szbuf)
{
    const char *v0 = strchr(value, sep);

    if (v0 == NULL) return value;
    if (v0 - value >= szbuf) return NULL;
    memcpy(buf, value, v0 - value);
    buf[v0 - value] = 0;
    return buf;
}

static cmd_type_t
check_access(const char *arg, char *userbuf, size_t szuserbuf)
{
    const char *subsys; char subsysbuf[128]; size_t subsyslen;
    char *ssh_client; const char *ip; char ipbuf[64]; size_t iplen;
    int rc; struct passwd pwdbuf, *pwd; char pwdstrs[512];
    const char *user; size_t userlen;
    ssorecord_t *ssoaccess;
    unsigned iter;
    const ssoaccess_rec_t *rec;
    char rec_user[sizeof(rec->user) + 1];
    char rec_subsys[sizeof(rec->subsys) + 1];
    char rec_ip[sizeof(rec->ip) + 1];

    /* Get subsys */
    if (!(subsys = getprefix(arg, '/', subsysbuf, sizeof(subsysbuf))))
	die("The subsysect name in [%s] is too long.", arg);
    subsyslen = strlen(subsys);

    /* Get ip address from environment SSH_CLIENT */
    ssh_client = getenv("SSH_CLIENT");
    if (ssh_client == NULL) ip = "";
    else if (!(ip = getprefix(ssh_client, ' ', ipbuf, sizeof(ipbuf))))
	die("IP address in [%s] is too long.", ssh_client);
    iplen = strlen(ip);
    /* Get username by getuid, getpwuid. */
    rc = getpwuid_r(getuid(), &pwdbuf, pwdstrs, sizeof(pwdstrs), &pwd);
    if (rc != 0)
	die("getpwuid_r failed: %d(%s)", rc,
	    strerror_r(rc, pwdstrs, sizeof(pwdstrs)));
    user = pwd->pw_name;
    userlen = strlen(user);
    if (userbuf) snprintf(userbuf, szuserbuf, "%s", user);

    if (!(ssoaccess = ssorecord_open(access_fn, sizeof(ssoaccess_rec_t), "rb")))
	die("Open [%s] failed", access_fn);
    for (rec = (const ssoaccess_rec_t *)ssorecord_first(ssoaccess, &iter);
	 rec;
	 rec = (const ssoaccess_rec_t *)ssorecord_next(ssoaccess, &iter)) {
	if (rec->base.type != 'g') continue;
	ssofield_getstr(rec_user, rec->user, sizeof(rec->user));
	if (strcmp(user, rec_user)) continue;
	ssofield_getstr(rec_subsys, rec->subsys, sizeof(rec->subsys));
	if (strcmp(subsys, rec_subsys)) continue;
	ssofield_getstr(rec_ip, rec->ip, sizeof(rec->ip));
	if (*rec_ip != 0 && strcmp(rec_ip, ip)) continue;
	ssorecord_close(ssoaccess);
	return ct_gitshell;
    }
    ssorecord_close(ssoaccess);
    die("All auth failed");
    return ct_gitshell;
}
