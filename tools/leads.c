#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dds_dll.h"
/* usage: leads "N:..." trump(0=S,1=H,2=D,3=C,4=N) leader(0=N,1=E,2=S,3=W) */
int main(int c,char**v){
  struct dealPBN d; struct futureTricks f; memset(&d,0,sizeof d);
  SetResources(400,1);
  d.trump=atoi(v[2]); d.first=atoi(v[3]); strcpy(d.remainCards,v[1]);
  int r=SolveBoardPBN(d,-1,3,0,&f,0);
  if(r!=1){printf("err %d\n",r);return 1;}
  const char*s="SHDC",*rk="xx23456789TJQKA";
  for(int i=0;i<f.cards;i++){printf("%c%c",s[f.suit[i]],rk[f.rank[i]]);
    for(int k=2;k<15;k++) if(f.equals[i]&(1<<k)) printf("/%c",rk[k]);
    printf(":%d ",13-f.score[i]);}
  printf("\n"); return 0;}
