#include  "ssodefs.h"
#include  <errno.h>
#include  <grp.h>
#include  <curl/curl.h>

typedef struct {
    char buf[256], *cur, *end;
}  retbuf_t;

static size_t
retbuf_writer(void *ptr, size_t sz, size_t nmemb, void *data)
{
    size_t rsz = sz * nmemb;
    retbuf_t *rbuf = (retbuf_t *)data;

    if (rbuf->cur + rsz > rbuf->end) rsz = rbuf->end - rbuf->cur;
    memcpy(rbuf->cur, ptr, rsz);
    rbuf->cur += rsz;
    return rsz;
}

#define SSOCURL_SETOPT(h, opt, val)				\
    (retcode = curl_easy_setopt((h), (opt), (val))) != CURLE_OK
#define SSOCURL_LOG(self, opt, url, retcode)				\
    ssoenv_syslog((self), LOG_ERR,					\
		  "curl_easy_setopt(%s) for url [%s] failed: %u(%s)",	\
		  #opt, (url), (retcode), curl_easy_strerror(retcode));
static int
geturl(const ssoenv_t *self, const char *url, retbuf_t *buf)
{
    CURLcode retcode;
    CURL *curlh;

    if ((retcode = curl_global_init(CURL_GLOBAL_ALL)) != CURLE_OK) {
	ssoenv_syslog(self, LOG_ERR,
		      "curl_global_init for url [%s] failed: %u(%s)",
		      url, retcode, curl_easy_strerror(retcode));
	goto errquit0;
    }
    if (!(curlh = curl_easy_init())) {
	ssoenv_syslog(self, LOG_ERR,
		      "curl_easy_init for url [%s] failed", url);
	goto errquit1;
    }
    if (SSOCURL_SETOPT(curlh, CURLOPT_URL, url)) {
	SSOCURL_LOG(self, CURLOPT_URL, url, retcode);
	goto errquit2;
    }
    if (SSOCURL_SETOPT(curlh, CURLOPT_WRITEFUNCTION, retbuf_writer)) {
	SSOCURL_LOG(self, CURLOPT_WRITEFUNCTION, url, retcode);
	goto errquit2;
    }

    buf->cur = buf->buf; buf->end = buf->buf + sizeof(buf->buf) - 1;
    if (SSOCURL_SETOPT(curlh, CURLOPT_WRITEDATA, buf)) {
	SSOCURL_LOG(self, CURLOPT_WRITEDATA, url, retcode);
	goto errquit2;
    }
    if (SSOCURL_SETOPT(curlh, CURLOPT_USERAGENT, "ssoauth")) {
	SSOCURL_LOG(self, CURLOPT_USERAGENT, url, retcode);
	goto errquit2;
    }
    if ((retcode = curl_easy_perform(curlh)) != CURLE_OK) {
	ssoenv_syslog(self, LOG_ERR,
		      "curl_easy_perform for url [%s] failed: %u(%s)",
		      url, retcode, curl_easy_strerror(retcode));
	goto errquit2;
    }
    curl_easy_cleanup(curlh);
    curl_global_cleanup();
    *buf->cur = 0;
    return SSOENV_SUCCESS(self);
 errquit2:
    curl_easy_cleanup(curlh);
 errquit1:
    curl_global_cleanup();
 errquit0:
    return SSOENV_SERVICE_ERR(self);
}

int
ssoenv_check_remote(ssoenv_t *self)
{
#ifndef NOT_REAL_REMOTE_CHECK
    int retval;
    char url[1024];
    retbuf_t buf;

    snprintf(url, sizeof(url),
	     "http://%s?orgname=%s&sub=%u&ip=%s&user=%s&pwd=%s",
	     "192.168.1.190:8090/magicsso/certify",
	     "hackos", 100001, "192.168.1.191",
	     self->username, self->enchexpwd);
    retval = geturl(self, url, &buf);
    if (retval != SSOENV_SUCCESS(self)) return retval;
    if (strncmp(buf.buf, "1|", 2)) {
	ssoenv_syslog(self, LOG_NOTICE,
		      "remote check [%s] with [%s] failed: [%s]",
		      self->username, self->enchexpwd, buf.buf);
	return SSOENV_AUTH_ERR(self);
    }
    self->uid = (uid_t)atoi(buf.buf + 2);
#endif
    self->auth = sso_auth;
    return SSOENV_SUCCESS(self);
}
