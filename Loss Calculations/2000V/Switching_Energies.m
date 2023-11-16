load('Eon_Id_89.mat')
Eon_175=Eon;
clear Eon
load('Eoff_Id_89.mat')
Eoff_175=Eoff;
clear Eoff

load('Er_Id_89.mat')
Er_175=Er;
clear Er


plot(Eon_175.I, Eon_175.E)
hold on
plot(Eoff_175.I, Eoff_175.E)
hold on
plot(Er_175.I, Er_175.E)
hold on

%%
Eon_175_Id = linspace(0,max(Eon_175.I),1000); 
figure
Eon_175_inter = interp1(Eon_175 .I,Eon_175 .E,Eon_175_Id);
Eon_175_inter(isnan(Eon_175_inter))=min(Eon_175_inter);
plot(Eon_175.I,Eon_175.E,'o',Eon_175_Id,Eon_175_inter,':x');
% xlim([0 2*pi]);
title('(Default) Linear Interpolation');
%%
Eoff_175_Id = linspace(0,max(Eoff_175.I),1000); 
figure
Eoff_175_inter = interp1(Eoff_175.I,Eoff_175.E,Eoff_175_Id);
Eoff_175_inter(isnan(Eoff_175_inter))=min(Eoff_175_inter);
plot(Eoff_175.I,Eoff_175.E,'o',Eoff_175_Id,Eoff_175_inter,':x');
% xlim([0 2*pi]);
title('(Default) Linear Interpolation');

%%
Er_175_Id = linspace(0,max(Er_175.I),1000); 
figure
Er_175_inter = interp1(Er_175.I,Er_175.E,Er_175_Id);
Er_175_inter(isnan(Er_175_inter))=min(Er_175_inter);
plot(Er_175.I,Er_175.E,'o',Er_175_Id,Er_175_inter,':x');
% xlim([0 2*pi]);
title('(Default) Linear Interpolation');

clear ans Eoff_175 Eon_175 Er_175

close all
