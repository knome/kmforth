
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#define e( name ) do {                                            \
    printf( "1  " #name " offset= %llu : size= %llu\n", (unsigned long long) &((struct stat *)0)->name, (unsigned long long) sizeof( ((struct stat*)0)->name )); \
  } while(0)

int main( int argc, char ** argv )
{
  printf( "0 struct stat : %llu\n", (unsigned long long) sizeof(struct stat) );
  e(st_dev);
  e(st_ino);
  e(st_mode);
  e(st_nlink);
  e(st_uid);
  e(st_gid);
  e(st_rdev);
  e(st_size);
  e(st_blksize);
  e(st_blocks);
  e(st_atime);
  e(st_mtime);
  e(st_ctime);
  
  printf("\n");
  
  printf("seek\n");
  printf("  SEEK_SET : %llu\n", (unsigned long long) SEEK_SET );
  printf("  SEEK_CUR : %llu\n", (unsigned long long) SEEK_CUR );
  printf("  SEEK_END : %llu\n", (unsigned long long) SEEK_END );
  
  return 0;
}
