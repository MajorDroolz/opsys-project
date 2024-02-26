#include "stdlib.h"
#include "stdio.h"

int main(void) {
  for (int i = 0; i < 100; i++) {
    srand48(i);

    for (int j = 0; j < 100; j++) {
      printf("%.10f\n", drand48());
    }

    printf("\n");
  }
}