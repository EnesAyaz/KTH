ma=0.8;
theta=0.5;

DA= (1+ma*sin(theta))/2;
DB= (1+ma*sin(theta-2*pi/3))/2;
DC= (1+ma*sin(theta+2*pi/3))/2;



SA_fs_mag= abs((2/pi).*sin(pi.*DA));
SB_fs_mag= abs((2/pi).*sin(pi.*DB));
SC_fs_mag= abs((2/pi).*sin(pi.*DC));

if abs(SA_fs_mag-SB_fs_mag) < SC_fs_mag && SC_fs_mag < (SA_fs_mag+SB_fs_mag)
    
cos_x= (-SC_fs_mag^2+SA_fs_mag^2+SB_fs_mag^2)/(2*SA_fs_mag*SB_fs_mag);
x=acos(cos_x);
PhiB=pi-x;

sin_y=SB_fs_mag*sin(x)/SC_fs_mag;
y=asin(sin_y);
PhiC=y-pi;

elseif SA_fs_mag> SB_fs_mag && SA_fs_mag> SB_fs_mag 
PhiB=pi;
PhiC=pi;
elseif SB_fs_mag> SA_fs_mag && SB_fs_mag> SC_fs_mag 
PhiB=pi;
PhiC=0;
elseif  SC_fs_mag> SA_fs_mag && SC_fs_mag> SB_fs_mag 
PhiB=0;
PhiC=pi;
else 
PhiB=0;
PhiC=0;   
end



% PhiB
mod(PhiB,2*pi)/2/pi
% PhiC
mod(PhiC,2*pi)/2/pi


