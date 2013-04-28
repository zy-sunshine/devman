#include  <sys/types.h>
#include  <pwd.h>
#include  <stdio.h>
#include  <stdlib.h>
#include  <unistd.h>
#include  <security/pam_appl.h>
#include  <security/pam_misc.h>

static struct pam_conv conv = { misc_conv, NULL };

int
main(int argc, char *argv[])
{
    int retval;
    pam_handle_t *pamh = NULL;
    const char *username = NULL;
    char buffer[128];
    struct passwd *pw;
    const char *tty;

    if (argc > 2) {
	fprintf(stderr, "Usage: %s [username]\n", argv[0]);
	exit(-1);
    }
    if (argc > 1) username = argv[1];

    if ((retval = pam_start("ssopamtest", username, &conv, &pamh)) != PAM_SUCCESS) {
	fprintf(stderr, "pam_start for [%s] failed: %u(%s).\n",
		username, retval, pam_strerror(pamh, retval));
	goto errquit0;
    }

    pw = getpwuid(getuid());
    if (pw != NULL) {
	if ((retval = pam_set_item(pamh, PAM_RUSER, pw->pw_name)) != PAM_SUCCESS) {
	    fprintf(stderr, "pam_set_item(PAM_RUSER, [%s]) failed: %u(%s).\n",
		    pw->pw_name, retval, pam_strerror(pamh, retval));
	    goto errquit1;
	}
	
    }
    if ((retval = gethostname(buffer, sizeof(buffer) - 1))) {
	perror("failed to look up hostname");
	goto errquit1;
    }
    if ((retval = pam_set_item(pamh, PAM_RHOST, buffer)) != PAM_SUCCESS) {
	fprintf(stderr, "pam_set_item(PAM_RHOST, [%s]) failed: %u(%s).\n",
		buffer, retval, pam_strerror(pamh, retval));
	goto errquit1;
    }
    if ((tty = ttyname(fileno(stdin)))) {
	if ((retval = pam_set_item(pamh, PAM_TTY, tty)) != PAM_SUCCESS) {
	    fprintf(stderr, "pam_set_item(PAM_TTY, [%s]) failed: %u(%s).\n",
		    tty, retval, pam_strerror(pamh, retval));
	    goto errquit1;
	}
    }

    if ((retval = pam_authenticate(pamh, 0)) != PAM_SUCCESS) {
	fprintf(stderr, "pam_authenticate(0) failed: %u(%s).\n",
		retval, pam_strerror(pamh, retval));
	goto errquit1;
    }
    retval = pam_acct_mgmt(pamh, 0);
    if (retval == PAM_NEW_AUTHTOK_REQD) {
	fprintf(stderr, "Request new password\n");
	if ((retval = pam_chauthtok(pamh, PAM_CHANGE_EXPIRED_AUTHTOK)) != PAM_SUCCESS) {
	    fprintf(stderr, "pam_chauthtok(PAM_CHANGE_EXPIRED_AUTHTOK) failed: %u(%s).\n",
		    retval, pam_strerror(pamh, retval));
	    goto errquit1;
	}
    } else if (retval != PAM_SUCCESS) {
	fprintf(stderr, "pam_acct_mgmt(0) failed: %u(%s).\n",
		retval, pam_strerror(pamh, retval));
	goto errquit1;
    }

    if ((retval = pam_setcred(pamh, PAM_ESTABLISH_CRED)) != PAM_SUCCESS) {
	fprintf(stderr, "pam_setcred(PAM_ESTABLISH_CRED) failed: %u(%s).\n",
		retval, pam_strerror(pamh, retval));
	goto errquit1;
    }

    if ((retval = pam_open_session(pamh, 0)) != PAM_SUCCESS) {
	fprintf(stderr, "pam_open_session(0) failed: %u(%s).\n",
		retval, pam_strerror(pamh, retval));
	goto errquit1;
    }

    pam_get_item(pamh, PAM_USER, (const void **)&username);
    fprintf(stderr, "The user [%s] has been authenticated and logged in.\n",
	    username);

    if ((retval = pam_close_session(pamh, 0)) != PAM_SUCCESS) {
	fprintf(stderr, "pam_close_session(0) failed: %u(%s).\n",
		retval, pam_strerror(pamh, retval));
    }

    if ((retval = pam_end(pamh, PAM_SUCCESS)) != PAM_SUCCESS) {
	fprintf(stderr, "pam_end(PAM_SUCCESS) failed: %u(%s).\n",
		retval, pam_strerror(pamh, retval));
    }
    pamh = NULL;

    return 0;
 errquit1:
    pam_end(pamh, PAM_SUCCESS);
    pamh = NULL;
 errquit0:
    return -1;
}
