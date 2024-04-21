function x_f = fourser(x,nharm)
%FOURSER: Fourier series expansion
% fourser(x,nharm)
%
% Computes the nharm first terms of the fourier series expansion of
% the time series x. The first element of the output corresponds to the DC
% level.
%
% Staffan Norrga 2004
%
N=length(x);
fftx=fft(x);
x_f=[fftx(1) 2*fftx(2:nharm)]/N;