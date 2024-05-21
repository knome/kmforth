
#define _GNU_SOURCE
#define _POSIX_C_SOURCE 1999309L

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>

#define s( structure ) do {                                             \
    printf( "0 " #structure " : %llu\n", (unsigned long long) sizeof(structure) ); \
  } while(0)

#define e( structure, field ) do {                                       \
    printf( "1  " #field " offset= %llu : size= %llu\n", (unsigned long long) &((structure *)0)->field, (unsigned long long) sizeof( ((structure *)0)->field )); \
  } while(0)

#define v( value ) do {                         \
    printf( "2  " #value " : %llu\n", (unsigned long long) (value) );   \
  } while(0)

int main( int argc, char ** argv )
{
  s(struct stat);
  e(struct stat, st_dev);
  e(struct stat, st_ino);
  e(struct stat, st_mode);
  e(struct stat, st_nlink);
  e(struct stat, st_uid);
  e(struct stat, st_gid);
  e(struct stat, st_rdev);
  e(struct stat, st_size);
  e(struct stat, st_blksize);
  e(struct stat, st_blocks);
  e(struct stat, st_atime);
  e(struct stat, st_mtime);
  e(struct stat, st_ctime);
  
  printf("\n");
  
  v(SEEK_SET);
  v(SEEK_CUR);
  v(SEEK_END);
  
  printf("\n");
  
  s(struct timespec);
  e(struct timespec, tv_sec);
  e(struct timespec, tv_nsec);
  
  printf("\n");
  
  v(CLOCK_REALTIME);
  v(CLOCK_MONOTONIC);
  v(CLOCK_PROCESS_CPUTIME_ID);
  v(CLOCK_THREAD_CPUTIME_ID);
  
  return 0;
}
