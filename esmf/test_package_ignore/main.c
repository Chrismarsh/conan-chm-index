// Earth System Modeling Framework
// Copyright 2002-2020, University Corporation for Atmospheric Research,
// Massachusetts Institute of Technology, Geophysical Fluid Dynamics
// Laboratory, University of Michigan, National Centers for Environmental
// Prediction, Los Alamos National Laboratory, Argonne National Laboratory,
// NASA Goddard Space Flight Center.
// Licensed under the University of Illinois-NCSA License.


#include <stdio.h>
#include "ESMC.h"

int main(void){

  ESMC_Initialize(NULL, ESMC_ArgLast);
  
  printf("Hello ESMC World\n");

  ESMC_Finalize();
  
  return 0;
  
}
