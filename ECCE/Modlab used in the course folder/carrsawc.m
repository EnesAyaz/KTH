function carr = carrsawc(fi,curdir)
%Alternating sawtooth carriers
%
% carrsawc(fi,curdir);
%
%
carr=sawtooth(fi,0).*(curdir>0) + sawtooth(fi,1).*(curdir<=0);
