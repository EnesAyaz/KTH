function [wt,v]=threeltfcn(noofpts,pwm_angles)
% [wt,v]=threeltfcn(noofpts,pwm_angles)
%
% Create time function v(wt) from a set of switching angles during a period 
% for three-level harmonic elimination. Quarter-wave symmetry is assumed 
% i.e. the angles are only defined during one quarter of the fundamental
% cycle. Due to the quarter-wave symmetry, the number of elements in v 
% and wt is four times the input noofpts.
%
noofangles=length(pwm_angles);
%
wtq=pi/2*(0:noofpts-1)/noofpts;
%
if mod(noofangles,2)==0  % Even # of angles

    vq=zeros(1,noofpts);
%
    for k=1:2:noofangles-1
        vq( find((pwm_angles(k)<wtq) & (pwm_angles(k+1)>wtq)) )=1;
    end

else % Odd # of angles
    
    vq=zeros(1,noofpts);
%
    for k=1:2:noofangles-2
        vq( find((pwm_angles(k)<wtq) & (pwm_angles(k+1)>wtq)) )=1;
    end
    vq(find((pwm_angles(k+2)<wtq) & pi/2>wtq))=1;
end

vh=[vq vq(noofpts:-1:1)];
v=[vh -vh];
clear vq vh;

wt=2*pi*[0:4*noofpts-1]/(4*noofpts);
