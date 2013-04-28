#include "ssodefs.h"

int
main(int argc, char *argv[])
{
    char user[128], pwd[128], *p;
    ssoenv_t env;
    int retval;

    if (fgets(user, sizeof(user), stdin) == NULL) exit(6);
    if ((p = strchr(user, '\n')) == NULL) exit(7);
    *p = 0;
    if (fgets(pwd, sizeof(pwd), stdin) == NULL) exit(8);
    if ((p = strchr(pwd, '\n')) == NULL) exit(9);
    *p = 0;

    retval = ssoenv_init(&env, NULL, user, "", pwd, "rb");
    if (retval != SSOENV_SUCCESS(&env)) return retval;
    if (strcmp(user, pwd)) exit(10);
    return ssoenv_check_context(&env);
}
