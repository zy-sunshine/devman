#include "ssodefs.h"
#include <security/_pam_macros.h>
#include <security/pam_ext.h>
#include <security/pam_modules.h>

static const int ssoenv_pam_retarr[] = {
    PAM_SUCCESS, PAM_AUTH_ERR, PAM_SERVICE_ERR
};
static void
ssoenv_pam_syslogv(const ssoenv_t *self, int priority,
		   const char *fmt, va_list ap)
{
    pam_vsyslog((const pam_handle_t *)self->handle, priority, fmt, ap);
}

static int
ssoenv_pam_get_user(ssoenv_t *self, const char *prompt)
{
    int retval;

    retval = pam_get_user(PAMH(self), &self->username, prompt);
    if (retval != PAM_SUCCESS) return retval;
    if (!self->username || (*self->username == '\0')) {
	retval = pam_get_user(PAMH(self), &self->username, prompt);
	if (retval != PAM_SUCCESS) return retval;
	if (!self->username || (*self->username == '\0'))
	    return PAM_SERVICE_ERR;
    }
    return PAM_SUCCESS;
}

int
ssoenv_pam_get_pwd(ssoenv_t *self, const char *prompt) 
{
    int retval;
    const void *pwd;
    char *resp;

    retval = pam_get_item(PAMH(self), PAM_AUTHTOK, &pwd);
    if (retval != PAM_SUCCESS) return retval;
    if (pwd == NULL) {
	retval = pam_prompt(PAMH(self), PAM_PROMPT_ECHO_OFF,
			    &resp, "%s", prompt);
	if (retval != PAM_SUCCESS) return retval;
	if (resp == NULL) return PAM_CONV_ERR;
	retval = pam_set_item(PAMH(self), PAM_AUTHTOK, resp);
	_pam_overwrite(resp);
	_pam_drop(resp);
	if (retval != PAM_SUCCESS) return retval;

	retval = pam_get_item(PAMH(self), PAM_AUTHTOK, &pwd);
	if (retval != PAM_SUCCESS) return retval;
    }
    ssoenv_set_password(self, pwd);
    return PAM_SUCCESS;
}

int
ssoenv_pam_init(ssoenv_t *self, void *handle, const char *cachedir,
		const char *mode)
{
    int retval;
    char fpath[256];

    memset(self, 0, sizeof(*self));
    self->syslogv_func = ssoenv_pam_syslogv;
    self->handle = handle;
    self->retarr = ssoenv_pam_retarr;
    self->auth = no_auth;
    self->cachedir = cachedir;

    retval = ssoenv_pam_get_user(self, NULL);
    if (retval != PAM_SUCCESS) return retval;
    retval = pam_get_item(PAMH(self), PAM_RHOST, (const void **)&self->rhost);
    if (retval != PAM_SUCCESS) return retval;
    self->enchexpwd[0] = 0;
    snprintf(fpath, sizeof(fpath), "%s/ssousers.txt", cachedir);
    if (!(self->ssousers = ssorecord_open(fpath, sizeof(ssouser_rec_t), mode)))
	return PAM_SERVICE_ERR;
    return PAM_SUCCESS;
}

int
ssoenv_pam_init_with_pwd(ssoenv_t *self, void *handle, const char *cachedir,
			 const char *mode)
{
    int retval;

    retval = ssoenv_pam_init(self, handle, cachedir, mode);
    if (retval != PAM_SUCCESS) return retval;
    retval = ssoenv_pam_get_pwd(self, "Password: ");
    if (retval != PAM_SUCCESS) return retval;
    return PAM_SUCCESS;
}
