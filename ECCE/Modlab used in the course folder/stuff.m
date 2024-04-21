function n = stuff(d, noofpts);
%Creates sampled switching functions during one switching cycle
%
% n = stuff(d, noofpts)
%
% noofpts: (integer)
% d: (real vector with three elements) sum(d)=1
% n: (integer vector with three elements)
%
n1=noofpts*d;
n=round(n1);
nrest=n1-n;
sum1=sum(nrest);
[dummy,ind]=max(abs(nrest));   % Identify the element with max rounding error
n(ind)=round( n(ind)+sum1 );   % Adjust the element with max rounding error
if (sum(n)~=noofpts) error('Wrong number'); end;
