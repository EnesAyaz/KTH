function pwm = pwmmod2(carr,ref)
%Two-evel carrier based PWM modulation with natural sampling

% pwmmod2(carr, ref)
%
%
% The resulting pwm pattern assumes the values -1 and 1.
%
pwm=2*(ref>carr)-1;