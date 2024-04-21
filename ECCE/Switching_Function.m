addpath('C:\Github\KTH\ECCE\Modlab used in the course folder')

M=1;
p=21;
theta0= 0;
thetac= 0;
phi=  0;
nharm= p*5;

 V = anaspect1ph3lnsc(M, p, theta0, thetac, phi, nharm);

 plot(abs(V/4))