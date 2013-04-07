#include <stdio.h>
#include <error.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>

#define BUFSIZE 256

/*
 * Simple program for counting bytes frequences in specified files.
 */
int main(int argc, const char *argv[])
{
    if (argc < 2) {
        error(1, 0, "file name wasn't specified");
    }
    const char *filename = argv[1];
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        error(2, 0, "file '%s' can't be opened for reading", filename);
    }
    size_t nread = 0, total = 0;

    size_t counts[256];
    // initialize counts array to all zeros
    for (int i = 0; i < 256; i++)
        counts[i] = 0;

    char buf[BUFSIZE];
    while ((nread = fread(buf, 1, BUFSIZE, file)) != 0) {
        for (int i = 0; i < nread; i++) {
            counts[buf[i]]++;
        }
        total += nread;
    }
    if (ferror(file)) {
        error(3, errno, "error while reading file '%s'", filename);
    }
    if (total == 0) {
        printf("file '%s' is empty\n", filename);    
        exit(0);
    }

    printf("Show results ([y]es/[n]o)?: ");
    fgets(buf, 4, stdin);
    // strip trailing newline
    if (buf[strlen(buf) - 1] == '\n')
        buf[strlen(buf) - 1] = '\0';
    if (strcmp(buf, "yes") == 0 || strcmp(buf, "y") == 0) {
        // format results
        printf("Total %d bytes\n", total);
        for (int i = 0; i < 256; i++) {
            printf("0x%02X: %.2f%% (%d bytes)\n", (unsigned char)i, (float)counts[i] / total * 100, counts[i]);
        }
    }
    return 0;
}
