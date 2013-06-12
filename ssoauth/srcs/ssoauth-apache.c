#include "ssodefs.h"

/* Usage: ssoauth.exe SSOCACHE_PATH */
int
main(int argc, char *argv[])
{
    int retval;
    ssoenv_t env;
    char user[128], pwd[128], *p;

    if (argc != 2) exit(8);

    /* Get login, pwd, encpwdhex */
    if (fgets(user, sizeof(user), stdin) == NULL) exit(9);
    if ((p = strchr(user, '\n')) == NULL) exit(10);
    *p = 0;
    if (fgets(pwd, sizeof(pwd), stdin) == NULL) exit(11);
    if ((p = strchr(pwd, '\n')) == NULL) exit(12);
    *p = 0;

    retval = ssoenv_init(&env, argv[1], user, "", pwd, "rb+");
    if (retval != SSOENV_SUCCESS(&env)) return retval;
    retval = ssoenv_cache_scan(&env);
    if (retval == SSOENV_SERVICE_ERR(&env)) return retval;
    else if (retval == SSOENV_AUTH_ERR(&env)) {
	// TODO: open it for remote sso check, or cache user to local
	//retval = ssoenv_check_remote(&env);
	//if (retval != SSOENV_SUCCESS(&env)) return retval;
	//retval = ssoenv_cache_setpwd(&env);
	//if (retval != SSOENV_SUCCESS(&env)) return retval;
	return retval;
    }
    retval = ssoenv_check_context(&env);
    ssoenv_close(&env);
    return retval;
}
