import java.util.Random;
import java.util.*;

int totalIteraciones= 1000;
int totalAccionesPorIter= 50;
int[][] listaEstados;
int[][] contadorAcciones;
int fR=10;
int z=0;
int xini=100,yini=100;
int cuadrosw=7;
int cuadrosh=5;
int tam= 70;
/*inicio,normal,fin*/
int[][] colores={{255,255,0,50},{0,255,204,50},{0,53,255,50}};
int[] inicio= {2,4};
int[] fin= {6,3};
int v=-1;
Random rand;
int [][] mEstadoAccion; /*cols=up,right,down,left*/
float epsilon=.65;
float alpha= .95;

int[] vientoSN= {0,0,1,2,0,1,0};
int[][] centrosEstados;

void setup() {
  background(255);
  frameRate(fR);
  size(800,600);
  smooth();
  int i,j,k,m=0;
  rand= new Random(8761);
  mEstadoAccion= new int[cuadrosw*cuadrosh][4];
  centrosEstados= new int[cuadrosw*cuadrosh][2];
  for(i=0;i<cuadrosw;i++) {
    for(j=0;j<cuadrosh;j++) {
      for(k=0;k<4;k++) {
        mEstadoAccion[m][k]=0;
        /*println(i,j,k,m);*/
      }
      m=m+1;
    }
  }
  /*for(i=0;i<35;i++) {
    println(i,i%cuadrosw,i/cuadrosw,((i/cuadrosw)*cuadrosw+(i%cuadrosw)));
  }*/
  grid();
  viento();
  listaEstados= new int[totalIteraciones][totalAccionesPorIter];
  contadorAcciones= new int[totalIteraciones][2];
  recorre(totalIteraciones,totalAccionesPorIter);
}

void grid() {
  stroke(111);
  int i,j,x=xini,y;
  for(i=0;i<cuadrosw;i++) {
    y=yini;
    for(j=0;j<cuadrosh;j++) {
      if(i+1==inicio[0] && j+1==inicio[1]) { fill(colores[0][0],colores[0][1],colores[0][2],colores[0][3]); }
      else if(i+1==fin[0] && j+1==fin[1]) { fill(colores[2][0],colores[2][1],colores[2][2],colores[2][3]); }
      else { fill(colores[1][0],colores[1][1],colores[1][2],colores[1][3]); }
      rect(x,y,tam,tam);
      centrosEstados[j*cuadrosw+i][0]= (int) (x + (tam/2));
      centrosEstados[j*cuadrosw+i][1]= (int) (y + (tam/2));
      y=y+tam;
    }
    x=x+tam;
  }
  for(i=0;i<cuadrosw*cuadrosh;i++) {
    fill(255,0,0,50);
    stroke(255,0,0,50);
    ellipse((centrosEstados[i][0]),(centrosEstados[i][1]),10,10);
  }
}
void viento() {
  int i;
  int particleLen=15;
  for(i=0;i<vientoSN.length;i++) {
    //println(i);
    //println(rand.nextInt());
  }
}

int eligeAccion(int estado) {
  int i;
  int maxVal=-999;
  int indMaxVal= -1;
  int accionElegida= -1;
  ArrayList listaMaxVal= new ArrayList(); 
  if(rand.nextFloat()<epsilon) {
    for(i=0;i<4;i++) {
      //print(mEstadoAccion[estado][i]);
      if(mEstadoAccion[estado][i]>maxVal) {
        maxVal= mEstadoAccion[estado][i];
        indMaxVal= i;
      }
    }
    //println("---Despues de recorrido:"+indMaxVal+","+maxVal);
    for(i=0;i<4;i++) {
      if(mEstadoAccion[estado][i]==maxVal) {
        listaMaxVal.add(i);
      }
    }
    if(listaMaxVal.size()>1) {
      //println("Aleatorio entre " + listaMaxVal.size());  
      accionElegida= (int)listaMaxVal.get(rand.nextInt(listaMaxVal.size()));
    }
    else {
      //println("Maximo Valor");
      accionElegida= indMaxVal;
    }
  }
  else {
    //println("Completamente Aleatorio");
    accionElegida= rand.nextInt(3);
  }
  //println(accionElegida);
  return(accionElegida);
}
int ejecutaAccion(int estado,int accion) {
  int x,y,x0,y0;
  //movimiento inicial
  x= estado%cuadrosw;
  y= (int) estado/cuadrosw;
  x0=x;
  y0=y;
  switch(accion) {
    case 0: y=y-1; break; //up
    case 1: x=x+1; break; //right
    case 2: y=y+1; break; //down
    case 3: x=x-1; break; //left
  }
  //rebote
  if(x<0) { x=0; }
  if(y<0) { y=0; }
  if(x>(cuadrosw-1)) { x=cuadrosw-1; }
  if(y>(cuadrosh-1)) { y=cuadrosh-1; }
  //efecto viento
  y= y - vientoSN[x];
  if(y<0) { y=0; }
  return(y*cuadrosw+x);
}
int calculaRecompensa(int estado,int accion) {
  int recompensa= 0;
  int nuevoEstado= ejecutaAccion(estado,accion);
  if(nuevoEstado==fin[1]*cuadrosw+fin[0]) {
    recompensa= 100;
  }
  else if (nuevoEstado== estado) {
    recompensa= -7;
  }
  else {
    recompensa= -5;
  }
  return(recompensa);
}
void aprende(int estado, int accion, int recompensa) {
  int valActual= mEstadoAccion[estado][accion];
  if(valActual==0) { mEstadoAccion[estado][accion]= recompensa; }
  else {
    mEstadoAccion[estado][accion]= (int) (valActual + alpha * (recompensa - valActual));
  }
}

int[] posicionEstado(int estado) {
  int x,y;
  int[] posicion= {0,0};
  posicion[0]=(tam * estado%cuadrosw);
  posicion[1]=(tam * (int)estado/cuadrosw);
  return(posicion);
}
void dibujaTrayectoria(int[] estadosRecorridos,int nAcc,int llegaFin) {
  noFill();
  int i,x,y;
  int z2= z+tam+10;
  int[] pos;
  //stroke(50,50,50,170);
  if(llegaFin==1) {
    stroke(10,255,25,125);
  }
  else {
    stroke(200,200,200,75);
  }
  smooth();
  beginShape();
  x= centrosEstados[estadosRecorridos[0]][0];
  y= centrosEstados[estadosRecorridos[0]][1];
  curveVertex(x,y);
  for(i=0;i<(nAcc);i++) {
    x= centrosEstados[estadosRecorridos[i]][0];
    y= centrosEstados[estadosRecorridos[i]][1];
    curveVertex(x,y);
  }
  x= centrosEstados[estadosRecorridos[(nAcc-1)]][0];
  y= centrosEstados[estadosRecorridos[(nAcc-1)]][1];
  curveVertex(x,y);
  endShape();
}
void recorre(int maxIteraciones,int maxAcciones) {
  //loop();
  int estadoInicial,estadoActual,accionElegida,estadoSiguiente,recompensa;
  int maxIter= maxIteraciones,nIter=0;
  int maxAcc= maxAcciones,nAcc=0;
  int llegaFin= 0;
  int[] estadosRecorridos= new int[maxAcciones];
  estadoInicial= inicio[1]*cuadrosw+inicio[0];
  while(nIter < maxIter) {
    estadoActual= estadoInicial;
    while(llegaFin == 0 && nAcc < maxAcc) {
      estadosRecorridos[nAcc]= estadoActual;
      listaEstados[nIter][nAcc]= estadoActual;
      accionElegida= eligeAccion(estadoActual);
      estadoSiguiente= ejecutaAccion(estadoActual,accionElegida);
      recompensa= calculaRecompensa(estadoActual,accionElegida);
      //println(nIter,nAcc,llegaFin,estadoActual,accionElegida,estadoSiguiente,recompensa);
      aprende(estadoActual,accionElegida,recompensa);
      if(estadoSiguiente== fin[1]*cuadrosw+fin[0]) { llegaFin= 1; }
      estadoActual=estadoSiguiente;
      nAcc= nAcc + 1;
    }
    //println("trayectoria "+nIter+",puntos "+nAcc);
    //dibujaTrayectoria(estadosRecorridos,nAcc,llegaFin);
    contadorAcciones[nIter][0]=nAcc;
    contadorAcciones[nIter][1]=llegaFin;
    nIter= nIter + 1;
    estadoActual= estadoInicial;
    nAcc= 0;
    llegaFin= 0;
    estadosRecorridos= new int[maxAcciones];
  }
  //noLoop();
}

/*
int estadoInicial= inicio[1]*cuadrosw+inicio[0];
int accionElegida= eligeAccion(estadoInicial);
int estadoSiguiente= ejecutaAccion(estadoInicial,accionElegida);
int recompensa= calculaRecompensa(estadoInicial,accionElegida);
aprende(estadoInicial,accionElegida,recompensa);
*/


void draw() {
  v= v+1;
  int i;
  i=v;
  //println(v);
  //grid();
  //viento();
  //noLoop();
  //totalIteraciones,totalAccionesPorIter
  //recorre(totalIteraciones,totalAccionesPorIter);
  //for(i=0;i<totalIteraciones;i++) {
    dibujaTrayectoria(listaEstados[i],contadorAcciones[i][0],contadorAcciones[i][1]);
    if(i>=totalIteraciones) { noLoop();}
  //}
  //println("recorrido");
  //noLoop();
}