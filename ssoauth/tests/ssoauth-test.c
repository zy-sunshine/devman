#include "../srcs/ssodefs.h"

/* Usage: ssoauth.exe SSOCACHE_PATH USER UID RHOST PWD */
int
main(int argc, char *argv[])
{
    ssoenv_t env;
    int retval;
    const char *prompt;

    if (argc != 6) exit(8);

    ssoenv_init(&env, argv[1], argv[2], argv[4], argv[5], "rb+");
    env.uid = atoi(argv[3]);
    printf("env.username = [%s]\n", env.username);
    printf("env.enchexpwd = [%s]\n", env.enchexpwd);
    retval = ssoenv_cache_scan(&env);
    if (retval == SSOENV_SERVICE_ERR(&env)) goto show;
    else if (retval == SSOENV_AUTH_ERR(&env)) {
	retval = ssoenv_check_remote(&env);
	if (retval != SSOENV_SUCCESS(&env)) goto show;
	retval = ssoenv_cache_setpwd(&env);
	if (retval != SSOENV_SUCCESS(&env)) goto show;
    }
    retval = ssoenv_check_context(&env);
 show:
    if (retval == SSOENV_SUCCESS(&env)) prompt = "success";
    else if (retval == SSOENV_AUTH_ERR(&env)) prompt = "auth err";
    else if (retval == SSOENV_SERVICE_ERR(&env)) prompt = "service err";
    else prompt = "unknown";
    printf("RESULT = %d, [%s]\n", retval, prompt);
    return retval;
}
