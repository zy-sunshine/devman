#include <sys/types.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void
showpwd(const char *prompt, struct passwd *pwdbufptr, int rc)
{
    char errbuf[128];
    if (pwdbufptr == NULL) {
	if (rc == 0) printf("%s is not found\n", prompt);
	else {
	    strerror_r(rc, errbuf, sizeof(errbuf));
	    printf("%s failed: %d(%s)\n", prompt, rc, errbuf);
	}
    } else {
	printf("======== %s ========\n", prompt);
	printf("\tpw_name = [%s]\n", pwdbufptr->pw_name);
	printf("\tpw_passwd = [%s]\n", pwdbufptr->pw_passwd);
	printf("\tpw_uid = [%u]\n", (unsigned)pwdbufptr->pw_uid);
	printf("\tpw_uid = [%u]\n", (unsigned)pwdbufptr->pw_gid);
	printf("\tpw_gecos = [%s]\n", pwdbufptr->pw_gecos);
	printf("\tpw_dir = [%s]\n", pwdbufptr->pw_dir);
	printf("\tpw_shell = [%s]\n", pwdbufptr->pw_shell);
    }
}

int
main(int argc, char *argv[])
{
    int idx;
    char prompt[64];
    struct passwd pwdbuf, *pwdbufptr;
    char pwdstrbuf[1024];
    int rc;

    if (argc == 1) printf("Usage: %s UID ...\n", argv[0]);
    for (idx = 1; idx < argc; ++idx) {
	if (strspn(argv[idx], "0123456789") == strlen(argv[idx])) {
	    snprintf(prompt, sizeof(prompt),
		     "getpwuid(%u)", (unsigned)atoi(argv[idx]));
	    rc = getpwuid_r((uid_t)atoi(argv[idx]), &pwdbuf,
			    pwdstrbuf, sizeof(pwdstrbuf), &pwdbufptr);
	} else {
	    snprintf(prompt, sizeof(prompt), "getpwnam(%s)", argv[idx]);
	    rc = getpwnam_r(argv[idx], &pwdbuf,
			    pwdstrbuf, sizeof(pwdstrbuf), &pwdbufptr);
	}
	showpwd(prompt, pwdbufptr, rc);
    }
    return 0;
}
