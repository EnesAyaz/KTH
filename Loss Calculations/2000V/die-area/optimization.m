conduction_loss=0.5;

switching_loss=0.5;

motor_loss_a=0;
freq=0.5:0.1:1.5;
die_area=0.5:0.1:2;

motor_loss=[];
inverter_loss=[];
for f=freq
    inverter_loss_x=[];
    motor_loss_x=[];
    for d=die_area
        inverter_loss_x=[inverter_loss_x, (conduction_loss/d +switching_loss*d*f)];
        motor_loss_x=[motor_loss_x, motor_loss_a/f ];
    end
    inverter_loss=[inverter_loss; inverter_loss_x];
    motor_loss= [motor_loss; motor_loss_x];
end


[X,Y] = meshgrid(die_area,freq);
contourf(X,Y,inverter_loss/2+motor_loss/2)
colorbar
xlabel('Die area (p.u)')
ylabel('Frequency (p.u)')
title(' Total Loss (p.u)')