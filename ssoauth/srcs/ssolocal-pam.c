#include "ssodefs.h"
#define  PAM_SM_AUTH
#define  PAM_SM_ACCOUNT
#define  PAM_SM_SESSION
#define  PAM_SM_PASSWORD
#include <security/pam_ext.h>
#include <security/pam_modules.h>

PAM_EXTERN int
pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    int retval;
    ssoenv_t env;

    if (argc != 1) {
	pam_syslog(pamh, LOG_ERR, "Usage: AUTHTOKFILE");
	return PAM_SERVICE_ERR;
    }
    retval = ssoenv_pam_init(&env, pamh, argv[0], "rb");
    if (retval != PAM_SUCCESS) {
	pam_syslog(pamh, LOG_ERR, "ssolocal in pam_init failure: %d(%s)",
		   retval, pam_strerror(pamh, retval));
	return retval;
    }
    retval = ssoenv_shortcut_scan(&env);
    if (retval != PAM_AUTH_ERR) return retval;
    retval = ssoenv_pam_get_pwd(&env, "Password: ");
    if (retval != PAM_SUCCESS) {
	pam_syslog(pamh, LOG_ERR, "ssolocal in get pwd failure: %d(%s)",
		   retval, pam_strerror(pamh, retval));
	return retval;
    }
    if ((retval = ssoenv_cache_scan(&env)) != PAM_SUCCESS) {
	pam_syslog(pamh, LOG_ERR,
		   "ssolocal for [%s] in cache_scan failure: %d(%s)",
		   env.username, retval, pam_strerror(pamh, retval));
	return retval;
    }
    pam_syslog(pamh, LOG_NOTICE, "retval = %d(%s)",
	       retval, pam_strerror(pamh, retval));
    if ((retval = ssoenv_shortcut_append(&env)) != PAM_SUCCESS) {
	pam_syslog(pamh, LOG_ERR,
		   "ssolocal for [%s] in shortcut_append failure: %d(%s)",
		   env.username, retval, pam_strerror(pamh, retval));
	return retval;
    }
    ssoenv_close(&env);
    return retval;
}

PAM_EXTERN int
pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    return PAM_SUCCESS;
}

PAM_EXTERN int
pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    pam_syslog(pamh, LOG_NOTICE, "pam_sm_acct_mgmt called inapproperiately");
    return PAM_SERVICE_ERR;
}

PAM_EXTERN int
pam_sm_open_session(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    pam_syslog(pamh, LOG_NOTICE, "pam_sm_open_session called inapproperiately");
    return PAM_SERVICE_ERR;
}

PAM_EXTERN int
pam_sm_close_session(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    pam_syslog(pamh, LOG_NOTICE,
	       "pam_sm_close_session called inapproperiately");
    return PAM_SERVICE_ERR;
}

PAM_EXTERN int
pam_sm_chauthtok(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    pam_syslog(pamh, LOG_NOTICE, "pam_sm_chauthtok called inapproperiately");
    return PAM_SERVICE_ERR;
}
