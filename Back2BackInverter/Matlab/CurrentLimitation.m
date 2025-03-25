Udc=1250;

M1x=linspace(0,1,10);
M2x=linspace(0,1,10);
delta=linspace(0,90,90);
delta=10;

L=500e-6;
omega_x=2*pi*[50 100 300 500];
omega=omega_x(4);


I_max_y=[];
for M1=M1x
I_max_x=[];
for M2=M2x
Imax= (Udc^2/2)*sqrt(M1^2+M2^2-2*M1*M2*cosd(delta))/(omega*L);
I_max_x=[I_max_x, Imax];
end
I_max_y=[I_max_y;I_max_x ];
end

[X,Y] = meshgrid(M1x,M2x);

mesh(X,Y,I_max_y,'FaceAlpha','0.5')

min(I_max_y)
%%

M1=0.1;
M2=0.1;
delta=10;
Imax= (Udc^2/2)*sqrt(M1^2+M2^2-2*M1*M2*cosd(delta))/(omega*L)

