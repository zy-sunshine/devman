#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "ssorecords.h"

void
ssofield_getstr(char *buf, const void *record, size_t szrec)
{
    char *ptr = buf + szrec;
    memcpy(buf, record, szrec);
    for (;;) {
	*ptr = 0;
	if (ptr == buf) break;
	--ptr;
	if (*ptr != ' ') break;
    }
}
void
ssouser_rec_make(ssouser_rec_t *self, char type, uid_t uid,
		 const char *user, const char *enchexpwd)
{
    /* RELATED VALUES: A */
    snprintf((char *)self, sizeof(*self), "%c|%-8u|%-32s|%-32s\n",
	     type, uid, user, enchexpwd);
}
void
ssoaccess_rec_make(ssoaccess_rec_t *self, char type, unsigned useridx,
		   const char *ip, const char *path)
{
    /* RELATED VALUES: B */
    snprintf((char *)self, sizeof(*self), "%c|%-6u|%-16s|%-48s\n",
	     type, useridx, ip == NULL ? "" : ip, path);
}

ssorecord_t *
ssorecord_open(const char *fname, size_t szrec, const char *mode)
{
    int rc;
    struct stat st;
    ssorecord_t *self;

    if ((rc = stat(fname, &st)) < 0) goto errquit0;
    if (st.st_size % szrec != 0) goto errquit0;
    if (!(self = malloc(sizeof(ssorecord_t) + st.st_size + 8 * szrec)))
	goto errquit0;
    if (!(self->fp = fopen(fname, mode))) goto errquit1;
    strncpy(self->mode, mode, sizeof(self->mode));
    self->szrec = szrec;
    self->numrec = st.st_size / szrec;
    self->maxrec = self->numrec + 8;
    self->start = (char *)(self + 1);
    if (fread(self->start, 1, st.st_size, self->fp) < st.st_size) goto errquit2;
    return self;
 errquit2:
    fclose(self->fp);
 errquit1:
    free(self);
 errquit0:
    return NULL;
}

void
ssorecord_close(ssorecord_t *self)
{
    fclose(self->fp);
    free(self);
}

const ssorecbase_t *
ssorecord_first(const ssorecord_t *self, unsigned *iter)
{
    *iter = 0;
    return ssorecord_next(self, iter);
}

const ssorecbase_t *
ssorecord_next(const ssorecord_t *self, unsigned *iter)
{
    const char *ret;
    while (*iter < self->numrec) {
	ret = (const char *)(self->start + (*iter)++ * self->szrec);
	if (*ret != ' ') return (const ssorecbase_t *)ret;
    }
    return NULL;
}

const ssorecbase_t *
ssorecord_get(const ssorecord_t *self, unsigned idx)
{
    char *ptr;
    if (idx >= self->numrec) return NULL;
    ptr = self->start + idx * self->szrec;
    return *ptr == ' ' ? NULL : (const ssorecbase_t *)ptr;
}

int
ssorecord_remove(ssorecord_t *self, unsigned idx)
{
    size_t offset;
    char *ptr; 

    if (idx >= self->numrec) return -1;
    if (strcmp(self->mode, "rb+")) return -1;
    offset = idx * self->szrec;
    ptr = self->start + offset;
    *ptr = ' ';
    if (fseek(self->fp, offset, SEEK_SET) < 0) return -1;
    if (fwrite(ptr, 1, 1, self->fp) < 1) return -1;
    return 0;
}

int
ssorecord_modify(ssorecord_t *self, const ssorecbase_t *rec, unsigned idx)
{
    size_t offset;
    char *ptr;
    size_t rc;

    if (idx > self->numrec) return -1;
    if (strcmp(self->mode, "rb+")) return -1;
    offset = idx * self->szrec;
    ptr = self->start + offset;
    memcpy(ptr, rec, self->szrec);
    if (fseek(self->fp, offset, SEEK_SET) < 0) return -1;
    rc = fwrite(ptr, 1, self->szrec, self->fp);
    if (rc < self->szrec) return -1;
    return 0;
}

int
ssorecord_add(ssorecord_t *self, const ssorecbase_t *rec)
{
    unsigned idx;
    for (idx = 0; idx < self->numrec; ++idx) {
	if (self->start[idx * self->szrec] != ' ') continue;
	return ssorecord_modify(self, rec, idx);
    }
    return self->numrec < self->maxrec ?
	ssorecord_modify(self, rec, self->numrec++) : -1;
}
