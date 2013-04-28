#ifndef  SSORECORDS_H
#define  SSORECORDS_H

#include  <stdio.h>

/* RELATED VALUES: AB */
typedef struct {
    char type;   /* ' ' => unused */
    char sep0;   /* '|' */
}  ssorecbase_t;

/* RELATED VALUES: A */
typedef struct {
    ssorecbase_t base;  /* l => local user, s => sso user */
    char uid[8];
    char sep1;
    char user[32];
    char sep2;
    char enchexpwd[32];
    char cr;
}  ssouser_rec_t;

/* RELATED VALUES: B */
typedef struct {
    ssorecbase_t base; /* s => svn, g => git, t => trac. */
    char user[32];
    char sep1;
    char ip[16];
    char sep2;
    char subsys[32];
    char cr;
}  ssoaccess_rec_t;

typedef struct {
    FILE *fp;
    char mode[4];
    size_t szrec;
    size_t numrec;
    size_t maxrec;
    char *start;
}  ssorecord_t;

void ssofield_getstr(char *buf, const void *record, size_t szrec);
void ssouser_rec_make(ssouser_rec_t *self, char type, uid_t uid,
		      const char *user, const char *enchexpwd);
void ssoaccess_rec_make(ssoaccess_rec_t *self, char type, unsigned useridx,
			const char *ip, const char *path);

ssorecord_t *ssorecord_open(const char *fname, size_t szrec, const char *mode);
void ssorecord_close(ssorecord_t *self);
const ssorecbase_t *ssorecord_first(const ssorecord_t *self, unsigned *iter);
const ssorecbase_t *ssorecord_next(const ssorecord_t *self, unsigned *iter);
const ssorecbase_t *ssorecord_get(const ssorecord_t *self, unsigned idx);
int ssorecord_remove(ssorecord_t *self, unsigned idx);
int ssorecord_modify(ssorecord_t *self, const ssorecbase_t *rec, unsigned idx);
int ssorecord_add(ssorecord_t *self, const ssorecbase_t *rec);
#define ssorec_iter2idx(v)  ((v)-1)

#endif  /* SSORECORDS_H */
