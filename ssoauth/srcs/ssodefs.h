#ifndef  SSODEFS_H
#define  SSODEFS_H

#include  <sys/types.h>
#include  <sys/stat.h>
#include  <fcntl.h>
#include  <stdarg.h>
#include  <stdio.h>
#include  <stdlib.h>
#include  <string.h>
#include  <syslog.h>
#include  <unistd.h>

#ifdef __cplusplus
#define EXTC_BEGIN extern "C" {
#define EXTC_END   }
#else
#define EXTC_BEGIN
#define EXTC_END
#endif

EXTC_BEGIN

#include  "ssorecords.h"

#define  SSOENV_SUCCESS(self)      ((self)->retarr[0])
#define  SSOENV_AUTH_ERR(self)     ((self)->retarr[1])
#define  SSOENV_SERVICE_ERR(self)  ((self)->retarr[2])

#define PAMH(self)  ((pam_handle_t *)((self)->handle))

typedef enum {
    no_auth, shortcut_auth, sso_auth, local_auth
}  authtype_t;

typedef struct ssoenv_s ssoenv_t;
struct ssoenv_s {
    void
    (* syslogv_func)(const ssoenv_t *self, int priority,
		     const char *fmt, va_list ap);
    void *handle;
    const int *retarr; /* SUCCESS, AUTH_FAILED, SERVICE_ERR */
    authtype_t auth;
    const char *cachedir;
    const char *username;
    const char *rhost; /* remote host */
    uid_t uid;
    char enchexpwd[33];
    ssorecord_t *ssousers;
};

void ssoenv_syslog(const ssoenv_t *self, int priority, const char *fmt, ...);

int ssoenv_init(ssoenv_t *self, const char *cachedir, const char *user,
		const char *rhost, const char *pwd, const char *mode);
int ssoenv_pam_init(ssoenv_t *self, void *handle, const char *cachedir,
		    const char *mode);
int ssoenv_pam_get_pwd(ssoenv_t *self, const char *prompt);
int ssoenv_pam_init_with_pwd(ssoenv_t *self, void *handle,
			     const char *cachedir, const char *mode);
void ssoenv_close(ssoenv_t *self);

void ssoenv_set_password(ssoenv_t *self, const char *password);
int ssoenv_shortcut_scan(ssoenv_t *self);
int ssoenv_shortcut_append(const ssoenv_t *self);
int ssoenv_cache_scan(ssoenv_t *self);
int ssoenv_cache_setpwd(ssoenv_t *self);
int ssoenv_check_remote(ssoenv_t *self);
int ssoenv_check_context(const ssoenv_t *self);

EXTC_END

#endif /* SSODEFS_H */
